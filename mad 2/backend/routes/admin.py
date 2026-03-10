from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from models import db, User, CompanyProfile, PlacementDrive, Application, StudentProfile

admin_bp = Blueprint('admin_bp', __name__)

def check_admin_permission():
    if get_jwt().get('role') != 'admin': 
        return False
    return True

@admin_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    students = User.query.filter_by(role='student').all()
    result = []
    for s in students:
        prof = StudentProfile.query.filter_by(user_id=s.id).first()
        result.append({
            "id": s.id,
            "username": s.username,
            "is_active": s.is_active,
            "department": prof.department if prof else "N/A",
            "cgpa": prof.cgpa if prof else "N/A",
            "resume_path": prof.resume_path if prof else None
        })
    return jsonify(result)

@admin_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    companies = CompanyProfile.query.filter_by(is_approved=True).all()
    result = []
    for c in companies:
        result.append({
            "id": c.user_id, 
            "name": c.company_name,
            "hr_contact": c.hr_contact,
            "is_active": c.user_ref.is_active
        })
    return jsonify(result)

@admin_bp.route('/pending-companies', methods=['GET'])
@jwt_required()
def get_pending_companies():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    waiting = CompanyProfile.query.filter_by(is_approved=False).all()
    return jsonify([{"id": c.id, "name": c.company_name} for c in waiting])

@admin_bp.route('/approve-company/<int:comp_id>', methods=['POST'])
@jwt_required()
def approve_comp(comp_id):
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    company_obj = CompanyProfile.query.get(comp_id)
    if company_obj:
        company_obj.is_approved = True
        db.session.commit()
    return jsonify({"msg": "Approved"})

@admin_bp.route('/pending-drives', methods=['GET'])
@jwt_required()
def get_pending_drives():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    waiting = PlacementDrive.query.filter_by(status='Pending').all()
    return jsonify([{"id": d.id, "title": d.job_title} for d in waiting])

@admin_bp.route('/approve-drive/<int:drive_id>', methods=['POST'])
@jwt_required()
def approve_drive(drive_id):
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    drive_obj = PlacementDrive.query.get(drive_id)
    if drive_obj:
        drive_obj.status = 'Approved'
        db.session.commit()
    return jsonify({"msg": "Approved"})

@admin_bp.route('/blacklist/<int:user_id>', methods=['POST'])
@jwt_required()
def toggle_blacklist(user_id):
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    user_obj = User.query.get(user_id)
    if user_obj:
        user_obj.is_active = not user_obj.is_active
        db.session.commit()
    return jsonify({"msg": "User status changed"})

@admin_bp.route('/all-drives', methods=['GET'])
@jwt_required()
def get_all_drives():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    drives = PlacementDrive.query.all()
    return jsonify([{
        "id": d.id, "title": d.job_title, "company": d.company_ref.company_name, 
        "status": d.status, "description": d.job_description
    } for d in drives])

@admin_bp.route('/all-applications', methods=['GET'])
@jwt_required()
def get_all_apps():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    apps = Application.query.all()
    return jsonify([{
        "id": a.id, "student_name": a.student_ref.username,
        "drive_title": a.drive_ref.job_title, "company": a.drive_ref.company_ref.company_name
    } for a in apps])