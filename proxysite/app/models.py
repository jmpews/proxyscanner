__author__ = 'jmpews'
import datetime

from flask.ext.sqlalchemy import BaseQuery

from app.extensions import db


class ProxyQuery(BaseQuery):
    pass

class Proxy(db.Model):
    __tablename__='Proxylist'
    query_class=ProxyQuery
    id=db.Column(db.Integer,primary_key=True)
    ip=db.Column(db.String(15))
    port=db.Column(db.Integer)
    type=db.Column(db.String(8))
    anonymous=db.Column(db.String(16))
    position=db.Column(db.String(16))
    connect_time=db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self,ip,port,type,anonymous,position,connect_time):
        self.ip=ip
        self.port=port
        self.type=type
        self.anonymous=anonymous
        self.position=position
        self.connect_time=connect_time
    def __repr__(self):
        return "<%s:%s:%s>" % (self.ip,self.port,self.position)
