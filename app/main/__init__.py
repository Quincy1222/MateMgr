#!/usr/bin/env python
# coding: utf-8

# app/main/__init__.py

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
