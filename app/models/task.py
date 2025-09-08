from datetime import datetime, date
from app import db

class Task(db.Model):
    """Task model for managing student assignments and todos"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(100), nullable=False)
    
    # Task properties
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, in_progress, completed, overdue
    difficulty = db.Column(db.Integer, default=3)  # 1-5 scale
    estimated_hours = db.Column(db.Float, default=1.0)
    
    # Dates
    due_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Task categories for better organization
    category = db.Column(db.String(50), default='assignment')  # assignment, project, exam, reading, other
    
    # Gamification
    points_awarded = db.Column(db.Integer, default=0)
    
    def mark_completed(self):
        """Mark task as completed and award points"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Award points based on priority and difficulty
        points_map = {'low': 10, 'medium': 20, 'high': 30, 'urgent': 50}
        base_points = points_map.get(self.priority, 20)
        self.points_awarded = base_points + (self.difficulty * 5)
        
        # Add points to user
        from app.models.gamification import UserPoints
        user_points = UserPoints.query.filter_by(user_id=self.user_id).first()
        if not user_points:
            user_points = UserPoints(user_id=self.user_id, total_points=0)
            db.session.add(user_points)
        
        user_points.total_points += self.points_awarded
        user_points.tasks_completed += 1
    
    def is_overdue(self):
        """Check if task is overdue"""
        return self.due_date < date.today() and self.status != 'completed'
    
    def days_until_due(self):
        """Get days until due date"""
        delta = self.due_date - date.today()
        return delta.days
    
    @property
    def priority_color(self):
        """Get color class for priority"""
        colors = {
            'low': 'success',
            'medium': 'warning', 
            'high': 'danger',
            'urgent': 'dark'
        }
        return colors.get(self.priority, 'secondary')
    
    @property
    def status_color(self):
        """Get color class for status"""
        colors = {
            'pending': 'secondary',
            'in_progress': 'primary',
            'completed': 'success',
            'overdue': 'danger'
        }
        return colors.get(self.status, 'secondary')
    
    def to_dict(self):
        """Convert task to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'subject': self.subject,
            'priority': self.priority,
            'status': self.status,
            'difficulty': self.difficulty,
            'estimated_hours': self.estimated_hours,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'category': self.category,
            'points_awarded': self.points_awarded,
            'is_overdue': self.is_overdue(),
            'days_until_due': self.days_until_due()
        }
    
    def __repr__(self):
        return f'<Task {self.title}>'