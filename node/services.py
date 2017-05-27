
import urlparse
import socket
import os

from ..common import httpService
from ..common import xml_funcs

MYPORT = 8123
IP = '225.0.0.250'
MYTTL = 1


class Search_service (httpService.Http_service):

    def __init__(self, memory):
        self.memory = memory

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

    def find_name(self, mem, name):
        files = []
        ids = []
        for i in range(len(mem)):
            if name in mem[i]['filename']:
                files.append(mem[i]['filename'])
                ids.append(i)
        return files, ids


class Id_service (httpService.Http_service):

    def __init__(self, memory):
        self.memory = memory

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


class Sender (httpService.Http_service):

    def __init__(self):
        pass

    def service(self, params, object):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        s.sendto('node,%s' % (params['port']), (IP, MYPORT))
