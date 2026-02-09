from xml.etree.ElementTree import Element, SubElement, tostring
import urllib.parse
from xml.sax.saxutils import escape

def create_didl_item(item, base_url, parent_id="0"):
    # item is a MediaItem model from DB
    didl = Element('item', id=str(item.id), parentID=str(parent_id), restricted="0")
    
    SubElement(didl, 'dc:title').text = item.title
    
    # Class
    upnp_class = "object.item"
    if item.media_type == "video":
        upnp_class = "object.item.videoItem"
    elif item.media_type == "audio":
        upnp_class = "object.item.audioItem"
    elif item.media_type == "image":
        upnp_class = "object.item.imageItem"
        
    SubElement(didl, 'upnp:class').text = upnp_class
    SubElement(didl, 'dc:date').text = item.last_modified.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Resource
    filename_enc = urllib.parse.quote(item.filename)
    res_url = f"{base_url}/media/{item.id}/{filename_enc}"
    # Adding DLNA flag 01700000... for broad compatibility
    res = SubElement(didl, 'res', protocolInfo=f"http-get:*:{item.mime_type}:DLNA.ORG_OP=01;DLNA.ORG_CI=0;DLNA.ORG_FLAGS=01700000000000000000000000000000")
    res.text = res_url
    res.set('size', str(item.size))
    
    if item.duration:
        hours = int(item.duration // 3600)
        minutes = int((item.duration % 3600) // 60)
        seconds = int(item.duration % 60)
        res.set('duration', f"{hours}:{minutes:02}:{seconds:02}.000")

    return didl

def create_didl_container(container_id, title, parent_id, child_count, base_url):
    didl = Element('container', id=str(container_id), parentID=str(parent_id), restricted="0", searchable="0")
    SubElement(didl, 'dc:title').text = title
    SubElement(didl, 'upnp:class').text = "object.container.storageFolder"
    return didl 

def wrap_soap_response(action_name, service_type, return_args):
    # Manual construction to avoid global namespace issues and ensure clean output
    xml = ['<?xml version="1.0" encoding="utf-8"?>']
    xml.append('<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">')
    xml.append('<s:Body>')
    xml.append(f'<u:{action_name}Response xmlns:u="{service_type}">')
    
    for key, value in return_args.items():
        val = escape(value) if isinstance(value, str) else value
        xml.append(f'<{key}>{val}</{key}>')
    
    xml.append(f'</u:{action_name}Response>')
    xml.append('</s:Body>')
    xml.append('</s:Envelope>')
    
    return '\n'.join(xml).encode('utf-8')
