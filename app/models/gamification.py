from datetime import datetime
from app import db

class UserPoints(db.Model):
    """User points and statistics for gamification"""
    __tablename__ = 'user_points'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Points and stats
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    tasks_completed = db.Column(db.Integer, default=0)
    study_minutes = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=0)
    
    # Achievements
    achievements_unlocked = db.Column(db.Integer, default=0)
    
    # Timestamps
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_level(self):
        """Calculate user level based on points"""
        # Level up every 1000 points
        new_level = (self.total_points // 1000) + 1
        if new_level > self.level:
            self.level = new_level
            return True  # Level up occurred
        return False
    
    @property
    def points_to_next_level(self):
        """Points needed for next level"""
        next_level_points = self.level * 1000
        return next_level_points - self.total_points
    
    @property
    def progress_percentage(self):
        """Progress percentage to next level"""
        current_level_points = (self.level - 1) * 1000
        next_level_points = self.level * 1000
        progress = self.total_points - current_level_points
        total_needed = next_level_points - current_level_points
        return min(100, (progress / total_needed) * 100)
    
    @property
    def study_hours(self):
        """Total study hours"""
        return round(self.study_minutes / 60, 1)
    
    @property
    def rank_title(self):
        """Get rank title based on level"""
        if self.level >= 50:
            return "Study Master"
        elif self.level >= 30:
            return "Academic Expert"
        elif self.level >= 20:
            return "Knowledge Seeker"
        elif self.level >= 10:
            return "Dedicated Student"
        elif self.level >= 5:
            return "Rising Scholar"
        else:
            return "Beginner"
    
    def __repr__(self):
        return f'<UserPoints {self.user_id}: {self.total_points} points>'

class Achievement(db.Model):
    """Achievement system for gamification"""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='🏆')
    points_reward = db.Column(db.Integer, default=100)
    
    # Achievement criteria
    criteria_type = db.Column(db.String(50), nullable=False)  # tasks_completed, study_hours, streak_days, etc.
    criteria_value = db.Column(db.Integer, nullable=False)
    
    # Achievement properties
    is_active = db.Column(db.Boolean, default=True)
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def rarity_color(self):
        """Get color for achievement rarity"""
        colors = {
            'common': 'secondary',
            'rare': 'primary',
            'epic': 'warning',
            'legendary': 'danger'
        }
        return colors.get(self.rarity, 'secondary')
    
    def __repr__(self):
        return f'<Achievement {self.name}>'

class UserAchievement(db.Model):
    """Junction table for user achievements"""
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='user_achievements')
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id'),)
    
    def __repr__(self):
        return f'<UserAchievement {self.user_id}:{self.achievement_id}>'