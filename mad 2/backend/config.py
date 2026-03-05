import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'my_secret_key_for_flask'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'placement.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'my_secret_key_for_jwt_tokens'
    
    # Celery & Redis Configuration
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    
    # Caching Configuration
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = 'redis://localhost:6379/1' # Using database 1 for cache
    CACHE_DEFAULT_TIMEOUT = 300 # 5 minutes