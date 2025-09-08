from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Task, StudySession, UserPoints
from app.utils.ai_helper import get_study_recommendations

api_bp = Blueprint('api', __name__)

@api_bp.route('/pomodoro/start', methods=['POST'])
@login_required
def start_pomodoro():
    """Start a Pomodoro session"""
    data = request.get_json()
    subject = data.get('subject', 'General Study')
    task_id = data.get('task_id')
    
    # Create study session
    session = StudySession(
        subject=subject,
        duration=25,  # Standard Pomodoro duration
        session_type='pomodoro',
        user_id=current_user.id,
        task_id=task_id if task_id else None
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'session_id': session.id,
        'message': 'Pomodoro session started!'
    })

@api_bp.route('/pomodoro/complete', methods=['POST'])
@login_required
def complete_pomodoro():
    """Complete a Pomodoro session"""
    data = request.get_json()
    session_id = data.get('session_id')
    focus_rating = data.get('focus_rating', 5)
    notes = data.get('notes', '')
    
    session = StudySession.query.filter_by(
        id=session_id,
        user_id=current_user.id
    ).first()
    
    if not session:
        return jsonify({'success': False, 'message': 'Session not found'}), 404
    
    session.end_time = datetime.utcnow()
    session.focus_rating = focus_rating
    session.notes = notes
    session.pomodoro_cycles = 1
    session.calculate_points()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'points_earned': session.points_earned,
        'message': f'Pomodoro completed! You earned {session.points_earned} points!'
    })

@api_bp.route('/tasks/<int:task_id>/toggle-status', methods=['POST'])
@login_required
def toggle_task_status(task_id):
    """Toggle task status between pending and completed"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
    
    if task.status == 'completed':
        task.status = 'pending'
        task.completed_at = None
        message = 'Task marked as pending'
        points = 0
    else:
        task.mark_completed()
        message = f'Task completed! You earned {task.points_awarded} points!'
        points = task.points_awarded
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'status': task.status,
        'points_earned': points,
        'message': message
    })

@api_bp.route('/tasks/<int:task_id>/update-priority', methods=['POST'])
@login_required
def update_task_priority(task_id):
    """Update task priority"""
    data = request.get_json()
    priority = data.get('priority')
    
    if priority not in ['low', 'medium', 'high', 'urgent']:
        return jsonify({'success': False, 'message': 'Invalid priority'}), 400
    
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
    
    task.priority = priority
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'priority': priority,
        'message': 'Priority updated successfully'
    })

@api_bp.route('/study-recommendations', methods=['GET'])
@login_required
def study_recommendations():
    """Get AI-powered study recommendations"""
    try:
        # Get user's recent study data
        recent_sessions = StudySession.query.filter_by(
            user_id=current_user.id
        ).order_by(StudySession.created_at.desc()).limit(10).all()
        
        pending_tasks = Task.query.filter_by(
            user_id=current_user.id,
            status='pending'
        ).order_by(Task.due_date).limit(5).all()
        
        # Get recommendations from AI helper
        recommendations = get_study_recommendations(recent_sessions, pending_tasks)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Unable to generate recommendations at this time',
            'recommendations': [
                "Take regular breaks every 25-30 minutes",
                "Focus on high-priority tasks first",
                "Review completed material regularly",
                "Set specific study goals for each session"
            ]
        })

@api_bp.route('/user/stats', methods=['GET'])
@login_required
def user_stats():
    """Get comprehensive user statistics"""
    user_points = UserPoints.query.filter_by(user_id=current_user.id).first()
    
    if not user_points:
        user_points = UserPoints(user_id=current_user.id)
        db.session.add(user_points)
        db.session.commit()
    
    # Calculate additional stats
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    completed_tasks = Task.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).count()
    
    overdue_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.due_date < date.today(),
        Task.status != 'completed'
    ).count()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_points': user_points.total_points,
            'level': user_points.level,
            'rank_title': user_points.rank_title,
            'tasks_completed': user_points.tasks_completed,
            'study_hours': user_points.study_hours,
            'streak_days': user_points.streak_days,
            'total_tasks': total_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'overdue_tasks': overdue_tasks,
            'points_to_next_level': user_points.points_to_next_level,
            'progress_percentage': user_points.progress_percentage
        }
    })

@api_bp.route('/quick-task', methods=['POST'])
@login_required
def quick_add_task():
    """Quickly add a task via API"""
    data = request.get_json()
    
    task = Task(
        title=data.get('title'),
        subject=data.get('subject', 'General'),
        priority=data.get('priority', 'medium'),
        due_date=datetime.strptime(data.get('due_date'), '%Y-%m-%d').date(),
        user_id=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'task': task.to_dict(),
        'message': 'Task added successfully!'
    })

@api_bp.route('/dashboard/summary', methods=['GET'])
@login_required
def dashboard_summary():
    """Get dashboard summary data"""
    today = date.today()
    
    # Today's tasks
    todays_tasks = Task.query.filter_by(
        user_id=current_user.id,
        due_date=today
    ).count()
    
    completed_today = Task.query.filter_by(
        user_id=current_user.id,
        due_date=today,
        status='completed'
    ).count()
    
    # Study time today
    today_sessions = StudySession.query.filter_by(
        user_id=current_user.id,
        date=today
    ).all()
    
    study_minutes_today = sum(session.duration for session in today_sessions)
    
    return jsonify({
        'success': True,
        'summary': {
            'todays_tasks': todays_tasks,
            'completed_today': completed_today,
            'study_hours_today': round(study_minutes_today / 60, 1),
            'completion_rate_today': (completed_today / todays_tasks * 100) if todays_tasks > 0 else 0
        }
    })