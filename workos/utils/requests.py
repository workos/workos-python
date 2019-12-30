import requests

import workos

REQUEST_METHOD_GET = 'get'
REQUEST_METHOD_POST = 'post'

class RequestHelper(object):
    def __init__(self):
        self.set_base_api_url(workos.base_api_url)

    def set_base_api_url(self, base_api_url):
        self.base_api_url = '{}{{}}'.format(base_api_url)

    def generate_api_url(self, path):
        return self.base_api_url.format(path)

    def request(self, path, method=REQUEST_METHOD_GET, params=None):
        url = self.generate_api_url(path)
        response = getattr(requests, method)(url, params=params)

        return response.json()