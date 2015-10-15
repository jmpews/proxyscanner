__author__ = 'jmpews'
__email__ = 'jmpews@gmail.com'

import requests
import time
import sys
sys.path.append('..')
from scanner.proxyloop import ProxyIOLoop
from scanner.sqldb import session,Proxy

def gethttps():
    result=[]
    url='http://proxy.mimvp.com/api/fetch.php?orderid=860150919155536286&num=30&country_group=1&http_type=1,2&isp=3,5&anonymous=5&result_format=json'
    r=requests.get(url)
    r=r.json()
    r=r['result']
    for x in r:
        ip,port=x['ip:port'].split(':')
        result.append((ip,int(port)))
    return result


def func(ip,port,proxytype,connect_time):
    print(ip,':',port)
    print(connect_time)
    p=Proxy(ip,port,proxytype,connect_time)
    session.add(p)
    session.commit()
    # f=open('r.txt','a')
    # f.write(ip+':'+str(port)+' '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
    # f.flush()
    # f.close()


# 添加基本回调
proxyloop=ProxyIOLoop.initialize(callback=func)

# 检测proxy是否可用
r_http=gethttps()
# proxyloop.addipsl(r_http)

# 添加一个IP段列表,进行扫描
iplists=[]
ipfile=open('ip_beijing.txt','r',encoding='utf-8')
for line in ipfile:
    tmp=line.split('\t')
    iplists.append((tmp[0],tmp[1]))

proxyloop.scanips(iplists,proxytype='http')

proxyloop.start()
print('Proxy Scan Start...')
