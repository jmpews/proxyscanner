__author__ = 'jmpews'
__email__ = 'jmpews@gmail.com'

import socket
import time
import select
import threading
import struct

MyLock = threading.RLock()


# 一个socket对象
class Sock(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_fileno = self.sock.fileno()
        self.starttime = int(time.time())
        self.sock.setblocking(0)
        # 端口复用
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        # close发送RST,不存在TIME_WAIT状态
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        # EINPROGRESS
        self.errno = self.sock.connect_ex((ip, port))
        self.connected = False

    # 检测超时,timeout1为connect的超时时间.timeout2为send后的接受超时.
    def checktimeout(self, timeout=4):
        currenttime = int(time.time())
        if currenttime - self.starttime > timeout:
            self.sock.close()
            return True
        return False

    # 检测error
    def checkerror(self):
        # 常见error ECONNREFUSED ETIMEDOUT EHOSTUNREACH
        self.errno = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if self.errno == 0 or self.errno==socket.errno.EINPROGRESS:
            return True
        self.sock.close()
        return False

    # 检测是否建立好连接
    def checkconnected(self):
        try:
            host = self.sock.getpeername()
        except:
            # 做异常处理
            self.errno = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            self.sock.close()
            return False
        else:
            self.rip, self.rport = host
            return True

    # 设置建立连接
    def setconnected(self):
        self.connected = True
        self.starttime = int(time.time())

# HTTP代理对象
class ProxyHttp(Sock):
    def __init__(self, ip, port, proxytype):
        super(ProxyHttp, self).__init__(ip, port)
        self.proxytype = proxytype

    # 发送检测数据
    def senddata(self):
        checkstr = 'GET / HTTP/1.1\r\nHost:202.207.209.82\r\n\r\n'
        if self.checkerror():
            try:
                self.sock.send(checkstr.encode())
            except:
                # 做异常处理
                self.errno = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                self.sock.close()
                return False
            else:
                return True

    # 检测返回数据
    def checkdata(self):
        if self.checkerror() and self.checkconnected():
            data = self.sock.recv(1024)
            if data.find(b'hello') != -1:
                # 验证成功处理
                return True
        return False


# socks5代理
class ProxySocks(Sock):
    def __init__(self, ip, port, proxytype):
        super(ProxySocks, self).__init__(ip, port)
        self.proxytype = proxytype

    # 发送检测数据
    def senddata(self):
        if self.checkerror():
            try:
                self.sock.send(b'\x05\x02\x00\x02')
            except:
                # 做异常处理
                self.errno = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                self.sock.close()
                return False
            else:
                return True
    # 检测返回数据
    def checkdata(self):
        if self.checkerror() and self.checkconnected():
            data = self.sock.recv(1024)
            if data.find(b'\x05\x00') != -1:
                # 验证成功处理
                return True
        return False


# 工厂模式
# sock=Porxy.initialize(self,ip,port,proxytype)
class Proxy:
    @classmethod
    def initialize(cls, ip, port, proxytype):
        if proxytype == 'http':
            return ProxyHttp(ip, port, proxytype)
        elif proxytype == 'socks':
            return ProxySocks(ip, port, proxytype)


# 普通模式
# sock=ProxySock(ip,port,proxytype)
class ProxySock(Sock):
    def __init__(self, ip, port, proxytype):
        super(ProxySock, self).__init__(ip, port)
        self.proxytype = proxytype
        pass

    def senddata(self):
        if self.checkerror():
            if self.proxytype == 'http':
                connstr = 'GET / HTTP/1.1\r\nHost:hm.baidu.com\r\n\r\n'
                try:
                    self.sock.send(connstr.encode())
                except:
                    # 做异常处理
                    self.errno = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                    self.sock.close()
                    return False
                else:
                    return True
            elif self.proxytype == 'socks':
                try:
                    self.sock.send(b'\x05\x02\x00\x02')
                except:
                    # 做异常处理
                    self.errno = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                    self.sock.close()
                    return False
                else:
                    return True

    def checkdata(self):
        if self.checkerror() and self.checkconnected():
            data = self.sock.recv(1024)
            if self.proxytype == 'http':
                if data.find(b'200 OK') != -1:
                    # 验证成功处理
                    return True
            elif self.proxytype == 'socks':
                if data.find(b'\x05\x00') != -1:
                    # 验证成功处理
                    return True

# 暂不使用
class LockContext(object):
    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, type, value, traceback):
        if type != None:
            pass
        self.lock.release()
        return False

class Loop(threading.Thread):
    def __init__(self,callback=None):
        threading.Thread.__init__(self)
        # 如何处理待接受和待发送的socket?
        # 一种方法,可以选择将output和input分开存放
        # self.outputsocks={}
        # self.inputsocks={}
        # 另一种方法,合并,用connected属性标记区分,在select需要重新生成两部socket列表
        # self.socks = {}
        self.callback=callback
        self.runout = False
        self.ips=None
        self.ipsl=[]

    # ip列表
    def addipsl(self, ipsl, proxytype='http'):
        # 根据现成list生成
        # [[ip,port]]
        for ip,port in ipsl:
            self.ipsl.append((ip,port,proxytype))

    # 扫描IP段
    # 采用生成器防止大列表爆掉
    def scanips(self, ips, proxytype='http', ports=[80,3128]):
        def s2n(str):
            i = [int(x) for x in str.split('.')]
            return i[0] << 24 | i[1] << 16 | i[2] << 8 | i[3]

        def n2ip(num):
            return '%s.%s.%s.%s' % (
                (num & 0xFF000000) >> 24,
                (num & 0x00FF0000) >> 16,
                (num & 0x0000FF00) >> 8,
                (num & 0x000000FF)
            )
        # 根据IP段生成列表
        def func():
            for s, e in ips:
                for t in range(s2n(s), s2n(e)):
                    for port in ports:
                        yield n2ip(t), port, proxytype

        self.ips = func()




