# 🎓 StudyFlow - Smart Student Productivity Tracker

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, full-stack web application designed to help students manage tasks, track study sessions, and boost productivity through gamification and AI-powered insights.

## 🌟 Features

### 📋 Task Management
- **Smart Task Organization**: Create, edit, and organize tasks with priorities, subjects, and due dates
- **Calendar Integration**: Visual calendar view with FullCalendar.js
- **Status Tracking**: Pending, In Progress, Completed, and Overdue statuses
- **Quick Actions**: Keyboard shortcuts and quick-add functionality

### ⏱️ Pomodoro Timer
- **Built-in Timer**: Customizable work/break intervals
- **Session Tracking**: Automatic logging of study sessions
- **Focus Rating**: Rate your productivity after each session
- **Break Management**: Smart break suggestions and timing

### 📊 Analytics & Insights
- **Progress Visualization**: Interactive charts with Chart.js
- **Study Patterns**: Weekly and monthly trend analysis
- **Subject Distribution**: Time allocation across different subjects
- **Productivity Metrics**: Focus ratings and completion rates

### 🎮 Gamification System
- **Points & Levels**: Earn points for completing tasks and studying
- **Achievements**: Unlock badges for various milestones
- **Leaderboard**: Compete with other users
- **Streaks**: Maintain study and task completion streaks

### 🤖 AI-Powered Features
- **Study Recommendations**: Personalized suggestions based on your patterns
- **Schedule Optimization**: AI-suggested study schedules
- **Performance Analysis**: Insights into your productivity patterns

### 📧 Smart Notifications
- **Email Reminders**: Deadline notifications and weekly summaries
- **Browser Notifications**: Real-time alerts for Pomodoro sessions
- **Progress Reports**: Automated weekly and monthly reports

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, SQLite for development)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/studyflow.git
   cd studyflow
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   # Required: SECRET_KEY, DATABASE_URL, MAIL_* settings
   ```

5. **Initialize the database**
   ```bash
   python app.py deploy
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Use demo account: username `demo`, password `demo123`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Application
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///studyflow.db
# For PostgreSQL: postgresql://username:password@localhost/studyflow

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
ADMIN_EMAIL=admin@studyflow.com

# AI Integration (Optional)
OPENAI_API_KEY=your-openai-api-key
```

### Database Setup

**SQLite (Development)**
```bash
# Automatic setup with app initialization
python app.py deploy
```

**PostgreSQL (Production)**
```bash
# Install PostgreSQL and create database
createdb studyflow

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@localhost/studyflow

# Run migrations
python app.py deploy
```

## 📁 Project Structure

```
studyflow/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models/                  # Database models
│   │   ├── user.py             # User model
│   │   ├── task.py             # Task model
│   │   ├── study_session.py    # Study session model
│   │   └── gamification.py     # Points and achievements
│   ├── routes/                  # Route blueprints
│   │   ├── auth.py             # Authentication routes
│   │   ├── main.py             # Main dashboard routes
│   │   ├── tasks.py            # Task management routes
│   │   ├── analytics.py        # Analytics routes
│   │   └── api.py              # API endpoints
│   └── utils/                   # Utility modules
│       ├── forms.py            # WTForms
│       └── ai_helper.py        # AI integration
├── templates/                   # Jinja2 templates
│   ├── base.html               # Base template
│   ├── auth/                   # Authentication templates
│   ├── dashboard/              # Dashboard templates
│   ├── tasks/                  # Task management templates
│   └── analytics/              # Analytics templates
├── static/                      # Static files
│   ├── css/style.css           # Custom styles
│   ├── js/app.js               # Main JavaScript
│   └── img/                    # Images
├── tests/                       # Unit tests
├── config.py                   # Configuration
├── app.py                      # Main application file
├── requirements.txt            # Python dependencies
├── Procfile                    # Heroku deployment
└── README.md                   # This file
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 🚀 Deployment

### Heroku Deployment

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set FLASK_ENV=production
   heroku config:set DATABASE_URL=your-postgres-url
   # Add other environment variables
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

### Render Deployment

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy automatically on git push

### Docker Deployment

```bash
# Build image
docker build -t studyflow .

# Run container
docker run -p 5000:5000 --env-file .env studyflow
```

## 🎯 Usage Guide

### Getting Started

1. **Create Account**: Register with your email and create a secure password
2. **Set Goals**: Configure your daily study goals in your profile
3. **Add Tasks**: Create your first task with subject, priority, and due date
4. **Start Studying**: Use the Pomodoro timer for focused study sessions
5. **Track Progress**: View your analytics and earn achievements

### Best Practices

- **Consistent Logging**: Log all study sessions for accurate analytics
- **Realistic Goals**: Set achievable daily and weekly study targets
- **Regular Reviews**: Check your analytics weekly to identify patterns
- **Use Priorities**: Properly prioritize tasks to focus on what matters most
- **Take Breaks**: Follow the Pomodoro technique for optimal productivity

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 API Documentation

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Tasks
- `GET /api/tasks` - Get user tasks
- `POST /api/quick-task` - Create quick task
- `POST /api/tasks/{id}/toggle-status` - Toggle task completion
- `POST /api/tasks/{id}/update-priority` - Update task priority

### Study Sessions
- `POST /api/pomodoro/start` - Start Pomodoro session
- `POST /api/pomodoro/complete` - Complete Pomodoro session

### Analytics
- `GET /api/dashboard-stats` - Dashboard statistics
- `GET /api/analytics/chart-data` - Chart data for analytics
- `GET /api/user/stats` - User statistics

## 🔒 Security Features

- **Password Hashing**: Werkzeug secure password hashing
- **CSRF Protection**: Flask-WTF CSRF tokens
- **Session Management**: Secure Flask-Login sessions
- **Input Validation**: Comprehensive form validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection

## 🎨 UI/UX Features

- **Responsive Design**: Mobile-first Bootstrap 5 design
- **Dark Mode Support**: Automatic dark mode detection
- **Accessibility**: WCAG 2.1 compliant
- **Progressive Web App**: Offline functionality and app-like experience
- **Smooth Animations**: CSS3 and JavaScript animations
- **Intuitive Navigation**: User-friendly interface design

## 📊 Performance

- **Optimized Queries**: Efficient database queries with SQLAlchemy
- **Caching**: Redis caching for improved performance
- **CDN Integration**: Static file delivery via CDN
- **Lazy Loading**: Progressive content loading
- **Minified Assets**: Compressed CSS and JavaScript

## 🛠️ Tech Stack

**Backend:**
- Flask 2.3+ (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL/SQLite (Database)
- Flask-Login (Authentication)
- Flask-Mail (Email notifications)
- APScheduler (Background tasks)

**Frontend:**
- Bootstrap 5.3 (CSS framework)
- Chart.js (Data visualization)
- FullCalendar.js (Calendar component)
- Vanilla JavaScript (No heavy frameworks)

**Deployment:**
- Gunicorn (WSGI server)
- Heroku/Render (Cloud platforms)
- Docker (Containerization)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Bootstrap Team** for the amazing CSS framework
- **Chart.js Team** for beautiful data visualization
- **Flask Community** for the excellent web framework
- **All Contributors** who helped make this project better

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/studyflow/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/studyflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/studyflow/discussions)
- **Email**: benugopal2005@gmail.com

---

**Made with ❤️ for students worldwide**

*StudyFlow - Transform your study habits, achieve your goals!*