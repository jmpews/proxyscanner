# ScanProxy
分析协议构造验证数据，采用异步非阻塞socket发送数据，不采用request的方式。

之前没分清国内和国外的IP段，导致去扫国外的，一片超时。所以才有下文的超时处理，但是国内一般不会涉及到超时。但这里还是要说下自己的想法。

首先采用非阻塞的connect，会立即返回，如果返回`EINPROGRESS`,表明正在连接属于正常，在此期间使用`getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)`获取socket的错误，无论对于*正在连接*还是*连接完成*都返回0,直到出现超时异常或其他错误，才返回其他错误码。

#### 如果我们提前做超时异常处理，如何做？
假如三次握手包，要在网络中存在N秒多，那这几秒内，没有函数去判断是否连接完成，因为处在正在连接的过程中，`getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)`对于*正在连接*和*连接完成*的socket都返回0。但是我们可以通过`read()`或者`send()`或者`getpeername()`报异常，来判断。

几个注意点:

* 1.IP的区段 http://ips.chacuo.net/
* 2.非阻塞connect的返回码'EINPROGRESS',表示正在连接
* 3.`getpeername()`验证连接

### Http代理验证方式
当你发送`‘CONNECT %s:%s HTTP/1.1\r\nHost: %s:%s\r\nProxy-Connection: keep-alive\r\n\r\n’%（ip,port)`,接收到的response包含`b'Connection established'`表明，可以作为代理。或者直接connect后`send()`一个get请求

### Socks5代理代理验证
当你发送`b'\x05\x02\x00\x02'`，接收到的data包含`b'\x05\x00'`,可以作为代理，这里仅仅是简单说明，但其中还涉及到验证等等复杂问题。


## How to Use it ?
### 1. 验证Proxy_ip列表

```
def func(ip,port,proxytype):
    print(ip,':',port,proxytype)

proxyloop=ProxyIOLoop(callback=func)
proxyloop.addipsl([('183.129.190.179',1080),('183.129.190.178',1080)],roxytype='http')
proxyloop.start()
```

### 2. 扫描IP段是否存在代理

```
def func(ip,port,proxytype):
    print(ip,':',port,proxytype)

proxyloop=ProxyIOLoop(callback=func)
proxyloop.scanips([('202.38.134.0', '202.38.134.255'),('122.144.128.0', '122.144.255.255')],proxytype='socks',ports=[80, 1080, 3128, 8080])
proxyloop.start()
```

### 3. 可以在回调函数处理中将扫描到的proxy丢到redis.