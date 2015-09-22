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

def addproxy(result):
    with db.pipeline() as pipe:
        for x in result:
            pipe.sismember('proxy',x)
        din=pipe.execute()
    with db.pipeline() as pipe:
        for i in range(len(din)):
            if not din[i]:
                pipe.sadd('proxy',result[i])
        pipe.execute()

def dateproxy():
    allproxy=db.smembers('proxy')
    https=[]
    socks5=[]
    for x in allproxy:
        s=x.decode().split(',')
        if s[2]=='http':
            https.append((s[0],int(s[1])))
        else:
            socks5.append((s[0],int(s[1])))

    res_https=checkproxy(genips(https,l=True))
    res_socks=checkproxy(genips(socks5,l=True),proxytype='socks5')
    print(allproxy)
    print(res_https)
    print(res_socks)
    # db.delete('proxy')
    addproxy(res_https)
    addproxy(res_socks)

# while True:
#     dateproxy()
#     time.sleep(3)

while True:

    for i in range(3):
        proxx=db.smembers('proxy')
        if len(proxx)>40:
            print('over.............')
            continue

        https=gethttps()
        ips=genips(https,l=True)
        result=checkproxy(ips)
        addproxy(result)

        socks=getsocks5()
        ips=genips(socks,l=True)
        result=checkproxy(ips,proxytype='socks5')
        addproxy(result)
        time.sleep(5)
        print('sleep.')

    dateproxy()