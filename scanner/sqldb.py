__author__ = 'jmpews'

from sqlalchemy import create_engine

from sqlalchemy import Column,Integer,String,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()
engine=create_engine('sqlite:///../test.db',echo=False)

class Proxy(Base):
    __tablename__='Proxylist'
    id=Column(Integer,primary_key=True)
    ip=Column(String(15))
    port=Column(Integer)
    type=Column(String(8))
    connect_time=Column(Integer)
    create_time = Column(DateTime, default=datetime.datetime.now())

    def __init__(self,ip,port,type,connect_time):
        self.ip=ip
        self.port=port
        self.type=type
        self.connect_time=connect_time
    def __repr__(self):
        return "<%s:%s:%s>" % (self.ip,self.port,self.type)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session=Session()

