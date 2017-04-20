# -*- coding: utf-8 -*-

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

MYPORT = 8123
MYGROUP_4 = '225.0.0.250'
MYTTL = 1 
def node_in(nodes, ip, t) :
    length=len(nodes)
    for n in range(length):
        if nodes[n]['ip'] == ip:
            nodes[n]['lasttime']=t.strftime('%M:%S')
            return True
    return False
    
    
def listener():
    nodes=[]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(('', MYPORT))
    mreq = struct.pack("4sl", socket.inet_aton(MYGROUP_4), socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    s.settimeout(2)
    while True:
        print 'stuck in receive'
        try:
            data, sender = s.recvfrom(1500)
            print 'SENDER'+ str(sender[0])+str(sender[1])
            if not data:
                break
            while data[-1:] == '\0': data = data[:-1]
            data=data.split(',')
            node_list(sender, nodes)
        except socket.timeout as e:
            print e
            break
    print 'done'

        
    
def sub_nodes(nodes):
    t=datetime.datetime.now().time()
    for i in range(len(nodes)):
        time=nodes[i].get('lasttime').split(':')
        sec=int(time[0])*60+int(time[1])
        now=int(t.strftime('%M'))*60+int(t.strftime('%S'))
        if (now-sec)>=10:
            print ('len before'+str(len(nodes)))
            print i
            nodes.pop(i)
            i-=1


def node_list(data,nodes):
    t=datetime.datetime.now().time()
    if not node_in(nodes, data[0], t):
        nodes.append({'ip': data[0], 'port': data[1], 'lasttime':t.strftime('%M:%S')})     
    sub_nodes(nodes)
    return nodes
        

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
                print buf
                util.send_all(s,buf)
        else:
            util.send_all(s,dic.get('content'))
    finally:
        if 'file_name' in dic:
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
                            print 'work'
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

def client (args, uri_beg, search, nodes):
    output=[]
    for node in nodes:
        print 'NODE     %s'%(node)
        with contextlib.closing(
            socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
            )
        ) as s:
            s.connect((
                nodes[node].get('ip', '127.0.0.1'),
                nodes[node].get('port', constants.DEFAULT_HTTP_PORT),
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
                    print 'IM HEEERRRREEE'
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

                    output.append(buff)
                print 'OUTPUT      %s'%output
            finally:
                pass
    return output
