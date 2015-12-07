import time
import select
import threading
from .proxysock import Proxy,GeneralProxyError
from .utils import n2ip,ip2n
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
        self.default_callback=callback
        self.sum_ipsl=0
        self.sum_ips=0
        self.scanned_ips=0
        self.scanned_ipsl=0

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
                func(self)
            else:
                break
    # ip列表
    def addipsl(self, ipsl,callback=None,proxytype='http'):
        """

        :param ipsl: [[ip,port],[ip,port]]
        :param callback:
        :param proxytype:
        :return:
        """
        self.sum_ipsl=len(ipsl)

        for ip,port in ipsl:
            self.ipsl.append((ip,port,proxytype,callback))

    # 扫描IP段
    # 采用生成器防止大列表爆掉
    def scanips(self, ips,proxytype='http', ports=[443]):

        for s,e in ips:
            self.sum_ips+=(ip2n(e)-ip2n(s))

        # 根据IP段生成列表
        def func():
            for s, e in ips:
                for t in range(ip2n(s), ip2n(e)):
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
        """
        1. 手动处理超时,关闭连接,
        2. 使用filter,也可以使用for
            self.outputsocks=dict(filter(lambda x:not x[1].checktimeout(4),self.outputsocks.items()))
            self.inputsocks=dict(filter(lambda x:not x[1].checktimeout(5),self.inputsocks.items()))
        """
        tmp=[]
        for fd,sock in self.outputsocks.items():
            if sock.checktimeout(5):
                sock.sock.close()
                tmp.append(fd)
        for fd in tmp:
            self.outputsocks.pop(fd)


        tmp=[]
        for fd,sock in self.inputsocks.items():
            if sock.checktimeout(3):
                sock.sock.close()
                tmp.append(fd)
        for fd in tmp:
            self.inputsocks.pop(fd)


    def updateips(self,MAX_CONNECT=1000):
        """
        1. 删除超时的socket
        2. 补充socket连接池,维持数量

        :param lens:连接池的数量
        :return:
        """
        self.dealtimeout()

        if len(self.ipsl)!=0:
            for ip,port,proxytype,callback in self.ipsl:
                sock = Proxy.initialize(ip, port, proxytype,callback)
                if sock.sock.fileno()>MAX_CONNECT:
                    sock.sock.close()
                    break
                self.outputsocks[sock.sock.fileno()] = sock
                self.ipsl.remove((ip,port,proxytype,callback))
                self.scanned_ipsl+=1
            if len(self.ipsl)==0 and self.ips==None:
                self.runout=True

        if self.ips!=None:
            while True:
                try:
                    ip, port, proxytype = self.ips.__next__()
                    sock = Proxy.initialize(ip, port, proxytype)
                    if sock.sock.fileno()>MAX_CONNECT:
                        sock.sock.close()
                        break
                    self.outputsocks[sock.sock.fileno()] = sock
                    self.scanned_ips+=1
                except StopIteration:
                    # 执行完毕
                    self.runout = True
                    break

    def run(self):
        """
        1. 新的线程执行事件循环
        2. 检查定时器
        3. 更新socket连接池

        :return:
        """

        while True:
            self.checktimer()
            self.updateips()

            self.outputs = [x.sock for x in self.outputsocks.values()]
            self.inputs = [x.sock for x in self.inputsocks.values()]

            readable, writeable, exceptional = select.select(self.inputs, self.outputs,[] , 1)

            for x in writeable:
                sock = self.outputsocks.pop(x.fileno())
                try:
                    sock.senddata()
                except GeneralProxyError:
                    print('! send error')
                else:
                    sock.setconnected()
                    self.inputsocks[x.fileno()]=sock

            for x in readable:
                sock = self.inputsocks.pop(x.fileno())
                try:
                    sock.checkdata()
                except GeneralProxyError:
                    print(' read error')
                else:
                    connect_timeout=int(time.time()-sock.starttime)
                    if sock.callback==None:
                        self.default_callback(sock.ip,sock.port,sock.proxytype,sock.anonymous,connect_timeout)
                    else:
                        sock.callback(sock.ip,sock.port,sock.proxytype,sock.anonymous,connect_timeout)


            # 生成器没有数据并且socks全部处理完毕,跳出循环.
            if len(self.inputsocks)==0 and len(self.outputsocks)==0 and self.runout:
                print('Loop empty...')
                time.sleep(2)

class EPollLoop(Loop):
    """
    采用第二种方法把input和output放在一个socks列表
    """
    def __init__(self,callback):
        super(EPollLoop,self).__init__(callback=callback)
        self.epoll = select.epoll()
        self.socks={}

    def dealtimeout(self):
        tmp=[]
        for fd,sock in self.socks.items():
            if sock.connected:
                if sock.checktimeout(5):
                    sock.sock.close()
                    self.epoll.unregister(fd)
                    # self.socks.pop(fd)
                    tmp.append(fd)


            else:
                if sock.checktimeout(3):
                    sock.sock.close()
                    self.epoll.unregister(fd)
                    # self.socks.pop(fd)
                    tmp.append(fd)
        for fd in tmp:
            self.socks.pop(fd)


    def updateips(self,MAX_CONNECT=2000):
        self.dealtimeout()
        if len(self.ipsl)!=0:
            for ip,port,proxytype,callback in self.ipsl:
                sock = Proxy.initialize(ip, port, proxytype,callback)
                if sock.sock.fileno() >MAX_CONNECT:
                    sock.sock.close()
                    break
                self.socks[sock.sock.fileno()] = sock
                self.epoll.register(sock.sock.fileno(),select.EPOLLOUT|select.EPOLLET)
                self.ipsl.remove((ip,port,proxytype,callback))
                self.scanned_ipsl+=1
            if len(self.ipsl)==0 and self.ips==None:
                self.runout=True
        # maybe多余
        if self.ips!=None:
            while True:
                try:
                    ip, port, proxytype = self.ips.__next__()
                    sock = Proxy.initialize(ip, port, proxytype)
                    if sock.sock.fileno()>MAX_CONNECT:
                        sock.sock.close()
                        break
                    self.socks[sock.sock.fileno()] = sock
                    self.epoll.register(sock.sock.fileno(),select.EPOLLOUT|select.EPOLLET)
                    self.scanned_ips+=1
                except StopIteration:
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
                    try:
                        sock.senddata()
                    except GeneralProxyError:
                        print(' read error')
                    else:
                        sock.setconnected()
                        self.epoll.modify(fd, select.EPOLLIN|select.EPOLLET)

                if event & select.EPOLLIN:
                    sock=self.socks.pop(fd)
                    self.epoll.unregister(fd)
                    try:
                        sock.checkdata()
                    except GeneralProxyError:
                        print(' read error')

                    else:
                        connect_timeout=int(time.time()-sock.starttime)
                        if sock.callback==None:
                            self.default_callback(sock.ip,sock.port,sock.proxytype,sock.anonymous,connect_timeout)
                        else:
                            sock.callback(sock.ip,sock.port,sock.proxytype,sock.anonymous,connect_timeout)

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