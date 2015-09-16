__author__ = 'jmpews'
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip='211.218.126.189'
port=3128
sock.connect((ip, port))
# connstr="CONNECT %s:%s HTTP/1.1\r\nHost: %s:%s\r\nProxy-Connection: keep-alive\r\n\r\n" % (ip,port,ip,port)
connstr="CONNECT github.com:443 HTTP/1.1\r\nHost: github.com:443\r\nProxy-Connection: keep-alive\r\n\r\n"

print(connstr)
sock.send(connstr.encode())

r=sock.recv(1024)
print(r)