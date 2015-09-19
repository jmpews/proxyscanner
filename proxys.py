__author__ = 'jmpews'
import socket
from redisq import RedisQueue
import errno
import select
import time
import utils

# 采用非阻塞的connect,每个IP测试4个端口,手动做好每个socket的connect的超时处理
# 几个注意点:
# 1.IP的区段 http://ips.chacuo.net/
# 2.非阻塞connect的返回码'EINPROGRESS',表示正在连接
# 3.http代理的验证方式,send一段http报文,验证返回.




rq=RedisQueue('socks5')

# # 爬取IP段
# ipfile=open('ip_jiangsu.txt','r',encoding='utf-8')
# iplist=[]
# for line in ipfile:
#     tmp=line.split('\t')
#     iplist.append((tmp[0],tmp[1]))
# ipfile.close()

# 从米扑上购买代理
ipfile=open('socks5.txt','r',encoding='utf-8')
iplist=[]
for line in ipfile:
    tmp=line.split(':')
    iplist.append((tmp[0],int(tmp[1])))
ipfile.close()

ips=utils.genips(iplist,l=True)
# ips=utils.genips([('180.161.130.11','180.161.130.12')])



inputs=[]
outputs=[]
outputimeouts=[]

#test
# outputimeouts+=utils.addips('118.144.108.254')
flag=0
while outputimeouts or inputs or not flag:
    # 清理超时socket和补充数据
    outputimeouts,outputs,flag=utils.updatelist(outputimeouts,ips)
    readable,writeable,exceptional=select.select(inputs,outputs,[],2)
    for x in readable:
        try:
            errwrite=x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            detial=x.getpeername()
            print(detial)
            data=x.recv(1024)
            print(data)
        except Exception as e:
            inputs.remove(x)
            print('Read-Error:',errwrite)
            x.close()
            continue
        if utils.checkhttp(data):
            print('HTTP: ',detial)
            rq.put('http:'+detial[0]+':'+str(detial[1]))
        if utils.checksocks(data):
            print('SOCK5: ',detial)
            rq.put('http:'+detial[0]+':'+str(detial[1]))
        inputs.remove(x)
        x.close()

    for x in writeable:
        erro=x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        # connect拒绝
        if erro==errno.ECONNREFUSED:
            # print('conn refuse.')
            outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
            # outputs.remove(x)
            x.close()
            continue

        # 超时
        elif erro==errno.ETIMEDOUT:
            # print('conn timeout.')
            outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
            # outputs.remove(x)
            x.close()
            continue

        # 不可到达
        elif erro==errno.EHOSTUNREACH:
            # print('host unreach.')
            outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
            # outputs.remove(x)
            x.close()
            continue

        # 正常connect
        # 发送http代理验证数据
        elif erro==0:
            print('connect success')
            utils.sendsocks(x)
            # utils.sendhttp(x)
            outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
            # outputs.remove(x)
            inputs.append(x)

    for x in exceptional:
        print('====EXCEP====')
    print(outputimeouts,inputs,flag)
    # ip=ips.__next__()
    # print(ip)
    # print('loop...')
