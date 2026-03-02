from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db, User, CompanyProfile, PlacementDrive, Application

admin_bp = Blueprint('admin', __name__)

# helper function to check admin role
def check_admin_permission():
    claims = get_jwt()
    if claims.get('role') != 'admin': 
        return False
    return True

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    is_admin = check_admin_permission()
    if not is_admin:
        return jsonify({"msg": "Unauthorized"}), 403
        
    num_students = User.query.filter_by(role='student').count()
    num_companies = CompanyProfile.query.filter_by(is_approved=True).count()
    num_drives = PlacementDrive.query.count()
    
    return jsonify({
        "students": num_students,
        "companies": num_companies,
        "drives": num_drives
    })

@admin_bp.route('/pending-companies', methods=['GET'])
@jwt_required()
def get_unapproved_companies():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    
    companies = CompanyProfile.query.filter_by(is_approved=False).all()
    results = []
    for comp in companies:
        results.append({
            "id": comp.id, 
            "name": comp.company_name, 
            "hr": comp.hr_contact
        })
    return jsonify(results)

@admin_bp.route('/approve-company/<int:comp_id>', methods=['POST'])
@jwt_required()
def approve_comp(comp_id):
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    
    company_obj = CompanyProfile.query.get(comp_id)
    if company_obj is not None:
        company_obj.is_approved = True
        db.session.commit()
        return jsonify({"msg": "Approved successfully"})
    return jsonify({"msg": "Not found"}), 404

@admin_bp.route('/pending-drives', methods=['GET'])
@jwt_required()
def get_unapproved_drives():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    
    drives = PlacementDrive.query.filter_by(status='Pending').all()
    results = []
    for d in drives:
        results.append({
            "id": d.id, 
            "title": d.job_title, 
            "company": d.company_ref.company_name
        })
    return jsonify(results)

@admin_bp.route('/approve-drive/<int:drive_id>', methods=['POST'])
@jwt_required()
def approve_new_drive(drive_id):
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    
    drive_obj = PlacementDrive.query.get(drive_id)
    if drive_obj is not None:
        drive_obj.status = 'Approved'
        db.session.commit()
        return jsonify({"msg": "Drive approved"})
    return jsonify({"msg": "Not found"}), 404

@admin_bp.route('/students', methods=['GET'])
@jwt_required()
def get_all_students():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    
    students_list = User.query.filter_by(role='student').all()
    data = []
    for s in students_list:
        data.append({"id": s.id, "username": s.username, "email": s.email, "is_active": s.is_active})
    return jsonify(data)

@admin_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_all_approved_companies():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    
    comp_list = CompanyProfile.query.filter_by(is_approved=True).all()
    data = []
    for c in comp_list:
        data.append({"id": c.user_id, "name": c.company_name, "is_active": c.user_account.is_active})
    return jsonify(data)

@admin_bp.route('/blacklist/<int:target_user_id>', methods=['POST'])
@jwt_required()
def toggle_user_blacklist(target_user_id):
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    
    user = User.query.get(target_user_id)
    if user.role == 'admin':
        return jsonify({"msg": "Cannot blacklist the admin"}), 400
    
    # flip the boolean value
    if user.is_active == True:
        user.is_active = False
    else:
        user.is_active = True
        
    db.session.commit()
    return jsonify({"msg": "User status changed"})

@admin_bp.route('/all-drives', methods=['GET'])
@jwt_required()
def view_all_drives():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    
    all_d = PlacementDrive.query.all()
    data = []
    for d in all_d:
        data.append({
            "id": d.id, "title": d.job_title, "company": d.company_ref.company_name, 
            "status": d.status, "description": d.job_description
        })
    return jsonify(data)

@admin_bp.route('/all-applications', methods=['GET'])
@jwt_required()
def view_all_apps():
    if not check_admin_permission(): return jsonify({"msg": "Unauthorized"}), 403
    
    apps = Application.query.all()
    data = []
    for a in apps:
        data.append({
            "id": a.id, "student_name": a.student_ref.username, 
            "drive_title": a.drive_ref.job_title, "company": a.drive_ref.company_ref.company_name, 
            "date": a.application_date.strftime('%Y-%m-%d'), "status": a.status
        })
    return jsonify(data)