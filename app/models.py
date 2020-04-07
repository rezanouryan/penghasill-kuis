from app import db
from datetime import datetime
from flask_user import UserMixin
from flask import current_app


# Relationship table:
user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer(), db.ForeignKey(
                          'users.id', ondelete='CASCADE')),
                      db.Column('role_id', db.Integer(), db.ForeignKey(
                          'roles.id', ondelete='CASCADE'))
                      )

student_enroll = db.Table('student_enroll',
                          db.Column('user_id', db.Integer(), db.ForeignKey(
                              'users.id', ondelete='CASCADE')),
                          db.Column('quiz_id', db.Integer(), db.ForeignKey(
                              'quizzes.id', ondelete='CASCADE')),
                          db.Column('score_uptilnow', db.Integer),
                          db.Column('attempts', db.Integer),
                          db.Column('high_score', db.Integer),
                          db.Column('question_left', db.Integer),
                          db.Column('quizid_left', db.Integer),
                          db.Column('ctr_left', db.Integer),
                          db.Column('dttm', db.DateTime,
                                    default=datetime.utcnow)
                          )


# User
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False,
                         server_default=u'', unique=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                            backref=db.backref('users', lazy=True))

    quizzes = db.relationship('Quiz', secondary=student_enroll,
                            backref=db.backref('users', lazy='joined'))



    def check_password(self, plain_password):
        return current_app.user_manager.password_manager.verify_password(plain_password, self.password)

    def set_password(self, password):
        self.password = current_app.user_manager.password_manager.hash_password(
            password)


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
    topic = db.Column(db.String(200))
    enroll_code = db.Column(db.String(), unique=True)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)


    questions = db.relationship(Question, lazy='subquery',
                                backref=db.backref('questions', lazy=True))
    

