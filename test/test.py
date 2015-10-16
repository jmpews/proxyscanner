# test
def func():
    from flask import Flask
    from proxys.application import init_app
    app = Flask('ScanProxy')
    init_app(app)
    app.test_request_context().push()
    from proxys.models import Proxy

    proxylist=Proxy.query.filter_by(type='Server').order_by(Proxy.id.desc()).limit(10)
    for t in proxylist:
        print(t.id)


# proxy test
def func():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('180.169.18.9',80))
    checkstr = 'GET /nav.js HTTP/1.1\r\nHost:interface.bilibili.com\r\n\r\n'
    sock.send(checkstr.encode())
    data=sock.recv(1024)
    if data.find(b'loadLoginInfo') != -1:
        # 验证成功处理
        print('success')
    elif data.find(b'HTTP/1.1 200 OK') != -1:
        print('error')
        print(data)

def func2():
    from scanner.proxyloop import ProxyIOLoop
    def func(ip,port,proxytype,connect_time):
        print(ip,':',port,'-',proxytype)
    # 添加基本回调
    proxyloop=ProxyIOLoop.initialize(callback=func)
    proxyloop.scanips([('42.159.152.215','42.159.152.235')])
    proxyloop.start()

func()