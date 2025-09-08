#!/usr/bin/env python3
"""
StudyFlow Application Runner
Quick start script for development and production
"""

import os
import sys
from app import create_app, db
from app.models import User, Task, StudySession, UserPoints, Achievement

def setup_database():
    """Initialize database and create demo data"""
    print("🔧 Setting up database...")
    
    # Create all tables
    db.create_all()
    
    # Create demo user if it doesn't exist
    demo_user = User.query.filter_by(username='demo').first()
    if not demo_user:
        print("👤 Creating demo user...")
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
        db.session.commit()
        
        print("✅ Demo user created successfully!")
        print("   Username: demo")
        print("   Password: demo123")
    
    print("✅ Database setup complete!")

def create_achievements():
    """Create default achievements"""
    achievements = [
        {
            'name': 'First Steps',
            'description': 'Complete your first task',
            'icon': '🎯',
            'criteria_type': 'tasks_completed',
            'criteria_value': 1,
            'points_reward': 50,
            'rarity': 'common',
            'is_active': True
        },
        {
            'name': 'Getting Started',
            'description': 'Complete 10 tasks',
            'icon': '📚',
            'criteria_type': 'tasks_completed',
            'criteria_value': 10,
            'points_reward': 100,
            'rarity': 'common',
            'is_active': True
        },
        {
            'name': 'Study Warrior',
            'description': 'Study for 100 hours total',
            'icon': '⚔️',
            'criteria_type': 'study_hours',
            'criteria_value': 100,
            'points_reward': 500,
            'rarity': 'epic',
            'is_active': True
        }
    ]
    
    for achievement_data in achievements:
        existing = Achievement.query.filter_by(name=achievement_data['name']).first()
        if not existing:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
    
    db.session.commit()

def main():
    """Main application runner"""
    print("🚀 Starting StudyFlow Application...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Setup database
            setup_database()
            create_achievements()
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            print("Please check your database configuration and try again.")
            sys.exit(1)
    
    # Get configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Server starting on http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print("=" * 50)
    print("📝 Demo Account:")
    print("   Username: demo")
    print("   Password: demo123")
    print("=" * 50)
    print("🎯 Ready! Open your browser and navigate to the URL above")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    try:
        # Run the application
        app.run(host='0.0.0.0', port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 StudyFlow stopped. Thanks for using our app!")
        sys.exit(0)

if __name__ == '__main__':
    main()