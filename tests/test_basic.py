"""
Basic tests for StudyFlow application
"""

import unittest
from datetime import date, datetime
from app import create_app, db
from app.models import User, Task, StudySession, UserPoints

class BasicTestCase(unittest.TestCase):
    """Basic test cases for the application"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_app_exists(self):
        """Test that the app exists"""
        self.assertIsNotNone(self.app)
    
    def test_app_is_testing(self):
        """Test that the app is in testing mode"""
        self.assertTrue(self.app.config['TESTING'])
    
    def test_index_page(self):
        """Test the index page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'StudyFlow', response.data)
    
    def test_user_model(self):
        """Test user model creation and methods"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        # Test password checking
        self.assertTrue(user.check_password('testpass'))
        self.assertFalse(user.check_password('wrongpass'))
        
        # Test full name property
        self.assertEqual(user.full_name, 'Test User')
    
    def test_task_model(self):
        """Test task model creation and methods"""
        # Create user first
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create task
        task = Task(
            title='Test Task',
            subject='Mathematics',
            priority='high',
            due_date=date.today(),
            user_id=user.id
        )
        db.session.add(task)
        db.session.commit()
        
        # Test task properties
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.priority_color, 'danger')  # high priority = danger color
        self.assertFalse(task.is_overdue())  # due today, not overdue
    
    def test_study_session_model(self):
        """Test study session model"""
        # Create user first
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create study session
        session = StudySession(
            subject='Mathematics',
            duration=60,  # 60 minutes
            focus_rating=8,
            user_id=user.id
        )
        db.session.add(session)
        db.session.commit()
        
        # Test session properties
        self.assertEqual(session.duration_hours, 1.0)
        self.assertEqual(session.productivity_level, 'Excellent')
    
    def test_user_points_model(self):
        """Test user points and gamification"""
        # Create user
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create user points
        points = UserPoints(
            user_id=user.id,
            total_points=1500,
            tasks_completed=10,
            study_minutes=300
        )
        db.session.add(points)
        db.session.commit()
        
        # Test level calculation
        points.calculate_level()
        self.assertEqual(points.level, 2)  # 1500 points = level 2
        self.assertEqual(points.rank_title, 'Beginner')
        self.assertEqual(points.study_hours, 5.0)  # 300 minutes = 5 hours
    
    def test_login_required_routes(self):
        """Test that protected routes require login"""
        protected_routes = [
            '/dashboard',
            '/tasks/',
            '/pomodoro',
            '/analytics/',
            '/auth/profile'
        ]
        
        for route in protected_routes:
            response = self.client.get(route)
            # Should redirect to login page
            self.assertIn(response.status_code, [302, 401])
    
    def test_user_registration(self):
        """Test user registration process"""
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check user was created
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'new@example.com')
    
    def test_user_login(self):
        """Test user login process"""
        # Create user first
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        # Test login
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_task_creation_api(self):
        """Test task creation via API"""
        # Create and login user
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        # Login
        self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        # Create task via API
        response = self.client.post('/api/quick-task', 
            json={
                'title': 'API Test Task',
                'subject': 'Testing',
                'priority': 'medium',
                'due_date': date.today().isoformat()
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Verify task was created
        task = Task.query.filter_by(title='API Test Task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.user_id, user.id)

if __name__ == '__main__':
    unittest.main()