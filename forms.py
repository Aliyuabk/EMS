from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length, EqualTo

# Login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('school', 'School Admin'), ('jera', 'Jera Admin')])
    submit = SubmitField('Login')

# Exam selection form (example)
class ExamSelectionForm(FlaskForm):
    exam_type = SelectField('Exam Type', choices=[('QE', 'Qualifying Exam'), ('BECE', 'Basic Education Certificate Exam')])
    exam_year = StringField('Year', validators=[DataRequired()])
    exam_date = DateField('Exam Date', validators=[DataRequired()])
    submit = SubmitField('Continue')
