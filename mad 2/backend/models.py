from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'student', 'company'
    is_active = db.Column(db.Boolean, default=True)

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    full_name = db.Column(db.String(150))
    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    resume_path = db.Column(db.String(255)) 

    user_ref = db.relationship('User', backref='student_profile')

class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(150), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    
    user_ref = db.relationship('User', backref='company_profile')

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Pending') 
    
    company_ref = db.relationship('CompanyProfile', backref='drives')

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    status = db.Column(db.String(20), default='Applied')
    application_date = db.Column(db.DateTime, default=datetime.utcnow)

    student_ref = db.relationship('User', backref='applications')
    drive_ref = db.relationship('PlacementDrive', backref='applications')