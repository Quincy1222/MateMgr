#!/usr/bin/env python
# coding: utf-8

# app/main/forms.py

from flask.ext.wtf import Form 
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import Required, Length 
 
class SearchForm(Form): 
    keyword = StringField(u'关键字', validators=[Required(), Length(2, 32)])

    search_spec = BooleanField(u'搜索规格')
    search_notes = BooleanField(u'搜索备注') 

    search = SubmitField(u'搜索')
 
class MateInfoForm(Form): 
    id = HiddenField('id')
    cate_id = HiddenField('cate_id')

    code = StringField(u'代码', validators=[Required(), Length(2, 32)])
    name = StringField(u'名称', validators=[Required(), Length(2, 32)])
    spec = StringField(u'规格', validators=[Required(), Length(2, 128)])
    cate = StringField(u'类别', validators=[Required(), Length(2, 32)])
    notes = StringField(u'备注')

    save = SubmitField(u'保存')