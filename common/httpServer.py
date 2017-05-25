
import contextlib
import datetime
import errno
import os
import socket
import struct
import sys
import traceback
import urlparse

from . import constants
from . import send_it
from . import util
from . import xml_func
from . import httpService




class Http_server(object):

    def __init__(self, args):
        self.services={'uri':httpService.Http_service()}
        self.bind_address=args.bind_address
        self.bind_port=args.bind_port
        

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


    def str_headers(self, headers):
        head=""
        for key,val in headers.iteritems():
            head+="%s: %s\r\n"%(key,val)
        return head

        
    def build_message(self, s, dic, object):
        headers = dic.get('headers', {})
        if 'content' in dic:
            dic['headers']['Content-Length']=len(dic.get('content'))
        try:
            f=None
            if 'file_name' in dic:
                f=open(dic.get('file_name'), 'rb')
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
            util.send_all(s,ret.encode('utf-8'))
            if 'file_name' in dic:
                buf = ''
                while True:
                    #print (buf)
                    buf = f.read(constants.BLOCK_SIZE)
                    if not buf:
                        break
                    #print buf
                    util.send_all(s,buf)
            else:
                util.send_all(s,dic.get('content'))
        finally:
            if 'file_name' in dic:
                f.close()

    
    def register(self, uri, service_obj):
        Service = httpService.Http_service()
        Service = service_obj
        self.services[uri] = Service
        
        
    def uri_check(self, dic, uri):
        #print 'URI   %s'%uri
        if uri == None:
            pass
        else:
            ser = uri.split('?')[0]+'?'
            #print ser
            if ser in self.services:
                ret = self.services[ser].service(dic, self.services[ser])
            else:
                ret={
                    'code': 404,
                    'message': 'File not found',
                    'headers': {
                     'Content-Type': 'text/plain',
                    },
                    'content': 'Error : not known service:%s'%(uri),
                }
        return ret
        
        
    def server(self, object):
        print('start')
        nodes={}
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
                while s == None:
                    try:
                        s, addr = sl.accept()
                    except socket.timeout as e:
                        print e
                    multi_param={
                                'nodes' : nodes,
                                'port' : self.bind_port,
                    }
                    object.uri_check(multi_param, 'None')
                    #print 'NODES    %s'%nodes
                #print 'NODES    %s'%nodes
                with contextlib.closing(s):
                    status_sent = True
                    try:
                        rest = bytearray()

                        uri = object.check(s, rest)
                        param = urlparse.parse_qs(
                            urlparse.urlparse(uri).query
                        ).values()
                        #print uri
                        dic={
                            'uri' : uri,
                            'nodes' : nodes
                        }
                        message = object.uri_check(dic, uri)
                        #print message
                        if message != None:
                            object.build_message(s, message, object)
                        status_sent=True
                    except IOError as e:
                        traceback.print_exc()
                        if not status_sent:
                            if e.errno == errno.ENOENT:
                                code=404
                                message= 'File Not Found'
                                status={
                                    'code': code,
                                    'message': message,
                                    'headers': {
                                     'Content-Type': 'text/plain',
                                    },
                                    'content': 'Error %s %s\r\n%s'%(code,message,e),
                                }
                                
                                object.build_message(s, status, object)
                                #print 'work'
                            else:
                                code=500
                                message= 'Internal Error'
                                status={
                                    'code': code,
                                    'message': message,
                                    'headers': {
                                     'Content-Type': 'text/plain',
                                    },
                                    'content': 'Error %s %s\r\n%s'%(code,message,e),
                                }
                                object.build_message(s, status, object)
                    except Exception as e:
                        traceback.print_exc()
                        if not status_sent:
                            code=500
                            message= 'Internal Error'
                            status={
                                'code': code,
                                'message': message,
                                'headers': {
                                 'Content-Type': 'text/plain',
                                },
                                'content': 'Error %s %s\r\n%s'%(code,message,e),
                            }
                            object.build_message(s, status, object)
