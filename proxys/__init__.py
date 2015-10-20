__author__ = 'jmpews'
from flask import Flask
app = Flask('ScanProxy')
from proxys.application import init_app
init_app(app)
