from flask import Blueprint
from . import chat, data, gmail, jira

bp = Blueprint('v1', __name__, url_prefix='/v1')

bp.register_blueprint(gmail.bp)
bp.register_blueprint(jira.bp)
bp.register_blueprint(data.bp)
bp.register_blueprint(chat.bp)