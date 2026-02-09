import urllib.request
import urllib.parse
import json
import traceback

BASE_URL = "http://localhost:8200"

def test_stream_size():
    try:
        # 1. Get Library Item
        req = urllib.request.Request(f"{BASE_URL}/api/library/browse")
        req.add_header("Authorization", "Basic YWRtaW46YWRtaW4=")
        
        item = None
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if not data:
                print("No items.")
                return
            item = data[0]

        print(f"Testing Item: {item['title']} (ID: {item['id']})")
        
        # Construct Stream URL
        filename_enc = urllib.parse.quote(item['filename'])
        stream_url = f"{BASE_URL}/media/{item['id']}/{filename_enc}"
        
        print(f"Stream URL: {stream_url}")
        
        # 2. Check Stream Headers (GET with Range 0-1)
        req_stream = urllib.request.Request(stream_url)
        req_stream.add_header("Range", "bytes=0-1")
        
        with urllib.request.urlopen(req_stream) as stream_resp:
            print(f"Status: {stream_resp.status}")
            print(f"Content-Type: {stream_resp.headers.get('Content-Type')}")
            cr = stream_resp.headers.get('Content-Range')
            print(f"Content-Range: {cr}")
            
            if cr:
                total_size = cr.split('/')[-1]
                print(f"Total File Size: {total_size} bytes")
            else:
                print("No Content-Range header!")
                    
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_stream_size()
