__author__ = 'jmpews'
import socket
import time
import select
import errno

#发送验证字符串
def _sendhttp(x):
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
        print('Send Error: ',x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR))


#检查response是否存在字符串
def _checkhttp(data):
    # connect方法验证
    # if data.find(b'Connection established')==-1:

    # 直接验证200 code
    if data.find(b'200 OK')==-1:
        return False
    return True

# 发送socks验证数据
def _sendsocks(x):
    try:
        x.send(b'\x05\x02\x00\x02')
    except Exception as e:
        print('Send Error: ',x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR))

#检查response是否存在字符串.
def _checksocks(data):
    if data.find(b'\x05\x00') == -1:
        return False
    return True


# 采用生成器方式,防止超长list爆内存
def genips(ipl,list=False):
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
    if not list:
        # 根据IP段生成列表
        for s,e in ipl:
            for t in range(s2n(s),s2n(e)):
                for port in httports:
                    yield n2ip(t),port
    else:
        # 根据现成list生成
        # [[ip,port]]
        for x in ipl:
            yield x


def _connect(ip,port):
    tm=int(time.time())
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 非阻塞connect
    sock.setblocking(0)
    err=sock.connect_ex((ip, port))
    return (sock,sock.fileno(),tm)

# 检查sock是否超时
def _checktimeout_output(x):
    t=time.time()
    if x[2]+5<t:
        try:
            x[0].getpeername()
        except:
            x[0].close()
            return False
    return True

# read设定超时时间.
def _checktimeout_input(x):
    t=time.time()
    if x[1]+5<t:
        x[0].close()
        return False
    return True

# 更新列表,维持非阻塞connect
def updatelist(outputimeouts,inputimeouts,ips):
    # 清除超时connect
    # 由于非阻塞的connect,所以要手动排除超时的connect
    flag=0
    outputimeouts=list(filter(_checktimeout_output,outputimeouts))
    inputimeouts=list(filter(_checktimeout_input,inputimeouts))

    # 维持数据数量
    if len(outputimeouts)<400:
        for i in range(400-len(outputimeouts)):
            try:
                ip,port=ips.__next__()
            except StopIteration:
                # 循环到ip列表最后
                flag=1
                break
            outputimeouts.append(_connect(ip,port))

    #补充数据
    outputs=[x[0] for x in outputimeouts]
    inputs=[x[0] for x in inputimeouts]
    return outputimeouts,outputs,inputimeouts,inputs,flag

#
def checkproxy(ipl,list=False,proxytype='http'):
    inputs=[]
    outputs=[]
    outputimeouts=[]
    inputimeouts=[]
    result=[]
    # ip生成器
    ips=genips(ipl,list=False)
    flag=0
    while outputimeouts or inputs or not flag:
        # 清理超时socket和补充数据
        outputimeouts,outputs,inputimeouts,inputs,flag=updatelist(outputimeouts,inputimeouts,ips)
        readable,writeable,exceptional=select.select(inputs,outputs,[],2)
        for x in readable:
            try:
                errwrite=x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                detial=x.getpeername()
                # print(detial)
                data=x.recv(1024)
                # print(data)
            except Exception as e:
                inputimeouts=list(filter(lambda tm:tm[0].fileno()!=x.fileno(),inputimeouts))
                print('Read-Error:',errwrite)
                x.close()
                continue
            if proxytype=='http':
                if _checkhttp(data):
                    result.append(','.join([detial[0],str(detial[1]),proxytype]))
                    # 丢到redis
                    # rq.put('http:'+detial[0]+':'+str(detial[1]))
            else:
                if _checksocks(data):
                    result.append(','.join([detial[0],str(detial[1]),proxytype]))
                    # 丢到redis
                    # rq.put('http:'+detial[0]+':'+str(detial[1]))
            inputimeouts=list(filter(lambda tm:tm[0].fileno()!=x.fileno(),inputimeouts))
            # inputs.remove(x)
            x.close()

        for x in writeable:
            erro=x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            # connect拒绝
            if erro==errno.ECONNREFUSED:
                outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
                x.close()
                continue

            # 超时
            elif erro==errno.ETIMEDOUT:
                outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
                x.close()
                continue

            # 不可到达
            elif erro==errno.EHOSTUNREACH:
                outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
                x.close()
                continue

            # 正常connect
            # 发送http代理验证数据
            elif erro==0:
                if proxytype=='http':
                    _sendhttp(x)
                else:
                    _sendsocks(x)
                outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
                inputimeouts.append([x,time.time()])


        for x in exceptional:
            print('====EXCEP====')
    return result