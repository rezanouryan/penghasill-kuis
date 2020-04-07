from flask import Blueprint, render_template, redirect, url_for
from flask_user import roles_required
from flask import current_app

# Set up blueprint
admin_bp = Blueprint('admin_bp', __name__, template_folder='templates', static_folder='static')

@admin_bp.route('/admin', methods=['GET'])
@roles_required('admin')
def root():
    return redirect(url_for('admin_bp.dashboard'))


@admin_bp.route('/admin/dashboard', methods=['GET'])
@roles_required('admin')
def dashboard():
    return render_template('dashboard.html')

