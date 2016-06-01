#!/usr/bin/env python
# coding: utf-8

# manage.py

import os, sys

project_home = 'D:\\apps\MateMgr\\venv\\Lib\\site-packages'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import create_app, db 
from app.models import Material, User, Category, Property, Role, SystemInfo
from flask.ext.script import Manager, Shell 
from flask.ext.migrate import Migrate, MigrateCommand 
 
app = create_app(os.getenv('FLASK_CONFIG') or 'default') 
manager = Manager(app) 
migrate = Migrate(app, db) 
 
def make_shell_context(): 
    return dict(app=app, db=db, User=User, Mate=Material, Cate=Category, Prop=Property) 

manager.add_command("shell", Shell(make_context=make_shell_context)) 
manager.add_command('db', MigrateCommand)

@manager.command
def init_data():
    Property.insert_items()
    Role.insert_roles()
    User.init_users()

@manager.command
def import_svn_data():
    from svn import svn
    import logging

    # 创建一个logger  
    logger = logging.getLogger('app_matemgr.main')
    logger.propagate = False
    logger.setLevel(logging.DEBUG)  
      
    #if not logger.handlers:
    # 创建一个handler，用于写入日志文件  
    fh = logging.FileHandler('D:\\imports.log')  
    fh.setLevel(logging.DEBUG)  
      
    # 定义handler的输出格式  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
      
    # 给logger添加handler  
    logger.addHandler(fh)  

    TITLE = 'BOM Revision'
    repo_root = u'http://svn.ygct.com:82/svn/YGCT'
    path = u'/Temporary/机电产品线/知识库/物料汇总表.xls'
    username='wangquanyuan'
    password='wang@\x31\x31\x34\x34'

    last_rev = SystemInfo.query.filter_by(title=TITLE).first()

    if last_rev is None:
        last_rev = SystemInfo(title=TITLE)
        db.session.add(last_rev)

    filename = os.path.join(app.config['TMP_FOLDER'], "tmp.xls")

    svn = svn(repo_root, username, password)

    rev = svn.fetch_revision(path)
    logger.info('Rev of BOM is %s' % (rev))
    
    if last_rev.value is None or int(last_rev.value) != rev:
        logger.info(u'当前Revision：%s, 可以更新。' % (last_rev.value or '-'))

        filename = svn.export_file(path, filename)
        if filename:
            logger.info(u'BOM 已经导出：%s' % (filename))
            
            succ, count = Material.importFromExcel(filename)
            if succ:
                logger.info(u'成功导入/更新%d个物料' % count)

                last_rev.value = rev
                db.session.commit()

            else:
                logger.info(u'导入失败')
        else:
            logger.info(u'下载文件失败')
    else:
        logger.info(u'Revsion 尚未改变，暂时不更新.')

if __name__ == '__main__': 
    manager.run()