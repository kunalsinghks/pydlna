from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from contextlib import asynccontextmanager
import logging
import os
import secrets
import mimetypes
import subprocess
import re
import asyncio
import signal
from pathlib import Path
from pydantic import BaseModel
from xml.etree import ElementTree

from ..config import settings, update_media_paths, update_settings
from ..db import get_session, init_db
from ..models import MediaItem
from ..services.cds import ContentDirectoryService
from ..services.cms import ConnectionManagerService
from ..scanner import MediaScanner
from sqlmodel import select

logger = logging.getLogger(__name__)

# --- Models for API ---
class SettingsUpdate(BaseModel):
    friendly_name: str | None = None
    port: int | None = None

class PathsUpdate(BaseModel):
    paths: list[str]

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server lifespan starting...")
    await init_db()
    
    from ..core.ssdp import start_ssdp
    transport, protocol = await start_ssdp()
    
    scanner = MediaScanner(settings.media_paths)
    
    async def periodic_scan():
        while True:
            try:
                await scanner.scan()
            except Exception as e:
                logger.error(f"Scheduled scan failed: {e}")
            await asyncio.sleep(300) 

    scan_task = asyncio.create_task(periodic_scan())
    yield
    scan_task.cancel()
    if transport:
        transport.close()

app = FastAPI(title=settings.app_name, lifespan=lifespan)
templates = Jinja2Templates(directory="d:/Anti Gravity/Article/pydlna/web/templates")

cds_service = ContentDirectoryService()
cms_service = ConnectionManagerService()

# --- DLNA / UPnP Discovery ---
@app.get("/description.xml")
async def get_description():
    xml_content = f"""<?xml version="1.0"?>
<root xmlns="urn:schemas-upnp-org:device-1-0">
  <specVersion><major>1</major><minor>0</minor></specVersion>
  <device>
    <deviceType>urn:schemas-upnp-org:device:MediaServer:1</deviceType>
    <friendlyName>{settings.friendly_name}</friendlyName>
    <manufacturer>PyDLNA Team</manufacturer>
    <modelName>PyDLNA</modelName>
    <UDN>uuid:{settings.uuid}</UDN>
    <serviceList>
      <service>
        <serviceType>urn:schemas-upnp-org:service:ContentDirectory:1</serviceType>
        <serviceId>urn:upnp-org:serviceId:ContentDirectory</serviceId>
        <SCPDURL>/cds_scpd.xml</SCPDURL>
        <controlURL>/ContentDirectory/control</controlURL>
        <eventSubURL>/ContentDirectory/event</eventSubURL>
      </service>
      <service>
        <serviceType>urn:schemas-upnp-org:service:ConnectionManager:1</serviceType>
        <serviceId>urn:upnp-org:serviceId:ConnectionManager</serviceId>
        <SCPDURL>/cms_scpd.xml</SCPDURL>
        <controlURL>/ConnectionManager/control</controlURL>
        <eventSubURL>/ConnectionManager/event</eventSubURL>
      </service>
    </serviceList>
  </device>
</root>"""
    return Response(content=xml_content, media_type="text/xml")

@app.get("/cds_scpd.xml")
async def get_cds_scpd():
    # Full SCDP for ContentDirectory to satisfy picky clients
    xml_content = """<?xml version="1.0"?>
<scpd xmlns="urn:schemas-upnp-org:service-1-0">
  <specVersion><major>1</major><minor>0</minor></specVersion>
  <actionList>
    <action><name>GetSortCapabilities</name><argumentList><argument><name>SortCaps</name><direction>out</direction><relatedStateVariable>SortCapabilities</relatedStateVariable></argument></argumentList></action>
    <action><name>GetSearchCapabilities</name><argumentList><argument><name>SearchCaps</name><direction>out</direction><relatedStateVariable>SearchCapabilities</relatedStateVariable></argument></argumentList></action>
    <action><name>GetSystemUpdateID</name><argumentList><argument><name>Id</name><direction>out</direction><relatedStateVariable>SystemUpdateID</relatedStateVariable></argument></argumentList></action>
    <action>
      <name>Browse</name>
      <argumentList>
        <argument><name>ObjectID</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_ObjectID</relatedStateVariable></argument>
        <argument><name>BrowseFlag</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_BrowseFlag</relatedStateVariable></argument>
        <argument><name>Filter</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_Filter</relatedStateVariable></argument>
        <argument><name>StartingIndex</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_Index</relatedStateVariable></argument>
        <argument><name>RequestedCount</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable></argument>
        <argument><name>SortCriteria</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_SortCriteria</relatedStateVariable></argument>
        <argument><name>Result</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_Result</relatedStateVariable></argument>
        <argument><name>NumberReturned</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable></argument>
        <argument><name>TotalMatches</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable></argument>
        <argument><name>UpdateID</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_UpdateID</relatedStateVariable></argument>
      </argumentList>
    </action>
  </actionList>
  <serviceStateTable>
    <stateVariable sendEvents="no"><name>SearchCapabilities</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>SortCapabilities</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="yes"><name>SystemUpdateID</name><dataType>ui4</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_ObjectID</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_Result</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_BrowseFlag</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_Filter</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_Index</name><dataType>ui4</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_Count</name><dataType>ui4</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_SortCriteria</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>A_ARG_TYPE_UpdateID</name><dataType>ui4</dataType></stateVariable>
  </serviceStateTable>
</scpd>"""
    return Response(content=xml_content, media_type="text/xml")

