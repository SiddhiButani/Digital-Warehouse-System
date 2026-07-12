from flask import Flask, redirect, url_for, session
import os
from config import Config
from database.db import get_db_connection, init_db

# Import Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.products import products_bp
from routes.inventory import inventory_bp
from routes.supplier import supplier_bp
from routes.analytics import analytics_bp
from routes.reports import reports_bp

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize upload/QR directories and DB if not exists
    Config.init_app()
    
    # Check if database exists, if not initialize and seed it
    if not os.path.exists(Config.DB_PATH):
        init_db()

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(supplier_bp, url_prefix='/suppliers')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Base route handler
    @app.route('/home')
    def home_redirect():
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    import os
    app = create_app()
    print("-------------------------------------------------------")
    print(" Digital Warehouse Management System (Flask Server)    ")
    print(" Host address: http://127.0.0.1:5000                   ")
    print("-------------------------------------------------------")
    app.run(debug=True, host='127.0.0.1', port=5000)
