# -*- coding: utf-8 -*-

import contextlib
import errno
import os
import socket
import traceback
import urlparse

from . import constants
from . import util
from . import send_it


def check(args, s, rest):
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


def str_headers(headers):
    head=""
    for key,val in headers.iteritems():
        head+="%s: %s\r\n"%(key,val)
    return head

    
def build_message(s,dic):
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
                str_headers(dic['headers']),
            )
        util.send_all(s,ret.encode('utf-8'))
        if 'file_name' in dic:
            buf = ''
            while True:
                print (buf)
                buf = f.read(constants.BLOCK_SIZE)
                if not buf:
                    break
                util.send_all(s,buf)
        else:
            util.send_all(s,dic.get('content'))
    finally:
        f.close()


def server(args, func, mem=None):
    print('start')
    with contextlib.closing(
        socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    ) as sl:
        sl.bind((args.bind_address, args.bind_port))
        sl.listen(10)
        while True:
            s, addr = sl.accept()
            with contextlib.closing(s):
                status_sent = True
                try:
                    rest = bytearray()

                    uri = check(args, s, rest)
                    param = urlparse.parse_qs(
                        urlparse.urlparse(uri).query
                    ).values()
                    print uri
                    build_message(s,func(s, uri, param, args, mem))
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
                            
                            build_message(status)
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
                            build_message(status)
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
                        build_message(status)
