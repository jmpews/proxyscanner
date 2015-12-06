# # Test
#
# # SQLAlchemy测试
# def func5():
#     from flask import Flask
#     from app.application import init_app
#     app = Flask('ScanProxy')
#     init_app(app)
#     app.test_request_context().push()
#     from app.models import Proxy
#     proxylist=Proxy.query.filter_by(type='http').order_by(Proxy.id.desc())
#     for t in proxylist:
#         print(t.ip)
#
#
# # 手动检测该IP是否存在http proxy
# def func4():
#     import socket
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.connect(('101.66.253.22',8080))
#     checkstr = 'GET /nav.js HTTP/1.1\r\nHost:interface.bilibili.com\r\n\r\n'
#     sock.send(checkstr.encode())
#     data=sock.recv(1024)
#     if data.find(b'loadLoginInfo') != -1:
#         # 验证成功处理
#         print('success')
#     elif data.find(b'HTTP/1.1 200 OK') != -1:
#         print('error')
#         print(data)
#
# def func2():
#     from scanner.ext.proxyloop import ProxyIOLoop
#     def func(ip,port,proxytype,connect_time):
#         print(ip,':',port,'-',proxytype)
#     # 添加基本回调
#     proxyloop=ProxyIOLoop.initialize(callback=func)
#     proxyloop.scanips([('121.52.240.175','121.52.240.181')])
#     proxyloop.start()
#
# def func3():
#     from scanner.ext.proxyloop import ProxyIOLoop
#     def func(ip,port,proxytype,connect_time):
#         print(ip,':',port,'-',proxytype)
#     # 添加基本回调
#     proxyloop=ProxyIOLoop.initialize(callback=func)
#     proxyloop.addipsl([('183.43.184.2',3128),('183.43.54.124',3128)])
#     proxyloop.start()
#
# # 检测SQLALChemy
# def func6():
#     from scanner.ext.sqldb import session,Proxy
#     def func(ip,port,proxytype,connect_time):
#         p=Proxy(ip,port,proxytype,connect_time)
#         session.add(p)
#         session.commit()
#     r=session.query(Proxy).filter(Proxy.type=='httpp').first()
#     print(r)
#     # session.query(Proxy).filter(Proxy.type=='http').delete()
#     # session.commit()
#     # checkproxylist=[]
#     # for t in r:
#     #     checkproxylist.append((t.ip,t.port))
#     # proxyloop=ProxyIOLoop.initialize(callback=func)
#     # proxyloop.addipsl(checkproxylist)
#     # proxyloop.start()
#
# # func6()
# # func4()
#
#
# from scanner.ext.proxyloop import ProxySocks
# socks5=ProxySocks('23.110.7.32',443,'socks')
# socks5.senddata()
# socks5.checkdata()


import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1',1080))
sock.send(b'\x05\x02\x00\x02')
data=sock.recv(1024)
print(data)
checkstr = 'GET / HTTP/1.1\r\nHost:www.baidu.com\r\n\r\n'
sock.send(checkstr.encode())
data=sock.recv(1024)
print(data)