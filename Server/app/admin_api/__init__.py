from flask import Blueprint

admin_api = Blueprint('admin_api', __name__)

from . import views
