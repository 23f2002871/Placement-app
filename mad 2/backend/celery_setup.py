from celery import Celery


celery = Celery(
    'placement_tasks', 
    broker='redis://localhost:6379/0', 
    backend='redis://localhost:6379/0'
)

celery.conf.timezone = 'Asia/Kolkata'