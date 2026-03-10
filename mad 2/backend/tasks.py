import csv
import os
from datetime import datetime, timedelta
from celery.schedules import crontab
from celery_setup import celery
from models import db, Application, PlacementDrive, User
from app import build_app

#  Import Mail  
from flask_mail import Message
from extensions import mail

#  Flask app 
flask_app = build_app()

#  SCHEDULED JOBS 
celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'tasks.daily_reminder_job',
        'schedule': crontab(hour=9, minute=0), 
    },
    'send-monthly-report': {
        'task': 'tasks.monthly_admin_report_job',
        'schedule': crontab(day_of_month='1', hour=8, minute=0), 
    }
}

#  EXPORT CSV 
@celery.task
def generate_csv_for_student(student_id, email):
    with flask_app.app_context():
        my_apps = Application.query.filter_by(student_id=student_id).all()
        
        if not os.path.exists('exports'):
            os.makedirs('exports')
            
        file_path = f"exports/student_{student_id}_data.csv"
        
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Drive Title', 'Company', 'Date Applied', 'Status'])
            
            for a in my_apps:
                writer.writerow([
                    a.drive_ref.job_title, 
                    a.drive_ref.company_ref.company_name, 
                    a.application_date.strftime('%Y-%m-%d'), 
                    a.status
                ])
                
        #  Actually sending the email to MailHog
        msg = Message("Your Application History Export", recipients=[email])
        msg.body = "Hello! Your requested CSV export of your application history is complete. Please find the file on the server."
        mail.send(msg)
        
        return file_path

#  DAILY REMINDERS 
@celery.task
def daily_reminder_job():
    with flask_app.app_context():
        tomorrow = datetime.now() + timedelta(days=1)
        closing_soon = PlacementDrive.query.filter(
            PlacementDrive.status == 'Approved',
            db.func.date(PlacementDrive.application_deadline) == tomorrow.date()
        ).all()
        
        if len(closing_soon) == 0:
            return "No deadlines tomorrow."
            
        students = User.query.filter_by(role='student').all()
        
        for drive in closing_soon:
            for s in students:
                applied = Application.query.filter_by(student_id=s.id, drive_id=drive.id).first()
                if applied is None:
                    #  Send reminder email to MailHog 
                    msg = Message(f"URGENT: {drive.company_ref.company_name} Deadline Tomorrow!", recipients=[s.email])
                    msg.body = f"Hello {s.username},\n\nDon't forget! The application deadline for '{drive.job_title}' at {drive.company_ref.company_name} closes tomorrow. Log in to apply now."
                    mail.send(msg)
                    
        return "Reminders sent"

#  MONTHLY REPORT 
@celery.task
def monthly_admin_report_job():
    with flask_app.app_context():
        total_drives = PlacementDrive.query.count()
        total_apps = Application.query.count()
        selected_students = Application.query.filter_by(status='Selected').count()
        
        html_content = f"""
        <html>
            <body>
                <h2>Monthly Placement Cell Activity Report</h2>
                <p>Summary of platform activity for this month:</p>
                <ul>
                    <li>Total Placement Drives Created: <b>{total_drives}</b></li>
                    <li>Total Applications Submitted: <b>{total_apps}</b></li>
                    <li>Total Students Selected: <b>{selected_students}</b></li>
                </ul>
            </body>
        </html>
        """
        
        #  Send HTML email to MailHog 
        admin_user = User.query.filter_by(role='admin').first()
        msg = Message("Monthly Placement Report", recipients=[admin_user.email])
        msg.html = html_content  
        mail.send(msg)
        
        return "Report generated"