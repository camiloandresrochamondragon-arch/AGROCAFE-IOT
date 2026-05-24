from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html', titulo='Inicio')
@main_bp.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html', titulo='Analytics')