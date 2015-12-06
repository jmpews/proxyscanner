__author__ = 'jmpews'
from flask import Blueprint

index_blue = Blueprint('index', __name__)
from . import index
