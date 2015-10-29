__author__ = 'jmpews'
__email__ = 'jmpews@gmail.com'

import sys

import requests

sys.path.append('..')
from scanner.ext import session,ProxyIOLoop,Proxy

from scanner.ext import find as IPFIND

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
    if session.query(Proxy).filter(Proxy.ip==ip,Proxy.port==port,Proxy.type==proxytype).first()==None:
        try:
            pos=IPFIND(ip).split('\t')
            if pos[len(pos)-2]=='':
               position=pos[len(pos)-1]
            else:
                position=pos[len(pos)-2]+'.'+pos[len(pos)-1]
        except:
            position='None.None'
            print('ERROR:IP',ip)
        p=Proxy(ip,port,proxytype,anonymous,position,connect_time)
        session.add(p)
        session.commit()
    # f=open('r.txt','a')
    # f.write(ip+':'+str(port)+' '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
    # f.flush()
    # f.close()

def TimerCheck(proxytype='http'):
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
proxyloop.addtimer(TimerCheck,3600*12,once=False)

# 添加一个IP段列表,进行扫描
filelist=['ip_guangdong.txt','ip_zhejiang.txt','ip_shanghai.txt','ip_beijing.txt']
iplists=[]
for f in filelist:
    ipfile=open('iplists/'+f,'r',encoding='utf-8')
    for line in ipfile:
        tmp=line.split('\t')
        iplists.append((tmp[0],tmp[1]))
    ipfile.close()
# proxyloop.addipsl(iplists,callback=func2)
# proxyloop.scanips([('182.254.153.50','182.254.153.59')],proxytype='http')
proxyloop.scanips(iplists,proxytype='http')

proxyloop.start()
print('Proxy Scan Start...')
