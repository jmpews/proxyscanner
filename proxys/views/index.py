__author__ = 'jmpews'

from flask import Module
from proxys.models import Proxy
from flask import render_template

index_module=Module(__name__)

@index_module.route('/')
def index():
    proxylist=Proxy.query.all()
    return render_template('index.html',proxylist=proxylist)