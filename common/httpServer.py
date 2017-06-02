
import contextlib
import errno
import os
import socket
import traceback

from . import constants
from . import util
from . import httpService


## Http server
class Http_server(object):

    ## Constructor.
    def __init__(self, ip, port):
        self.services = {}
        self.bind_address = ip
        self.bind_port = port

    ## Check http ask.   
    def check(self, s, rest):
        req, rest = util.recv_line(s, rest)
        req_comps = req.split(' ', 2)
        if req_comps[2] != constants.HTTP_SIGNATURE:
            raise RuntimeError('Not HTTP protocol')
        if len(req_comps) != 3:
            raise RuntimeError('Incomplete HTTP protocol')

        method, uri, signature = req_comps
        if method != 'GET':
            raise RuntimeError(
                "HTTP unsupported method '%s'" % method
            )

        if not uri or uri[0] != '/':
            raise RuntimeError("Invalid URI")
        return uri

    ## Convert headers to string.
    def str_headers(self, headers):
        head = ""
        for key, val in headers.iteritems():
            head += "%s: %s\r\n" % (key, val)
        return head

    ## Http message builder.
    # @param socket to send a message
    # @param dict of http ask
    # run all over the dict and build a right http message
    def build_message(self, s, dic, object):
        if 'content' in dic:
            dic['headers']['Content-Length'] = len(dic.get('content'))
        try:
            f = None
            if 'file_name' in dic:
                f = open(dic.get('file_name'), 'rb')
                dic['headers']['Content-Length'] = os.fstat(f.fileno()).st_size

            ret = (
                    '%s %s %s\r\n'
                    '%s'
                    '\r\n'
                ) % (
                    constants.HTTP_SIGNATURE,
                    dic.get('status', '200'),
                    dic.get('message', 'OK'),
                    object.str_headers(dic['headers']),
                )
            util.send_all(s, ret.encode('utf-8'))
            if 'file_name' in dic:
                buf = ''
                while True:
                    buf = f.read(constants.BLOCK_SIZE)
                    if not buf:
                        break
                    util.send_all(s, buf)
            else:
                util.send_all(s, dic.get('content'))
        finally:
            if 'file_name' in dic:
                f.close()

    ## Registry of http services.
    # @param string of the servise's uri
    # @param httpService object 
    def register(self, uri, service_obj):
        Service = httpService.Http_service()
        Service = service_obj
        self.services[uri] = Service

    ## Checking the uri service.
    # @param dict of params for service func
    # @param string of uri
    # checking the uri and run the right http service
    def uri_check(self, dic, uri):
        if uri == None:
            pass
        else:
            ser = uri.split('?')[0]+'?'
            if ser in self.services:
                ret = self.services[ser].service(dic, self.services[ser])
            elif uri == '/':
                ret = self.services['/'].service(dic, self.services['/'])
            else:
                ret = {
                    'code': 404,
                    'message': 'File not found',
                    'headers': {
                     'Content-Type': 'text/plain',
                    },
                    'content': 'Error : not known service:%s' % (uri),
                }
        return ret

    ## Http service.
    def server(self, object):
        print('start')
        nodes = {}
        with contextlib.closing(
            socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
            )
        ) as sl:
            sl.settimeout(2)
            sl.bind((self.bind_address, self.bind_port))
            sl.listen(10)

            while True:
                uri = None
                s = None
                while s is None:
                    try:
                        s, addr = sl.accept()
                    except socket.timeout as e:
                        print e
                    multi_param = {
                                'nodes': nodes,
                                'port': self.bind_port,
                    }
                    object.uri_check(multi_param, 'None')
                with contextlib.closing(s):
                    status_sent = True
                    try:
                        rest = bytearray()

                        uri = object.check(s, rest)
                        dic = {
                            'uri': uri,
                            'nodes': nodes,
                            'port': self.bind_port
                        }
                        message = object.uri_check(dic, uri)

                        if message is not None:
                            object.build_message(s, message, object)
                        status_sent = True
                    except IOError as e:
                        traceback.print_exc()
                        if not status_sent:
                            if e.errno == errno.ENOENT:
                                code = 404
                                message = 'File Not Found'
                                status = {
                                    'code': code,
                                    'message': message,
                                    'headers': {
                                     'Content-Type': 'text/plain',
                                    },
                                    'content': 'Error %s %s\r\n%s' % (
                                        code, message, e
                                    ),
                                }

                                object.build_message(s, status, object)
                            else:
                                code = 500
                                message = 'Internal Error'
                                status = {
                                    'code': code,
                                    'message': message,
                                    'headers': {
                                     'Content-Type': 'text/plain',
                                    },
                                    'content': 'Error %s %s\r\n%s' % (
                                        code, message, e
                                    ),
                                }
                                object.build_message(s, status, object)
                    except Exception as e:
                        traceback.print_exc()
                        if not status_sent:
                            code = 500
                            message = 'Internal Error'
                            status = {
                                'code': code,
                                'message': message,
                                'headers': {
                                 'Content-Type': 'text/plain',
                                },
                                'content': 'Error %s %s\r\n%s' % (
                                    code, message, e
                                ),
                            }
                            object.build_message(s, status, object)
