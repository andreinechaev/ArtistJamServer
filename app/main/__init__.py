__author__ = 'faradey'

from flask import Blueprint

main = Blueprint('main', __name__)

from app.main import main_controller
