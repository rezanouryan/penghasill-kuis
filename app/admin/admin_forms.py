from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, validators, HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from datetime import datetime


class AddQuizForm(FlaskForm):
    """Add new quiz form."""
    name = StringField('Quiz Name',
                       validators=[DataRequired()])
    topic = StringField('Topic',
                       validators=[DataRequired()])
    deadline = DateField('Deadline (in WIB)', format='%Y-%m-%d',
                         validators=[DataRequired()],
                         default=datetime.now())
    max_attempt = IntegerField('Max Attempt Allowed',
                             [validators.NumberRange(min=0, max=10), DataRequired()],
                             default=3)
    submit = SubmitField("Add New Quiz!")


class DeleteUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    delete_button = SubmitField("I understand all data related to this user will be deleted.")