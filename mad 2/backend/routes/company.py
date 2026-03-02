from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, CompanyProfile, PlacementDrive, Application
from datetime import datetime

company_bp = Blueprint('company', __name__)

# Helper to verify company
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
def fetch_company_name():
    profile, error_msg = check_company_status()
    if error_msg is not None:
        return jsonify({"msg": error_msg}), 403
    return jsonify({"company_name": profile.company_name})

@company_bp.route('/drives', methods=['POST', 'GET'])
@jwt_required()
def manage_drives():
    profile, error_msg = check_company_status()
    if error_msg is not None:
        return jsonify({"msg": error_msg}), 403

    if request.method == 'POST':
        req_data = request.get_json()
        
        # parse the date string
        formatted_date = datetime.strptime(req_data.get('deadline'), '%Y-%m-%d')
        
        new_drive_obj = PlacementDrive(
            company_id=profile.id,
            job_title=req_data.get('job_title'),
            job_description=req_data.get('job_description'),
            eligibility_criteria=req_data.get('eligibility_criteria'),
            location=req_data.get('location'),
            salary=req_data.get('salary'),
            application_deadline=formatted_date
        )
        db.session.add(new_drive_obj)
        db.session.commit()
        return jsonify({"msg": "Drive sent to admin for approval."}), 201
        
    elif request.method == 'GET':
        my_drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
        result = []
        for d in my_drives:
            result.append({
                "id": d.id, 
                "title": d.job_title, 
                "deadline": d.application_deadline.strftime('%Y-%m-%d'), 
                "status": d.status
            })
        return jsonify(result)

@company_bp.route('/drives/<int:drive_id>/close', methods=['PUT'])
@jwt_required()
def mark_drive_complete(drive_id):
    profile, error_msg = check_company_status()
    if error_msg is not None:
        return jsonify({"msg": error_msg}), 403
        
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=profile.id).first()
    if drive is not None:
        drive.status = 'Closed'
        db.session.commit()
        return jsonify({"msg": "Marked as closed"})
    return jsonify({"msg": "Drive not found"}), 404

@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@jwt_required()
def fetch_drive_applications(drive_id):
    profile, error_msg = check_company_status()
    if error_msg is not None:
        return jsonify({"msg": error_msg}), 403
        
    student_apps = Application.query.filter_by(drive_id=drive_id).all()
    res = []
    for app in student_apps:
        res.append({
            "app_id": app.id, 
            "student_name": app.student_ref.username, 
            "date": app.application_date.strftime('%Y-%m-%d'), 
            "status": app.status
        })
    return jsonify(res)

@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@jwt_required()
def change_app_status(app_id):
    profile, error_msg = check_company_status()
    if error_msg is not None:
        return jsonify({"msg": error_msg}), 403
        
    app_record = Application.query.get(app_id)
    if app_record is not None:
        req_data = request.get_json()
        app_record.status = req_data.get('status')
        db.session.commit()
        return jsonify({"msg": "Application updated"})
    return jsonify({"msg": "Not found"}), 404