#!/usr/bin/env python3
"""
StudyFlow - Smart Student Productivity Tracker
A comprehensive Flask-based web application for student task management,
study tracking, and productivity analytics with gamification features.

Author: StudyFlow Team
Version: 1.0.0
"""

import os
from datetime import datetime
from flask import Flask
from flask_migrate import upgrade
from app import create_app, db
from app.models import User, Task, StudySession, UserPoints, Achievement

# Create Flask application
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Task': Task,
        'StudySession': StudySession,
        'UserPoints': UserPoints,
        'Achievement': Achievement
    }

@app.cli.command()
def deploy():
    """Run deployment tasks"""
    # Create database tables
    db.create_all()
    
    # Create default achievements
    create_default_achievements()
    
    # Create demo user if in development
    if app.config.get('FLASK_ENV') == 'development':
        create_demo_user()
    
    print("Deployment completed successfully!")

def create_default_achievements():
    """Create default achievements for gamification"""
    achievements = [
        {
            'name': 'First Steps',
            'description': 'Complete your first task',
            'icon': '🎯',
            'criteria_type': 'tasks_completed',
            'criteria_value': 1,
            'points_reward': 50,
            'rarity': 'common'
        },
        {
            'name': 'Getting Started',
            'description': 'Complete 10 tasks',
            'icon': '📚',
            'criteria_type': 'tasks_completed',
            'criteria_value': 10,
            'points_reward': 100,
            'rarity': 'common'
        },
        {
            'name': 'Task Master',
            'description': 'Complete 50 tasks',
            'icon': '🏆',
            'criteria_type': 'tasks_completed',
            'criteria_value': 50,
            'points_reward': 250,
            'rarity': 'rare'
        },
        {
            'name': 'Study Warrior',
            'description': 'Study for 100 hours total',
            'icon': '⚔️',
            'criteria_type': 'study_hours',
            'criteria_value': 100,
            'points_reward': 500,
            'rarity': 'epic'
        },
        {
            'name': 'Consistency King',
            'description': 'Maintain a 7-day study streak',
            'icon': '👑',
            'criteria_type': 'streak_days',
            'criteria_value': 7,
            'points_reward': 200,
            'rarity': 'rare'
        },
        {
            'name': 'Pomodoro Pro',
            'description': 'Complete 100 Pomodoro sessions',
            'icon': '🍅',
            'criteria_type': 'pomodoro_sessions',
            'criteria_value': 100,
            'points_reward': 300,
            'rarity': 'epic'
        },
        {
            'name': 'Early Bird',
            'description': 'Complete a task before 8 AM',
            'icon': '🐦',
            'criteria_type': 'early_completion',
            'criteria_value': 1,
            'points_reward': 75,
            'rarity': 'common'
        },
        {
            'name': 'Night Owl',
            'description': 'Study after 10 PM',
            'icon': '🦉',
            'criteria_type': 'late_study',
            'criteria_value': 1,
            'points_reward': 75,
            'rarity': 'common'
        },
        {
            'name': 'Perfect Week',
            'description': 'Complete all tasks for a week',
            'icon': '💯',
            'criteria_type': 'perfect_week',
            'criteria_value': 1,
            'points_reward': 400,
            'rarity': 'epic'
        },
        {
            'name': 'Study Legend',
            'description': 'Reach Level 25',
            'icon': '🌟',
            'criteria_type': 'level_reached',
            'criteria_value': 25,
            'points_reward': 1000,
            'rarity': 'legendary'
        }
    ]
    
    for achievement_data in achievements:
        existing = Achievement.query.filter_by(name=achievement_data['name']).first()
        if not existing:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
    
    db.session.commit()
    print("Default achievements created!")

def create_demo_user():
    """Create a demo user for testing"""
    demo_user = User.query.filter_by(username='demo').first()
    if not demo_user:
        demo_user = User(
            username='demo',
            email='demo@studyflow.com',
            first_name='Demo',
            last_name='User'
        )
        demo_user.set_password('demo123')
        db.session.add(demo_user)
        db.session.commit()
        
        # Create user points
        user_points = UserPoints(user_id=demo_user.id, total_points=150)
        db.session.add(user_points)
        
        # Create sample tasks
        sample_tasks = [
            {
                'title': 'Complete Math Assignment',
                'description': 'Solve problems 1-20 from Chapter 5',
                'subject': 'Mathematics',
                'priority': 'high',
                'due_date': datetime.now().date(),
                'category': 'assignment',
                'difficulty': 4
            },
            {
                'title': 'Read History Chapter',
                'description': 'Read Chapter 12: World War II',
                'subject': 'History',
                'priority': 'medium',
                'due_date': datetime.now().date(),
                'category': 'reading',
                'difficulty': 2
            },
            {
                'title': 'Science Lab Report',
                'description': 'Write lab report for chemistry experiment',
                'subject': 'Chemistry',
                'priority': 'urgent',
                'due_date': datetime.now().date(),
                'category': 'project',
                'difficulty': 5
            }
        ]
        
        for task_data in sample_tasks:
            task = Task(user_id=demo_user.id, **task_data)
            db.session.add(task)
        
        # Create sample study session
        study_session = StudySession(
            user_id=demo_user.id,
            subject='Mathematics',
            duration=45,
            session_type='pomodoro',
            focus_rating=8,
            notes='Completed algebra problems, feeling confident'
        )
        db.session.add(study_session)
        
        db.session.commit()
        print("Demo user created with sample data!")

# Remove deprecated before_first_request - tables created in deploy command

if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Starting StudyFlow Application...")
    print(f"📊 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🌐 Port: {port}")
    print(f"🔧 Debug: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)