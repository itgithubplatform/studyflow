from datetime import datetime, date
from app import db

class StudySession(db.Model):
    """Study session model for tracking study time and productivity"""
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    
    # Session details
    session_type = db.Column(db.String(50), default='regular')  # regular, pomodoro, intensive, review
    focus_rating = db.Column(db.Integer, default=5)  # 1-10 scale for productivity
    notes = db.Column(db.Text)
    
    # Pomodoro specific
    pomodoro_cycles = db.Column(db.Integer, default=0)
    breaks_taken = db.Column(db.Integer, default=0)
    
    # Timestamps
    date = db.Column(db.Date, nullable=False, default=date.today)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Optional task association
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    task = db.relationship('Task', backref='study_sessions')
    
    # Gamification
    points_earned = db.Column(db.Integer, default=0)
    
    def calculate_points(self):
        """Calculate points based on session duration and focus"""
        base_points = self.duration // 15  # 1 point per 15 minutes
        focus_bonus = (self.focus_rating - 5) * 2  # Bonus/penalty based on focus
        self.points_earned = max(0, base_points + focus_bonus)
        
        # Add points to user
        from app.models.gamification import UserPoints
        user_points = UserPoints.query.filter_by(user_id=self.user_id).first()
        if not user_points:
            user_points = UserPoints(user_id=self.user_id, total_points=0)
            db.session.add(user_points)
        
        user_points.total_points += self.points_earned
        user_points.study_minutes += self.duration
    
    @property
    def duration_hours(self):
        """Get duration in hours"""
        return round(self.duration / 60, 2)
    
    @property
    def productivity_level(self):
        """Get productivity level based on focus rating"""
        if self.focus_rating >= 8:
            return 'Excellent'
        elif self.focus_rating >= 6:
            return 'Good'
        elif self.focus_rating >= 4:
            return 'Average'
        else:
            return 'Poor'
    
    @property
    def session_color(self):
        """Get color class for session type"""
        colors = {
            'regular': 'primary',
            'pomodoro': 'success',
            'intensive': 'warning',
            'review': 'info'
        }
        return colors.get(self.session_type, 'secondary')
    
    def to_dict(self):
        """Convert session to dictionary for API responses"""
        return {
            'id': self.id,
            'subject': self.subject,
            'duration': self.duration,
            'duration_hours': self.duration_hours,
            'session_type': self.session_type,
            'focus_rating': self.focus_rating,
            'notes': self.notes,
            'pomodoro_cycles': self.pomodoro_cycles,
            'breaks_taken': self.breaks_taken,
            'date': self.date.isoformat(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'created_at': self.created_at.isoformat(),
            'task_id': self.task_id,
            'points_earned': self.points_earned,
            'productivity_level': self.productivity_level
        }
    
    def __repr__(self):
        return f'<StudySession {self.subject} - {self.duration}min>'