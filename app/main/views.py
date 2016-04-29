#!/usr/bin/env python
# coding: utf-8

# app/main/views.py


import os.path
import json

from flask import request, render_template, session, redirect, url_for, current_app, flash, jsonify
from flask.ext.login import login_required
from werkzeug import secure_filename
from sqlalchemy import or_
from jinja2 import contextfilter

from . import main
from .forms import SearchForm, MateInfoForm, MateAttachForm
from .. import db
from ..models import Material, Category, MaterialAttach
from ..decorators import permission_required


ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@contextfilter
def getCatePath(env, category):
    parents_title = [category.title]
    parent = category.parent
    while parent:
        parents_title = [parent.title] + parents_title

        parent = parent.parent

    result = '/ '.join(t for t in parents_title)

    return '/ ' + result

main.add_app_template_filter(getCatePath)

# 主页：搜索
# 可匿名访问
@main.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        keyword = form.keyword.data
        option = form.option.data

        if option == 'code':
            items = db.session.query(Material).filter(Material.code.like("%%%s%%" % keyword)).all()
        elif option == 'name':
            items = db.session.query(Material).filter(Material.name.like("%%%s%%" % keyword)).all()
        elif option == 'spec':
            items = db.session.query(Material).filter(Material.spec.like("%%%s%%" % keyword)).all()
        elif option == 'notes':
            items = db.session.query(Material).filter(Material.notes.like("%%%s%%" % keyword)).all()

        items_count = len(items)
        if items_count > 10:
            flash(u'查询结果超过10项，只显示部分内容，建议调整关键字')
        elif items_count == 0:
            flash(u'没有匹配的内容，请更换关键字')

        return render_template('main/index.html', form=form, items=items[:10])

    return render_template('main/index.html', form=form)

# 物料详情
# 可匿名访问
@main.route('/detail')
def detail():
    id = request.args.get('id')
    
    if not id:
        return redirect(url_for('.index'))
        
    mate = Material.query.filter_by(id=id).first()
    if not mate.cate:
        for i in range(len(mate.code) - 1, 3, -1):
            code_prefix = mate.code[:i]
            cate = Category.query.filter_by(prefix=code_prefix).first()

            if cate:
                mate.cate = cate

                db.session.add(mate)
                db.session.commit()

                break

    attach = MaterialAttach.query.filter_by(mate_id=mate.id).all()
    print len(attach)

    return render_template('main/detail.html', item=mate, attach=attach)


@main.route('/view_attach')
def view_attach():
    mid = request.args.get('mid', -1)
    aid = request.args.get('aid', -1)

    attach = MaterialAttach.query.filter_by(mate_id=mid, id=aid).first_or_404()

    return render_template('main/view_attach.html', src=attach.filepath)

# 删除物料
# 管理权限
@main.route('/delete')
@login_required
def delete():
    id = request.args.get('id')
    mate = Material.query.filter_by(id=id).first_or_404()

    return redirect(url_for('.index'))

# 编辑物料信息
# 管理权限
@main.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = MateInfoForm()
    if request.method == 'GET':
        id = request.args.get('id')
        
        mate = Material.query.filter_by(id=id).first_or_404()
        
        form.id.data = mate.id
        form.code.data = mate.code
        form.name.data = mate.name
        form.spec.data = mate.spec
        form.notes.data = mate.notes
        form.cate.data = mate.cate.title
        form.cate_id.data = mate.cate.id
        
        return render_template('main/edit.html', form=form)
     
    if form.validate_on_submit():
        id = form.id.data
        mate = Material.query.filter_by(id=id).first_or_404()
        
        mate.code = form.code.data
        mate.name = form.name.data
        mate.spec = form.spec.data
        mate.notes = form.notes.data
        mate.cate = Category.query.filter_by(id=form.cate_id.data).first()
        
        db.session.add(mate)
        db.session.commit()
        
        flash(u'更新成功')
        return redirect(url_for('.detail', id=id))
        
    form.id.data = mate.id
    form.code.data = mate.code
    form.name.data = mate.name
    form.spec.data = mate.spec
    form.notes.data = mate.notes
        
    return render_template('main/edit.html', form=form)

#添加物料附件
# 管理权限
@main.route('/attach', methods=['GET', 'POST'])
@login_required
def attach():
    form = MateAttachForm()
    if request.method == 'GET':
        id = request.args.get('id')
        
        mate = Material.query.filter_by(id=id).first_or_404()

        form.mate_id.data = mate.id

        return render_template('main/attach.html', form=form, mate=mate)

    if form.validate_on_submit():
        id = form.mate_id.data
        mate = Material.query.filter_by(id=id).first_or_404()

        _type = form.attach_type.data
        file = form.file.data

        safe_filename = secure_filename(file.filename)
        filename = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)
            
        file.save(filename)

        attach = MaterialAttach(attach_type=_type, mate_id=mate.id, filepath=safe_filename)
        
        db.session.add(attach)
        db.session.commit()

        flash(u'成功添加附加')

        return redirect(url_for('.detail', id=mate.id))

    return render_template('main/attach.html', form=form, mate=mate)

# 新增物料
# 管理权限
@main.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = MateInfoForm()

    if form.validate_on_submit():
        m = Material(code=form.code.data,
                     name=form.name.data,
                     spec=form.spec.data,
                     notes=form.notes.data)
        db.session.add(m)
        db.session.commit()
        
        flash(u'物料已添加')
        
        return redirect(url_for('.detail', id=m.id))
        
    return render_template('main/create.html', form=form)

# 导入物料表
# 管理权限
@main.route('/import', methods=['GET', 'POST'])
@login_required
def import_data():
    if request.method == 'POST':
        file = request.files['excel_file']

        if file and allowed_file(file.filename):
            filename = os.path.join(
                current_app.config['TMP_FOLDER'], 
                secure_filename(file.filename))
            
            file.save(filename)
            
            succ, count = Material.importFromExcel(filename)
            if succ:
                flash(u'成功导入/更新%d个物料' % count)

                return redirect(url_for('.import_data'))
            else:
                flash(u'导入失败')
        else:
            flash(u'错误，不支持此类型的文件')

    return render_template('main/import_data.html')


### 测试用
@main.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        json_file = request.files['json_file']

        try:
            Category.load_json(json_file)

            flash(u'导入成功')
        except Exception as e:
            flash(u'内部错误：'+str(e))

            pass

    return render_template('main/test.html')

@main.route('/get_nodes', methods=['GET', 'POST'])
def get_nodes():

    id = request.form.get('id')
    categories = Category.query.all()

    ret_lst = []
    for item in categories:
        if item.parent:
            ret_lst.append({"id": item.id, "pId": item.parent.id, "name": item.title})
        else:
            ret_lst.append({"id": item.id, "pId": 0, "name": item.title})
    return json.dumps(ret_lst)


@main.route('/admin')
def admin():
    action = request.args.get('action')
    id = request.args.get('id')

    if action == 'remove':
        c = Category.query.filter_by(id=id).first_or_404()

        if len(c.children) == 0:
            db.session.delete(c)
        else:
            db.session.commit()

    elif action == 'rename':
        value = request.args.get('value')
        if value:
            c = Category.query.filter_by(id=id).first_or_404()
            c.title = value
            db.session.commit()

    return "Ok"

