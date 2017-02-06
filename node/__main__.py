#/usr/bin/python


import argparse
import os

#C:\cygwin64\tmp>python -m Dsearch.node --bind-port 8070

from ..common import constants
from ..common import send_it
from ..common import xml_func
from ..common import http_util


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
        '--base',
        default='./',
        help='Base directory to search fils in, default: %(default)s',
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
    args.base = os.path.normpath(os.path.realpath(args.base))
    return args


def node(s, uri, param, args, mem):
    normal_out = True
    if uri.startswith('/search?'):
        files, ids = find_name(mem, param[0][0])
        output = xml_func.xml_form(files, ids)
    elif uri.startswith('/get_file?'):
        normal_out = False
        file_name = os.path.join(
            mem[int(param[0][0])]['root'],
            mem[int(param[0][0])]['filename'],
        )
        send_it.send_file(s, file_name)
        status_sent = True
    else:
        raise RuntimeError('Do not get known service')

    if normal_out:
        send_it.send_xml(s, output)
        status_sent = True
    return status_sent


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
    mem = mem_list(args.directory)
    http_util.server(args, node, mem)
if __name__ == '__main__':
    main()
