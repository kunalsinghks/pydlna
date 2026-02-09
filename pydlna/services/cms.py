from pydlna.xml_utils import wrap_soap_response

SERVICE_TYPE = "urn:schemas-upnp-org:service:ConnectionManager:1"

class ConnectionManagerService:
    async def handle_action(self, action, args):
        if action == "GetProtocolInfo":
            # List supported formats
            # Simplification: Support everything over http-get
            source_protocols = [
                "http-get:*:video/mp4:*",
                "http-get:*:video/x-matroska:*",
                "http-get:*:video/avi:*",
                "http-get:*:audio/mpeg:*",
                "http-get:*:image/jpeg:*",
                "http-get:*:*:*"
            ]
            
            return wrap_soap_response("GetProtocolInfo", SERVICE_TYPE, {
                "Source": ",".join(source_protocols),
                "Sink": ""
            })
            
        elif action == "PrepareForConnection":
             return wrap_soap_response("PrepareForConnection", SERVICE_TYPE, {
                 "ConnectionID": "0",
                 "AVTransportID": "0",
                 "RcsID": "0"
             })
             
        elif action == "ConnectionComplete":
             return wrap_soap_response("ConnectionComplete", SERVICE_TYPE, {})
        
        elif action == "GetCurrentConnectionIDs":
             return wrap_soap_response("GetCurrentConnectionIDs", SERVICE_TYPE, {
                 "ConnectionIDs": "0"
             })

        elif action == "GetCurrentConnectionInfo":
             return wrap_soap_response("GetCurrentConnectionInfo", SERVICE_TYPE, {
                 "RcsID": "0",
                 "AVTransportID": "0",
                 "ProtocolInfo": "http-get:*:*:*",
                 "PeerConnectionManager": "",
                 "PeerConnectionID": "-1",
                 "Direction": "Output",
                 "Status": "OK"
             })
        
        return b""
