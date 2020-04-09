from flask import Blueprint, render_template, redirect, url_for
from flask_user import roles_required, login_required, current_user
from flask import Blueprint, render_template
from ..models import User, Quiz, db
from flask import current_app
from datetime import datetime
from sqlalchemy import and_
from .student_forms import EnrollForm

# Set up blueprint
student_bp = Blueprint('student_bp', __name__, template_folder='templates', static_folder='static')

@student_bp.route('/student', methods=['GET'])
def root():
    return redirect(url_for('student_bp.dashboard'))


@student_bp.route('/student/dashboard', methods=['GET'])
@login_required
def dashboard():
    data = dict()
    data['dashboard_type'] = 'Student'
    data['ct_registered_user'] = User.query.count()
    data['quizzes_created'] = Quiz.query.count()
    data['quizzes_enrolled'] = Quiz.query.with_parent(current_user).count()
    data['quizzes_completed'] = 0

    data['upcoming_quizzes'] = Quiz.query.with_parent(current_user).filter(datetime.now() < Quiz.deadline).order_by(Quiz.deadline).all()
    for i in range(len(data['upcoming_quizzes'])):
        # data['user_enrolled'][i].users_enrolled = User.query.with_parent(data['upcoming_quizzes'][i]).count()
        print(data['upcoming_quizzes'][i].enroll_code)

    
    data['enroll_form'] = EnrollForm()

    return render_template('index_student.html', **data)

@student_bp.route('/student/quizzes', methods=['GET'])
@login_required
def quizzes():
    pass