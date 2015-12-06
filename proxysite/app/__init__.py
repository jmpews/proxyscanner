__author__ = 'jmpews'
from flask import Flask,request


from .extensions import db
from .models import Proxy


from .views import index_blue
from config import DefalutConfig


app=Flask(__name__)
app.config.from_object(DefalutConfig)

db.init_app(app)
app.test_request_context().push()
db.create_all()

app.register_blueprint(index_blue,url_prefix='')

@app.route('/checkproxy')
def checkproxy():
    if request.method=='GET':
        localip=DefalutConfig.realip
        remote_ip=request.args.get('rip','127.0.0.1')
        proxy_ip1=request.environ.get('HTTP_VIA',None)
        proxy_ip2=request.environ.get('HTTP_X_FORWARDED_FOR',None)
        print(proxy_ip1,':',proxy_ip2)
        code='transparent'
        if proxy_ip1!=None:
            if proxy_ip2==localip:
                code='transparent'
            elif proxy_ip2==remote_ip:
                code='anonymous'
        elif proxy_ip1==None and proxy_ip2==None:
            code='highanonymity'
        else:
            code='notknow'
        # print(request.headers.get('User-Agent'))
        return 'jmpews0307:'+code+':'

@app.route('/shadowsocks')
def shadowsocks():
    if request.method=='GET':
        return 'shadowsocks'