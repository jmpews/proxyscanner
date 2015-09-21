__author__ = 'jmpews'
import socket
import time

#发送验证字符串
def sendhttp(x):
    # # 两种验证方式
    # # 根据http 的connect方法验证,需要支持connect方法
    # try:
    #     t=x.getpeername()
    # except Exception as e:
    #     print(e)
    #     print('Send Error: ',x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR))
    # connstr="CONNECT %s:%s HTTP/1.1\r\nHost: %s:%s\r\nProxy-Connection: keep-alive\r\n\r\n" % (t[0],t[1],t[0],t[1])
    # x.send(connstr.encode())

    #直接尝试访问一次
    connstr='GET / HTTP/1.1\r\nHost:hm.baidu.com\r\n\r\n'
    try:
        x.send(connstr.encode())
    except Exception as e:
        print(e)
        print('Send Error: ',x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR))


#检查response是否存在字符串
def checkhttp(data):
    # connect方法验证
    # if data.find(b'Connection established')==-1:

    # 直接验证200 code
    if data.find(b'200 OK')==-1:
        return False
    return True

# 发送socks验证数据
def sendsocks(x):
    try:
        x.send(b'\x05\x02\x00\x02')
    except Exception as e:
        print(e)
        print('Send Error: ',x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR))
#检查response是否存在字符串.
def checksocks(data):
    if data.find(b'\x05\x00') == -1:
        return False
    return True


# 采用生成器方式,防止超长list爆内存
def genips(ipl,l=False):
    httports=[80,1080,3128,8080]
    def s2n(str):
        i=[int(x) for x in str.split('.')]
        return i[0]<<24|i[1]<<16|i[2]<<8|i[3]
    def n2ip(num):
        return '%s.%s.%s.%s' % (
            (num&0xFF000000)>>24,
            (num&0x00FF0000)>>16,
            (num&0x0000FF00)>>8,
            (num&0x000000FF)
        )
    if not l:
        for s,e in ipl:
            for t in range(s2n(s),s2n(e)):
                for port in httports:
                    yield n2ip(t),port
    else:
        for x in ipl:
            yield x


# 对于每个IP生成4个socket,表示检查4个常见端口
def addips(ip,port):
    tm=int(time.time())
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 非阻塞connect
    sock.setblocking(0)
    err=sock.connect_ex((ip, port))
    return (sock,sock.fileno(),tm)

# 检查sock是否超时
def checktimeout(x):
    t=time.time()
    if x[2]+6<t:
        try:
            x[0].getpeername()
        except:
            x[0].close()
            return False
    return True

def updatelist(outputimeouts,ips):
    # 清除超时connect
    # 由于非阻塞的connect,所以要手动排除超时的connect
    flag=0
    outputimeouts=list(filter(checktimeout,outputimeouts))

    # 维持数据数量
    if len(outputimeouts)<400:
        for i in range(400-len(outputimeouts)):
            try:
                ip,port=ips.__next__()
            except StopIteration:
                # 循环到ip列表最后
                flag=1
                break
            outputimeouts.append(addips(ip,port))

    #补充数据
    outputs=[x[0] for x in outputimeouts]
    return outputimeouts,outputs,flag