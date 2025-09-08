from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app import db
from app.models import Task, StudySession, UserPoints

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
@login_required
def index():
    """Analytics dashboard"""
    # Get date range from query params
    days = int(request.args.get('days', 30))
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Basic statistics
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    completed_tasks = Task.query.filter_by(
        user_id=current_user.id, 
        status='completed'
    ).count()
    
    total_study_time = db.session.query(
        func.sum(StudySession.duration)
    ).filter_by(user_id=current_user.id).scalar() or 0
    
    # Recent performance
    recent_sessions = StudySession.query.filter(
        StudySession.user_id == current_user.id,
        StudySession.date >= start_date
    ).all()
    
    recent_study_time = sum(session.duration for session in recent_sessions)
    avg_focus_rating = sum(session.focus_rating for session in recent_sessions) / len(recent_sessions) if recent_sessions else 0
    
    # Subject breakdown
    subject_data = db.session.query(
        StudySession.subject,
        func.sum(StudySession.duration).label('total_time'),
        func.count(StudySession.id).label('session_count'),
        func.avg(StudySession.focus_rating).label('avg_focus')
    ).filter(
        StudySession.user_id == current_user.id,
        StudySession.date >= start_date
    ).group_by(StudySession.subject).all()
    
    # Task completion by priority - simplified
    priority_data = []
    for priority in ['low', 'medium', 'high', 'urgent']:
        total = Task.query.filter_by(user_id=current_user.id, priority=priority).count()
        completed = Task.query.filter_by(user_id=current_user.id, priority=priority, status='completed').count()
        if total > 0:
            priority_data.append((priority, total, completed))
    
    # Simple analytics HTML
    completion_rate = (completed_tasks/total_tasks*100) if total_tasks > 0 else 0
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Analytics - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}">StudyFlow</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1>📊 Analytics</h1>
        
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card bg-primary text-white">
                    <div class="card-body text-center">
                        <h3>{total_tasks}</h3>
                        <p>Total Tasks</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body text-center">
                        <h3>{completed_tasks}</h3>
                        <p>Completed</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body text-center">
                        <h3>{completion_rate:.1f}%</h3>
                        <p>Completion Rate</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white">
                    <div class="card-body text-center">
                        <h3>{round(total_study_time/60, 1)}</h3>
                        <p>Study Hours</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Study by Subject</h5>
                    </div>
                    <div class="card-body">
                        {''.join([f'<div class="mb-2"><strong>{subject}</strong><br><small>{round(total_time/60, 1)} hours | {session_count} sessions</small></div>' for subject, total_time, session_count, avg_focus in subject_data])}
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Task Completion by Priority</h5>
                    </div>
                    <div class="card-body">
                        {''.join([f'<div class="mb-2"><strong>{priority.title()}</strong><br><small>{completed}/{total} completed ({round(completed/total*100 if total > 0 else 0, 1)}%)</small></div>' for priority, total, completed in priority_data])}
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@analytics_bp.route('/productivity')
@login_required
def productivity():
    """Detailed productivity analysis"""
    # Get monthly data for the last 12 months
    monthly_data = []
    for i in range(12):
        month_start = date.today().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Tasks completed in this month
        tasks_completed = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status == 'completed',
            func.date(Task.completed_at) >= month_start,
            func.date(Task.completed_at) <= month_end
        ).count()
        
        # Study hours in this month
        study_minutes = db.session.query(
            func.sum(StudySession.duration)
        ).filter(
            StudySession.user_id == current_user.id,
            StudySession.date >= month_start,
            StudySession.date <= month_end
        ).scalar() or 0
        
        monthly_data.append({
            'month': month_start.strftime('%Y-%m'),
            'month_name': month_start.strftime('%B %Y'),
            'tasks_completed': tasks_completed,
            'study_hours': round(study_minutes / 60, 1)
        })
    
    monthly_data.reverse()
    
    # Weekly productivity pattern
    weekly_pattern = []
    for day in range(7):  # 0 = Monday, 6 = Sunday
        day_sessions = StudySession.query.filter(
            StudySession.user_id == current_user.id,
            extract('dow', StudySession.date) == (day + 1) % 7  # PostgreSQL uses 0=Sunday
        ).all()
        
        avg_duration = sum(s.duration for s in day_sessions) / len(day_sessions) if day_sessions else 0
        avg_focus = sum(s.focus_rating for s in day_sessions) / len(day_sessions) if day_sessions else 0
        
        weekly_pattern.append({
            'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day],
            'avg_duration': round(avg_duration, 1),
            'avg_focus': round(avg_focus, 1),
            'session_count': len(day_sessions)
        })
    
    # Simple productivity HTML
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Productivity - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}">StudyFlow</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1>📈 Productivity Analysis</h1>
        
        <div class="card mb-4">
            <div class="card-header">
                <h5>Monthly Progress</h5>
            </div>
            <div class="card-body">
                {''.join([f'<div class="mb-2"><strong>{data["month_name"]}</strong><br><small>{data["tasks_completed"]} tasks | {data["study_hours"]} hours</small></div>' for data in monthly_data[-6:]])}
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h5>Weekly Pattern</h5>
            </div>
            <div class="card-body">
                {''.join([f'<div class="mb-2"><strong>{pattern["day"]}</strong><br><small>Avg: {pattern["avg_duration"]} min | Focus: {pattern["avg_focus"]}/10</small></div>' for pattern in weekly_pattern])}
            </div>
        </div>
    </div>
