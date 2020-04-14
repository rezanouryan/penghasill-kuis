from flask import Blueprint, render_template, redirect, url_for, request, current_app, jsonify, make_response
from flask_user import roles_required
from ..models import User, Quiz, db, Role, Question
from datetime import datetime, timedelta
from .admin_forms import AddQuizForm, DeleteUserForm
from ..quiz_generator.article import Article
import pytz
from requests.exceptions import ConnectionError as ce
from ..helper.date_time_utils import local_time

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
            "enroll_code": "<strong>" + (x.enroll_code or "") + "</strong>",
            "date_created": local_time(x.date_created),
            "deadline": local_time(x.deadline),
            "status": "<span class='status-icon bg-secondary'></span> Expired" if x.is_expired else "<span class='status-icon bg-success'></span> Upcoming",
            "action": '<a href="' + url_for('admin_bp.view_quiz', enroll_code=(str(x.enroll_code).lower() or "")) + '" class="btn btn-primary btn-sm">Show report and questions</a> &nbsp;'
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
            local = pytz.timezone('Asia/Jakarta')
            name = add_quiz_form.name.data
            topic = add_quiz_form.topic.data
            deadline = (add_quiz_form.deadline.data +
                        timedelta(days=1)).strftime("%Y-%m-%d")
            deadline = local.localize(datetime.strptime(
                deadline, "%Y-%m-%d"), is_dst=None)
            deadline = deadline.astimezone(pytz.utc) - timedelta(seconds=1)
            max_attempt = add_quiz_form.max_attempt.data

            quiz = Quiz(name=name, topic=topic, deadline=deadline,
                        max_attempt=max_attempt)

            quiz.set_enroll_code()

            article = None
            try:
                article = Article(topic)
            except ce as err:
                return make_response(err.__str__(), 408)
            if hasattr(article, 'quiz'):
                from ..quiz_generator.article import get_question_set
                ten_random = article.quiz.get_ten_random()
                random_propers = article.quiz.get_random_propers()
                random_loc = article.quiz.get_random_locations()
                question_set = [get_question_set(
                    q.text, q.gaps) for q in ten_random]
                question_set = list(
                    filter(lambda x: x is not None, question_set))

                if len(question_set) == 0:
                    return make_response(" No question generated. Try again with different keyword.", 402)

                for q in question_set:
                    quest = Question(**q)
                    quiz.questions.append(quest)

                failed = False
                try:
                    db.session.add(quiz)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    db.session.flush()
                    failed = True

                if failed:
                    return make_response(" There are something error when putting quiz data into database. Please try again or contact admin for further information.", 402)
                else:
                    return make_response(f"Quiz {name} with topic {topic} and deadline {deadline.strftime('%B %d, %Y %X %Z')} are succesfully generated. {len(question_set)} question(s) are generated for this quiz.", 201)
            else:
                return make_response(f" Cannot find article about {topic} in DBpedia for question generator. Please make sure topic {topic} is exists. ", 402)

        pass

    pass


@admin_bp.route('/admin/quiz/<enroll_code>', methods=['GET'])
@roles_required('admin')
def view_quiz(enroll_code):
    data = {}
    data['quiz'] = Quiz.query.filter(
        Quiz.enroll_code == enroll_code.upper()).first()
    data['questions'] = data['quiz'].questions

    return render_template('quiz_admin.html', **data)


@admin_bp.route('/admin/user-management', methods=['GET'])
@roles_required('admin')
def user_management():
    data = {}
    data['delete_user_form'] = DeleteUserForm()
    return render_template('user_man_admin.html', **data)


@admin_bp.route('/admin/list-user-serverside', methods=['GET'])
@roles_required('admin')
def list_user_serverside():
    from ..serverside import table_schemas
    from ..serverside.serverside_table import ServerSideTable
    data = []
    for x in User.query.filter(User.roles == None).all():
        entry = {
            "id": x.id,
            "username": x.username,
            "display_name": "<strong>" + f"{x.first_name} {x.last_name}" + "</strong>",
            "date_created": local_time(x.date_created),
            "action": '<button data-userondelete="' + x.username + '" class="btn btn-danger btn-sm deleteuser">Delete</button> &nbsp;'
        }
        data.append(entry)

    columns = table_schemas.SERVERSIDE_USERS_COLUMNS
    data = ServerSideTable(request, data, columns).output_result()
    return jsonify(data)


@admin_bp.route('/admin/delete-user', methods=['POST'])
@roles_required('admin')
def delete_user():
    if request.method == 'POST':
        delete_form = DeleteUserForm(request.form)
        if delete_form.validate_on_submit():
            username = delete_form.username.data

            User.query.filter(User.username == username).delete()
            db.session.commit()
            return make_response(f"User {username} is succesfully deleted", 202)
        return make_response(f"Error deleting user {username}. The user that you want to delete might be already not exists.", 400)
