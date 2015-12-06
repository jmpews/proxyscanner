
class Config:
    pass

class DefalutConfig(Config):
    DEBUG=True
    realip='112.126.76.80'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../../test.db'