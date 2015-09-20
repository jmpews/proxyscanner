__author__ = 'jmpews'
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip='112.84.130.4:10000'
ip,port=ip.split(':')
print(ip,port)
sock.connect((ip, int(port)))

# connstr='GET / HTTP/1.1\r\nHost:hm.baidu.com\r\n\r\n'
connstr='GET / HTTP/1.1\r\nHost:weixin.sxuhome.com\r\n\r\n'
# connstr="CONNECT %s:%s HTTP/1.1\r\nHost: %s/:%s\r\nProxy-Connection: keep-alive\r\n\r\n" % (ip,port,ip,port)
# connstr="CONNECT github.com:443 HTTP/1.1\r\nHost: github.com:443\r\nProxy-Connection: keep-alive\r\n\r\n"
sock.send(connstr.encode())
#
# sock.send(b'\x05\x02\x00\x02')


r=sock.recv(1024)
sock.close()
# print(r.find(b'\x05\x00'))
print(r)
import time
# import select
# sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock1.setblocking(0)
# err1=sock1.connect_ex(('118.144.108.254', 3128))
#
# sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock2.setblocking(0)
# err2=sock2.connect_ex(('202.207.209.83', 80))
# # while True:
# #     print(sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR))
# #     time.sleep(3)
# r=select.select([sock1,sock2],[sock1],[sock1,sock2],60*20)
# r[1][0].send(b'test')
# print(r)

# ipfile=open('ip_shanghai.txt','r',encoding='utf-8')
# for line in ipfile:
#     print(line.split('\t'))