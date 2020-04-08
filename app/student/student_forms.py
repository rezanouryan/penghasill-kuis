from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField, validators
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class EnrollForm(FlaskForm):
    """Add new quiz form."""
    enroll_code = StringField('Enroll Code')
    submit = SubmitField("Enroll me!")