@app.get("/cms_scpd.xml")
async def get_cms_scpd():
    xml_content = """<?xml version="1.0"?>
<scpd xmlns="urn:schemas-upnp-org:service-1-0">
  <specVersion><major>1</major><minor>0</minor></specVersion>
  <actionList>
    <action><name>GetProtocolInfo</name><argumentList><argument><name>Source</name><direction>out</direction><relatedStateVariable>SourceProtocolInfo</relatedStateVariable></argument><argument><name>Sink</name><direction>out</direction><relatedStateVariable>SinkProtocolInfo</relatedStateVariable></argument></argumentList></action>
  </actionList>
  <serviceStateTable>
    <stateVariable sendEvents="yes"><name>SourceProtocolInfo</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="yes"><name>SinkProtocolInfo</name><dataType>string</dataType></stateVariable>
    <stateVariable sendEvents="no"><name>CurrentConnectionIDs</name><dataType>string</dataType></stateVariable>
  </serviceStateTable>
</scpd>"""
    return Response(content=xml_content, media_type="text/xml")

# --- Control Action Handlers ---
@app.post("/ContentDirectory/control")
async def cds_control(request: Request):
    soap_action = request.headers.get("SOAPACTION", "")
    action = soap_action.replace('"', '').split('#')[-1]
    body_str = (await request.body()).decode('utf-8', errors='ignore')
    args = {}
    for tag in ['ObjectID', 'BrowseFlag', 'StartingIndex', 'RequestedCount']:
        pattern = rf'<[^/>:]*?:?{tag}[^>]*>(.*?)</[^>]*?:?{tag}>'
        match = re.search(pattern, body_str, re.IGNORECASE | re.DOTALL)
        if match: args[tag] = match.group(1).strip()
    response_xml = await cds_service.handle_action(action, args)
    return Response(content=response_xml, media_type="text/xml; charset=utf-8")

@app.post("/ConnectionManager/control")
async def cms_control(request: Request):
    soap_action = request.headers.get("SOAPACTION", "")
    action = soap_action.replace('"', '').split('#')[-1]
    response_xml = await cms_service.handle_action(action, {})
    return Response(content=response_xml, media_type="text/xml")

# --- Web UI Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.app_name})

@app.get("/api/settings")
async def get_settings_api():
    return {
        "media_paths": [str(p) for p in settings.media_paths],
        "port": settings.port,
        "friendly_name": settings.friendly_name,
        "uuid": settings.uuid
    }

@app.post("/api/settings/general")
async def update_general_settings(update: SettingsUpdate):
    update_settings(update.model_dump(exclude_unset=True))
    return {"status": "ok"}

@app.post("/api/settings/paths")
async def update_paths_api(update: PathsUpdate):
    update_media_paths(update.paths)
    return {"status": "ok"}

@app.get("/api/library/browse")
async def api_browse():
    async with get_session() as session:
        stmt = select(MediaItem).order_by(MediaItem.title)
        res = await session.execute(stmt)
        return res.scalars().all()

@app.post("/api/control/{action}")
async def api_control(action: str):
    if action == "rescan":
        scanner = MediaScanner(settings.media_paths)
        asyncio.create_task(scanner.scan())
        return {"status": "scanning"}
    elif action == "clear_cache":
        async with get_session() as session:
            from sqlmodel import delete
            await session.execute(delete(MediaItem))
            await session.commit()
        return {"status": "cleared"}
    elif action == "stop":
        os.kill(os.getpid(), signal.SIGINT)
        return {"status": "stopping"}
    return {"status": "unknown_action"}

# --- Robust Streaming with Range Support ---
def get_range(range_header: str, file_size: int):
    if not range_header: return None
    match = re.match(r"bytes=(\d+)-(\d+)?", range_header)
    if not match: return None
    
    start = int(match.group(1))
    end = match.group(2)
    end = int(end) if end else file_size - 1
    
    if start >= file_size: return None
    if end >= file_size: end = file_size - 1
    return start, end

@app.get("/media/{item_id}/{filename}")
async def stream_media(item_id: int, filename: str, request: Request):
    async with get_session() as session:
        item = await session.get(MediaItem, item_id)
        if not item or not os.path.exists(item.file_path):
            raise HTTPException(status_code=404)
        
        file_path = item.file_path
        file_size = os.path.getsize(file_path)
        mime = item.mime_type or mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        range_header = request.headers.get("Range")
        r = get_range(range_header, file_size)
        
        if r:
            start, end = r
            chunk_size = end - start + 1
            
            def file_iterator():
                with open(file_path, "rb") as f:
                    f.seek(start)
                    remaining = chunk_size
                    while remaining > 0:
                        to_read = min(remaining, 65536)
                        data = f.read(to_read)
                        if not data: break
                        yield data
                        remaining -= len(data)

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(chunk_size),
                "Content-Type": mime,
                "Access-Control-Allow-Origin": "*",
            }
            return StreamingResponse(file_iterator(), status_code=206, headers=headers)
        
        # Default full file
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": mime,
            "Access-Control-Allow-Origin": "*",
        }
        
        def full_file_iterator():
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(65536)
                    if not data: break
                    yield data

        return StreamingResponse(full_file_iterator(), headers=headers)

@app.get("/api/media/{item_id}/play.m3u")
async def get_m3u(item_id: int):
    async with get_session() as session:
        item = await session.get(MediaItem, item_id)
        if not item: raise HTTPException(status_code=404)
        m3u = f"#EXTM3U\n#EXTINF:-1,{item.title}\n{settings.base_url}/media/{item.id}/{item.filename}\n"
        return Response(content=m3u, media_type="audio/x-mpegurl")
