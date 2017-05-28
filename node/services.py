
import urlparse
import socket
import os

from ..common import httpService
from ..common import xml_funcs

## multicast port
MULTI_PORT = 8123
## multicast ip address
IP = '225.0.0.250'
## how much connections on multicast
MYTTL = 1

##Search service.
class Search_service (httpService.Http_service):

    ## Constructor.
    def __init__(self, memory):
        self.memory = memory

    ## Search service.
    # @param params dict of params that the function needs
    def service(self, params, object):
        pars_uri = urlparse.parse_qs(params['uri'][8:])
        files, ids = object.find_name(self.memory, pars_uri.get('Search')[0])
        xml = xml_funcs.Xml()
        output = xml.xml_form(files, ids)

        ret = {
            'status': '200',
            'message': 'OK',
            'headers': {
                'Content-Type': 'text/xml',
            },
            'content': output,
        }
        return ret

    ## Find file names.
    # @param list of a memory map
    # #param string of a search ask
    # searching in memory map for a right file names.
    def find_name(self, mem, name):
        files = []
        ids = []
        for i in range(len(mem)):
            if name in mem[i]['filename']:
                files.append(mem[i]['filename'])
                ids.append(i)
        return files, ids

## Id search of files.
class Id_service (httpService.Http_service):

    ## Constructor.
    def __init__(self, memory):
        self.memory = memory

    ## Id search service.
    # @param params dict of params that the function needs
    # get a file from the right place in the memory by id
    def service(self, params, object):
        pars_uri = urlparse.parse_qs(params['uri'][10:])
        file_name = os.path.join(
            self.memory[int(pars_uri.get('id')[0])]['root'],
            self.memory[int(pars_uri.get('id')[0])]['filename'],
        )
        ret = {
            'status': '200',
            'message': 'OK',
            'file_name': file_name,
            'headers': {
                'Content-Type': 'text/html',
            }
        }
        return ret

## Multicast sender
class Sender (httpService.Http_service):

    ## Constructor.
    def __init__(self):
        pass

    ## Multicast sender service.
    # @param params dict of params that the function needs
    # sending a port to front server by multicast
    def service(self, params, object):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        s.sendto('node,%s' % (params['port']), (IP, MULTI_PORT))
