
from ..common import httpClient


## Node aware client.
class Node_client(object):

    ## Constructor.
    def __init__(self, nodes):
        self.nodes = nodes

    ## Node client.
    # @param string of uri
    # @param string of search ask
    # @param string of url
    # go through the nodes and send them a serch ask
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
