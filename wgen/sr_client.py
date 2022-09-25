import http.client
import json


class AqmSrClient:
    def __init__(self, api_host, api_key):
        self._api_host = api_host
        self._api_key = api_key
        self._headers = {
            "X-RapidAPI-Key": self._api_key,
            "X-RapidAPI-Host": self._api_host,
        }
        print(repr(self._headers))

    def get_spot_ids(self):
        print(self._api_host)
        conn = http.client.HTTPSConnection(self._api_host)
        conn.request("GET", f"/spots", headers=self._headers)
        res = conn.getresponse()
        data = res.read()
        data.decode("utf-8")
        result = json.loads(data)
        conn.close()
        return result

    def get_spot_info(self, spot_id):
        conn = http.client.HTTPSConnection(self._api_host)
        conn.request("GET", f"/{spot_id}/info", headers=self._headers)
        res = conn.getresponse()
        data = res.read()
        data.decode("utf-8")
        result = json.loads(data)
        conn.close()
        return result

    def get_waves(self, spot_id):
        conn = http.client.HTTPSConnection(self._api_host)
        conn.request("GET", f"/{spot_id}/waves", headers=self._headers)
        res = conn.getresponse()
        data = res.read()
        data.decode("utf-8")
        result = json.loads(data)
        conn.close()
        return result
