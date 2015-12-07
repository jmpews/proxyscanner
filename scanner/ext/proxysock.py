import logging
import socket
import time
import struct
import re
from setttings import *

p=re.compile(b'jmpews0307:(\w+?):')

PROXY_SOCKS5=1
PROXY_HTTP=2
PROXY_SS=3

class ProxyError(IOError):
    """
    from pysocks
    """
    def __init__(self, msg, socket_err=None):
        self.msg = msg
        self.socket_err = socket_err

        if socket_err:
            self.msg += ": {0}".format(socket_err)

    def __str__(self):
        return self.msg

class GeneralProxyError(ProxyError): pass

class Sock(object):
    """
    socket 对象
    """
    def __init__(self, ip, port,callback=None):
        self.ip = ip
        self.port = port
        self.anonymous='None'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.starttime = int(time.time())
        self.sock.setblocking(0)
        # 端口复用
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        # close发送RST,不存在TIME_WAIT状态
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        # EINPROGRESS
        self.sock.connect_ex((ip, port))
        self.connected = False
        self.callback=callback

    # 检测超时,timeout1为connect的超时时间.timeout2为send后的接受超时.
    def checktimeout(self, timeout=4):
        currenttime = int(time.time())
        if currenttime - self.starttime > timeout:
            return True
        return False

    def checkerror(self):
        # 常见error ECONNREFUSED ETIMEDOUT EHOSTUNREACH
        self.errno = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if self.errno == 0 or self.errno==socket.errno.EINPROGRESS:
            return True
        return False


    # 设置连接状态
    def setconnected(self):
        self.connected = True
        self.starttime = int(time.time())

    # 发送数据
    def send(self,data):
        try:
            self.sock.send(data)
        except:
            # logging.error('! %s:%s send error'%(self.ip,self.port))
            if self.checkerror():
                logging.info('> normal error.')
            self.sock.close()
            raise GeneralProxyError("send error")

    # 接收数据
    def recv(self):
        try:
            data = self.sock.recv(1024)
        except:
            # logging.error('! %s:%s recv error'%(self.ip,self.port))
            if self.checkerror():
                logging.info('> normal error.')
            self.sock.close()
            raise GeneralProxyError("recv error")
        return data

# HTTP代理对象
class ProxyHttp(Sock):
    def __init__(self, ip, port,callback=None):
        super(ProxyHttp, self).__init__(ip, port,callback)

    # 发送检测数据
    def senddata(self):
        # checkstr = 'GET /checkproxy?rip=%s HTTP/1.1\r\nHost:'+HOST+'\r\n\r\n' %(self.ip)
        self.send(HTTP_REQ.encode())


    # 检测返回数据
    def checkdata(self):
        status,data = self.sock.recv(1024)
        r=p.findall(data)
        if len(r)!=0:
            self.anonymous=r[0].decode()
            return True
        return False


# socks5代理
class ProxySocks5(Sock):
    def __init__(self, ip, port,callback=None):
        super(ProxySocks5, self).__init__(ip, port,callback)

    def senddata(self):
        self.send(b'\x05\x02\x00\x02')

    def checkdata(self):
        data = self.recv()
        if data.find(b'\x05\x00') != -1:
            return True
        return False


# shadowsocks

class ProxyShadowsocks(Sock):
    def __init__(self, ip, port,callback=None):
        super(ProxyShadowsocks, self).__init__(ip, port,callback)
        self.pay_load=None
        self.Encryptor=None

    def set_payload(self,data):
        self.pay_load=data
    def set_Encryptor(self,Encryptor):
        self.Encryptor=Encryptor

    def senddata(self):
        if  payload:
            return self.send(self.pay_load)
        else:
            print("! no pay_load")
            time.sleep(500)


    def checkdata(self):
        data = self.recv()
        if data:
            if self.Encryptor:
                data=self.Encryptor.decrypt(data)
                print(data)
                # print(data)
                if data.find(b'Hello')!=-1:
                    print('success')
                    print(self.ip)
            else:
                print('! no Encryptor')
                time.sleep(400)
        return False


# 工厂模式
# sock=Porxy.initialize(self,ip,port,proxytype)
class Proxy:
    @classmethod
    def initialize(cls, ip, port, proxytype,callback=None):
        if proxytype == PROXY_HTTP:
            return ProxyHttp(ip, port, callback)
        elif proxytype ==PROXY_SOCKS5:
            return ProxySocks5(ip, port, callback)
        elif proxytype ==PROXY_SS:
            return ProxyShadowsocks(ip, port, callback)

if __name__=='__main__':
    from ext.shadowsocks.common import pack_addr
    from ext.shadowsocks import encrypt,common
    # encryptor = encrypt.Encryptor(b'password', 'aes-256-cfb')
    # shadowsocksdata=common.pack_addr('112.126.76.80')+b'\x00\x50'+b'GET /shadowsocks HTTP/1.1\r\nHost:'+HOST+b'\r\n\r\n'
    # shadowsocksdata=common.pack_addr('112.126.76.80')+b'\x00\x50'+b'GET / HTTP/1.1\r\nHost:weixin.sxuhome.com\r\n\r\n'
    # shadowsocksdata = encryptor.encrypt(shadowsocksdata)
    # payload=pack_addr('112.126.76.80')+b'\x00\x50'+b'GET / HTTP/1.1\r\nHost:weixin.sxuhome.com\r\n\r\n'

    # proxy=Proxy.initialize('23.110.7.32',443,proxytype=PROXY_SS)
    # from ext.utils import SSEncryptor
    # encryptor=SSEncryptor('password')
    # data=encryptor.encrypt(payload)
    # proxy.set_payload(data)
    # proxy.set_Encryptor(encryptor)
    #
    # time.sleep(1)
    # proxy.senddata()
    # time.sleep(1)
    # proxy.checkdata()


