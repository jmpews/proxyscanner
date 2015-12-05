__author__ = 'jmpews'

from sqlalchemy import create_engine

from sqlalchemy import Column,Integer,String,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()
engine=create_engine('sqlite:///../test.db',echo=False)

class Proxy(Base):
    __tablename__='Proxylist'
    id=Column(Integer,primary_key=True)
    ip=Column(String(15))
    port=Column(Integer)
    type=Column(String(8))
    anonymous=Column(String(16))
    position=Column(String(16))
    connect_time=Column(Integer)
    create_time = Column(DateTime)

    def __init__(self,ip,port,type,anonymous,position,connect_time):
        self.ip=ip
        self.port=port
        self.type=type
        self.anonymous=anonymous
        self.position=position
        self.connect_time=connect_time
        self.create_time=datetime.now()
    def __repr__(self):
        return "<%s:%s:%s>" % (self.ip,self.port,self.position)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session=Session()

