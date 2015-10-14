__author__ = 'jmpews'

from flask import Flask
from proxys.application import init_app
from scanner.proxyloop import ProxyIOLoop
app = Flask('ScanProxy')
init_app(app)
if True:
    print('app run.')
    app.run()
else:
    print('You must start Scanner first!')