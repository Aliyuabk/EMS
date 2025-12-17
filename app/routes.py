from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms import LoginForm, StudentForm, ExamForm, SubjectScoreForm
from app.models import db, User, Zone, School, Student, Exam, Subject
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

# --- LOGIN ---
@main.route('/', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- DASHBOARD ---
@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# --- STUDENT MANAGEMENT ---
@main.route('/students', methods=['GET','POST'])
@login_required
def students():
    form = StudentForm()
    form.school.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    if form.validate_on_submit():
        filename = None
        if form.photo.data:
            filename = secure_filename(form.photo.data.filename)
            form.photo.data.save(os.path.join('app/static/uploads', filename))
        student = Student(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            gender=form.gender.data,
            school_id=form.school.data,
            photo=filename
        )
        db.session.add(student)
        db.session.commit()
        flash('Student registered successfully')
        return redirect(url_for('main.students'))
    students = Student.query.all()
    return render_template('students.html', form=form, students=students)
# --- EXAM SELECTION ---
@main.route('/exams', methods=['GET','POST'])
@login_required
def exams():
    form = ExamForm()
    form.student.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in Student.query.order_by(Student.last_name).all()]
    if form.validate_on_submit():
        exam = Exam(
            student_id=form.student.data,
            exam_type=form.exam_type.data,
            year=form.year.data
        )
        db.session.add(exam)
        db.session.commit()
        flash('Exam started successfully')
        return redirect(url_for('main.exam_subjects', exam_id=exam.id))
    return render_template('exams.html', form=form)

# --- SUBJECT SCORES ENTRY ---
@main.route('/exam/<int:exam_id>/subjects', methods=['GET','POST'])
@login_required
def exam_subjects(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    # Define subjects based on exam type
    subjects_list = ['English', 'Mathematics', 'Civic Education', 'Sciences', 'Commercial']
    # Preload subjects if not exist
    for sub_name in subjects_list:
        if not Subject.query.filter_by(exam_id=exam.id, name=sub_name).first():
            db.session.add(Subject(name=sub_name, exam_id=exam.id))
    db.session.commit()

    subjects = Subject.query.filter_by(exam_id=exam.id).all()
    
    if request.method == 'POST':
        for subject in subjects:
            ca = request.form.get(f'ca_{subject.id}', type=float)
            exam_score = request.form.get(f'exam_{subject.id}', type=float)
            subject.ca_score = ca
            subject.exam_score = exam_score
        db.session.commit()
        flash('Scores saved successfully')
        return redirect(url_for('main.results', exam_id=exam.id))

    return render_template('exam_subjects.html', exam=exam, subjects=subjects)
# --- RESULTS DISPLAY ---
@main.route('/results/<int:exam_id>')
@login_required
def results(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    subjects = exam.subjects
    total_score = sum([sub.total for sub in subjects])
    average_score = total_score / len(subjects) if subjects else 0
    credits = sum([1 for sub in subjects if sub.total >= 50])  # Example: 50+ is a credit
    return render_template('results.html', exam=exam, subjects=subjects, total_score=total_score, average_score=average_score, credits=credits)
@main.route('/subject_analysis')
@login_required
def subject_analysis():
    subjects = Subject.query.all()
    analysis = {}
    for sub in subjects:
        name = sub.name
        if name not in analysis:
            analysis[name] = {'registered':0, 'not_registered':0}
        analysis[name]['registered'] += 1 if sub.ca_score or sub.exam_score else 0
        analysis[name]['not_registered'] += 1 if not sub.ca_score and not sub.exam_score else 0
    return render_template('subject_analysis.html', analysis=analysis)

