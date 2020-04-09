from flask import Blueprint, render_template
from flask import current_app, redirect, url_for
from flask_login import current_user
from .models import User

# Set up blueprint
main_bp = Blueprint('main_bp', __name__,
                    template_folder='templates', static_folder='static')


@main_bp.route('/', methods=['GET'])
def main():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()

    if current_user.has_role('admin'):
        return redirect(url_for('admin_bp.dashboard'))
    else:
        return redirect(url_for('student_bp.dashboard'))


@main_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    pass