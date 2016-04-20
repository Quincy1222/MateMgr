#!/usr/bin/env python
# coding: utf-8

# app/auth/__init__.py

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
