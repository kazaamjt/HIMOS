from flask import Blueprint

main = Blueprint('dashboard', __name__)

from . import views
