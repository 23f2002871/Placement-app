import csv
import os
from datetime import datetime, timedelta
from celery.schedules import crontab
from celery_setup import celery
from models import db, Application, PlacementDrive, User
from app import build_app

# We need the Flask app context so our background jobs can talk to the database
flask_app = build_app()

# ---- 1. SCHEDULED JOBS CONFIGURATION ----
celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'tasks.daily_reminder_job',
        'schedule': crontab(hour=9, minute=0), # Every day at 9:00 AM
    },
    'send-monthly-report': {
        'task': 'tasks.monthly_admin_report_job',
        'schedule': crontab(day_of_month='1', hour=8, minute=0), # 1st of every month at 8 AM
    }
}

# ---- 2. ASYNC JOB: EXPORT CSV ----
@celery.task
def generate_csv_for_student(student_id, email):
    with flask_app.app_context():
        my_apps = Application.query.filter_by(student_id=student_id).all()
        
        # Making a folder called 'exports' if it doesn't exist
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
                
        print(f"--> [ASYNC JOB] CSV generated! Mock Alert Sent to: {email}")
        return file_path

# ---- 3. SCHEDULED JOB: DAILY REMINDERS ----
@celery.task
def daily_reminder_job():
    with flask_app.app_context():
        print("--> [CRON JOB] Checking for upcoming deadlines...")
        
        # Finding drives closing tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        closing_soon = PlacementDrive.query.filter(
            PlacementDrive.status == 'Approved',
            db.func.date(PlacementDrive.application_deadline) == tomorrow.date()
        ).all()
        
        if len(closing_soon) == 0:
            print("No deadlines tomorrow.")
            return "Done"
            
        students = User.query.filter_by(role='student').all()
        
        for drive in closing_soon:
            for s in students:
                # Checking if they already applied
                applied = Application.query.filter_by(student_id=s.id, drive_id=drive.id).first()
                if applied is None:
                    print(f"--> [G-CHAT MOCK] Reminder to {s.email}: {drive.job_title} at {drive.company_ref.company_name} closes tomorrow!")
                    
        return "Reminders sent"

# ---- 4. SCHEDULED JOB: MONTHLY REPORT ----
@celery.task
def monthly_admin_report_job():
    with flask_app.app_context():
        print("--> [CRON JOB] Generating Monthly Admin Report...")
        
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
        
        print(f"--> [EMAIL MOCK] Sending HTML Report to Admin...\n{html_content}")
        return "Report generated"