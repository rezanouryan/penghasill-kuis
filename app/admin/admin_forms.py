from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField, validators
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class AddQuizForm(FlaskForm):
    """Add new quiz form."""
    name = StringField('Quiz Name',
                       validators=[DataRequired()])
    topic = StringField('Topic',
                       validators=[DataRequired()])
    deadline = DateField('Deadline', format='%Y-%m-%d',
                         validators=[DataRequired()])
    max_attempt = IntegerField('Max Attempt Allowed',
                             [validators.NumberRange(min=0, max=10)])
    submit = SubmitField("Add New Quiz!")
