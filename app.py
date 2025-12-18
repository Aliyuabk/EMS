from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, bcrypt, Admin, Zone, School, Exam, Student, Subject, Result

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

# Initialize DB and default admins
def init_db():
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='schooladmin').first():
            admin1 = Admin(username='schooladmin', role='school')
            admin1.set_password('school123')
            db.session.add(admin1)
        if not Admin.query.filter_by(username='jeraadmin').first():
            admin2 = Admin(username='jeraadmin', role='jera')
            admin2.set_password('jera123')
            db.session.add(admin2)
        db.session.commit()
init_db()

# ---------- LOGIN ----------
from forms import LoginForm

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data, role=form.role.data).first()
        if admin and admin.check_password(form.password.data):
            flash(f'Welcome {admin.role.capitalize()} Admin!', 'success')
            if admin.role == 'school':
                return redirect(url_for('school_dashboard'))
            else:
                return redirect(url_for('jera_dashboard'))
        else:
            flash('Login failed. Check username, password, or role.', 'danger')
    return render_template('login.html', form=form)

# ---------- DASHBOARDS ----------
@app.route('/dashboard/school')
def school_dashboard():
    return render_template('school_dashboard.html')


@app.route('/dashboard/jera', methods=['GET', 'POST'])
def jera_dashboard():
    zones = Zone.query.all()
    schools = School.query.all()
    exams = Exam.query.all()
    return render_template('jera_dashboard.html', zones=zones, schools=schools, exams=exams)


# ---------- EXAM MANAGEMENT ----------
@app.route('/jera/exam_management', methods=['GET', 'POST'])
def exam_management():
    schools = School.query.all()
    exams = Exam.query.all()
    subjects = Subject.query.all()

    selected_school = request.form.get('school_id')
    selected_exam = request.form.get('exam_id')
    selected_student = request.form.get('student_id')

    students = Student.query.filter_by(school_id=selected_school).all() if selected_school else []
    results = None
    if selected_student:
        results = Result.query.filter_by(student_id=selected_student).all()

    if request.method == 'POST' and 'save_results' in request.form:
        for subject in subjects:
            ca_score = float(request.form.get(f'ca_{subject.id}', 0))
            exam_score = float(request.form.get(f'exam_{subject.id}', 0))
            total_score = ca_score + exam_score
            result = Result.query.filter_by(student_id=selected_student, subject_id=subject.id).first()
            if not result:
                result = Result(student_id=selected_student, subject_id=subject.id)
            result.ca_score = ca_score
            result.exam_score = exam_score
            result.total = total_score
            db.session.add(result)
        db.session.commit()
        flash("Results saved successfully.", "success")
        return redirect(url_for('exam_management'))

    return render_template(
        'exam_management.html', schools=schools, exams=exams,
        students=students, subjects=subjects, results=results,
        selected_school=selected_school, selected_exam=selected_exam,
        selected_student=selected_student
    )

# ---------- SUBJECT ANALYSIS ----------
@app.route('/jera/subject_analysis', methods=['GET', 'POST'])
def subject_analysis():
    subjects = Subject.query.all()
    exams = Exam.query.all()
    zones = Zone.query.all()
    selected_subject = request.form.get('subject_id')
    selected_exam = request.form.get('exam_id')
    selected_zone = request.form.get('zone_id')

    analysis_data = None
    if request.method == 'POST' and selected_subject:
        results_query = Result.query.join(Student).join(School).join(Zone).filter(
            Result.subject_id==selected_subject
        )
        if selected_zone:
            results_query = results_query.filter(School.zone_id==selected_zone)

        registered = results_query.count()
        not_registered = Student.query.count() - registered
        analysis_data = {'registered': registered, 'not_registered': not_registered}

    return render_template('subject_analysis.html', subjects=subjects, exams=exams,
                           zones=zones, analysis_data=analysis_data)

# ---------- ANALYTICS ----------
@app.route('/jera/analytics')
def analytics():
    total_schools = School.query.count()
    total_students = Student.query.count()
    male_students = Student.query.filter_by(gender='Male').count()
    female_students = Student.query.filter_by(gender='Female').count()

    students_with_5_credits = 0
    for student in Student.query.all():
        total_subjects = len(student.results)
        credit_count = sum(1 for r in student.results if r.total >= 50)
        if credit_count >= 5:
            students_with_5_credits += 1

    return render_template('analytics.html',
                           total_schools=total_schools,
                           total_students=total_students,
                           male_students=male_students,
                           female_students=female_students,
                           students_with_5_credits=students_with_5_credits)

# ---------- PHOTO CARD ----------
@app.route('/jera/photo_card/<int:student_id>')
def photo_card(student_id):
    student = Student.query.get(student_id)
    exam = Exam.query.order_by(Exam.year.desc()).first()  # latest exam
    return render_template('photo_card.html', student=student, exam=exam)

@app.route('/jera/zone_management', methods=['GET', 'POST'])
def zone_management():
    zones = Zone.query.all()
    # You can implement school/student registration here
    return render_template('zone_management.html', zones=zones)

def init_zones_and_schools():
    with app.app_context():
        # Example zone
        zone = Zone.query.filter_by(name='Jigawa North').first()
        if not zone:
            zone = Zone(name='Jigawa North')
            db.session.add(zone)
            db.session.commit()

        # Example school
        if not School.query.filter_by(name='ABC Secondary School').first():
            school = School(
                code='JN001',  # <-- add a unique code
                name='ABC Secondary School',
                zone_id=zone.id
            )
            db.session.add(school)

        if not School.query.filter_by(name='XYZ Secondary School').first():
            school = School(
                code='JN002',  # <-- add a unique code
                name='XYZ Secondary School',
                zone_id=zone.id
            )
            db.session.add(school)

        db.session.commit()


# ---------- RUN APP ----------
if __name__ == '__main__':
    app.run(debug=True)
