import requests
from xmltodict import unparse

class Requester(object):
    def __init__(self, base_url, app_key, debug=False):
        self.base_url = base_url
        self.app_key = app_key
        self.debug = debug

    def request(self, method, endpoint, body=None, headers=None):
        method = method.upper()
        assert method in ["GET", "POST", "PUT", "DELETE"]

        url = self.base_url + endpoint
        if headers is None:
            headers = dict()
        headers.update({"Content-Type": "application/xml",
                        "Finicity-App-Key": str(self.app_key)})

        if self.debug:
            print("Sending request to {}".format(url))

        if method == "POST":
            body = unparse(body, full_document=False)
            response = requests.post(url, data=body, headers=headers, timeout=30)
        elif method == "PUT":
            body = unparse(body, full_document=False)
            response = requests.put(url, data=body, headers=headers, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            response = requests.get(url, headers=headers, params=body, timeout=30)
        return response
