import os

class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'warehouse-super-secret-key-12345'
    
    # Database configuration
    DB_PATH = os.path.join(BASE_DIR, 'database', 'warehouse.db')
    
    # Upload and generated assets directories
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    QRCODE_FOLDER = os.path.join(BASE_DIR, 'static', 'qrcodes')
    
    # Export reports directories
    REPORTS_PDF_DIR = os.path.join(BASE_DIR, 'reports', 'pdf')
    REPORTS_EXCEL_DIR = os.path.join(BASE_DIR, 'reports', 'excel')
    
    # Low stock threshold
    LOW_STOCK_THRESHOLD = 10
    
    # Allowed image file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    @classmethod
    def init_app(cls):
        # Create necessary directories if they don't exist
        for path in [cls.UPLOAD_FOLDER, cls.QRCODE_FOLDER, cls.REPORTS_PDF_DIR, cls.REPORTS_EXCEL_DIR, os.path.join(cls.BASE_DIR, 'database')]:
            os.makedirs(path, exist_ok=True)
