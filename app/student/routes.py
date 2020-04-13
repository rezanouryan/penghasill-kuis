from flask import Blueprint, render_template, redirect, url_for, request, make_response
from flask_user import roles_required, login_required, current_user
from flask import Blueprint, render_template
from ..models import User, Quiz, db, StudentEnroll
from flask import current_app
from datetime import datetime
from sqlalchemy import and_
from .student_forms import EnrollForm

# Set up blueprint
student_bp = Blueprint('student_bp', __name__,
                       template_folder='templates', static_folder='static')


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
    data['completed_quizzes'] = Quiz.query.with_parent(current_user).filter(
        datetime.now() > Quiz.deadline).order_by(Quiz.deadline).all()

    for i in range(len(data['completed_quizzes'])):
        student_enrollment = StudentEnroll.select_by_user_and_quiz(current_user, data['completed_quizzes'][i])
        data['completed_quizzes'][i].high_score = student_enrollment.high_score
        data['completed_quizzes'][i].date_enrolled = student_enrollment.date_enrolled
        
        

    data['upcoming_quizzes'] = Quiz.query.with_parent(current_user).filter(
        datetime.now() < Quiz.deadline).order_by(Quiz.deadline).all()
    for i in range(len(data['upcoming_quizzes'])):
        student_enrollment = StudentEnroll.select_by_user_and_quiz(current_user, data['upcoming_quizzes'][i])
        data['upcoming_quizzes'][i].remaining_attempts = student_enrollment.remaining_attempts
        data['upcoming_quizzes'][i].high_score = student_enrollment.high_score
        data['upcoming_quizzes'][i].date_enrolled = student_enrollment.date_enrolled




    data['enroll_form'] = EnrollForm()

    return render_template('index_student.html', **data)


@student_bp.route('/student/enroll-quiz', methods=['POST'])
@login_required
def enroll_quiz():
    if request.method == 'POST':
        enroll_form = EnrollForm(request.form)
        if enroll_form.validate_on_submit():
            enroll_code = enroll_form.enroll_code.data
            quiz_entity = Quiz.query.filter(
                Quiz.enroll_code == enroll_code).first()
            student_enroll_entity = StudentEnroll.select_by_user_and_quiz(current_user, quiz_entity)
            if student_enroll_entity:
                return make_response(" User already enrolled", 402)
                

            if quiz_entity:
                current_user.quizzes.append(quiz_entity)
                failed = False
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    db.session.flush()  # for resetting non-commited .add()
                    failed = True

                if failed:
                    return make_response(" There are something error when putting enrollment data into database. Please try again or contact admin for further information.", 402)
                else:
                    return make_response(f" User {current_user.username} are succesfully enrolled to quiz with enrollment code {enroll_code}. Please check it on dashboard", 201)
            else:
                return make_response(f" Cannot find quiz with enroll code {enroll_code} in database. Please make sure enroll code is correct. ", 402)
        return make_response(f" Error during form validate, please make sure input are correct type", 402)
        

@student_bp.route('/student/quiz-management', methods=['GET'])
@login_required
def quiz_management():
    pass
