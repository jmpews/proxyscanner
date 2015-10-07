__author__ = 'jmpews'
import requests
from proxyloop import ProxyIOLoop
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

def getsocks5():
    result=[]
    url='http://proxy.mimvp.com/api/fetch.php?orderid=860150919155536286&num=30&country_group=1&http_type=5&isp=3,5&anonymous=5&result_format=json'
    r=requests.get(url)
    r=r.json()
    r=r['result']
    for x in r:
        ip,port=x['ip:port'].split(':')
        result.append((ip,int(port)))
    return result

def func(ip,port,proxytype):
    print(ip,':',port,proxytype)
r_http=gethttps()
print(r_http)
r_socks=getsocks5()
print(r_socks)
proxyloop=ProxyIOLoop()
proxyloop.addipsl(r_http)
# proxyloop.addipsl(r_socks,proxytype='socks')
proxyloop.scanips([('183.129.190.176','183.129.190.180')],proxytype='socks')
proxyloop.start(callback=func)