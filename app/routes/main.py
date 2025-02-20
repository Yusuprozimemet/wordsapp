from flask import Blueprint, render_template
from app.services.word_service import WordService

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')