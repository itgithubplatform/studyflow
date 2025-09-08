from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from app import db
from app.models import User, Task, StudySession, UserPoints, Achievement, UserAchievement

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with overview"""
    today = date.today()
    
    # Get today's tasks
    todays_tasks = Task.query.filter_by(
        user_id=current_user.id,
        due_date=today
    ).order_by(Task.priority.desc()).all()
    
    # Get overdue tasks
    overdue_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.due_date < today,
        Task.status != 'completed'
    ).count()
    
    # Get upcoming tasks (next 7 days)
    upcoming_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.due_date > today,
        Task.due_date <= today + timedelta(days=7),
        Task.status != 'completed'
    ).order_by(Task.due_date).limit(5).all()
    
    # Get recent study sessions
    recent_sessions = StudySession.query.filter_by(
        user_id=current_user.id
    ).order_by(desc(StudySession.created_at)).limit(5).all()
    
    # Calculate statistics
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    completed_tasks = Task.query.filter_by(
        user_id=current_user.id, 
        status='completed'
    ).count()
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get user points
    user_points = UserPoints.query.filter_by(user_id=current_user.id).first()
    if not user_points:
        user_points = UserPoints(user_id=current_user.id)
        db.session.add(user_points)
        db.session.commit()
    
    # Study hours this week
    week_start = today - timedelta(days=today.weekday())
    week_sessions = StudySession.query.filter(
        StudySession.user_id == current_user.id,
        StudySession.date >= week_start
    ).all()
    
    week_hours = sum(session.duration for session in week_sessions) / 60
    
    # Simple dashboard HTML response
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>StudyFlow Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#"><i class="bi bi-mortarboard-fill me-2"></i>StudyFlow</a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">Welcome, {current_user.first_name}!</span>
                <a class="nav-link" href="{url_for('auth.logout')}">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4">📊 Dashboard</h1>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <h5>Total Points</h5>
                        <h2>{user_points.total_points if user_points else 0}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <h5>Today's Tasks</h5>
                        <h2>{len(todays_tasks)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white">
                    <div class="card-body">
                        <h5>Overdue Tasks</h5>
                        <h2>{overdue_tasks}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <h5>Week Hours</h5>
                        <h2>{week_hours:.1f}</h2>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Today's Tasks</h5>
                    </div>
                    <div class="card-body">
                        {"<p>No tasks for today!</p>" if not todays_tasks else ""}
                        {''.join([f'<div class="mb-2"><strong>{task.title}</strong><br><small>{task.subject} - {task.priority}</small></div>' for task in todays_tasks[:5]])}
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Recent Study Sessions</h5>
                    </div>
                    <div class="card-body">
                        {"<p>No study sessions yet!</p>" if not recent_sessions else ""}
                        {''.join([f'<div class="mb-2"><strong>{session.subject}</strong><br><small>{session.duration} min - Focus: {session.focus_rating}/10</small></div>' for session in recent_sessions[:5]])}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-body text-center">
                        <h5>Quick Actions</h5>
                        <a href="{url_for('tasks.add')}" class="btn btn-primary me-2">Add Task</a>
                        <a href="{url_for('main.pomodoro')}" class="btn btn-success me-2">Start Pomodoro</a>
                        <a href="{url_for('tasks.index')}" class="btn btn-info me-2">View All Tasks</a>
                        <a href="{url_for('analytics.index')}" class="btn btn-warning">Analytics</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@main_bp.route('/pomodoro')
@login_required
def pomodoro():
    """Pomodoro timer page"""
    subjects = db.session.query(Task.subject).filter_by(
        user_id=current_user.id
    ).distinct().all()
    subjects = [s[0] for s in subjects]
    
    # Simple pomodoro HTML response
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Pomodoro Timer - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}"><i class="bi bi-mortarboard-fill me-2"></i>StudyFlow</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{url_for('main.dashboard')}">Dashboard</a>
                <a class="nav-link" href="{url_for('auth.logout')}">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header bg-success text-white text-center">
                        <h3><i class="bi bi-stopwatch me-2"></i>Pomodoro Timer</h3>
                    </div>
                    <div class="card-body text-center">
                        <div class="mb-4">
                            <h1 id="timer" class="display-1 text-primary">25:00</h1>
                        </div>
                        <div class="mb-4">
                            <button id="startBtn" class="btn btn-success btn-lg me-2">Start</button>
                            <button id="pauseBtn" class="btn btn-warning btn-lg me-2">Pause</button>
                            <button id="resetBtn" class="btn btn-secondary btn-lg">Reset</button>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Subject:</label>
                            <select class="form-select">
                                <option>General Study</option>
                                {''.join([f'<option>{subject}</option>' for subject in subjects])}
                            </select>
                        </div>
                        <p class="text-muted">Focus for 25 minutes, then take a 5-minute break!</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let timeLeft = 25 * 60;
        let isRunning = false;
        let timer;
        
        function updateDisplay() {{
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            document.getElementById('timer').textContent = 
                `${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
        }}
        
        document.getElementById('startBtn').onclick = function() {{
            if (!isRunning) {{
                isRunning = true;
                timer = setInterval(() => {{
                    timeLeft--;
                    updateDisplay();
                    if (timeLeft <= 0) {{
                        clearInterval(timer);
                        isRunning = false;
                        alert('Pomodoro completed! Take a break!');
                        timeLeft = 25 * 60;
                        updateDisplay();
                    }}
                }}, 1000);
            }}
        }};
        
        document.getElementById('pauseBtn').onclick = function() {{
            if (isRunning) {{
                clearInterval(timer);
                isRunning = false;
            }}
        }};
        
        document.getElementById('resetBtn').onclick = function() {{
            clearInterval(timer);
            isRunning = false;
            timeLeft = 25 * 60;
            updateDisplay();
        }};
    </script>
</body>
</html>
    '''

@main_bp.route('/leaderboard')
@login_required
def leaderboard():
    """Leaderboard page showing top users"""
    # Get top users by points
    top_users = db.session.query(User, UserPoints).join(
        UserPoints, User.id == UserPoints.user_id
    ).order_by(desc(UserPoints.total_points)).limit(10).all()
    
    # Get current user's rank
    user_rank = db.session.query(func.count(UserPoints.id)).filter(
        UserPoints.total_points > current_user.points.total_points
    ).scalar() + 1 if current_user.points else None
    
    # Simple leaderboard HTML response
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Leaderboard - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}"><i class="bi bi-mortarboard-fill me-2"></i>StudyFlow</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{url_for('main.dashboard')}">Dashboard</a>
                <a class="nav-link" href="{url_for('auth.logout')}">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4"><i class="bi bi-trophy me-2"></i>Leaderboard</h1>
                <div class="card">
                    <div class="card-body">
                        <p class="text-center">Your Rank: #{user_rank or 'N/A'}</p>
                        <div class="list-group">
                            {''.join([f'<div class="list-group-item d-flex justify-content-between align-items-center"><div><strong>#{i+1} {user.first_name} {user.last_name}</strong></div><span class="badge bg-primary">{points.total_points} pts</span></div>' for i, (user, points) in enumerate(top_users[:10])])}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@main_bp.route('/achievements')
@login_required
def achievements():
    """Achievements page"""
    # Get all achievements
    all_achievements = Achievement.query.filter_by(is_active=True).all()
    
    # Get user's unlocked achievements
    unlocked_ids = [ua.achievement_id for ua in current_user.user_achievements]
    
    unlocked_achievements = []
    locked_achievements = []
    
    for achievement in all_achievements:
        if achievement.id in unlocked_ids:
            unlocked_achievements.append(achievement)
        else:
            locked_achievements.append(achievement)
    
    # Simple achievements HTML response
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Achievements - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}"><i class="bi bi-mortarboard-fill me-2"></i>StudyFlow</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{url_for('main.dashboard')}">Dashboard</a>
                <a class="nav-link" href="{url_for('auth.logout')}">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4"><i class="bi bi-award me-2"></i>Achievements</h1>
                
                <h3 class="text-success">Unlocked ({len(unlocked_achievements)})</h3>
                <div class="row mb-4">
                    {''.join([f'<div class="col-md-4 mb-3"><div class="card border-success"><div class="card-body text-center"><h4>{achievement.icon}</h4><h5>{achievement.name}</h5><p>{achievement.description}</p><small class="text-success">+{achievement.points_reward} points</small></div></div></div>' for achievement in unlocked_achievements])}
                </div>
                
                <h3 class="text-muted">Locked ({len(locked_achievements)})</h3>
                <div class="row">
                    {''.join([f'<div class="col-md-4 mb-3"><div class="card border-secondary"><div class="card-body text-center opacity-50"><h4>{achievement.icon}</h4><h5>{achievement.name}</h5><p>{achievement.description}</p><small class="text-muted">+{achievement.points_reward} points</small></div></div></div>' for achievement in locked_achievements])}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@main_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    today = date.today()
    
    # Tasks by status
    task_stats = db.session.query(
        Task.status, func.count(Task.id)
    ).filter_by(user_id=current_user.id).group_by(Task.status).all()
    
    # Study hours by subject (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    subject_stats = db.session.query(
        StudySession.subject, func.sum(StudySession.duration)
    ).filter(
        StudySession.user_id == current_user.id,
        StudySession.date >= thirty_days_ago
    ).group_by(StudySession.subject).all()
    
    # Weekly study trend (last 7 days)
    weekly_stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_sessions = StudySession.query.filter(
            StudySession.user_id == current_user.id,
            StudySession.date == day
        ).all()
        total_minutes = sum(session.duration for session in day_sessions)
        weekly_stats.append({
            'date': day.strftime('%Y-%m-%d'),
            'hours': round(total_minutes / 60, 1)
        })
    
    return jsonify({
        'task_stats': dict(task_stats),
        'subject_stats': {subject: round(minutes/60, 1) for subject, minutes in subject_stats},
        'weekly_stats': list(reversed(weekly_stats))
    })