from flask import Blueprint, render_template, redirect, url_for
from flask_user import roles_required
from flask import current_app
from ..models import User, Quiz, db
from datetime import datetime
from .admin_forms import AddQuizForm

# Set up blueprint
admin_bp = Blueprint('admin_bp', __name__, template_folder='templates', static_folder='static')

@admin_bp.route('/admin', methods=['GET'])
@roles_required('admin')
def root():
    return redirect(url_for('admin_bp.dashboard'))


@admin_bp.route('/admin/dashboard', methods=['GET'])
@roles_required('admin')
def dashboard():

    data = dict()
    data['ct_registered_user'] = User.query.count()
    data['quizzes_created'] = Quiz.query.count()
    data['quizzes_completed'] = Quiz.query.filter(datetime.now() > Quiz.deadline).count()

    data['upcoming_quizzes'] = Quiz.query.filter(datetime.now() < Quiz.deadline).order_by(Quiz.deadline).all()
    for i in range(len(data['upcoming_quizzes'])):
        data['upcoming_quizzes'][i].users_enrolled = User.query.with_parent(data['upcoming_quizzes'][i]).count()
        print(data['upcoming_quizzes'][i].enroll_code)

    data['leaderboard'] = User.get_leaderboard()

    data['add_quiz_form'] = AddQuizForm()
    # print(data['leaderboard'])

    return render_template('index_admin.html', **data)

