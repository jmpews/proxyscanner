import time
import select
import threading
from .proxysock import Proxy


class Loop(threading.Thread):
    def __init__(self,callback):
        """
         如何处理待接受和待发送的socket?
        一种方法,可以选择将output和input分开存放
        self.outputsocks={}
        self.inputsocks={}
        另一种方法,合并,用connected属性标记区分,在select需要重新生成两部socket列表
        self.socks = {}
        """
        threading.Thread.__init__(self)
        self.runout = False
        self.ips=None
        self.ipsl=[]
        self.callbacks=[]
        self.scancallback=callback

    def addtimer(self,func,timeout,once=1):
        cur=int(time.time())
        if once:
            self.callbacks.append((func,cur,timeout,1))
        else:
            self.callbacks.append((func,cur,timeout,0))
        self.callbacks.sort(key=lambda x:x[1])

    def checktimer(self):
        cur=int(time.time())
        for func,prev,timeout,once in self.callbacks:
            if prev+timeout<cur:
                self.callbacks.remove((func,prev,timeout,once))
                if not once:
                    self.callbacks.append((func,cur,timeout,once))
                func()
            else:
                break
    # ip列表
    def addipsl(self, ipsl,callback=None,proxytype='http'):
        # 根据现成list生成
        # [[ip,port]]
        for ip,port in ipsl:
            self.ipsl.append((ip,port,proxytype,callback))

    # 扫描IP段
    # 采用生成器防止大列表爆掉
    def scanips(self, ips,proxytype='http', ports=[443]):
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
    """
    对于select我们采用第一种方法 inputs和outputs分开
    """
    def __init__(self,callback):
        super(SelectIOLoop,self).__init__(callback=callback)
        self.outputs=[]
        self.inputs=[]
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
            for ip,port,proxytype,callback in self.ipsl:
                sock = Proxy.initialize(ip, port, proxytype,callback)
                if sock.sock.fileno():
                    sock.sock.close()
                    break
                self.outputsocks[sock.sock.fileno()] = sock
                self.ipsl.remove((ip,port,proxytype,callback))
            if len(self.ipsl)==0 and self.ips==None:
                self.runout=True
        if self.ips!=None:
            while True:
                try:
                    ip, port, proxytype = self.ips.__next__()
                    sock = Proxy.initialize(ip, port, proxytype)
                    if sock.sock.fileno()>lens:
                        sock.sock.close()
                        break
                    self.outputsocks[sock.sock.fileno()] = sock
                except StopIteration:
                    # 执行完毕
                    self.runout = True
                    break

    def run(self):
        while True:
            self.checktimer()
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
                    connect_time=int(time.time()-sock.starttime)
                    if sock.callback==None:
                        self.scancallback(sock.ip,sock.port,sock.proxytype,sock.anonymous,connect_time)
                    else:
                        sock.callback(sock.ip,sock.port,sock.proxytype,sock.anonymous,connect_time)

            for x in exceptional:
                print('proxy error!')

            print(self.ips.__next__())

            # 生成器没有数据并且socks全部处理完毕,跳出循环.
            if len(self.inputsocks)==0 and len(self.outputsocks)==0 and self.runout:
                print('Loop empty...')
                time.sleep(2)

class EPollLoop(Loop):
    def __init__(self,callback):
        super(EPollLoop,self).__init__(callback=callback)
        self.epoll = select.epoll()
        # 这里采用第二种法
        self.socks={}

    def dealtimeout(self):
        tmp=[]
        for k,v in self.socks.items():
            if v.connected:
                if v.checktimeout(5):
                    tmp.append(k)
            else:
                if v.checktimeout(4):
                    tmp.append(k)
        for k in tmp:
            self.epoll.unregister(k)
            self.socks.pop(k)

    # 删除超时socket,补充列表数量
    def updateips(self,lens=2000):
        self.dealtimeout()
        # 补充socket数量,以保持充分利用
        if len(self.ipsl)!=0:
            for ip,port,proxytype,callback in self.ipsl:
                sock = Proxy.initialize(ip, port, proxytype,callback)
                if sock.sock.fileno() >lens:
                    sock.sock.close()
                    break
                self.socks[sock.sock.fileno()] = sock
                self.epoll.register(sock.sock.fileno(),select.EPOLLOUT|select.EPOLLET)
                self.ipsl.remove((ip,port,proxytype,callback))
            if len(self.ipsl)==0 and self.ips==None:
                self.runout=True
        # maybe多余
        if self.ips!=None:
            while True:
                try:
                    ip, port, proxytype = self.ips.__next__()
                    sock = Proxy.initialize(ip, port, proxytype)
                    if sock.sock.fileno()>lens:
                        sock.sock.close()
                        break
                    self.socks[sock.sock.fileno()] = sock
                    self.epoll.register(sock.sock.fileno(),select.EPOLLOUT|select.EPOLLET)
                except StopIteration:
                    # 执行完毕
                    self.runout = True
                    break

    def run(self):
        while True:
            self.checktimer()
            self.updateips()
            events=self.epoll.poll(1)
            for fd,event in events:
                if event & select.EPOLLOUT:
                    sock=self.socks[fd]
                    if sock.senddata():
                        sock.setconnected()
                        self.epoll.modify(fd, select.EPOLLIN|select.EPOLLET)

                if event & select.EPOLLIN:
                    sock=self.socks.pop(fd)
                    self.epoll.unregister(fd)
                    if sock.checkdata():
                        connect_time=int(time.time()-sock.starttime)
                        if sock.callback==None:
                            self.scancallback(sock.ip,sock.port,sock.proxytype,sock.anonymous,connect_time)
                        else:
                            sock.callback(sock.ip,sock.port,sock.proxytype,sock.anonymous,connect_time)

            if len(self.socks)==0 and self.runout:
                print('Loop empty...')
                time.sleep(2)

# 工厂模式
class ProxyIOLoop:
    @classmethod
    def initialize(cls,callback):
        ProxyIOLoop.running=True
        print(ProxyIOLoop.running)
        if hasattr(select, "epoll"):
            return EPollLoop(callback=callback)
        return SelectIOLoop(callback=callback)