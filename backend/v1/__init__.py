from flask import Blueprint
from . import gmail
from . import jira

bp = Blueprint('v1', __name__, url_prefix='/v1')

bp.register_blueprint(gmail.bp)
bp.register_blueprint(jira.bp)
