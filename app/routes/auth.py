from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import db
from app.models import User, UserPoints
from app.utils.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.dashboard')
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    
    # Simple HTML response as fallback
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>StudyFlow - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .glass-card {{ background: rgba(255,255,255,0.25); backdrop-filter: blur(15px); border-radius: 20px; }}
    </style>
</head>
<body>
    <div class="container vh-100 d-flex align-items-center">
        <div class="row justify-content-center w-100">
            <div class="col-md-6">
                <div class="glass-card p-5">
                    <h2 class="text-white text-center mb-4">
                        <i class="bi bi-mortarboard-fill me-2"></i>StudyFlow Login
                    </h2>
                    <form method="POST">
                        {form.hidden_tag()}
                        <div class="mb-3">
                            {form.username.label(class_="form-label text-white")}
                            {form.username(class_="form-control", placeholder="Username")}
                        </div>
                        <div class="mb-3">
                            {form.password.label(class_="form-label text-white")}
                            {form.password(class_="form-control", placeholder="Password")}
                        </div>
                        <div class="mb-3">
                            {form.remember_me(class_="form-check-input")}
                            {form.remember_me.label(class_="form-check-label text-white")}
                        </div>
                        <div class="d-grid mb-3">
                            {form.submit(class_="btn btn-primary btn-lg")}
                        </div>
                    </form>
                    <div class="text-center">
                        <a href="{url_for('auth.register')}" class="btn btn-outline-light">Create Account</a>
                    </div>
                    <div class="mt-4 p-3 bg-info bg-opacity-25 rounded text-white text-center">
                        <small>Demo: username=<code>demo</code>, password=<code>demo123</code></small><br>
                        <button class="btn btn-sm btn-success mt-2" onclick="document.querySelector('[name=username]').value='demo'; document.querySelector('[name=password]').value='demo123';">Use Demo</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Create user points record
            user_points = UserPoints(user_id=user.id)
            db.session.add(user_points)
            db.session.commit()
            
            flash('🎉 Welcome to StudyFlow! Your account has been created successfully.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
    
    # Simple HTML response as fallback
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>StudyFlow - Register</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        body {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); min-height: 100vh; }}
        .glass-card {{ background: rgba(255,255,255,0.25); backdrop-filter: blur(15px); border-radius: 20px; }}
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="glass-card p-5">
                    <h2 class="text-white text-center mb-4">
                        <i class="bi bi-person-plus-fill me-2"></i>Join StudyFlow
                    </h2>
                    <form method="POST">
                        {form.hidden_tag()}
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                {form.first_name.label(class_="form-label text-white")}
                                {form.first_name(class_="form-control")}
                            </div>
                            <div class="col-md-6 mb-3">
                                {form.last_name.label(class_="form-label text-white")}
                                {form.last_name(class_="form-control")}
                            </div>
                        </div>
                        <div class="mb-3">
                            {form.username.label(class_="form-label text-white")}
                            {form.username(class_="form-control")}
                        </div>
                        <div class="mb-3">
                            {form.email.label(class_="form-label text-white")}
                            {form.email(class_="form-control")}
                        </div>
                        <div class="mb-3">
                            {form.password.label(class_="form-label text-white")}
                            {form.password(class_="form-control")}
                        </div>
                        <div class="mb-3">
                            {form.password2.label(class_="form-label text-white")}
                            {form.password2(class_="form-control")}
                        </div>
                        <div class="d-grid mb-3">
                            {form.submit(class_="btn btn-success btn-lg")}
                        </div>
                    </form>
                    <div class="text-center">
                        <a href="{url_for('auth.login')}" class="btn btn-outline-light">Already have an account?</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out successfully. See you soon!', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', title='Profile', user=current_user)