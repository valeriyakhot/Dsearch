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
from ..common import xml_func
from ..common import http_util

HTML_SEARCH = 'search_form.html'
URI_SEARCH = '/search?Search='
URI_ID = '/get_file?id='
HTML_TABLE_HEADER='''<!DOCTYPE html><html><body><table style="width:35%" ; border= "2px solid #dddddd">  <tr>    <th align="left"> Filename </th>    <th align="left">Option</th>   </tr>'''
HTML_END='''</table></body></html>'''


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
    nodes = {
        '127.0.0.1:8040': {
            'ip': '127.0.0.1',
            'port': 8040,
        },
        '127.0.0.1:8070': {
            'ip': '127.0.0.1',
            'port': 8070,
         }
     }
    if  nodes:
        if uri.startswith(URI_SEARCH):
            if len(uri) != len(URI_SEARCH):
                out = http_util.client(args, URI_SEARCH, param[0][0], nodes)
                output=HTML_TABLE_HEADER
                for key in nodes:
                    for o in out:
                        output+=xml_func.xml_to_html(o, key)
                output+='<a href="/form?file=search_form.html">&lt;Back&gt;</a>'+HTML_END
            ret = {
                'status': '200',
                'message': 'OK',
                'headers': {
                    'Content-Type': 'text/html',
                }, 
                'content': output,
            }
        elif uri.startswith('/view_file?'):
            pars_uri=urlparse.parse_qs(uri[11:])
            node=pars_uri.get('node')[0]
            id=pars_uri.get('id')[0]
            print "NODE   %s"%{str(node):nodes[str(node)]}
            output = http_util.client(args, URI_ID, id, {str(node):nodes[str(node)]})
            print 'FRONT  OUTPUT    %s'%(output)
            ret = {
                'status': '200',
                'message': 'OK',
                'headers': {
                    'Content-Type': 'text/html',
                }, 
                'content': str(output[0]),
            }
        elif uri.startswith('/download_file?'):
            pars_uri=urlparse.parse_qs(uri[15:])
            node=pars_uri.get('node')[0]
            id=pars_uri.get('id')[0]
            output = http_util.client(args, URI_ID, id, {str(node):nodes[str(node)]})
            ret = {
                'status': '200',
                'message': 'OK',
                'headers': {
                    'Content-Disposition': 'attachment; filename=b.txt;',
                    'Content-Type': 'text/html',
                }, 
                'content': str(output[0]),
            }

        elif uri.startswith('/form?'):
            ret = {
                'status': '200',
                'message': 'OK',
                'file_name':param[0][0],
                'headers': {
                    'Content-Type': 'text/html',
                }
            }
        else:
            ret={
                'code': 404,
                'message': 'File not found',
                'headers': {
                 'Content-Type': 'text/plain',
                },
                'content': 'Error : not known service:%s'%(uri),
            }
    else:
        ret={
                'code':500,
                'message': 'No search services',
                'headers': {
                 'Content-Type': 'text/plain',
                },
                'content': 'Error :No search services',
            }

   
    return ret


def main():
    args = parse_args()
    http_util.server(args, front)

if __name__ == '__main__':
    main()
