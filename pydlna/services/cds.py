import logging
import base64
import re
from pathlib import Path
from sqlalchemy import select, func
from xml.etree.ElementTree import Element, tostring

from pydlna.config import settings
from pydlna.db import get_session
from pydlna.models import MediaItem, MediaType
from pydlna.xml_utils import create_didl_item, create_didl_container, wrap_soap_response

logger = logging.getLogger(__name__)

SERVICE_TYPE = "urn:schemas-upnp-org:service:ContentDirectory:1"

class ContentDirectoryService:
    def __init__(self):
        pass

    async def handle_action(self, action, args):
        if action == "GetSortCapabilities":
            return wrap_soap_response("GetSortCapabilities", SERVICE_TYPE, {"SortCaps": ""})
        elif action == "GetSearchCapabilities":
            return wrap_soap_response("GetSearchCapabilities", SERVICE_TYPE, {"SearchCaps": ""})
        elif action == "GetSystemUpdateID":
            return wrap_soap_response("GetSystemUpdateID", SERVICE_TYPE, {"Id": "1"})
        elif action == "Browse":
            return await self.browse(args)
        else:
            return wrap_soap_response(action, SERVICE_TYPE, {})

    async def browse(self, args):
        object_id = args.get('ObjectID', '0')
        browse_flag = args.get('BrowseFlag', 'BrowseDirectChildren')
        start_index = int(args.get('StartingIndex', 0))
        requested_count = int(args.get('RequestedCount', 0))
        
        logger.info(f"CDS Browse: ID={object_id}, Flag={browse_flag}")
        all_results = []

        try:
            async with get_session() as session:
                if browse_flag == 'BrowseMetadata':
                    if object_id == '0':
                        all_results.append(create_didl_container("0", settings.friendly_name, "-1", -1, settings.base_url))
                    elif object_id.startswith("fold:"):
                        try:
                            f_path = Path(base64.b64decode(object_id[5:].encode()).decode()).resolve()
                            all_results.append(create_didl_container(object_id, f_path.name or str(f_path), "0", -1, settings.base_url))
                        except: pass
                    elif object_id.isdigit():
                        item = await session.get(MediaItem, int(object_id))
                        if item: all_results.append(create_didl_item(item, settings.base_url))
                
                else:
                    if object_id == "0":
                        for p in settings.media_paths:
                            if p.exists():
                                p_res = p.resolve()
                                safe_id = "fold:" + base64.b64encode(str(p_res).encode()).decode()
                                all_results.append(create_didl_container(safe_id, p.name or str(p), "0", -1, settings.base_url))
                    
                    elif object_id.startswith("fold:"):
                        try:
                            folder_path = Path(base64.b64decode(object_id[5:].encode()).decode()).resolve()
                            if folder_path.exists():
                                for entry in folder_path.iterdir():
                                    if entry.is_dir() and not entry.name.startswith('.'):
                                        entry_res = entry.resolve()
                                        safe_id = "fold:" + base64.b64encode(str(entry_res).encode()).decode()
                                        all_results.append(create_didl_container(safe_id, entry.name, object_id, -1, settings.base_url))
                                
                                search_path = str(folder_path)
                                stmt = select(MediaItem).where(func.lower(MediaItem.parent_path) == search_path.lower())
                                res = await session.execute(stmt)
                                items = res.scalars().all()
                                for item in items:
                                    all_results.append(create_didl_item(item, settings.base_url, parent_id=object_id))
                        except Exception as e:
                            logger.error(f"Error browsing folder {object_id}: {e}")

        except Exception as ge:
            logger.error(f"Global Browse Error: {ge}")

        total_matches = len(all_results)
        sliced = all_results[start_index:]
        if requested_count > 0: sliced = sliced[:requested_count]
        
        didl_header = (
            '<DIDL-Lite '
            'xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" '
            'xmlns:sec="http://www.sec.co.kr/">'
        )
        inner_xml = [tostring(r, encoding='unicode') for r in sliced]
        didl_xml = didl_header + "".join(inner_xml) + "</DIDL-Lite>"
        
        return wrap_soap_response("Browse", SERVICE_TYPE, {
            "Result": didl_xml,
            "NumberReturned": str(len(sliced)),
            "TotalMatches": str(total_matches),
            "UpdateID": "1"
        })
