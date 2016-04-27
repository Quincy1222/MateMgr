# wsgi

import os, sys

# add your project directory to the sys.path
project_home = u'/home/quincy/MateMgr'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import create_app

application = create_app(os.getenv('FLASK_CONFIG') or 'default')
