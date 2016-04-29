# wsgi

import os, sys

# add your project directory to the sys.path
project_home = r'D:\apps\MateMgr'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

mylibs = r'D:\apps\MateMgr\venv\Lib\site-packages'
if mylibs not in sys.path:
    sys.path = [mylibs] + sys.path

from app import create_app

application = create_app(os.getenv('FLASK_CONFIG') or 'default')
