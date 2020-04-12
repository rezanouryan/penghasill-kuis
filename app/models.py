from app import db
from datetime import datetime
from flask_user import UserMixin
from flask import current_app
from sqlalchemy import func, desc
from .serverside import table_schemas
from .serverside.serverside_table import ServerSideTable
from .quiz_generator.article import Article
from base64 import b32encode
from random import randint

# Relationship table:
user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer(), db.ForeignKey(
                          'users.id', ondelete='CASCADE')),
                      db.Column('role_id', db.Integer(), db.ForeignKey(
                          'roles.id', ondelete='CASCADE'))
                      )


class StudentEnroll(db.Model):
    __tablename__ = 'student_enroll'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    score_uptilnow = db.Column(db.Integer, default=0)

    high_score = db.Column(db.Integer, default=0)

    attempt = db.Column(db.Integer, default=0)
    date_enrolled = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='student_enroll')
    quiz = db.relationship('Quiz', backref='student_enroll')

    @property
    def is_completed(self):
        return True if self.attempts > 0 else False

    @property
    def active_attempts(self):
        return True if self.question_answered else False

    @property
    def score_in_percentage(self):
        return self.score_uptilnow / len(self.quiz.questions) * 100

    @property
    def high_score_in_percentage(self):
        return self.high_score / len(self.quiz.questions) * 100

    @staticmethod
    def select_by_user_and_quiz(user_obj, quiz_obj):
        return StudentEnroll.query.with_parent(user_obj).with_parent(quiz_obj).first()

    def start_new_attempt(self):
        """
        Return type:
        True: if user doesn't exceed max attempt
        False: user exceeded max attempt
        """
        if self.attempts + 1 > self.quiz.max_attempt:
            return False
        self.score_uptilnow = 0
        self.question_answered = []
        self.question_length = len(self.quiz.questions)
        return True

    def set_score(self, question_obj, user_answer, score=1):
        """
        question_obj: instance of class Question
        user_answer: Integer 1, 2, or 3

        Return type:
        False: if user already answered question in attempt
        True: if question still not yet answered by user in attempt
        """
        if question_obj.id in question_answered:
            return False

        self.question_answered.append[question_obj.id]
        if user_answer == question_obj.answer:
            self.score_uptilnow += score
        return True

    def finish_attempt(self):
        self.high_score = self.high_score if self.score_uptilnow < self.high_score else self.score_uptilnow
        self.score_uptilnow = 0
        self.question_length = 0
        self.question_answered = None
        self.attempts += 1

    def is_all_answered(self):
        return True if self.active_attempts and len(self.question_answered) == self.question_length else False


# User
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String, nullable=False,
                         server_default=u'', unique=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                            backref=db.backref('users', lazy=True))

    date_created = db.Column(db.DateTime, default=func.now())

    quizzes = db.relationship(
        'Quiz', secondary='student_enroll')

    def check_password(self, plain_password):
        return current_app.user_manager.password_manager.verify_password(plain_password, self.password)

    def set_password(self, password):
        self.password = current_app.user_manager.password_manager.hash_password(
            password)

    def has_role(self, role):
        """Returns `True` if the user identifies with the specified role.
        :param role: A role name or `Role` instance"""
        if isinstance(role, str):
            return role in (role.name for role in self.roles)
        else:
            return role in self.roles

    @staticmethod
    def get_student_completed_quiz_list(quiz_obj):
        return User\
            .query\
            .outerjoin(StudentEnroll, User.id == StudentEnroll.user_id)\
            .with_parent(quiz_obj)\
            .filter(User.roles == None, StudentEnroll.attempt > 0)\
            .all()

    @staticmethod
    def get_leaderboard():
        user_enroll_list = StudentEnroll.\
            query\
            .with_entities(User.username,
                           User.first_name,
                           User.last_name,
                           func.sum(
                               StudentEnroll.high_score)
                           )\
            .outerjoin(User, User.id == StudentEnroll.user_id)\
            .filter(User.roles == None)\
            .group_by(StudentEnroll.user_id
                      )\
            .order_by(desc(func.sum(
                StudentEnroll.high_score))
            ).all()
        # for i in range(len(user_enroll_list)):
        #     user_enroll_list[i].answer_ratio =
        # print(user_enroll_list)
        return user_enroll_list


# Role: (admin, student)
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False,
                     server_default=u'', unique=True)  # for @roles_accepted()
    # for display purposes
    label = db.Column(db.Unicode(255), server_default=u'')


# Question
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'),
                        nullable=False)

    question = db.Column(db.String(200))
    opt1 = db.Column(db.String(200))
    opt2 = db.Column(db.String(200))
    opt3 = db.Column(db.String(200))

    answer = db.Column(db.Integer)


# Quiz: List of quiz with specific topic
class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))
    topic = db.Column(db.String(200))
    enroll_code = db.Column(db.String(), unique=True)
    max_attempt = db.Column(db.Integer, default=3)

    date_created = db.Column(db.DateTime, default=func.now())
    deadline = db.Column(db.DateTime)

    questions = db.relationship(Question, lazy='subquery',
                                backref=db.backref('questions', lazy=True))

    users = db.relationship(
        'User', secondary='student_enroll')

    
    @property
    def is_expired(self):
        return True if datetime.now() > self.deadline else False

    @staticmethod
    def get_upcoming_quizzes():
        return Quiz.query.filter(datetime.now() < Quiz.deadline).order_by(Quiz.deadline).all()

    @staticmethod
    def get_completed_quizzes():
        return Quiz.query.filter(datetime.now() > Quiz.deadline).order_by(Quiz.deadline).all()

    def set_enroll_code(self):
        encoded =  b32encode(bytes(str(self.id).encode('utf-8'))).decode('utf-8')
        encoded = "".join([ str(randint(0, 9)) if c == '=' else c for c in encoded ])
        self.enroll_code  =  "Q" + self.name[0].upper() + self.topic[0].upper() + encoded
