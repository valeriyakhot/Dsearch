#/usr/bin/python


import argparse
import os

#HOW TO RUN : python -m Dsearch.node --bind-port 8070

from ..common import constants
from ..common import util
from ..common import xml_funcs
from ..common import httpServer
from . import memory
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


def main():
    args = parse_args()
    Memory = memory.Memory(args)
    mem = Memory.mem_list()
    search = services.Search_service(mem)
    id = services.Id_service(mem)
    sender = services.Sender()
    Server = httpServer.Http_server(args.bind_address, args.bind_port)
    Server.register('/get_file?', id)
    Server.register('/search?', search)
    Server.register('None?', sender)
    Server.server(Server)

if __name__ == '__main__':
    main()
