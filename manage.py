#!/usr/bin/env python
# coding: utf-8

# manage.py

import os, sys

project_home = 'D:\\apps\MateMgr\\venv\\Lib\\site-packages'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import create_app, db 
from app.models import Material, User, Category, Property, Role
from flask.ext.script import Manager, Shell 
from flask.ext.migrate import Migrate, MigrateCommand 
 
app = create_app(os.getenv('FLASK_CONFIG') or 'default') 
manager = Manager(app) 
migrate = Migrate(app, db) 
 
def make_shell_context(): 
    return dict(app=app, db=db, User=User, Mate=Material, Cate=Category, Prop=Property) 

@manager.command
def init_data():
	Property.insert_items()
	Role.insert_roles()
	User.init_users()
 
manager.add_command("shell", Shell(make_context=make_shell_context)) 
manager.add_command('db', MigrateCommand)

if __name__ == '__main__': 
    manager.run()