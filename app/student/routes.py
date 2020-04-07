from flask import Blueprint, render_template
from flask import current_app

# Set up blueprint
student_bp = Blueprint('student_bp', __name__, template_folder='templates', static_folder='static')

@student_bp.route('/admin', methods=['GET'])
def admin():
    pass

