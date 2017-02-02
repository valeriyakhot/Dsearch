# -*- coding: utf-8 -*-

import contextlib
import errno
import socket
import traceback
import urlparse

from . import constants
from . import util
from . import send_it

def check(args,s,rest) :
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
    
def server (args,func, mem=None) :
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

                    param = urlparse.parse_qs(urlparse.urlparse(uri).query).values()
                    
                    func(s, uri, param, args, mem)
                    
                except IOError as e:
                    traceback.print_exc()
                    if not status_sent:
                        if e.errno == errno.ENOENT:
                            send_it.send_status(s, 404, 'File Not Found', e)
                        else:
                            send_it.send_status(s, 500, 'Internal Error', e)
                except Exception as e:
                    traceback.print_exc()
                    if not status_sent:
                        send_it.send_status(s, 500, 'Internal Error', e)
                        
                        