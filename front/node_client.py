
from ..common import httpClient


class Node_client(object):

    def __init__(self, nodes):
        self.nodes = nodes

    def n_client(self, uri_beg, search, url):
        output = []
        for node in self.nodes:
            uri = uri_beg+search
            Client = httpClient.Client(
                            url, self.nodes[node].get('ip'),
                            self.nodes[node].get('port')
            )
            output.append(Client.client(uri))
        return output
