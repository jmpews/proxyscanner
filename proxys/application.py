__author__ = 'jmpews'
from proxys.extensions import db
from proxys import views
import os
from proxys import views

DEFAULT_NAME = "proxys"

DEFAULT_MODULES={
    views.index_module:"",
}

def init_app(app):
    app_name = DEFAULT_NAME
    modules = DEFAULT_MODULES
    init_cofigure(app)
    init_extensions(app)
    init_views(app, modules)


def init_cofigure(app):
    app.config.update(dict(
        debug=True,
        SQLALCHEMY_DATABASE_URI = 'sqlite:///../test.db'
    ))
def init_extensions(app):
    # 初始化数据库
    db.init_app(app)

def init_views(app,modules):
    for k,v in modules.items():
        app.register_module(k, url_prefix=v)