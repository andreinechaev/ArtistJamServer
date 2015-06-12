__author__ = 'faradey'

from flask import Blueprint

auth = Blueprint('auth', __name__)

from app.authentication import auth_controller
