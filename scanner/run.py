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


def func(ip,port,proxytype,anonymous,connect_time):
    print('扫描到一个IP')
    p=Proxy(ip,port,proxytype,anonymous,connect_time)
    session.add(p)
    session.commit()
    # f=open('r.txt','a')
    # f.write(ip+':'+str(port)+' '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
    # f.flush()
    # f.close()
def TimerCheck():
    def func(ip,port,proxytype,anonymous,connect_time):
        p=Proxy(ip,port,proxytype,anonymous,connect_time)
        session.add(p)
        session.commit()
    r=session.query(Proxy).filter(Proxy.type=='http').all()
    session.query(Proxy).filter(Proxy.type=='http').delete()
    session.commit()
    checkproxylist=[]
    print('原有长度',len(r))
    for t in r:
        checkproxylist.append((t.ip,t.port))
    proxyloop.addipsl(checkproxylist,callback=func)

def func2(ip,port,proxytype,anonymous,connect_time):
    p=Proxy(ip,port,proxytype,anonymous,connect_time)
    session.add(p)
    session.commit()

# 添加基本回调
proxyloop=ProxyIOLoop.initialize(callback=func)
proxyloop.addtimer(TimerCheck,3600,once=False)

# 检测proxy是否可用
# r_http=gethttps()
# proxyloop.addipsl(r_http,callback=func2)

# 添加一个IP段列表,进行扫描
iplists=[]
ipfile=open('ip_check.txt','r',encoding='utf-8')
for line in ipfile:
    tmp=line.split('\t')
    iplists.append((tmp[0],tmp[1]))
proxyloop.addipsl(iplists,callback=func2)
# proxyloop.scanips(iplists,proxytype='http')
# proxyloop.scanips([('182.254.153.50','182.254.153.59')],proxytype='http')


proxyloop.start()
print('Proxy Scan Start...')
