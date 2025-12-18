from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# ---------- Admin ----------
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'school' or 'jera'

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

# ---------- Zone ----------
class Zone(db.Model):
    __tablename__ = 'zones'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    schools = db.relationship('School', backref='zone', lazy=True)

    def __repr__(self):
        return f"<Zone {self.name}>"



# ---------- School ----------
class School(db.Model):
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)

    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=False)

    def __repr__(self):
        return f"<School {self.name} - Zone {self.zone_id}>"



# ---------- Exam ----------
class Exam(db.Model):
    __tablename__ = 'exam'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))  # QE / BECE
    year = db.Column(db.Integer)
    date = db.Column(db.Date)

# ---------- Student ----------
class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date)
    home_town = db.Column(db.String(50))
    lga = db.Column(db.String(50))
    guardian_contact = db.Column(db.String(20))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    results = db.relationship('Result', backref='student', lazy=True)

# ---------- Subject ----------
class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    results = db.relationship('Result', backref='subject', lazy=True)

# ---------- Result ----------
class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    ca_score = db.Column(db.Float)
    exam_score = db.Column(db.Float)
    total = db.Column(db.Float)

JIGAWA_ZONES = [
    "Auyo", "Babura", "Biriniwa", "Birnin Kudu",
    "Buji", "Dutse", "Gagarawa", "Garki",
    "Gumel", "Guri", "Gwaram", "Gwiwa",
    "Hadejia", "Jahun", "Kafin Hausa", "Kazaure",
    "Kiri Kasamma", "Kiyawa", "Maigatari", "Malam Madori",
    "Miga", "Ringim", "Roni", "Sule Tankarkar",
    "Taura", "Yankwashi"
]

def seed_zones():
    for name in JIGAWA_ZONES:
        zone = Zone.query.filter_by(name=name).first()
        if not zone:
            db.session.add(Zone(name=name))
    db.session.commit()

