# test
def func5():
    from flask import Flask
    from proxys.application import init_app
    app = Flask('ScanProxy')
    init_app(app)
    app.test_request_context().push()
    from proxys.models import Proxy
    proxylist=Proxy.query.filter_by(type='http').order_by(Proxy.id.desc())
    for t in proxylist:
        print(t.ip)


# proxy test
def func4():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('202.106.169.142',80))
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

def func3():
    from scanner.proxyloop import ProxyIOLoop
    def func(ip,port,proxytype,connect_time):
        print(ip,':',port,'-',proxytype)
    # 添加基本回调
    proxyloop=ProxyIOLoop.initialize(callback=func)
    proxyloop.addipsl([('183.43.184.2',3128),('183.43.54.124',3128)])
    proxyloop.start()


def func6():
    from scanner.sqldb import session,Proxy
    from scanner.proxyloop import ProxyIOLoop
    def func(ip,port,proxytype,connect_time):
        p=Proxy(ip,port,proxytype,connect_time)
        session.add(p)
        session.commit()
    r=session.query(Proxy).filter(Proxy.type=='http').all()
    session.query(Proxy).filter(Proxy.type=='http').delete()
    session.commit()
    checkproxylist=[]
    for t in r:
        checkproxylist.append((t.ip,t.port))
    proxyloop=ProxyIOLoop.initialize(callback=func)
    proxyloop.addipsl(checkproxylist)
    proxyloop.start()
func6()
# func4()