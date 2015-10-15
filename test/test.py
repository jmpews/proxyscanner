# test
from flask import Flask
from proxys.application import init_app
app = Flask('ScanProxy')
init_app(app)
app.test_request_context().push()
from proxys.models import Proxy

proxylist=Proxy.query.filter_by(type='Server').order_by(Proxy.id.desc()).limit(10)
for t in proxylist:
    print(t.id)