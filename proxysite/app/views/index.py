__author__ = 'jmpews'

from flask import Module,request
from flask import render_template

from app.models import Proxy

from . import index_blue as index_blue
index_module=Module(__name__)

@index_blue.route('/')
def index():
    r_type=request.args.get('proxytype','http')
    # proxylist=Proxy.query.all()
    proxylist=Proxy.query.filter_by(type=r_type).order_by(Proxy.id.desc()).limit(100)
    return render_template('index.html', proxylist=proxylist)