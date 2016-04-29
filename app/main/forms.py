#!/usr/bin/env python
# coding: utf-8

# app/main/forms.py

from flask.ext.wtf import Form 
from wtforms import StringField, SubmitField, HiddenField, RadioField, FileField, SelectField
from wtforms.validators import Required, Length 

class SearchForm(Form): 
    option  = RadioField(u'搜索选项', 
        choices=[('code', u'代码'), ('name', u'名称'), ('spec', u'规格'), ('notes', u'备注')],
        default='name', validators=[Required()])
    keyword = StringField(u'关键字', validators=[Required(), Length(2, 32)])

    search = SubmitField(u'查询')
 
class MateInfoForm(Form): 
    id = HiddenField('id')
    cate_id = HiddenField('cate_id')

    code = StringField(u'代码', validators=[Required(), Length(2, 32)])
    name = StringField(u'名称', validators=[Required(), Length(2, 32)])
    spec = StringField(u'规格', validators=[Required(), Length(2, 128)])
    cate = StringField(u'类别', validators=[Required(), Length(2, 32)])
    notes = StringField(u'备注')

    save = SubmitField(u'保存')

class MateAttachForm(Form): 
    mate_id = HiddenField('mate_id')

    attach_type = SelectField(u'附件类型', 
        choices=[(u'选型资料', u'选型资料'), (u'图纸', u'图纸'), (u'说明书', u'说明书')],
        validators=[Required()])
    file = FileField(u'附件')

    submit = SubmitField(u'提交')
