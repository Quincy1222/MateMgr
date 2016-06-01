#!/usr/bin/env python
# coding: utf-8

# config.py


import os
basedir = os.path.abspath(os.path.dirname(__file__))
    
MYSQL_DB   = 'material_magr'
MYSQL_USER = 'root'
MYSQL_PASS = 'toor'
MYSQL_HOST = 'localhost'
MYSQL_PORT = '3306'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tHis\x34newApPFlAsk\x01\x04520\x78YoliY!@wangqy'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    UPLOAD_FOLDER = os.path.join(basedir, 'user_upload')
    TMP_FOLDER = os.path.join(basedir, 'tmp')

    # FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    # FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    MATERIAL_COUNT_PER_PAGE = 15

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    # MAIL_SERVER = 'smtp.googlemail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'mysql://' + MYSQL_USER + ':' + MYSQL_PASS + '@' + MYSQL_HOST + ':' + MYSQL_PORT + '/' + MYSQL_DB

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'mysql://' + MYSQL_USER + ':' + MYSQL_PASS + '@' + MYSQL_HOST + ':' + MYSQL_PORT + '/' + MYSQL_DB

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://' + MYSQL_USER + ':' + MYSQL_PASS + '@' + MYSQL_HOST + ':' + MYSQL_PORT + '/' + MYSQL_DB

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
