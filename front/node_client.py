
import contextlib
import datetime
import errno
import os
import socket
import struct
import sys
import traceback
import urlparse

from ..common import constants
from ..common import xml_func
from ..common import http_util
from ..common import constants
from ..common import util
from ..common import xml_func
from ..common import http_util
from ..common import xml_funcs
from ..common import httpServer
from ..common import memory
from ..common import httpService
from ..common import httpClient

class Node_client(object):

    def __init__(self, nodes):
        self.nodes = nodes
        
        
    def n_client (self, uri_beg, search, url):
        output = []
        for node in self.nodes:
            uri = uri_beg+search
            Client = httpClient.Client(url, self.nodes[node].get('ip'), self.nodes[node].get('port'))
            output.append(Client.client(uri))
        return output
            
            