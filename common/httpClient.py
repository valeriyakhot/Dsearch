
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

class Client(object):

    def __init__(self, url, ip, port):
        self.url = url
        self.ip = ip
        self.port = port


    def client (self, uri):
        output = ''
        with contextlib.closing(
            socket.socket(
                family = socket.AF_INET,
                type = socket.SOCK_STREAM,
            )
        ) as s:
            s.connect((
                self.ip,
                self.port,
            ))
            util.send_all(
                s,
                (
                    (
                        'GET %s HTTP/1.1\r\n'
                        'Host: %s\r\n'
                        '\r\n'
                    ) % (
                        uri,
                        self.url + uri,
                    )
                ).encode('utf-8'),
            )

            rest = bytearray()

            #
            # Parse status line
            #
            status, rest = util.recv_line(s, rest)
            status_comps = status.split(' ', 2)
            if status_comps[0] != constants.HTTP_SIGNATURE:
                raise RuntimeError('Not HTTP protocol')
            if len(status_comps) != 3:
                raise RuntimeError('Incomplete HTTP protocol')

            signature, code, message = status_comps
            if code != '200':
                raise RuntimeError('HTTP failure %s: %s' % (code, message))

            content_length = None
            for i in range(constants.MAX_NUMBER_OF_HEADERS):
                line, rest = util.recv_line(s, rest)
                if not line:
                    break

                name, value = util.parse_header(line)
                if name == 'Content-Length':
                    content_length = int(value)
            else:
                raise RuntimeError('Too many headers')

            try:
                if content_length is None:
                    #print 'IM HEEERRRREEE'
                    buf = ''
                    while True:
                        buf += s.recv(constants.BLOCK_SIZE)
                        if not buf:
                            break
                    
                    output = buf

                    return output
                else:
                    buff = ''

                    left_to_read = content_length
                    while left_to_read > 0:
                        if not rest:
                            t = s.recv(constants.BLOCK_SIZE)
                            if not t:
                                raise RuntimeError(
                                    'Disconnected while waiting for content'
                                )
                            rest += t
                        buf, rest = rest[:left_to_read], rest[left_to_read:]
                        buff += buf
                        left_to_read -= len(buf)

                    output = buff
                #print 'OUTPUT      %s'%output
            finally:
                pass
        return output
