# 🚀 StudyFlow Quick Setup Guide

## Prerequisites
- Python 3.11+ installed
- Git (optional, for cloning)
- Modern web browser

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
# Navigate to the studyflow directory
cd studyflow

# Install required packages
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
# Copy environment template
copy .env .env.local  # Windows
# cp .env .env.local    # macOS/Linux

# Edit .env.local with your settings (optional for demo)
```

### 3. Initialize Database
```bash
# Create database and demo data
python app.py deploy
```

### 4. Run the Application
```bash
# Start the development server
python run.py
```

### 5. Access StudyFlow
- Open your browser to: http://localhost:5000
- **Demo Account**: username=`demo`, password=`demo123`
- Or create a new account by clicking "Register"

## Features to Try

### 📋 Task Management
1. Click "Add New Task" to create your first task
2. Set priority, due date, and difficulty
3. Use the checkbox to mark tasks complete
4. Filter tasks by status, subject, or priority

### ⏱️ Pomodoro Timer
1. Go to "Pomodoro" in the navigation
2. Select a subject and start a 25-minute focus session
3. Rate your focus level after completion
4. Take breaks and track your productivity

### 📊 Analytics
1. Visit "Analytics" to see your progress
2. View study time charts and task completion rates
3. Analyze your productivity patterns
4. Set and track study goals

### 🎮 Gamification
1. Earn points by completing tasks and study sessions
2. Level up and unlock achievements
3. Check the leaderboard to see top users
4. Maintain study streaks for bonus points

## Configuration Options

### Database
- **SQLite** (default): No setup required, perfect for testing
- **PostgreSQL**: Set `DATABASE_URL` in .env for production

### Email Notifications
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### AI Features (Optional)
```env
OPENAI_API_KEY=your-openai-api-key
```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Use a different port
python -c "from app import create_app; app = create_app(); app.run(port=5001)"
```

**Database errors:**
```bash
# Reset database
rm studyflow.db
python app.py deploy
```

**Missing dependencies:**
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt
```

### Getting Help
- Check the main README.md for detailed documentation
- Look at the code comments for implementation details
- Create an issue on GitHub for bugs or questions

## Next Steps

### For Development
1. Explore the code structure in `/app`
2. Check out the models in `/app/models`
3. Look at the API endpoints in `/app/routes/api.py`
4. Customize the UI in `/templates` and `/static`

### For Production
1. Set up PostgreSQL database
2. Configure email settings
3. Set strong SECRET_KEY
4. Deploy to Heroku, Render, or your preferred platform

### For Customization
1. Add new subjects in the task form
2. Modify achievement criteria in `app.py`
3. Customize colors and themes in `static/css/style.css`
4. Add new chart types in the analytics section

## Demo Data Included
- Sample user account (demo/demo123)
- Example tasks with different priorities
- Sample study session data
- Pre-configured achievements

Enjoy using StudyFlow! 🎓✨