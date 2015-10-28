# ScanProxy

分析协议构造验证数据，采用异步非阻塞socket去扫描IP，不采用requests或urllib的方式。根据不同平台使用select或者epoll同时并发2K非阻塞connect去检测IP是否存在代理,然后每隔12小时检测已存在IP是否失效.

之前没分清国内和国外的IP段，导致去扫国外的，一片超时。所以才有下文的超时处理,对于在几秒时间内没有完成socket连接的建立,就删除这个socket.

首先采用非阻塞的connect，会立即返回，如果返回`EINPROGRESS`,表明正在连接属于正常，在此期间使用`getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)`获取socket的错误，无论对于*正在连接*还是*连接完成*都返回0,直到出现超时异常或其他错误，才返回其他错误码。

#### 如果我们提前做超时异常处理，如何做？
假如三次握手包，要在网络中存在N秒多，那这几秒内，没有函数去判断是否连接完成，因为处在正在连接的过程中，`getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)`对于*正在连接*和*连接完成*的socket都返回0。但是我们可以通过`read()`或者`send()`或者`getpeername()`报异常，来判断。

几个注意点:

* 1.IP的区段 http://ips.chacuo.net/
* 2.非阻塞connect的返回码'EINPROGRESS',表示正在连接
* 3.`getpeername()`验证连接

## 设计方法?

对不同的proxy采用工厂模式,以及IO事件循环都采用工厂模式,在根据不同平台选择实现select还是EPoll.对于扫描到的IP采用回调的函数去处理.采用SQLALchemy去做数据库层处理




### Http代理验证方式
当你发送`‘CONNECT %s:%s HTTP/1.1\r\nHost: %s:%s\r\nProxy-Connection: keep-alive\r\n\r\n’%（ip,port)`,接收到的response包含`b'Connection established'`表明，可以作为代理。或者直接connect后`send()`一个get请求

### Socks5代理代理验证
当你发送`b'\x05\x02\x00\x02'`，接收到的data包含`b'\x05\x00'`,可以作为代理，这里仅仅是简单说明，但其中还涉及到验证等等复杂问题。


## How to Use it ?

```
# 对于扫描到的Proxy 回调函数处理
def func(ip,port,proxytype,anonymous,connect_time):
    if session.query(Proxy).filter(Proxy.ip==ip,Proxy.port==port,Proxy.type==proxytype).first()==None:
        try:
            # http://www.ipip.net/的IP数据库
            pos=IPFIND(ip).split('\t')
            if pos[len(pos)-2]=='':
               position=pos[len(pos)-1]
            else:
                position=pos[len(pos)-2]+'.'+pos[len(pos)-1]
        except:
            position='None.None'
            print('ERROR:IP',ip)
        # 数据库保存
        p=Proxy(ip,port,proxytype,anonymous,position,connect_time)
        session.add(p)
        session.commit()

# 定期检查proxy是否有效
def TimerCheck(proxytype='http'):
    # 回调函数
    def func(ip,port,proxytype,anonymous,connect_time):
        if session.query(Proxy).filter(Proxy.ip==ip,Proxy.port==port,Proxy.type==proxytype).first()==None:
            try:
                pos=IPFIND(ip).split('\t')
                if pos[len(pos)-2]=='':
                   position=pos[len(pos)-1]
                else:
                    position=pos[len(pos)-2]+'.'+pos[len(pos)-1]
            except:
                position='None.None'
            p=Proxy(ip,port,proxytype,anonymous,position,connect_time)
            session.add(p)
            session.commit()
    # 进行double检测,防止一次检测失误.
    r=session.query(Proxy).filter(Proxy.type==proxytype).all()
    session.query(Proxy).filter(Proxy.type==proxytype).delete()
    session.commit()
    checkproxylist=[]
    print('原有长度',len(r))
    for t in r:
        checkproxylist.append((t.ip,t.port))
    checkproxylist+=checkproxylist
    proxyloop.addipsl(checkproxylist,callback=func)

# 添加基本回调
proxyloop=ProxyIOLoop.initialize(callback=func)

# 添加定时器,once=False表明,执行完,再次更新该定时器,重新添加.once=True表明只执行一次.
proxyloop.addtimer(TimerCheck,3600*12,once=False)

# 添加一个IP段列表,进行扫描
filelist=['ip_beijing.txt','ip_shanghai.txt','ip_zhejiang.txt','ip_guangdong.txt']
iplists=[]
for f in filelist:
    ipfile=open('iplists/'+f,'r',encoding='utf-8')
    for line in ipfile:
        tmp=line.split('\t')
        iplists.append((tmp[0],tmp[1]))
    ipfile.close()

# 几种常见调用方式.
# proxyloop.addipsl(iplists,callback=func2)
# proxyloop.scanips([('182.254.153.50','182.254.153.59')],proxytype='http')
proxyloop.scanips(iplists,proxytype='http')
```

### 2. 扫描IP段是否存在代理

