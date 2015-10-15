__author__ = 'jmpews'
from flask.ext.sqlalchemy import BaseQuery
from flask.ext.sqlalchemy import SQLAlchemy
from proxys.extensions import db
import datetime


class ProxyQuery(BaseQuery):
    pass

class Proxy(db.Model):
    __tablename__='Proxylist'
    query_class=ProxyQuery
    id=db.Column(db.Integer,primary_key=True)
    ip=db.Column(db.String(15))
    port=db.Column(db.Integer)
    type=db.Column(db.String(8))
    connect_time=db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self,ip,port,type,connect_time):
        self.ip=ip
        self.port=port
        self.type=type
    def __repr__(self):
        return "<%s:%s:%s>" % (self.ip,self.port,self.type)