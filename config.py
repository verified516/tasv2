
import os

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'your-secret-key')
    
    # Use DATABASE_URL if available, otherwise construct from individual credentials
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        db_user = os.environ.get('PGUSER')
        db_pass = os.environ.get('PGPASSWORD')
        db_host = os.environ.get('PGHOST')
        db_port = os.environ.get('PGPORT')
        db_name = os.environ.get('PGDATABASE')
        DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
