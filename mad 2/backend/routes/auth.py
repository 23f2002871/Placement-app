from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User, CompanyProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def handle_login():
    req_data = request.get_json()
    username = req_data.get('username')
    password = req_data.get('password')

    found_user = User.query.filter_by(username=username).first()

    # Check if user exists and password matches
    if found_user is None or not found_user.verify_password(password):
        return jsonify({"msg": "Invalid credentials"}), 401
    
    # Check if admin blacklisted them
    if found_user.is_active == False:
        return jsonify({"msg": "This account is blacklisted."}), 403

    # Generate token and include the role
    token = create_access_token(identity=str(found_user.id), additional_claims={"role": found_user.role})
    return jsonify({"access_token": token, "role": found_user.role}), 200

@auth_bp.route('/register/student', methods=['POST'])
def register_new_student():
    req_data = request.get_json()
    
    # check if username is taken
    existing_user = User.query.filter_by(username=req_data.get('username')).first()
    if existing_user is not None:
        return jsonify({"msg": "Username is already taken"}), 400
    
    new_user = User(
        username=req_data.get('username'), 
        email=req_data.get('email'), 
        role='student'
    )
    new_user.hash_password(req_data.get('password'))
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "Student created successfully"}), 201

@auth_bp.route('/register/company', methods=['POST'])
def register_new_company():
    req_data = request.get_json()
    
    # check if username is taken
    existing_user = User.query.filter_by(username=req_data.get('username')).first()
    if existing_user is not None:
        return jsonify({"msg": "Username is already taken"}), 400
    
    # 1. Create the base user
    new_user = User(
        username=req_data.get('username'), 
        email=req_data.get('email'), 
        role='company'
    )
    new_user.hash_password(req_data.get('password'))
    db.session.add(new_user)
    db.session.flush() # get the user ID before committing
    
    # 2. Create the company profile linked to the user
    new_profile = CompanyProfile(
        user_id=new_user.id, 
        company_name=req_data.get('company_name'), 
        hr_contact=req_data.get('hr_contact')
    )
    db.session.add(new_profile)
    db.session.commit()
    
    return jsonify({"msg": "Company registered. Wait for admin approval."}), 201