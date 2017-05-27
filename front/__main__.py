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

#HOW TO RUN : python -m Dsearch.front --url http://localhost:8070/\ --bind-port 8080 

from ..common import constants
from ..common import util
from ..common import xml_funcs
from ..common import httpServer
from . import services

HTML_SEARCH = 'search_form.html'
URI_SEARCH = '/search?Search='
URI_ID = '/get_file?id='
HTML_TABLE_HEADER='''<!DOCTYPE html>
                                    <html>
                                    <body style="background: rgb(255,255,255)">
                                    <center>
                                    <table style="width:35%" ; border= "2px solid #dddddd"> 
                                    <tr>    <th align="left" ; style="background-color:aqua"> Filename 
                                    </th>  
                                    <th align="left" ; style="background-color:aqua">Option</th> 
                                    </tr>'''
HTML_END='''</table>
                  </center>
                  </body>
                  </html>'''


def parse_args():
    """Parse program argument."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--base',
        default='./Dsearch/front/%s',
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


def main():
    args = parse_args()
    Server = httpServer.Http_server(args.bind_address, args.bind_port)
    download = services.Download_service(args.url)
    view = services.View_service(args.url)
    form = services.Form_service(args.base)
    search = services.Search_service(args.url)
    listener = services.Listener()
    Server.register('/view_file?', view)
    Server.register('/form?', form)
    Server.register('/download_file?', download)
    Server.register('/search?', search)
    Server.register('None?', listener)
    Server.server(Server)

if __name__ == '__main__':
    main()
