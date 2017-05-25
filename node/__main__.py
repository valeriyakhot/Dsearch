#/usr/bin/python


import argparse
import os

#HOW TO RUN : python -m Dsearch.node --bind-port 8070

from ..common import constants
from ..common import xml_func
from ..common import http_util
from ..common import constants
from ..common import util
from ..common import xml_func
from ..common import http_util
from ..common import xml_funcs
from ..common import httpServer
from ..common import memory
from . import services


def parse_args():
    """Parse program argument."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bind-address',
        default='0.0.0.0',
        help='Bind address, default: %(default)s',
    )
    parser.add_argument(
        '--bind-port',
        default=constants.DEFAULT_HTTP_PORT,
        type=int,
        help='Bind port, default: %(default)s',
    )
    parser.add_argument(
        '--directory',
        default='./',
        help='Base directory to search fils in, default: %(default)s',
    )
    parser.add_argument(
        '--func',
        default='node',
        help='URL to use',
    )
    args = parser.parse_args()
    return args


def node(s, uri, param, args, dic):
    #print 'working'
    if uri.startswith('/search?'):
        files, ids = find_name(dic['memory'], param[0][0])
        output = xml_func.xml_form(files, ids)
        #print 'searching'

        ret = {
            'status': '200',
            'message': 'OK',
            'headers': {
                'Content-Type': 'text/xml',
            }, 
            'content': output,
        }
        
    elif uri.startswith('/get_file?'):
        #print 'give file'
        file_name = os.path.join(
            dic['memory'][int(param[0][0])]['root'],
            dic['memory'][int(param[0][0])]['filename'],
        )
        ret = {
            'status': '200',
            'message': 'OK',
            'file_name': file_name,
            'headers': {
                'Content-Type': 'text/html',
            }
        }
    else:
        raise RuntimeError('Do not get known service')



def mem_list(directory):
    mem = []
    for root, directories, filenames in os.walk(directory):
        for filename in filenames:
            mem.append({'root': root, 'filename': filename})
    return mem


def find_name(mem, name):
    files = []
    ids = []
    for i in range(len(mem)):
            if name in mem[i]['filename']:
                files.append(mem[i]['filename'])
                ids.append(i)
    return files, ids


def main():
    args = parse_args()
    Memory = memory.Memory(args)
    mem = Memory.mem_list()
    search = services.Search_service(mem)
    id = services.Id_service(mem)
    sender = services.Sender()
    Server = httpServer.Http_server(args)
    Server.register('/get_file?', id)
    Server.register('/search?', search)
    Server.register('None?', sender)
    Server.server(Server)
    #mem = mem_list(args.directory)
    #http_util.server(args, node, http_util.sender, mem)
if __name__ == '__main__':
    main()
