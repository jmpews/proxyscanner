

HOST='weixin.linevery.com'
HOST_REQ='/'
HTTP_REQ='GET / HTTP/1.1\r\nHost:'+HOST+'\r\n\r\n'
import struct,socket
payload=b'\x01'+socket.inet_aton('112.126.76.80')+struct.pack('!H',80)+HTTP_REQ.encode()
# payload=b'\x01'+socket.inet_pton(socket.AF_INET,'112.126.76.80')+b'\x00\x50'+b'GET / HTTP/1.1\r\nHost:weixin.sxuhome.com\r\n\r\n'
