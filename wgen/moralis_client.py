import http.client
import json
import base64
from random import randint
from time import sleep


class MoralisClient:
    def __init__(self, api_host, api_key):
        self._api_host = api_host
        self._api_key = api_key
        self._headers = {
            "accept": "application/json",
            "X-API-Key": self._api_key,
            "Content-Type": "application/json",
        }
        self._conn = http.client.HTTPSConnection(self._api_host)

    def ipfs_upload_folder(self, ipfs_path, content, retry_limit=3, call_count=0):
        conn = http.client.HTTPSConnection(self._api_host)
        content_b64 = base64.b64encode(content.encode("utf-8"))
        content_b64_str = content_b64.decode("utf-8")
        body = [{"path": ipfs_path, "content": content_b64.decode("utf-8")}]
        body_json = json.dumps(body)
        print(f"content_json={content}")
        print(f"content_b64={content_b64_str}")
        print(f"body_json={body_json}")
        conn.request(
            "POST", "/api/v2/ipfs/uploadFolder", body=body_json, headers=self._headers
        )
        response = conn.getresponse()
        r_status = response.status
        r_reason = response.reason
        result = None
        print(r_status, r_reason)
        if r_status == 429 and r_reason == "Too Many Requests":
            conn.close()
            call_count += 1
            if call_count < retry_limit:
                sleep(randint(1, 5))
                return self.ipfs_upload_folder(
                    ipfs_path, content, retry_limit=retry_limit, call_count=call_count
                )
        elif r_status == 200:
            data = response.read()
            result = None
            conn.close()
            if data:
                data.decode("utf-8")
                result = json.loads(data)
        return {"status": r_status, "reason": r_reason, "data": result}
