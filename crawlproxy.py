__author__ = 'jmpews'
import requests
from utils import genips
from proxys import checkproxy
def gethttps():
    result=[]
    url='http://proxy.mimvp.com/api/fetch.php?orderid=860150919155536286&num=30&country_group=1&http_type=1,2&anonymous=5&result_format=json'
    r=requests.get(url)
    r=r.json()
    r=r['result']
    for x in r:
        ip,port=x['ip:port'].split(':')
        result.append((ip,int(port)))
    # print(result)
    return result
# gethttps()

def getsocks5():
    result=[]
    url='http://proxy.mimvp.com/api/fetch.php?orderid=860150919155536286&num=30&country_group=1&http_type=5&anonymous=5&result_format=json'
    r=requests.get(url)
    r=r.json()
    r=r['result']
    for x in r:
        ip,port=x['ip:port'].split(':')
        result.append((ip,int(port)))
    # print(result)
    return result

import time
import redis
db=redis.StrictRedis(host='linevery.com', port=6379, db=0)

def addproxy(result,proxydb):
    with db.pipeline() as pipe:
        for x in result:
            pipe.sismember(proxydb,x)
        din=pipe.execute()
    with db.pipeline() as pipe:
        for i in range(len(din)):
            if not din[i]:
                pipe.sadd(proxydb,result[i])
        pipe.execute()

def dateproxy(proxydb,proxytype='http'):
    allproxy=db.smembers(proxydb)
    proxys=[]
    if proxytype=='http':
        for x in allproxy:
            s=x.decode().split(',')
            proxys.append((s[0],int(s[1])))
        res_proxy=checkproxy(genips(proxys,l=True))
        db.delete(proxydb)
        addproxy(res_proxy,proxydb)
    else:
        for x in allproxy:
            s=x.decode().split(',')
            proxys.append((s[0],int(s[1])))
        res_proxy=checkproxy(genips(proxys,l=True),proxytype='socks5')
        db.delete(proxydb)
        addproxy(res_proxy,proxydb)
# while True:
#     dateproxy()
#     time.sleep(3)

while True:

    for i in range(3):
        proxyhttp=db.smembers('proxyhttp')
        proxysocks5=db.smembers('proxysocks')

        if len(proxyhttp)<30:
            https=gethttps()
            ips=genips(https,l=True)
            result=checkproxy(ips)
            print(result)
            addproxy(result,'proxyhttp')
        if len(proxysocks5)<30:
            socks=getsocks5()
            ips=genips(socks,l=True)
            result=checkproxy(ips,proxytype='socks5')
            print(result)
            addproxy(result,'proxysocks')
        time.sleep(5)
        print('sleep...')

    dateproxy('proxyhttp','http')
    dateproxy('proxysocks','socks5')