from flask import Flask, render_template, redirect, url_for, flash, request, session
from config import Config
from models import db, bcrypt, Admin, Zone, School, Exam, Student, Subject, Result
from forms import LoginForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

# ----------------- INITIALIZE DB -----------------
def init_db():
    with app.app_context():
        db.create_all()

        # Add default admins
        if not Admin.query.filter_by(username='schooladmin').first():
            admin1 = Admin(username='schooladmin', role='school')
            admin1.set_password('school123')
            db.session.add(admin1)

        if not Admin.query.filter_by(username='jeraadmin').first():
            admin2 = Admin(username='jeraadmin', role='jera')
            admin2.set_password('jera123')
            db.session.add(admin2)

        # Add Jigawa Zones / LGAs
        jigawa_lgas = [
            "Auyo", "Babura", "Birnin Kudu", "Birnin Kudu East", "Birnin Kudu West",
            "Buji", "Gagarawa", "Garki", "Gumel", "Guri", "Gwaram", "Gwiwa",
            "Hadejia", "Jahun", "Kafin Hausa", "Kaugama", "Kazaure", "Kiri Kasama",
            "Kiyawa", "Maigatari", "Malam Madori", "Miga", "Ringim", "Roni", "Sule Tankarkar",
            "Taura", "Yankwashi"
        ]

        for lga in jigawa_lgas:
            if not Zone.query.filter_by(name=lga).first():
                db.session.add(Zone(name=lga))

        db.session.commit()

init_db()

# ----------------- LOGIN & SESSION -----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data, role=form.role.data).first()
        if admin and admin.check_password(form.password.data):
            session['user_id'] = admin.id
            session['role'] = admin.role
            flash(f'Welcome {admin.role.capitalize()} Admin!', 'success')
            return redirect(url_for('school_dashboard') if admin.role == 'school' else url_for('jera_dashboard'))
        else:
            flash('Login failed. Check username, password, or role.', 'danger')
    return render_template('login.html', form=form, title="Login Form")


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


