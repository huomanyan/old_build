import urllib
import json

import ssl
from functools import wraps
def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar

ssl.wrap_socket = sslwrap(ssl.wrap_socket)


class GraphQLClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.token = None

    def execute(self, query):
        return self._send(query)

    def inject_token(self, token):
        self.token = token

    def _send(self, query):
        data = {'query': query}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        if self.token is not None:
            headers['Authorization'] = 'Bearer {}'.format(self.token)

        req = urllib.request.Request(self.endpoint, json.dumps(data).encode('utf-8'), headers)

        try:
            response = urllib.request.urlopen(req)
            return response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            print((e.read()))
            print('')
            raise e