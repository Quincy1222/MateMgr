#!/usr/bin/env python
# coding: utf-8

# app/models.py


from . import db
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin

class Permission:
    QUERY  = 0x01        # 查询（匿名）
    APPLY  = (0x01 << 1) # 申请
    MODIFY = (0x01 << 2) # 修改
    ADMIN  = (0x01 << 3) # 审核 & 导入 & 删除

class Category(db.Model):
    ''' 物料类别 '''
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))  # 类型标题
    prefix = db.Column(db.String(16)) # 代码前缀
    notes = db.Column(db.String(32))  # 备注

    materials = db.relationship('Material', backref='cate')
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    parent = db.relationship('Category',
                             uselist=False,
                             remote_side=[id], backref="children")

    def __repr__(self):
        return '<Category %r>' % self.title

    @staticmethod
    def load_json(json_file):
        # "title": "xxxx", "parent": "父级". "prefix": "C_"
        #
        import json

        items = json.load(json_file)
        for item in items:
            c = Category(title=item['title'].encode('utf-8'))

            if item.has_key('prefix'):
                c.prefix = item['prefix']

            if item.has_key('parent') and item['parent'] != '':
                    c.parent = Category.query.filter_by(title=item['parent']).first()
            elif c.prefix:
                for i in range(len(c.prefix), 3, -1):
                    p = Category.query.filter_by(prefix=c.prefix[:i]).first()
                    print c.prefix[:i], p
                    if p:
                        c.parent = p
                        break

            if item.has_key('notes'):
                c.notes = item['notes']

            db.session.add(c)
            db.session.commit()

class Property(db.Model):
    ''' 物料状态属性
        * 新建立
        * 已修改
        * 已审核
        * 已作废
    '''
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    notes = db.Column(db.String(32))

    materials = db.relationship('Material', backref='prop')

    def __repr__(self):
        return '<Property %r>' % self.title

    @staticmethod
    def insert_items():
        items = {
            u'新建立': u'新建，未审核',
            u'已修改': u'已修改，未审核',
            u'已审核': u'已审核',
            u'已作废': u'已废止',
        }

        for i in items:
            item = Property.query.filter_by(title=i).first()
            if item is None:
                item = Property(title=i)
            item.notes = items[i][0]
            db.session.add(item)

        db.session.commit()

class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(64))
    spec = db.Column(db.String(128))
    notes = db.Column(db.String(128))

    cate_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    prop_id = db.Column(db.Integer, db.ForeignKey('properties.id'))

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def importFromCSV(csvFile):
        import csv
        with open(csvFile) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # print(row['id'])

                m = Material(code=row['code'].decode('utf-8'),
                            name=row['name'].decode('utf-8'),
                            spec=row['spec'].decode('utf-8'),
                            notes=row['remark'].decode('utf-8'),
                            cate_id=Category.query.first().id,
                            prop_id=Property.query.first().id)
                db.session.add(m)

            # commit
            db.session.commit()

    @staticmethod
    def importFromExcel(excelFilename):
        import xlrd

        book = xlrd.open_workbook(excelFilename)
        code_colnum = 0
        name_colnum = 1
        spec_colnum = 2
        unit_colnum = 3

        count = 0
        prop = Property.query.filter(Property.title.like(ur'%审核%')).first()

        for sheet in book.sheets():
            if  sheet.cell(0, code_colnum).value != u'品号' or \
                sheet.cell(0, name_colnum).value != u'品名' or \
                sheet.cell(0, spec_colnum).value != u'规格' or \
                sheet.cell(0, unit_colnum).value != u'单位':

                continue

            for row in range(1, sheet.nrows):
                code = sheet.cell(row, code_colnum).value
                name = sheet.cell(row, name_colnum).value
                spec = sheet.cell(row, spec_colnum).value
                unit = sheet.cell(row, unit_colnum).value

                m = Material.query.filter_by(code=code).first()

                if not m:
                    m = Material(code=code, prop=prop)

                m.name = name
                m.spec = spec

                db.session.add(m)
                count += 1

            db.session.commit()
        return (True, count)

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            u'普通用户': (Permission.QUERY |
                          Permission.APPLY, True), # 只能申请
            u'高级用户': (Permission.QUERY |
                          Permission.MODIFY |
                          Permission.APPLY, False), # 能申请，可修改
            u'代码管理员': (Permission.QUERY |
                            Permission.APPLY |
                            Permission.MODIFY |
                            Permission.ADMIN, False), # 申请，修改，审核，删除
            u'系统管理员': (0xff, False)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)

        db.session.commit()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMIN)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return  (permissions == Permission.QUERY)

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    notes = db.Column(db.String(128))
