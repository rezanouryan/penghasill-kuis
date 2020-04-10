from flask import Blueprint, render_template, redirect, url_for, request, current_app, jsonify
from flask_user import roles_required
from ..models import User, Quiz, db, Role
from datetime import datetime, timedelta
from .admin_forms import AddQuizForm
from ..quiz_generator.article import Article


# Set up blueprint
admin_bp = Blueprint('admin_bp', __name__,
                     template_folder='templates', static_folder='static')


@admin_bp.route('/admin', methods=['GET'])
@roles_required('admin')
def root():
    return redirect(url_for('admin_bp.dashboard'))


@admin_bp.route('/admin/dashboard', methods=['GET'])
@roles_required('admin')
def dashboard():

    MAX_ENTRY_UPCOMING = 10
    MAX_ENTRY_LEADERBOARD = 5
    MAX_ENTRY_COMPLETED = 5

    data = dict()
    data['ct_registered_user'] = User.query.filter(User.roles == None).count()
    data['ct_quizzes_created'] = Quiz.query.count()
    data['completed_quizzes'] = Quiz.get_completed_quizzes()[
        :MAX_ENTRY_COMPLETED]
    data['upcoming_quizzes'] = Quiz.get_upcoming_quizzes()[:MAX_ENTRY_UPCOMING]
    data['ct_quizzes_completed'] = len(data['completed_quizzes'])
    for i in range(len(data['upcoming_quizzes'])):
        data['upcoming_quizzes'][i].users_enrolled = User.query.with_parent(
            data['upcoming_quizzes'][i]).count()
    for i in range(len(data['completed_quizzes'])):
        data['completed_quizzes'][i].users_completed = len(
            User.get_student_completed_quiz_list(data['completed_quizzes'][i]))

    data['leaderboard'] = User.get_leaderboard()[:MAX_ENTRY_LEADERBOARD]

    data['add_quiz_form'] = AddQuizForm()
    # print(data['leaderboard'])

    return render_template('index_admin.html', **data)


@admin_bp.route('/admin/quiz-management', methods=['GET', 'POST'])
@roles_required('admin')
def quiz_management():

    data = dict()
    data['add_quiz_form'] = AddQuizForm()
    return render_template('quizzes_admin.html', **data)


@admin_bp.route('/admin/list-quiz-serverside', methods=['GET'])
@roles_required('admin')
def list_quiz_serverside():
    from ..serverside import table_schemas
    from ..serverside.serverside_table import ServerSideTable
    data = []
    for x in Quiz.query.all():
        entry = {
            "name": x.name,
            "topic": x.topic,
            "enroll_code": "<strong>" + x.enroll_code + "</strong>",
            "date_created": x.date_created,
            "deadline": x.deadline,
            "status": "<span class='status-icon bg-secondary'></span> Expired" if x.is_expired else "<span class='status-icon bg-success'></span> Upcoming",
            "action": '<a href="javascript:void(0)" data-enrollcode="' + x.enroll_code + '" class="btn btn-danger btn-sm">Delete</a> &nbsp;' + \
                      '<a href="javascript:void(0)" data-enrollcode="' + x.enroll_code + '" class="btn btn-primary btn-sm">Show report</a>'  
        }
        data.append(entry)

    columns = table_schemas.SERVERSIDE_QUIZZES_COLUMNS
    data = ServerSideTable(request, data, columns).output_result()
    return jsonify(data)


@admin_bp.route('/admin/add-quiz', methods=['POST'])
@roles_required('admin')
def add_quiz():
    add_quiz_form = AddQuizForm(request.form)
    if request.method == 'POST':
        if add_quiz_form.validate_on_submit():
            name = add_quiz_form.name.data
            topic = add_quiz_form.topic.data
            deadline = add_quiz_form.deadline.data
            max_attempt = add_quiz_form.max_attempt.data

            quiz = Quiz(name=name, topic=topic, deadline=deadline, max_attempt=max_attempt)

            article = Article(topic)
            if hasattr(article, 'quiz'):
                from ..quiz_generator.article import get_question_set
                ten_random = article.quiz.get_ten_random()
                random_propers = article.quiz.get_random_propers()
                random_loc = article.quiz.get_random_locations()
                

                question_set = [get_question_set(q.text, q.gaps) for q in ten_random]
                print(question_set)
                print(random_propers, random_loc)
            else:
                print("No_question")

        pass




    pass


@admin_bp.route('/admin/user-management', methods=['GET'])
@roles_required('admin')
def user_management():
    pass