</body>
</html>
    '''

@analytics_bp.route('/goals')
@login_required
def goals():
    """Goal tracking and recommendations"""
    # Calculate current streaks
    today = date.today()
    study_streak = 0
    task_streak = 0
    
    # Study streak calculation
    current_date = today
    while True:
        day_sessions = StudySession.query.filter(
            StudySession.user_id == current_user.id,
            StudySession.date == current_date
        ).first()
        
        if day_sessions:
            study_streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    # Task completion streak
    current_date = today
    while True:
        day_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status == 'completed',
            func.date(Task.completed_at) == current_date
        ).first()
        
        if day_tasks:
            task_streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    # Weekly goals progress
    week_start = today - timedelta(days=today.weekday())
    week_sessions = StudySession.query.filter(
        StudySession.user_id == current_user.id,
        StudySession.date >= week_start
    ).all()
    
    week_study_hours = sum(s.duration for s in week_sessions) / 60
    week_goal = current_user.study_goal_hours * 7  # Daily goal * 7 days
    
    week_tasks_completed = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status == 'completed',
        func.date(Task.completed_at) >= week_start
    ).count()
    
    # Simple goals HTML
    week_progress = (week_study_hours/week_goal*100) if week_goal > 0 else 0
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Goals - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}">StudyFlow</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1>🎯 Goals & Progress</h1>
        
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card bg-success text-white">
                    <div class="card-body text-center">
                        <h2>{study_streak}</h2>
                        <p>Study Streak (days)</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card bg-info text-white">
                    <div class="card-body text-center">
                        <h2>{task_streak}</h2>
                        <p>Task Streak (days)</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h5>Weekly Progress</h5>
            </div>
            <div class="card-body">
                <p><strong>Study Hours:</strong> {round(week_study_hours, 1)} / {week_goal} hours</p>
                <div class="progress mb-3">
                    <div class="progress-bar" style="width: {min(week_progress, 100)}%"></div>
                </div>
                <p><strong>Tasks Completed:</strong> {week_tasks_completed} this week</p>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@analytics_bp.route('/api/chart-data')
@login_required
def chart_data():
    """API endpoint for chart data"""
    chart_type = request.args.get('type', 'daily')
    days = int(request.args.get('days', 7))
    
    if chart_type == 'daily':
        # Daily study hours for the last N days
        data = []
        for i in range(days):
            day = date.today() - timedelta(days=i)
            day_sessions = StudySession.query.filter(
                StudySession.user_id == current_user.id,
                StudySession.date == day
            ).all()
            
            total_minutes = sum(session.duration for session in day_sessions)
            data.append({
                'date': day.strftime('%Y-%m-%d'),
                'hours': round(total_minutes / 60, 1)
            })
        
        return jsonify(list(reversed(data)))
    
    elif chart_type == 'subjects':
        # Study time by subject (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        subject_data = db.session.query(
            StudySession.subject,
            func.sum(StudySession.duration)
        ).filter(
            StudySession.user_id == current_user.id,
            StudySession.date >= thirty_days_ago
        ).group_by(StudySession.subject).all()
        
        return jsonify([{
            'subject': subject,
            'hours': round(minutes / 60, 1)
        } for subject, minutes in subject_data])
    
    elif chart_type == 'focus':
        # Focus rating trend
        sessions = StudySession.query.filter_by(
            user_id=current_user.id
        ).order_by(StudySession.date.desc()).limit(days).all()
        
        return jsonify([{
            'date': session.date.strftime('%Y-%m-%d'),
            'focus': session.focus_rating
        } for session in reversed(sessions)])
    
    return jsonify([])