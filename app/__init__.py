#!/usr/bin/env python
# coding: utf-8

# app/__init__.py

from flask import Flask
from flask.ext.bootstrap import Bootstrap, WebCDN
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.mail import Mail
# from flask.ext.moment import Moment
from my_config import config

bootstrap = Bootstrap()
# mail = Mail()
# moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    cdn_bootstrap = WebCDN('http://cdn.bootcss.com/bootstrap/3.3.6/')
    cdn_jquery = WebCDN('http://cdn.bootcss.com/jquery/2.2.0/')

    app.extensions['bootstrap']['cdns']['bootstrap'] = cdn_bootstrap
    app.extensions['bootstrap']['cdns']['jquery'] = cdn_jquery

    # mail.init_app(app)
    # moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # 附加路由和自定义的错误页面
    from .main import main as main_bp
    app.register_blueprint(main_bp) # , url_prefix='/'

    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app