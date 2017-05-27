
import datetime
import socket
import struct
import urlparse

from ..common import xml_funcs
from ..common import httpService
from . import node_client
HTML_SEARCH = 'search_form.html'
URI_SEARCH = '/search?Search='
URI_ID = '/get_file?id='
HTML_TABLE_HEADER = '''<!DOCTYPE html>
                                    <html>
                                    <body style="background: rgb(255,255,255)">
                                    <center>
                                    <table style="width:35%" ;
                                    border= "2px solid #dddddd">
                                    <tr>
                                    <th align="left" ;
                                    style="background-color:aqua"> Filename
                                    </th>
                                    <th align="left" ;
                                    style="background-color:aqua">Option</th>
                                    </tr>'''
HTML_END = '''</table>
                  </center>
                  </body>
                  </html>'''

MULTI_PORT = 8123
IP = '225.0.0.250'
MYTTL = 1


class Download_service (httpService.Http_service):

    def __init__(self, url):
        self.url = url

     ## Create a dictionary of HTTP protocol to download a file.
     # @param params dict of params that the function needs
     # @param object of a class to use other functions
    def service(self, params, object):
        if params['nodes'] != {}:
            pars_uri = urlparse.parse_qs(params['uri'][15:])
            node = pars_uri.get('node')[0]
            id = pars_uri.get('id')[0]
            Client = node_client.Node_client(
                                {str(node): params['nodes'][str(node)]}
            )
            output = Client.n_client(URI_ID, id, self.url)
            ret = {
                'status': '200',
                'message': 'OK',
                'headers': {
                    'Content-Disposition': 'attachment; filename=b.txt;',
                    'Content-Type': 'text/html',
                },
                'content': str(output[0]),
            }
        else:
            ret = {
                'code': 500,
                'message': 'No search services',
                'headers': {
                 'Content-Type': 'text/plain',
                },
                'content': 'Error :No search services',
            }
        return ret


class Search_service (httpService.Http_service):

    def __init__(self, url):
        self.url = url

    ## Search service of front-end server
    # @param params dict of params that the function needs
    # @param object of a class to use other functions
    # The function send to nodes a search ask 
    # after get the results it make a html table
    def service(self, params, object):
        if params['nodes'] != {}:
            pars_uri = urlparse.parse_qs(params['uri'][8:])
            Client = node_client.Node_client(params['nodes'])
            out = Client.n_client(
                            URI_SEARCH, pars_uri.get('Search')[0], self.url
            )
            output = HTML_TABLE_HEADER
            xml = xml_funcs.Xml()
            for key in params['nodes']:
                for o in out:
                    output += xml.xml_to_html(o, key)
            output += '''<a href="/form?file=search_form.html">
                                &lt;Back&gt;</a>'''+HTML_END
            ret = {
                'status': '200',
                'message': 'OK',
                'headers': {
                    'Content-Type': 'text/html',
                },
                'content': output,
            }
        else:
            ret = {
                'code': 500,
                'message': 'No search services',
                'headers': {
                 'Content-Type': 'text/plain',
                },
                'content': 'Error :No search services',
            }
        return ret


class View_service (httpService.Http_service):

    def __init__(self, url):
        self.url = url

    ## Create a dictionary of HTTP protocol to view a file.
    # @param params dict of params that the function needs
    # @param object of a class to use other functions
    def service(self, params, object):
        if params['nodes'] != {}:
            pars_uri = urlparse.parse_qs(params['uri'][11:])
            node = pars_uri.get('node')[0]
            id = pars_uri.get('id')[0]
            Client = node_client.Node_client(
                            {str(node): params['nodes'][str(node)]}
            )
            output = Client.n_client(URI_ID, id, self.url)
            ret = {
                'status': '200',
                'message': 'OK',
                'headers': {
                    'Content-Type': 'text/html',
                },
                'content': str(output[0]),
            }
        else:
            ret = {
                'code': 500,
                'message': 'No search services',
                'headers': {
                 'Content-Type': 'text/plain',
                },
                'content': 'Error :No search services',
            }
        return ret


class Form_service (httpService.Http_service):

    def __init__(self, base):
        self.base = base

    ## create a dictionary of HTTP protocol to open a file.
    # @param params dict of params that the function needs
    # @param object of a class to use other functions
    def service(self, params, object):
        pars_uri = urlparse.parse_qs(params['uri'][6:])
        ret = {
            'status': '200',
            'message': 'OK',
            'file_name': self.base % pars_uri.get('f')[0],
            'headers': {
                'Content-Type': 'text/html',
            }
        }
        return ret


class Listener (httpService.Http_service, object):

    def __init__(self):
        pass

    def service(self, params, object):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind(('', MULTI_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(IP), socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        s.settimeout(2)
        try:
            data, sender = s.recvfrom(1400)
            while data[-1:] == '\0':
                data = data[:-1]
            data = data.split(',')
            if data[0] == 'node':
                object.node_list(sender[0], data[1], params['nodes'], object)
        except socket.timeout as e:
            print e

    def sub_nodes(self, nodes):
        subs = []
        t = datetime.datetime.now().time()
        for node in nodes:
            time = nodes[node]['lasttime'].split(':')
            sec = int(time[0])*60+int(time[1])
            now = int(t.strftime('%M'))*60+int(t.strftime('%S'))
            if (now-sec) >= 10:
                subs.append(node)
        for sub in subs:
            nodes.pop(sub)

    def node_list(self, ip, port, nodes, object):
        t = datetime.datetime.now().time()
        node = '%s:%s' % (ip, port)
        nodes[node] = {
            'ip': ip, 'port': int(port),
            'lasttime': t.strftime('%M:%S')
        }
        object.sub_nodes(nodes)
        return nodes
