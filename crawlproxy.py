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
    url='http://proxy.mimvp.com/api/fetch.php?orderid=860150919155536286&num=10&country_group=1&http_type=5&anonymous=5&result_format=json'
    r=requests.get(url)
    r=r.json()
    r=r['result']
    for x in r:
        result.append(x['ip:port'].split(':'))
    print(result)

import time
import redis
db=redis.StrictRedis(host='linevery.com', port=6379, db=0)

def addproxy(result):
    with db.pipeline() as pipe:
        for x in result:
            pipe.sismember('proxy',x)
        din=pipe.execute()
        print(din)
    with db.pipeline() as pipe:
        for i in range(len(din)):
            if not din[i]:
                pipe.sadd('proxy',result[i])
        pipe.execute()

while True:
    https=gethttps()
    print(https)
    ips=genips(https,l=True)
    result=checkproxy(ips)
    print(result)
    addproxy(result)
    time.sleep(30)
    # socks=getsocks5()
    # ips=genips(socks,l=True)
    # result=checkproxy(ips,proxytype='socks5')
    # print(result)
    # addproxy(result)
    # time.sleep(10)
    # print('sleep.')