class SelectIOLoop(Loop):
    def __init__(self,callback=None):
        super(SelectIOLoop,self).__init__(self,callback=callback)
        self.outputs=[]
        self.inputs=[]
        # 对于select我们采用第一种方法 inputs和outputs分开
        self.outputsocks={}
        self.inputsocks={}

    def dealtimeout(self):
        # 使用filter,也可以使用for
        self.outputsocks=dict(filter(lambda x:not x[1].checktimeout(4),self.outputsocks.items()))
        self.inputsocks=dict(filter(lambda x:not x[1].checktimeout(5),self.inputsocks.items()))

    # 删除超时socket,补充列表数量
    def updateips(self,lens=1000):
        self.dealtimeout()
        # 补充socket数量,以保持充分利用
        if len(self.ipsl)!=0:
            for ip,port,proxytype in self.ipsl:
                sock = Proxy.initialize(ip, port, proxytype)
                if sock.sock_fileno>lens:
                    sock.sock.close()
                    break
                self.outputsocks[sock.sock_fileno] = sock
                self.ipsl.remove((ip,port,proxytype))
            if len(self.ipsl)==0 and self.ips==None:
                self.runout=True
        if self.ips!=None:
            while True:
                try:
                    ip, port, proxytype = self.ips.__next__()
                    sock = Proxy.initialize(ip, port, proxytype)
                    if sock.sock_fileno>lens:
                        sock.sock.close()
                        break
                    self.outputsocks[sock.sock_fileno] = sock
                except StopIteration:
                    # 执行完毕
                    self.runout = True

    def run(self):
        while True:
            # 先检查超时socket
            self.updateips()

            # 扫描两次,可以通过for用一次替代,也可以使用filter
            # self.outputs=list(filter(lambda x:not x.connected,self.socks.values()))
            self.outputs = [x.sock for x in self.outputsocks.values()]
            self.inputs = [x.sock for x in self.inputsocks.values()]

            readable, writeable, exceptional = select.select(self.inputs, self.outputs, self.outputs + self.inputs, 1)
            for x in writeable:
                sock = self.outputsocks.pop(x.fileno())
                if sock.senddata():
                    sock.setconnected()
                    self.inputsocks[x.fileno()]=sock

            for x in readable:
                sock = self.inputsocks.pop(x.fileno())
                if sock.checkdata():
                    if self.callback != None:
                        self.callback(sock.ip,sock.port,sock.proxytype)

            for x in exceptional:
                print('proxy error!')
            # 生成器没有数据并且socks全部处理完毕,跳出循环.
            if len(self.inputsocks)==0 and len(self.outputsocks)==0 and self.runout:
                print('Loop empty...')
                break

class EPollLoop(Loop):
    def __init__(self,callback=None):
        super(EPollLoop,self).__init__(self,callback=callback)
        self.epoll = select.epoll()
        # 这里采用第二种法
        self.socks={}

    def dealtimeout(self):
        for k,v in self.socks.items():
            if v.connected:
                if v[1].checktimeout(5):
                    self.epoll.unregister(k)
                    self.socks.pop(k)
            else:
                if v[1].checktimeout(4):
                    self.epoll.unregister(k)
                    self.socks.pop(k)

    # 删除超时socket,补充列表数量
    def updateips(self,lens=2000):
        self.dealtimeout()
        # 补充socket数量,以保持充分利用
        if len(self.ipsl)!=0:
            for ip,port,proxytype in self.ipsl:
                sock = Proxy.initialize(ip, port, proxytype)
                if sock.sock_fileno>lens:
                    sock.sock.close()
                    break
                self.socks[sock.sock_fileno] = sock
                self.epoll.register(sock.sock_fileno,select.EPOLLIN)
                self.ipsl.remove((ip,port,proxytype))
            if len(self.ipsl)==0 and self.ips==None:
                self.runout=True
        # maybe多余
        if self.ips!=None:
            while True:
                try:
                    ip, port, proxytype = self.ips.__next__()
                    sock = Proxy.initialize(ip, port, proxytype)
                    if sock.sock_fileno>lens:
                        sock.sock.close()
                        break
                    self.socks[sock.sock_fileno] = sock
                    self.epoll.register(sock.sock_fileno,select.EPOLLIN)
                except StopIteration:
                    # 执行完毕
                    self.runout = True

    def run(self):
        while True:
            self.updateips()
            events=self.epoll.poll()
            for fd,event in events:
                if event & select.EPOLLOUT:
                    sock=self.socks[fd]
                    if sock.checkdata():
                        if self.callback != None:
                            self.callback(sock.ip,sock.port,sock.proxytype)

                if event & select.EPOLLIN:
                    sock=self.socks.pop(fd)
                    if sock.checkdata():
                        if self.callback != None:
                            self.callback(sock.ip,sock.port,sock.proxytype)
            if len(self.socks)==0 and self.runout:
                print('Loop empty...')
                break

# 工厂模式
class ProxyIOLoop:
    @classmethod
    def initialize(cls,callback=None):
        if hasattr(select, "epoll"):
            return EPollLoop(callback=callback)
        return SelectIOLoop(callback=callback)