#/usr/bin/python


import argparse
import contextlib
import errno
import os
import socket
import traceback
import urlparse

#C:\cygwin64\tmp>python -m Dsearch.node --bind-port 8070

from ..common import constants
from ..common import util
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
        default='.',
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
    
def server():  
    args = parse_args()
    print('start')
    with contextlib.closing(
        socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    ) as sl:
        sl.bind((args.bind_address, args.bind_port))
        sl.listen(10)
        mem = mem_list(args.directory)
        while True:
            s, addr = sl.accept()
            with contextlib.closing(s):
                status_sent = True
                try:
                    rest = bytearray()

                    uri=http_util.check(args,s,rest)
                    
                    
                    param = urlparse.parse_qs(urlparse.urlparse(uri).query).values()
                    normal_out=True
                    if uri.startswith('/search?'):
                        files,ids= find_name(mem,param[0][0])
                        output=xml_func.xml_form(files,ids)
                    elif uri.startswith('/get_file?'):
                        normal_out=False
                        file_name = os.path.join(mem[int(param[0][0])]['root'],mem[int(param[0][0])]['filename'])
                        send_it.send_file(s,file_name)
                        status_sent=True
                    else:   
                        raise RuntimeError('Do not get known service' )

                    if normal_out:
                        send_it.send_xml(s,output)
                        status_sent=True
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
    
def mem_list(directory):
    mem=[]
    for root, directories, filenames in os.walk(directory):
        for filename in filenames: 
            mem.append({'root':root,'filename':filename})
    return mem
    
def find_name(mem,name):
    files=[]
    ids=[]
    for i in range(len(mem)):
            if name in mem[i]['filename']:
                files.append(mem[i]['filename'])
                ids.append(i)
    return files,ids

    
def main():
    server()
if __name__ == '__main__':
    main()



