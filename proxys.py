__author__ = 'jmpews'
import socket
from redisq import RedisQueue
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

# 采用生成器方式,防止超长list爆内存
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




ips=genips('40.3.115.51','70.0.0.128')
# ips=genips('110.0.0.1','126.0.0.1s28')
# ips=genips('210.0.0.1','230.0.0.128')


# for i in ips:
#     pass
# print(len(ips))
import errno

httports=[80,3128,8080,8888]

inputs=[]
outputs=[]

def addips(ip):
    socks=[]
    for port in httports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(0)
        err=sock.connect_ex((ip, port))
        socks.append(sock)
    return socks


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

rq=RedisQueue('proxy')

while True:
    # if len(outputs)<400:
    #     for i in range(100-int(len(outputs)/4)):
    #         try:
    #             ip=ips.__next__()
    #         except StopIteration:
    #             # 循环到ip列表最后
    #             break
    #
    #         outputs+=addips(ip)
    outputs+=addips('40.3.219.211')
    flag=0
    readable,writeable,exceptional=select.select(inputs,outputs,[],3)

    for x in readable:
        flag=1
        try:
            data=x.recv(1024)
        except Exception as e:
            x.close()
            print(e)
        if checkhttp(data):
            detial=x.getpeername()
            print(detial)
            rq.put(detial[0]+':'+str(detial[1]))
        else:
            print(data)
        inputs.remove(x)
        x.close()

    for x in writeable:
        print(x)
        flag=1
        erro=x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        # connect拒绝
        if erro==errno.ECONNREFUSED:
            print('conn refused.')
            outputs.remove(x)
            x.close()
            continue
        # 未建立连接
        elif erro==errno.EINPROGRESS:
            continue
        elif erro==errno.errno.EHOSTUNREACH:
            print('host unreach.')
            outputs.remove(x)
            x.close()
            continue
        # 发送http代理验证数据
        sendhttp(x)
        outputs.remove(x)
        inputs.append(x)

    for x in exceptional:
        flag=1
        print('====EXCEP====')
    ip=ips.__next__()
    print(ip)
    print('loop...')
    if not flag:
        outputs=[]