# -*- coding: utf-8 -*-

import tempfile
import argparse
import contextlib
import errno
import os
import socket
import sys
import traceback
import urlparse
import xml.etree.cElementTree as ET

#C:\cygwin64\tmp>python -m Dsearch.front --url http://localhost:8070/\ --bind-port 8080 --node-port 8070

from ..common import constants
from ..common import util
from ..common import send_it
from ..common import xml_func
from ..common import http_util

HTML_SEARCH =  'search_form.html'
URI_SEARCH = '/search?Search='
URI_ID = '/get_file?id='


def parse_args():
    """Parse program argument."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--base',
        default='.',
        help='Base directory to search fils in, default: %(default)s',
    )
    parser.add_argument(
        '--bind-address',
        default='0.0.0.0',
        help='Bind address, default: %(default)s',
    )
    parser.add_argument(
        '--bind-port',
        default=0,
        type=int,
        help='Bind port, default: %(default)s',
    )
    parser.add_argument(
        '--node-port',
        default=0,
        type=int,
        help='Bind port, default: %(default)s',
    )
    parser.add_argument(
        '--url',
        required=True,
        help='URL to use',
    )
    parser.add_argument(
        '--func',
        default='front',
        help='URL to use',
    )
    return parser.parse_args()


def front(s, uri, param, args, mem):
    normal_send = True

    if uri[:15] == URI_SEARCH:
        if len(uri) != len(URI_SEARCH):
            output = client(args, URI_SEARCH, param[0][0], True)

    elif uri.startswith('/view_file?'):
        output = client(args, URI_ID, param[0][0], False)

    elif uri.startswith('/download_file?'):
        normal_send = False
        output = client(args, URI_ID, param[0][0], False)
        send_it.download(s, output)

    elif uri.startswith('/form?'):
        normal_send = False
        send_it.send_file(s, HTML_SEARCH)

    else:
            raise RuntimeError('Do not get known service')

    if normal_send:
        send_it.send(s, output)


def client(args, uri_beg, search, xml_status):

    url = util.spliturl(args.url)
    if url.scheme != 'http':
        raise RuntimeError("Invalid URL scheme '%s'" % url.scheme)

    with contextlib.closing(
        socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    ) as s:
        s.connect((
            url.hostname,
            url.port if url.port else constants.DEFAULT_HTTP_PORT,
        ))
        uri = uri_beg+search
        util.send_all(
            s,
            (
                (
                    'GET %s HTTP/1.1\r\n'
                    'Host: %s\r\n'
                    '\r\n'
                ) % (
                    uri,
                    args.url+uri,
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

                buf = ''
                while True:
                    buf += s.recv(constants.BLOCK_SIZE)
                    if not buf:
                        break
                if xml_status:
                    output = xml_func.xml_to_html(buf)
                else:
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
                if xml_status:
                    output = xml_func.xml_to_html(buff)
                else:
                    output = buff

                return output

        finally:
            pass


def main():
    args = parse_args()
    http_util.server(args,front)

if __name__ == '__main__':
    main()
