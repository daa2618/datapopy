
import requests
from urllib.parse import urlsplit, urlunsplit


class Response:
    def __init__(self, url, **kwargs):
        self.url = url
        self.params=kwargs.get("params")
        self.headers=kwargs.get("headers")
        self.auth=kwargs.get("auth")
        
    def assert_response(self):
        #print(f"Getting the response from {self.url}")
        response = requests.get(url=self.url,
                               params=self.params,
                               headers=self.headers,
                               auth=self.auth)
        assert response.status_code == 200, response.raise_for_status()
        #print("The response was obtained")
        return response
    
    def get_base_url(self):
        split_url = urlsplit(self.url)
        return "://".join([split_url.scheme, split_url.netloc])
