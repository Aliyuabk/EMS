from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FileField
from wtforms.validators import DataRequired, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class StudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male','Male'), ('Female','Female')])
    school = SelectField('School', coerce=int)
    photo = FileField('Passport Photo')
    submit = SubmitField('Save')

class ExamForm(FlaskForm):
    student = SelectField('Student', coerce=int)
    exam_type = SelectField('Exam Type', choices=[('QE','QE'), ('BECE','BECE')])
    year = IntegerField('Year', validators=[DataRequired()])
    submit = SubmitField('Start Exam')

class SubjectScoreForm(FlaskForm):
    ca_score = IntegerField('CA Score', validators=[DataRequired()])
    exam_score = IntegerField('Exam Score', validators=[DataRequired()])
    submit = SubmitField('Save Score')
