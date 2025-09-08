from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    """User model with authentication and profile features"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Profile fields
    avatar_url = db.Column(db.String(200), default='https://via.placeholder.com/150')
    bio = db.Column(db.Text)
    study_goal_hours = db.Column(db.Integer, default=2)  # Daily study goal in hours
    
    # Account settings
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    study_sessions = db.relationship('StudySession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    points = db.relationship('UserPoints', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_total_points(self):
        """Get user's total points"""
        return self.points.total_points if self.points else 0
    
    def get_completed_tasks_today(self):
        """Get count of tasks completed today"""
        from datetime import date
        from app.models.task import Task
        return self.tasks.filter(
            Task.status == 'completed',
            db.func.date(Task.updated_at) == date.today()
        ).count()
    
    def get_study_hours_today(self):
        """Get total study hours for today"""
        from datetime import date
        sessions = self.study_sessions.filter(
            db.func.date(StudySession.date) == date.today()
        ).all()
        return sum(session.duration for session in sessions) / 60  # Convert minutes to hours
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))