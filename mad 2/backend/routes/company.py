from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from datetime import datetime
from models import db, CompanyProfile, PlacementDrive, Application, StudentProfile

company_bp = Blueprint('company_bp', __name__)

def check_company_status():
    if get_jwt().get('role') != 'company': 
        return None, "Not a company account"
    user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=user_id).first()
    if profile.is_approved == False: 
        return None, "Profile not yet approved by admin"
    return profile, None

@company_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_info():
    profile, err = check_company_status()
    if err: return jsonify({"msg": err}), 403
    return jsonify({"company_name": profile.company_name})

@company_bp.route('/drives', methods=['POST', 'GET'])
@jwt_required()
def manage_drives():
    profile, err = check_company_status()
    if err: return jsonify({"msg": err}), 403

    if request.method == 'POST':
        req_data = request.get_json()
        deadline_date = datetime.strptime(req_data.get('deadline'), '%Y-%m-%d')
        new_drive = PlacementDrive(
            company_id=profile.id,
            job_title=req_data.get('job_title'),
            job_description=req_data.get('job_description'),
            eligibility_criteria=req_data.get('eligibility_criteria'),
            location=req_data.get('location'),
            salary=float(req_data.get('salary')),
            application_deadline=deadline_date
        )
        db.session.add(new_drive)
        db.session.commit()
        return jsonify({"msg": "Drive created and sent to Admin for approval"}), 201

    elif request.method == 'GET':
        my_drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
        return jsonify([{
            "id": d.id, "title": d.job_title, "status": d.status,
            "description": d.job_description, "eligibility": d.eligibility_criteria,
            "salary": d.salary, "location": d.location,
            "deadline": d.application_deadline.strftime('%Y-%m-%d')
        } for d in my_drives])

@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@jwt_required()
def get_drive_apps(drive_id):
    profile, err = check_company_status()
    if err: return jsonify({"msg": err}), 403
    
    apps = Application.query.filter_by(drive_id=drive_id).all()
    result = []
    for a in apps:
        prof = StudentProfile.query.filter_by(user_id=a.student_id).first()
        result.append({
            "app_id": a.id,
            "student_name": a.student_ref.username,
            "status": a.status,
            "department": prof.department if prof else "N/A",
            "cgpa": prof.cgpa if prof else "N/A",
            "resume_path": prof.resume_path if prof else None
        })
    return jsonify(result)

@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@jwt_required()
def change_app_status(app_id):
    profile, err = check_company_status()
    if err: return jsonify({"msg": err}), 403
    app_record = Application.query.get(app_id)
    if app_record:
        req_data = request.get_json()
        app_record.status = req_data.get('status')
        db.session.commit()
        return jsonify({"msg": "Status updated successfully"})
    return jsonify({"msg": "Application not found"}), 404

@company_bp.route('/drives/<int:drive_id>/close', methods=['PUT'])
@jwt_required()
def close_drive(drive_id):
    profile, err = check_company_status()
    if err: return jsonify({"msg": err}), 403
    drive_record = PlacementDrive.query.get(drive_id)
    if drive_record and drive_record.company_id == profile.id:
        drive_record.status = 'Closed'
        db.session.commit()
        return jsonify({"msg": "Drive marked as complete"})
    return jsonify({"msg": "Drive not found"}), 404