import asyncio
import socket
import logging
import struct
import re
from email.utils import formatdate

from ..config import settings

logger = logging.getLogger(__name__)

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
MX = 1800 

class SSDPProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        logger.info("SSDP: Advertising on the network...")

    def datagram_received(self, data, addr):
        try:
            msg = data.decode('utf-8', errors='ignore')
            if 'M-SEARCH' in msg:
                # logger.info(f"SSDP: M-SEARCH from {addr}")
                self.handle_search(msg, addr)
        except Exception as e:
            logger.error(f"SSDP: Receive error: {e}")

    def handle_search(self, msg, addr):
        st_match = re.search(r'ST:\s*(.*)', msg, re.IGNORECASE)
        if not st_match: return
        st = st_match.group(1).strip()
        
        targets = [
            "upnp:rootdevice",
            f"uuid:{settings.uuid}",
            "urn:schemas-upnp-org:device:MediaServer:1",
            "urn:schemas-upnp-org:service:ContentDirectory:1",
            "urn:schemas-upnp-org:service:ConnectionManager:1"
        ]
        
        if st == "ssdp:all":
            for t in targets: self.send_response(addr, t)
        elif st in targets:
            self.send_response(addr, st)

    def send_response(self, addr, st):
        usn = f"uuid:{settings.uuid}"
        if st == "upnp:rootdevice": usn += "::upnp:rootdevice"
        elif st != f"uuid:{settings.uuid}": usn += f"::{st}"
            
        response = (
            'HTTP/1.1 200 OK\r\n'
            f'CACHE-CONTROL: max-age={MX}\r\n'
            'EXT:\r\n'
            f'LOCATION: {settings.base_url}/description.xml\r\n'
            f'SERVER: Windows/10.0 UPnP/1.1 PyDLNA/1.0\r\n'
            f'ST: {st}\r\n'
            f'USN: {usn}\r\n'
            'DATE: ' + formatdate(timeval=None, localtime=False, usegmt=True) + '\r\n'
            '\r\n'
        ).encode('utf-8')
        try:
            self.transport.sendto(response, addr)
        except: pass

async def start_ssdp():
    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    local_ip = settings._get_local_ip()
    
    # Bind to ALL interfaces for receiving
    try:
        sock.bind(('', SSDP_PORT))
    except Exception as e:
        logger.warning(f"SSDP: Bind failed (port 1900 might be in use by another UPnP service): {e}")

    try:
        # Join multicast on the specific interface
        mreq = struct.pack("4s4s", socket.inet_aton(SSDP_ADDR), socket.inet_aton(local_ip))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        # Multicast TTL 4 for broader reach
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
        # Set outgoing interface
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local_ip))
    except Exception as e:
        logger.error(f"SSDP: Multicast setup failed: {e}")

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: SSDPProtocol(),
        sock=sock
    )
    
    # Aggressive notification strategy
    async def advertiser():
        # High-frequency burst at startup
        for i in range(10):
            send_alive(transport, local_ip)
            await asyncio.sleep(1)
        
        # Periodic refresh
        while True:
            await asyncio.sleep(60) # Notifying every minute instead of 450s 
            send_alive(transport, local_ip)

    asyncio.create_task(advertiser())
    return transport, protocol

def send_alive(transport, local_ip):
    targets = [
        "upnp:rootdevice",
        f"uuid:{settings.uuid}",
        "urn:schemas-upnp-org:device:MediaServer:1",
        "urn:schemas-upnp-org:service:ContentDirectory:1",
        "urn:schemas-upnp-org:service:ConnectionManager:1"
    ]
    
    date_str = formatdate(timeval=None, localtime=False, usegmt=True)
    
    for nt in targets:
        usn = f"uuid:{settings.uuid}"
        if nt == "upnp:rootdevice": usn += "::upnp:rootdevice"
        elif nt != f"uuid:{settings.uuid}": usn += f"::{nt}"
            
        msg = (
            'NOTIFY * HTTP/1.1\r\n'
            f'HOST: {SSDP_ADDR}:{SSDP_PORT}\r\n'
            f'CACHE-CONTROL: max-age={MX}\r\n'
            f'LOCATION: {settings.base_url}/description.xml\r\n'
            f'NT: {nt}\r\n'
            'NTS: ssdp:alive\r\n'
            f'SERVER: Windows/10.0 UPnP/1.1 PyDLNA/1.0\r\n'
            f'USN: {usn}\r\n'
            f'DATE: {date_str}\r\n'
            '\r\n'
        ).encode('utf-8')
        try:
            transport.sendto(msg, (SSDP_ADDR, SSDP_PORT))
        except Exception as e:
            # logger.error(f"SSDP Notify error: {e}")
            pass
