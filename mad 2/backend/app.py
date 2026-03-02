from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from models import db, User
from config import Config

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.company import company_bp
from routes.student import student_bp

def build_app():
    # configure static and template folders for vue
    app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/static')
    app.config.from_object(Config)
    
    db.init_app(app)
    JWTManager(app)

    # create tables and initial admin
    with app.app_context():
        db.create_all()
        admin_exists = User.query.filter_by(role='admin').first()
        if admin_exists is None:
            admin_user = User(username='admin', email='admin@institute.edu', role='admin')
            admin_user.hash_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Created default admin account.")

    # connect the route files
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    # main route to serve the html file
    @app.route('/')
    def serve_frontend(): 
        return render_template('index.html')

    return app

if __name__ == '__main__':
    my_app = build_app()
    my_app.run(debug=True)