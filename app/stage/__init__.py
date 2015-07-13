__author__ = 'faradey'

from flask import Blueprint

stage = Blueprint('stage', __name__)

from app.stage import stage_controller
