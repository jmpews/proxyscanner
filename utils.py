__author__ = 'jmpews'
import socket
import time

#发送验证字符串
def sendhttp(x):
    t=x.getpeername()
    connstr="CONNECT %s:%s HTTP/1.1\r\nHost: %s:%s\r\nProxy-Connection: keep-alive\r\n\r\n" % (t[0],t[1],t[0],t[1])
    x.send(connstr.encode())

#检查response是否存在字符串
def checkhttp(data):
    if data.find(b'Connection established')==-1:
        return False
    return True

# 发送socks验证数据
def sendsocks(x):
    x.send(b'\x05\x02\x00\x02')

#检查response是否存在字符串.
def checksocks(data):
    if data.find(b'\x05\x00') == -1:
        return False
    return True

# 采用生成器方式,防止超长list爆内存
def genips(ipl):
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
    for s,e in ipl:
        for t in range(s2n(s),s2n(e)):
            yield n2ip(t)


# 对于每个IP生成4个socket,表示检查4个常见端口
def addips(ip):
    httports=[80,3128,8080,8888]
    socks=[]
    tm=int(time.time())
    for port in httports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 非阻塞connect
        sock.setblocking(0)
        err=sock.connect_ex((ip, port))
        socks.append((sock,sock.fileno(),tm))
    return socks

# 检查sock是否超时
def checktimeout(x):
    t=time.time()
    if x[2]+3<t:
        try:
            x[0].getpeername()
        except:
            # print('Exp:Host.')
            x[0].close()
            return False
    return True