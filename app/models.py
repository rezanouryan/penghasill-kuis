from app import db
from flask_user import UserMixin
from flask import current_app


# Relationship table
user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer(), db.ForeignKey(
                          'users.id', ondelete='CASCADE')),
                      db.Column('role_id', db.Integer(), db.ForeignKey(
                          'roles.id', ondelete='CASCADE'))
                      )


# Parent user
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

    def check_password(self, plain_password):
        return current_app.user_manager.password_manager.verify_password(plain_password, self.password)

    def set_password(self, password):
        self.password = current_app.user_manager.password_manager.hash_password(
            password)


# Child Role
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False,
                     server_default=u'', unique=True)  # for @roles_accepted()
    # for display purposes
    label = db.Column(db.Unicode(255), server_default=u'')
