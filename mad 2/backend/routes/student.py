import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, PlacementDrive, Application, CompanyProfile, User, StudentProfile
from extensions import cache

student_bp = Blueprint('student_bp', __name__)

UPLOAD_FOLDER = 'uploads/resumes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def check_student_role():
    if get_jwt().get('role') != 'student': return False
    return True

@student_bp.route('/profile', methods=['GET', 'POST'])
@jwt_required()
def manage_profile():
    if not check_student_role(): return jsonify({"msg": "Unauthorized"}), 403
    my_id = get_jwt_identity()
    profile = StudentProfile.query.filter_by(user_id=my_id).first()

    if request.method == 'GET':
        if not profile:
            return jsonify({"full_name": "", "department": "", "cgpa": "", "resume_path": ""})
        return jsonify({
            "full_name": profile.full_name,
            "department": profile.department,
            "cgpa": profile.cgpa,
            "resume_path": profile.resume_path
        })

    if request.method == 'POST':
        if not profile:
            profile = StudentProfile(user_id=my_id)
            db.session.add(profile)
        
        profile.full_name = request.form.get('full_name')
        profile.department = request.form.get('department')
        if request.form.get('cgpa'): profile.cgpa = float(request.form.get('cgpa'))

        if 'resume' in request.files:
            file = request.files['resume']
            if file.filename != '':
                filename = secure_filename(f"user_{my_id}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                profile.resume_path = filename

        db.session.commit()
        return jsonify({"msg": "Profile updated successfully!"})

@student_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    if not check_student_role(): return jsonify({"msg": "Unauthorized"}), 403
    companies = CompanyProfile.query.filter_by(is_approved=True).all()
    return jsonify([{
        "id": c.id, "name": c.company_name, "hr_contact": c.hr_contact
    } for c in companies])

@student_bp.route('/drives', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, key_prefix='student_drives') 
def list_approved_drives():
    if not check_student_role(): return jsonify({"msg": "Unauthorized"}), 403
    drives = PlacementDrive.query.filter_by(status='Approved').all()
    return jsonify([{
        "id": d.id, "company_id": d.company_id, "title": d.job_title,
        "company": d.company_ref.company_name, "description": d.job_description,
        "eligibility": d.eligibility_criteria, "salary": d.salary, 
        "location": d.location, "deadline": d.application_deadline.strftime('%Y-%m-%d')
    } for d in drives])

@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
@jwt_required()
def apply_to_drive(drive_id):
    if not check_student_role(): return jsonify({"msg": "Unauthorized"}), 403
    my_id = get_jwt_identity()
    
    existing_app = Application.query.filter_by(student_id=my_id, drive_id=drive_id).first()
    if existing_app:
        return jsonify({"msg": "You have already applied to this drive"}), 400
        
    new_app = Application(student_id=my_id, drive_id=drive_id)
    db.session.add(new_app)
    db.session.commit()
    return jsonify({"msg": "Application submitted successfully"}), 201

@student_bp.route('/applications', methods=['GET'])
@jwt_required()
def my_applications():
    if not check_student_role(): return jsonify({"msg": "Unauthorized"}), 403
    my_id = get_jwt_identity()
    my_apps = Application.query.filter_by(student_id=my_id).all()
    return jsonify([{
        "id": a.id, "drive_title": a.drive_ref.job_title,
        "company": a.drive_ref.company_ref.company_name,
        "status": a.status, "date": a.application_date.strftime('%Y-%m-%d')
    } for a in my_apps])

@student_bp.route('/export-csv', methods=['POST'])
@jwt_required()
def trigger_real_csv_export():
    if not check_student_role(): return jsonify({"msg": "Unauthorized"}), 403
    my_user_id = get_jwt_identity()
    student_record = User.query.get(my_user_id)
    from tasks import generate_csv_for_student
    generate_csv_for_student.delay(my_user_id, student_record.email)
    return jsonify({"msg": "Export started! Check MailHog for the alert."}), 202