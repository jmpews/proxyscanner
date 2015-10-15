__author__ = 'jmpews'

from flask import Flask
from proxys.application import init_app
app = Flask('ScanProxy')
init_app(app)