# ----------------- DECORATOR -----------------
def login_required(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Login required!', 'warning')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Unauthorized access!', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


# ----------------- DASHBOARDS -----------------
@app.route('/dashboard/school')
@login_required(role='school')
def school_dashboard():
    total_zones = Zone.query.count()
    total_schools = School.query.count()
    total_exams = Exam.query.count()
    return render_template('school_dashboard.html',
                           total_zones=total_zones,
                           total_schools=total_schools,
                           total_exams=total_exams)


@app.route('/dashboard/jera')
@login_required(role='jera')
def jera_dashboard():
    zones = Zone.query.all()
    schools = School.query.all()
    exams = Exam.query.all()
    return render_template('dashboard/jera_dashboard.html',
                           title="JERA Dashboard",
                           zones=zones,
                           schools=schools,
                           exams=exams)


# ----------------- ZONE CRUD -----------------
@app.route('/dashboard/zones')
@login_required(role='jera')
def zones():
    zones = Zone.query.all()
    return render_template('dashboard/zones.html', zones=zones, title="Zones")


@app.route('/zones/add', methods=['GET', 'POST'])
@login_required(role='jera')
def add_zone():
    if request.method == 'POST':
        name = request.form['name'].strip()
        if Zone.query.filter_by(name=name).first():
            flash('Zone already exists', 'danger')
            return redirect(url_for('add_zone'))

        db.session.add(Zone(name=name))
        db.session.commit()
        flash('Zone added successfully', 'success')
        return redirect(url_for('zones'))

    return render_template('dashboard/zone_form.html', title='Add Zone')


@app.route('/zones/edit/<int:zone_id>', methods=['GET', 'POST'])
@login_required(role='jera')
def edit_zone(zone_id):
    zone = Zone.query.get_or_404(zone_id)
    if request.method == 'POST':
        zone.name = request.form['name'].strip()
        db.session.commit()
        flash('Zone updated successfully', 'success')
        return redirect(url_for('zones'))
    return render_template('dashboard/zone_form.html', title='Edit Zone', zone=zone)


@app.route('/zones/delete/<int:zone_id>')
@login_required(role='jera')
def delete_zone(zone_id):
    zone = Zone.query.get_or_404(zone_id)
    if zone.schools:
        flash('Cannot delete zone with schools attached', 'danger')
        return redirect(url_for('zones'))

    db.session.delete(zone)
    db.session.commit()
    flash('Zone deleted successfully', 'success')
    return redirect(url_for('zones'))


# ----------------- SCHOOL CRUD -----------------
@app.route('/schools/add', methods=['GET', 'POST'])
@login_required(role='jera')
def add_school():
    zones = Zone.query.all()
    if request.method == 'POST':
        name = request.form['name'].strip()
        zone_id = request.form['zone_id']

        # Generate unique school code: ZONEID + sequential number
        zone = Zone.query.get(zone_id)
        existing_schools_count = School.query.filter_by(zone_id=zone_id).count()
        code = f"{zone.name[:3].upper()}{existing_schools_count + 1:03d}"  # e.g., "AUY001"

        # Check for duplicate school name
        if School.query.filter_by(name=name).first():
            flash('School name already exists', 'danger')
            return redirect(url_for('add_school'))

        school = School(name=name, code=code, zone_id=zone_id)
        db.session.add(school)
        db.session.commit()
        flash(f'School added successfully with code {code}', 'success')
        return redirect(url_for('list_schools'))

    return render_template('dashboard/add_school.html', zones=zones, title='Add School')



# ----------------- EXAM MANAGEMENT -----------------
@app.route('/jera/exam_management', methods=['GET', 'POST'])
@login_required(role='jera')
def exam_management():
    schools = School.query.all()
    exams = Exam.query.all()
    subjects = Subject.query.all()
    selected_school = request.form.get('school_id')
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

    return render_template('exam_management.html', schools=schools, exams=exams,
                           students=students, subjects=subjects, results=results,
                           selected_school=selected_school, selected_student=selected_student)


# ----------------- ANALYTICS -----------------
@app.route('/jera/analytics')
@login_required(role='jera')
def analytics():
    total_schools = School.query.count()
    total_students = Student.query.count()
    male_students = Student.query.filter_by(gender='Male').count()
    female_students = Student.query.filter_by(gender='Female').count()

    students_with_5_credits = 0
    for student in Student.query.all():
        credit_count = sum(1 for r in student.results if r.total >= 50)
        if credit_count >= 5:
            students_with_5_credits += 1

    return render_template('analytics.html',
                           total_schools=total_schools,
                           total_students=total_students,
                           male_students=male_students,
                           female_students=female_students,
                           students_with_5_credits=students_with_5_credits)

# ----------------- SCHOOL LIST BY ZONE -----------------
@app.route('/schools', methods=['GET', 'POST'])
@login_required(role='jera')
def list_schools():
    zones = Zone.query.all()
    selected_zone_id = None
    schools = []

    if request.method == 'POST':
        selected_zone_id = request.form.get('zone_id')
        if selected_zone_id:
            schools = School.query.filter_by(zone_id=selected_zone_id).all()

    return render_template('dashboard/list_schools.html',
                           zones=zones,
                           schools=schools,
                           selected_zone_id=selected_zone_id,
                           title='Schools by Zone')

@app.route('/schools/edit/<int:school_id>', methods=['GET', 'POST'])
@login_required(role='jera')
def edit_school(school_id):
    school = School.query.get_or_404(school_id)
    zones = Zone.query.all()

    if request.method == 'POST':
        school.name = request.form['name'].strip()
        school.zone_id = request.form['zone_id']
        db.session.commit()
        flash('School updated successfully', 'success')
        return redirect(url_for('list_schools'))

    return render_template('dashboard/edit_school.html', school=school, zones=zones, title='Edit School')


@app.route('/schools/delete/<int:school_id>')
@login_required(role='jera')
def delete_school(school_id):
    school = School.query.get_or_404(school_id)
    db.session.delete(school)
    db.session.commit()
    flash('School deleted successfully', 'success')
    return redirect(url_for('list_schools'))

# ----------------- RUN APP -----------------
if __name__ == '__main__':
    app.run(debug=True)
