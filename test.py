__author__ = 'jmpews'
import socket
socklist=[]
import struct
# for i in range(50):
# import socket
# sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.setblocking(0)
#     # sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
#     # sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 0, 0))
#     code=sock.connect(('58.220.2.131',80))
#     print(sock.fileno())
#     socklist.append(sock)
#
# import select
# while True:
#     try:
#         readable, writeable, exceptional = select.select([],socklist , [], 1)
#     except Exception as e:
#         print(e.__class__)
#         print(e)
#     for x in writeable:
#         socklist.remove(x)
#         print(len(socklist))
#         x.close()
#
# import time
# time.sleep(300)
# # readable, writeable, exceptional = select.select(socklist2,socklist2 , [], 1)
# def func():
#     for x in range(100):
#         print(1)
#         break
#
# print(func())

import socket
sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('116.228.169.203',80))
checkstr = 'GET / HTTP/1.1\r\nHost:202.207.209.82\r\n\r\n'
# checkstr = 'GET / HTTP/1.1\r\nHost:112.126.76.80\r\n\r\n'
# checkstr = 'GET / HTTP/1.1\r\nHost:180.149.132.47\r\n\r\n'
sock.send(checkstr.encode())
data=sock.recv(1024)
print(data)