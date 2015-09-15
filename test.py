__author__ = 'jmpews'
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('168.102.15.16', 8080))
sock.send("CONNECT 168.102.15.16:8080 HTTP/1.1\r\nHost: 168.102.15.16:8080\r\nProxy-Connection: keep-alive\r\n\r\n".encode())

r=sock.recv(1024).decode()
print(r)