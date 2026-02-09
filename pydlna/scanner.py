import asyncio
import os
import logging
from pathlib import Path
from datetime import datetime
from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import mimetypes
import subprocess
import json
import time

from pydlna.models import MediaItem, MediaType
from pydlna.db import get_session
from pydlna.config import settings

# ... imports

logger = logging.getLogger(__name__)

# Global lock to prevent concurrent scans
SCAN_LOCK = asyncio.Lock()

VIDEO_EXTS = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'}
AUDIO_EXTS = {'.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

class MediaScanner:
    def __init__(self, media_paths=None):
        # Ignore passed paths, use settings directly to ensure freshness
        pass
    
    async def scan(self):
        # Use current settings
        current_paths = settings.media_paths
        
        if SCAN_LOCK.locked():
            logger.warning("Scan already in progress. Skipping.")
            return

        async with SCAN_LOCK:
            logger.info(f"Starting sync of {len(current_paths)} paths")
            start_time = time.time()
            
            # 1. Gather all files from Disk (Threaded I/O)
            loop = asyncio.get_running_loop()
            # Pass paths explicitly to gather_files
            disk_map = await loop.run_in_executor(None, self._gather_files, current_paths)
            
            async with get_session() as session:
                # ... rest of logic remains, just context setup first ...
                # 2. Gather all files from DB
                logger.info("Fetching existing database records...")
                stmt = select(MediaItem.file_path)
                result = await session.execute(stmt)
                db_paths = result.scalars().all()
                
                # Normalize DB paths to match OS separator for comparison
                # If DB has forward slash on Windows, replace with backslash for the keys
                # This ensures we don't delete-then-add just because of separators
                db_map = {}
                for p in db_paths:
                    # Normalize separators to OS default (backslash on win)
                    norm_sep_path = str(Path(p).resolve())
                    db_map[norm_sep_path.lower()] = p 

                # 3. Calculate Diff using normalized keys
                disk_keys = set(disk_map.keys())
                db_keys = set(db_map.keys())
                
                to_add_keys = disk_keys - db_keys
                to_remove_keys = db_keys - disk_keys
                
                logger.info(f"Sync calculation: {len(db_keys)} existing, {len(to_add_keys)} new, {len(to_remove_keys)} removed.")

                # ... (rest of logic)

            # 4. Remove Deleted
            if to_remove_keys:
                # Retrieve original paths to delete
                to_remove_paths = [db_map[k] for k in to_remove_keys]
                
                chunk_size = 900
                for i in range(0, len(to_remove_paths), chunk_size):
                    chunk = to_remove_paths[i:i+chunk_size]
                    stmt = delete(MediaItem).where(MediaItem.file_path.in_(chunk))
                    await session.execute(stmt)
                
                try:
                    await session.commit()
                    logger.info(f"Removed {len(to_remove_paths)} stale items.")
                except Exception as e:
                    logger.error(f"Failed to commit deletions: {e}")
                    await session.rollback()

            # 5. Add New
            if to_add_keys:
                count = 0
                for k in to_add_keys:
                    real_path, mtype = disk_map[k]
                    try:
                        # Extract metadata
                        item = await loop.run_in_executor(None, self._extract_metadata_sync, Path(real_path), mtype)
                        
                        if item:
                            session.add(item)
                            count += 1
                            
                            if count % 20 == 0:
                                await session.commit()
                    except Exception as e:
                        err_msg = str(e)
                        if "no column named" in err_msg:
                            logger.error(f"SCHEMA MISMATCH: Column missing in database. YOU MUST CLICK 'CLEAR CACHE' in the Admin tab to fix this.")
                        else:
                            logger.error(f"Error adding {real_path}: {e}")
                            
                        await session.rollback()
                        # On rollback, the pending item is removed from session. 
                        # We continue to next item. 
                
                # Final commit
                try:
                    await session.commit()
                    logger.info(f"Added {count} new items.")
                except Exception as e:
                    logger.error(f"Final commit failed: {e}")
                    await session.rollback()

        duration = time.time() - start_time
        logger.info(f"Scan complete in {duration:.2f}s")
    
    def _gather_files(self, paths: list[Path]) -> dict:
        """Returns {lower_path: (abs_path, media_type)}"""
        found = {}
        for root_path in paths:
            if not root_path.exists():
                continue
            for root, dirs, files in os.walk(root_path):
                # Filter hidden dirs
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for f in files:
                    if f.startswith('.'): continue
                    path = Path(root) / f
                    # Use abspath to normalize separators and resolve relative segments
                    abs_path_str = str(path.resolve())
                    
                    ext = path.suffix.lower()
                    mtype = MediaType.UNKNOWN
                    if ext in VIDEO_EXTS: mtype = MediaType.VIDEO
                    elif ext in AUDIO_EXTS: mtype = MediaType.AUDIO
                    elif ext in IMAGE_EXTS: mtype = MediaType.IMAGE
                    else: continue
                    
                    found[abs_path_str.lower()] = (abs_path_str, mtype)
        return found
    
    def _extract_metadata_sync(self, path: Path, media_type: MediaType) -> MediaItem:
        # Re-verify existence just in case
        if not path.exists(): return None
        
        mime, _ = mimetypes.guess_type(path)
        try:
            stat = path.stat()
        except OSError: return None
            
        item = MediaItem(
            file_path=str(path.resolve()),
            filename=path.name,
            parent_path=str(path.parent.resolve()),
            title=path.stem,
            media_type=media_type,
            mime_type=mime or "application/octet-stream",
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime)
        )
        
        if media_type == MediaType.VIDEO:
            try:
                # On Windows, hide the console window for subprocesses
                creationflags = 0x08000000 if os.name == 'nt' else 0
                cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', str(path)]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, encoding='utf-8', errors='ignore', creationflags=creationflags)
                if res.returncode == 0:
                    data = json.loads(res.stdout)
                    if 'format' in data and 'duration' in data['format']:
                        item.duration = float(data['format']['duration'])
                    sub_count = 0
                    aud_count = 0
                    for stream in data.get('streams', []):
                        ctype = stream.get('codec_type')
                        if ctype == 'video':
                            item.width = int(stream.get('width', 0))
                            item.height = int(stream.get('height', 0))
                        elif ctype == 'audio':
                            aud_count += 1
                        elif ctype == 'subtitle':
                            sub_count += 1
                    
                    item.audio_tracks = aud_count
                    item.subtitle_tracks = sub_count
                    
                    # Check for EXTERNAL subtitles (.srt)
                    try:
                        srt_path = path.with_suffix('.srt')
                        if srt_path.exists():
                            # We'll treat external as an additional track (index -1 maybe?)
                            # For simplicity now, just increment count
                            item.subtitle_tracks += 1
                    except Exception: pass
            except Exception: pass
        return item
