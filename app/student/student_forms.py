from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField, validators, RadioField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class EnrollForm(FlaskForm):
    """Add new quiz form."""
    enroll_code = StringField('Enroll Code', validators=[DataRequired()])
    submit = SubmitField("Enroll me!")


class QuestionForm(FlaskForm):
    question_id = HiddenField(validators=[DataRequired()], default='')
    answer_option = RadioField('Select an answer:', choices=[(
        'opt1', 'Option 1'), ('opt2', 'Option 2'), ('opt3', 'Option 3')], validators=[DataRequired()])
    submit = SubmitField('Submit answer')
        
