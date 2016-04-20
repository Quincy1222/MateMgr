#!/usr/bin/env python
# coding: utf-8

# app/auth/views.py

from flask import request, render_template, session, redirect, url_for, current_app, flash
from flask.ext.login import login_user, login_required, logout_user

from sqlalchemy import or_

from . import auth
from .forms import LoginForm
from .. import db
from ..models import User

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)

            flash(u'已登录')
            
            return redirect(request.args.get('next') or url_for('main.index'))

        flash(u'账号和密码不匹配')

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'已注销')
    
    return redirect(url_for('main.index'))