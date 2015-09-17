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


rq=RedisQueue('proxy')

ipfile=open('ip_shanghai.txt','r',encoding='utf-8')
iplist=[]
for line in ipfile:
    tmp=line.split('\t')
    iplist.append((tmp[0],tmp[1]))

ips=utils.genips(iplist)
inputs=[]
outputs=[]
outputimeouts=[]

#test
# outputimeouts+=utils.addips('118.144.108.254')

while True:

    # 维持select内outputs
    if len(outputs)<400:
        for i in range(100-int(len(outputs)/4)):
            try:
                ip=ips.__next__()
            except StopIteration:
                # 循环到ip列表最后
                break
            outputimeouts+=utils.addips(ip)


    # 清除超时connect
    # 由于非阻塞的connect,所以要手动排除超时的connect
    outputimeouts=list(filter(utils.checktimeout,outputimeouts))
    outputs=[x[0] for x in outputimeouts]
    readable,writeable,exceptional=select.select(inputs,outputs,[],4)
    print('Len-Write: ',len(writeable))
    for x in readable:
        try:
            data=x.recv(1024)
            print(data)
        except Exception as e:
            x.close()
            print(e)
        if utils.checkhttp(data):
            detial=x.getpeername()
            print(detial)
            rq.put(detial[0]+':'+str(detial[1]))
        inputs.remove(x)
        x.close()

    for x in writeable:
        erro=x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        print(erro)
        # connect拒绝
        if erro==errno.ECONNREFUSED:
            print('conn refuse.')
            outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
            # outputs.remove(x)
            x.close()
            continue

        # 超时
        elif erro==errno.ETIMEDOUT:
            print('conn timeout.')
            outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
            # outputs.remove(x)
            x.close()
            continue

        # 不可到达
        elif erro==errno.EHOSTUNREACH:
            print('host unreach.')
            outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
            # outputs.remove(x)
            x.close()
            continue

        # 正常connect
        # 发送http代理验证数据
        elif erro==0:
            print('connect success')
            utils.sendhttp(x)
            outputimeouts=list(filter(lambda tm:tm[1]!=x.fileno(),outputimeouts))
            # outputs.remove(x)
            inputs.append(x)

    for x in exceptional:
        print('====EXCEP====')

    ip=ips.__next__()
    print(ip)
    print('loop...')
