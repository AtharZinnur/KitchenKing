"""
Configuration settings for Pic2Kitchen
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://recipe_g7ns_user:SHyD20kiT09R7bei9wVH6Fk5ydB0fHNl@dpg-d1lbcdp5pdvs73bpegq0-a.singapore-postgres.render.com/recipe_g7ns'
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/images/upload'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # YouTube API configuration
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY') or 'AIzaSyAASxTSqfFFIHF0hzyGMEDWsVSskLyyMgo'
    
    # Learning system configuration
    PREFERENCE_LEARNING_RATE = 0.1  # How quickly preferences adapt
    MIN_INTERACTIONS_FOR_PREFERENCE = 3  # Minimum interactions before considering preference
    
    # Recipe recommendation settings
    DEFAULT_RECIPE_COUNT = 7
    MAX_RECIPE_COUNT = 20

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Use environment variable for database in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        # Fix for SQLAlchemy requiring postgresql:// instead of postgres://
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}