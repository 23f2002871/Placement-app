from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, PlacementDrive, Application, CompanyProfile

student_bp = Blueprint('student', __name__)

def check_student_role():
    claims = get_jwt()
    if claims.get('role') != 'student': 
        return False
    return True

@student_bp.route('/companies', methods=['GET'])
@jwt_required()
def list_companies_for_student():
    if not check_student_role(): 
        return jsonify({"msg": "Unauthorized"}), 403
        
    comps = CompanyProfile.query.filter_by(is_approved=True).all()
    out = []
    for c in comps:
        out.append({"id": c.id, "name": c.company_name})
    return jsonify(out)

@student_bp.route('/drives', methods=['GET'])
@jwt_required()
def list_approved_drives():
    if not check_student_role(): 
        return jsonify({"msg": "Unauthorized"}), 403
        
    active_drives = PlacementDrive.query.filter_by(status='Approved').all()
    out = []
    for d in active_drives:
        out.append({
            "id": d.id, 
            "title": d.job_title, 
            "company": d.company_ref.company_name, 
            "company_id": d.company_id,
            "description": d.job_description, 
            "eligibility": d.eligibility_criteria, 
            "deadline": d.application_deadline.strftime('%Y-%m-%d'),
            "location": d.location,     
            "salary": d.salary          
        })
    return jsonify(out)

@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
@jwt_required()
def submit_application(drive_id):
    if not check_student_role(): 
        return jsonify({"msg": "Unauthorized"}), 403
        
    my_user_id = get_jwt_identity()
    
    # check if student already applied to this exact drive
    already_applied = Application.query.filter_by(student_id=my_user_id, drive_id=drive_id).first()
    if already_applied is not None:
        return jsonify({"msg": "You already applied here."}), 400
        
    new_app = Application(student_id=my_user_id, drive_id=drive_id)
    db.session.add(new_app)
    db.session.commit()
    return jsonify({"msg": "Application successful!"})

@student_bp.route('/applications', methods=['GET'])
@jwt_required()
def view_my_history():
    if not check_student_role(): 
        return jsonify({"msg": "Unauthorized"}), 403
        
    my_user_id = get_jwt_identity()
    my_apps = Application.query.filter_by(student_id=my_user_id).all()
    
    res = []
    for app in my_apps:
        res.append({
            "id": app.id, 
            "drive_title": app.drive_ref.job_title, 
            "company": app.drive_ref.company_ref.company_name, 
            "date": app.application_date.strftime('%Y-%m-%d'), 
            "status": app.status
        })
    return jsonify(res)

@student_bp.route('/export-csv', methods=['POST'])
@jwt_required()
def dummy_csv_export():
    # We will connect Celery here later
    return jsonify({"msg": "Celery export triggered (Placeholder)"}), 200