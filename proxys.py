__author__ = 'jmpews'
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect(('58.220.2.133', 80))
# sock.send("CONNECT github.com:443 HTTP/1.1\r\nHost: github.com:443\r\nProxy-Connection: keep-alive\r\n\r\n".encode())
# while True:
#     r=sock.recv(1024).decode()
#     if r!='':
#         print(r)

# sock.connect(('206.41.89.72', 3389))
# sock.send(b'\x05\x02\x00\x02')
# while True:
#     r=sock.recv(1024)
#     if r!=b'':
#         print(r)

#
def genips(s,e):
    def s2n(str):
        i=[int(x) for x in str.split('.')]
        return i[0]<<24|i[1]<<16|i[2]<<8|i[3]
    def n2ip(num):
        return '%s.%s.%s.%s' % (
            (num&0xFF000000)>>24,
            (num&0x00FF0000)>>16,
            (num&0x0000FF00)>>8,
            (num&0x000000FF)
        )
    for t in range(s2n(s),s2n(e)):
        yield n2ip(t)




ips=genips('40.0.0.1','70.0.0.128')
# ips=genips('110.0.0.1','126.0.0.1s28')
# ips=genips('210.0.0.1','230.0.0.128')


# for i in ips:
#     pass
# print(len(ips))
import errno
from unittest.case import TestCase
def assertErrorEquals(expected, actual, errstr=None):
    # Uses the textual names for easy reading.
    def strify(code):
        if code == 0:
            return 'OK'
        print(code)
        return errno.errorcode[code]
    TestCase.assertEquals(strify(expected),strify(actual),errstr)

httports=[80,3128,8080,8888]
def checkhttps(ip):
    for port in httports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))
        connstr="CONNECT %s:%s HTTP/1.1\r\nHost: %s:%s\r\nProxy-Connection: keep-alive\r\n\r\n" % (ip,port,ip,port)
        print(connstr)
        sock.send(connstr.encode())
        r=sock.recv(1024).decode()
        sock.close()
        print(r)

inputs=[]
outputs=[]
ip='168.102.15.16'
for port in httports:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)
    err=sock.connect_ex((ip, port))
    print(errno.errorcode[err])
    outputs.append(sock)


import select
import time
def sendhttp(x):
    t=x.getpeername()
    connstr="CONNECT %s:%s HTTP/1.1\r\nHost: %s:%s\r\nProxy-Connection: keep-alive\r\n\r\n" % (t[0],t[1],t[0],t[1])
    x.send(connstr.encode())

def checkhttp(data):
    if data.find(b'Connection established')==-1:
        return False
    return True

while inputs or outputs:
    # if len(inputs)<100:
    #     for i in range(100-len(inputs)):
    #         ip=ips.__next__()

    readable,writeable,exceptional=select.select(inputs,outputs,[],3)

    for x in readable:
        print(x.getpeername())
        data=x.recv(1024)
        if checkhttp():
            print(x.getpeername())
        inputs.remove(x)

    for x in writeable:
        erro=x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        # connect拒绝
        if erro==errno.ECONNREFUSED:
            print('conn refused.')
            outputs.remove(x)
            continue
        # 未建立连接
        elif erro==errno.EINPROGRESS:
            continue
        # 发送http代理验证数据
        sendhttp(x)
        outputs.remove(x)
        inputs.append(x)

    for x in exceptional:
        print('====EXCEP====')
    print('loop...')
    outputs=[]
