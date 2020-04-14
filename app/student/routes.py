from flask import Blueprint, render_template, redirect, url_for, request, make_response, jsonify, flash
from flask_user import roles_required, login_required, current_user
from flask import Blueprint, render_template
from ..models import User, Quiz, db, StudentEnroll, Question
from flask import current_app
from datetime import datetime
from sqlalchemy import and_
from .student_forms import EnrollForm, QuestionForm
from ..helper.date_time_utils import local_time


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
        student_enrollment = StudentEnroll.select_by_user_and_quiz(
            current_user, data['completed_quizzes'][i])
        data['completed_quizzes'][i].high_score = student_enrollment.high_score
        data['completed_quizzes'][i].date_enrolled = student_enrollment.date_enrolled

    data['upcoming_quizzes'] = Quiz.query.with_parent(current_user).filter(
        datetime.now() < Quiz.deadline).order_by(Quiz.deadline).all()
    for i in range(len(data['upcoming_quizzes'])):
        student_enrollment = StudentEnroll.select_by_user_and_quiz(
            current_user, data['upcoming_quizzes'][i])
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

            if quiz_entity:
                student_enroll_entity = StudentEnroll.select_by_user_and_quiz(
                    current_user, quiz_entity)
                if student_enroll_entity:
                    return make_response(" User already enrolled", 402)
                current_user.quizzes.append(quiz_entity)
                failed = False
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    db.session.flush()
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
    data = dict()
    data['enroll_form'] = EnrollForm()
    return render_template('quizzes_student.html', **data)


@student_bp.route("/student/list-quiz-serverside", methods=['GET'])
@login_required
def list_quiz_serverside():
    from ..serverside import table_schemas
    from ..serverside.serverside_table import ServerSideTable
    data = []
    for x in Quiz.query.with_parent(current_user).all():
        student_enrollment = StudentEnroll.select_by_user_and_quiz(
            current_user, x)
        rem_attempt = f'''<div class="small text-muted">Remaining attempt(s)</div>
                         <div>{student_enrollment.remaining_attempts} attempt(s)</div>
        ''' if datetime.now() < x.deadline else ''

        summary = rem_attempt + f'''<div class="small text-muted">{ ("Current Highscore" if datetime.now() < x.deadline else "Final Highscore") }</div>
                      <div><strong>{student_enrollment.high_score}</strong></div>'''
        entry = {
            "name": x.name,
            "topic": x.topic,
            "date_enrolled": local_time(student_enrollment.date_enrolled),
            "deadline": local_time(x.deadline),
            "summary": summary,
            "action": '<a href="' + url_for('student_bp.do_quiz', enroll_code=(str(x.enroll_code).lower() or "")) + f'" class="btn btn-primary btn-sm">{ ("Continue" if student_enrollment.active_attempt else "Start Attempt") }</a> &nbsp;'
        }
        data.append(entry)
    columns = table_schemas.SERVERSIDE_STUDENT_QUIZZES_COLUMNS
    data = ServerSideTable(request, data, columns).output_result()
    return jsonify(data)


@student_bp.route('/student/quiz/<enroll_code>', methods=['GET'])
@login_required
def do_quiz(enroll_code):
    data = dict()
    data['enroll_code'] = enroll_code
    data['question_form'] = QuestionForm()
    if request.method == 'GET':
        quiz_entity = Quiz.query.filter(
            Quiz.enroll_code == enroll_code.upper()).first()
        if quiz_entity:
            data['topic'] = quiz_entity.topic
            student_enrollment = StudentEnroll.select_by_user_and_quiz(
                current_user, quiz_entity)
            if student_enrollment:
                if not student_enrollment.active_attempt:
                    success = student_enrollment.start_new_attempt()
                    if success:
                        failed = False
                        try:
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()
                            db.session.flush()
                            failed = True
                        if failed:
                            # something error in database
                            return redirect(url_for('student_bp.quiz_management'), 408)

                        # SUCCESS: render question page
                        return render_template('question_student.html', **data)

                    else:
                        # error: user exceeded max attempt, redirect to quiz-management
                        return redirect(url_for('student_bp.quiz_management'), 403)
                else:
                    # redirect to question page to continue the quiz
                    return render_template('question_student.html', **data)
            else:
                # error: user not in enrollment. redirect
                return redirect(url_for('student_bp.quiz_management'), 403)
        else:
            # error: quiz didn't exists
            return redirect(url_for('student_bp.quiz_management'), 404)


@student_bp.route('/student/request-question/<enroll_code>', methods=['GET'])
@login_required
def request_question(enroll_code):
    data = dict()
    if request.method == 'GET':
        quiz_entity = Quiz.query.filter(
            Quiz.enroll_code == enroll_code.upper()).first()
        if quiz_entity:
            student_enrollment = StudentEnroll.select_by_user_and_quiz(
                current_user, quiz_entity)
            if student_enrollment:

                question_id = student_enrollment.question_unanswered[-1]
                question_entity = Question.query.filter(
                    Question.id == question_id).first()
                question_label = question_entity.question
                question_opt = [question_entity.opt1,
                                question_entity.opt2, question_entity.opt3]
                question_data = jsonify({
                    'question_id': question_id,
                    'question_label': question_label,
                    'question_opt': question_opt,
                    'question_complete': (True if len(student_enrollment.question_unanswered) < 2 else False)
                })
                return question_data
            else:
                return make_response(
                    f' Forbidden access. User not enrrolled to quiz.', 403)
        else:
            return make_response(
                f' Forbidden access. Cannot find quiz with enroll code: {enroll_code}', 403)


@student_bp.route('/student/answer-question/<enroll_code>', methods=['POST'])
@login_required
def answer_question(enroll_code):
    if request.method == 'POST':
        quiz_entity = Quiz.query.filter(
            Quiz.enroll_code == enroll_code.upper()).first()
        if quiz_entity:
            student_enrollment = StudentEnroll.select_by_user_and_quiz(
                current_user, quiz_entity)
            if student_enrollment:
                question_form = QuestionForm(request.form)
                # print(request.form)
                # print(question_form.question_id.data, question_form.answer_option.data)
                # if question_form.validate_on_submit():
                question_id = int(question_form.question_id.data)
                user_answer = question_form.answer_option.data

                question_entity = Question.query.filter(
                    Question.id == question_id).first()
                if question_entity:
                    student_enrollment.set_score(
                        question_entity, user_answer, score=10)
                    # Remove question that already answered
                    question_unanswered = student_enrollment.question_unanswered
                    question_unanswered.remove(question_id)
                    student_enrollment.question_unanswered = question_unanswered

                    failed = False
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        db.session.flush()
                        failed = True

                    if failed:
                        return make_response(' Failed during saving answer to database. Answer not saved, please try again', 408)
                    else:
                        if len(student_enrollment.question_unanswered) == 0:
                            resp = {
                                "redirect_to_home": True
                            }
                            return jsonify(resp)
                        return make_response(f'User answer: {user_answer} succesfully saved', 202)
                else:
                    return make_response(f' Forbidden access. No question found with id {question_id}', 403)
                # else:
                    # return make_response(f' Request sent with incomplete data.', 405)
            else:
                return make_response(
                    f' Forbidden access. User not enrolled to quiz.', 403)
        else:
            return make_response(
                f' Forbidden access. Cannot find quiz with enroll code: {enroll_code}', 403)
