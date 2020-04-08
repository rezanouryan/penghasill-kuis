import datetime

from flask import current_app
from flask_script import Command

from app import db
from app.models import User, Role, Quiz, Question, StudentEnroll


class InitDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        init_db()
        print('Database has been initialized.')


def init_db():
    """ Initialize the database."""
    db.drop_all()
    db.create_all()
    create_users()


def create_users():
    """ Create users """
    # Create all tables
    db.create_all()

    # Adding roles
    admin_role = find_or_create_role('admin', 'Admin')

    # Add users
    admin = find_or_create_user(
        'Admin', 'istrator', 'admin', 'Password1', admin_role)
    user_1 = find_or_create_user(
        'Member', 'ship', 'member1', 'Password1')
    user_2 = find_or_create_user(
        'Member2', 'ship2', 'member2', 'Password2')
    user_3 = find_or_create_user(
        'Member3', 'ship3', 'member3', 'Password3')

    question_list_1 = [
        (
            "Example Question 1",
            "Option 1",
            "Option 2",
            "Option 3",
            "1"
        ),
        (
            "Example Question 2",
            "Option 1",
            "Option 2",
            "Option 3",
            "3"
        ),
        (
            "Example Question 3",
            "Option 1",
            "Option 2",
            "Option 3",
            "2"
        )
    ]

    question_list_2 = [
        (
            "Example Question 1",
            "Option 1",
            "Option 2",
            "Option 3",
            "1"
        ),
        (
            "Example Question 2",
            "Option 1",
            "Option 2",
            "Option 3",
            "2"
        ),
        (
            "Example Question 3",
            "Option 1",
            "Option 2",
            "Option 3",
            "3"
        ),
        (
            "Example Question 4",
            "Option 1",
            "Option 2",
            "Option 3",
            "3"
        )
    ]

    question_list_3 = [
        (
            "Example Question 1",
            "Option 1",
            "Option 2",
            "Option 3",
            "1"
        ),
        (
            "Example Question 2",
            "Option 1",
            "Option 2",
            "Option 3",
            "2"
        ),
        (
            "Example Question 3",
            "Option 1",
            "Option 2",
            "Option 3",
            "3"
        ),
        (
            "Example Question 4",
            "Option 1",
            "Option 2",
            "Option 3",
            "3"
        )
    ]


    deadline_1 = datetime.datetime(2020, 4, 10)
    deadline_2 = datetime.datetime(2020, 4, 11)
    deadline_3 = datetime.datetime(2020, 3, 31)

    quiz_1 = find_or_create_quiz('Topic 1', 'QT34A23', question_list_1, deadline_1)
    quiz_2 = find_or_create_quiz('Topic 2', 'QT34F13', question_list_2, deadline_2)
    quiz_3 = find_or_create_quiz('Topic 3', 'QT34B22', question_list_3, deadline_1)
    quiz_4 = find_or_create_quiz('Topic 3', 'QT34B22', question_list_1, deadline_2)
    quiz_5 = find_or_create_quiz('Topic 3', 'QT34B22', question_list_2, deadline_3)


    # Scenario 1: user_1 enrolled quiz_1 but didn't start
    user_1.quizzes.append(quiz_1)

    # Scenario 2: user_1 not enrolled other quiz
    
    # Scenario 3: user_1 enrolled expired deadline quiz
    user_1.quizzes.append(quiz_5)
    
    # Scenario 4: user_1 enrolled quiz_2, already start quiz
    user_1.quizzes.append(quiz_2)
    student_enrollment = StudentEnroll.select_by_user_and_quiz(user_1, quiz_2)
    student_enrollment.score_uptilnow = 10
    
    # Scenario 5: user_1 enrolled quiz_3, completed
    user_1.quizzes.append(quiz_3)
    student_enrollment_2 = StudentEnroll.select_by_user_and_quiz(user_1, quiz_3)
    student_enrollment_2.attempt = 1
    student_enrollment_2.high_score = 3


    user_2.quizzes.append(quiz_1)
    user_3.quizzes.append(quiz_5)


    # User.query.with_parent(data['upcoming_quizzes'][i])
    # Save to DB
    db.session.commit()


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role


def find_or_create_user(first_name, last_name, username, password, role=None):
    """ Find existing user or create new user """
    user = User.query.filter(User.username == username).first()
    if not user:
        user = User(username=username,
                    first_name=first_name,
                    last_name=last_name,
                    password=current_app.user_manager.password_manager.hash_password(
                        password)
                    )
        if role:
            user.roles.append(role)
        db.session.add(user)
    return user


def find_or_create_quiz(topic, enroll_code, question_list=None, deadline=None):
    quiz = Quiz.query.filter(Quiz.topic == topic).first()
    if not quiz:
        quiz = Quiz(topic=topic, enroll_code=enroll_code)
        if question_list:
            for question, opt1, opt2, opt3, answer in question_list:
                quest = Question(question=question,
                                 opt1=opt1,
                                 opt2=opt2,
                                 opt3=opt3,
                                 answer=answer
                                 )
                quiz.questions.append(quest)
        if deadline:
            quiz.deadline = deadline
        db.session.add(quiz)
    return quiz
