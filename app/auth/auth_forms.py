"""Signup & login forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class SignupForm(FlaskForm):
    """User Signup Form."""
    first_name = StringField('First Name',
                       validators=[DataRequired()])
    last_name = StringField('Last Name',
                       validators=[DataRequired()])
    username = StringField('Username',
                        validators=[Length(min=6),
                                    DataRequired()]
                            )
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(min=6, message='Select a stronger password.')])
    confirm = PasswordField('Confirm Your Password',
                            validators=[DataRequired(),
                                        EqualTo('password', message='Passwords must match.')])
    submit = SubmitField("Let's Quiz!")


class LoginForm(FlaskForm):
    """User Login Form."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit=SubmitField("Let's Quiz!")
