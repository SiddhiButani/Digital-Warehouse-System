from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps
from models.user import User

auth_bp = Blueprint('auth', __name__)

def login_required(roles=None):
    """
    Decorator to restrict route access to authenticated users.
    Optionally restricts access to specific roles (e.g. ['Admin', 'Manager']).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to access this page.", "error")
                return redirect(url_for('auth.login'))
            
            if roles:
                user_role = session.get('user_role')
                # Normalize roles as list
                allowed_roles = [roles] if isinstance(roles, str) else roles
                if user_role not in allowed_roles:
                    flash("Access Denied: You do not have permissions for this page.", "error")
                    return redirect(url_for('dashboard.index'))
                    
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.verify_login(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("Invalid username or password.", "error")
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('auth.login'))
