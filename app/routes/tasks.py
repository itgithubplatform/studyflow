from datetime import datetime, date
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Task, StudySession
from app.utils.forms import TaskForm, StudySessionForm

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
@login_required
def index():
    """Tasks overview page"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    subject_filter = request.args.get('subject', 'all')
    priority_filter = request.args.get('priority', 'all')
    
    # Build query
    query = Task.query.filter_by(user_id=current_user.id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if subject_filter != 'all':
        query = query.filter_by(subject=subject_filter)
    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)
    
    # Order by due date and priority
    tasks = query.order_by(Task.due_date, Task.priority.desc()).all()
    
    # Get unique subjects for filter
    subjects = db.session.query(Task.subject).filter_by(
        user_id=current_user.id
    ).distinct().all()
    subjects = [s[0] for s in subjects]
    
    # Simple tasks list HTML
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>My Tasks - StudyFlow</title>
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
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1><i class="bi bi-list-task me-2"></i>My Tasks</h1>
            <a href="{url_for('tasks.add')}" class="btn btn-primary">Add Task</a>
        </div>
        
        <div class="row">
            {''.join([f'<div class="col-md-6 mb-3"><div class="card"><div class="card-body"><h5>{task.title}</h5><p class="text-muted">{task.subject}</p><small>Due: {task.due_date} | Priority: {task.priority}</small><div class="mt-2"><form method="POST" action="{url_for("tasks.complete", id=task.id)}" style="display:inline;"><button class="btn btn-sm btn-success">Complete</button></form><form method="POST" action="{url_for("tasks.delete", id=task.id)}" style="display:inline;" onsubmit="return confirm("Delete task?")"><button class="btn btn-sm btn-danger ms-1">Delete</button></form></div></div></div></div>' for task in tasks])}
        </div>
        
        {"<p class='text-center text-muted'>No tasks yet. <a href='" + url_for('tasks.add') + "'>Add your first task!</a></p>" if not tasks else ""}
    </div>
</body>
</html>
    '''

@tasks_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new task"""
    form = TaskForm()
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            subject=form.subject.data,
            priority=form.priority.data,
            difficulty=form.difficulty.data,
            estimated_hours=form.estimated_hours.data,
            due_date=form.due_date.data,
            category=form.category.data,
            user_id=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks.index'))
    
    # Simple add task HTML
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Add Task - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}"><i class="bi bi-mortarboard-fill me-2"></i>StudyFlow</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{url_for('tasks.index')}">Tasks</a>
                <a class="nav-link" href="{url_for('main.dashboard')}">Dashboard</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h3><i class="bi bi-plus-circle me-2"></i>Add New Task</h3>
                    </div>
                    <div class="card-body">
                        <form method="POST">
                            {form.hidden_tag()}
                            <div class="mb-3">
                                {form.title.label(class_="form-label")}
                                {form.title(class_="form-control")}
                            </div>
                            <div class="mb-3">
                                {form.description.label(class_="form-label")}
                                {form.description(class_="form-control")}
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    {form.subject.label(class_="form-label")}
                                    {form.subject(class_="form-control")}
                                </div>
                                <div class="col-md-6 mb-3">
                                    {form.priority.label(class_="form-label")}
                                    {form.priority(class_="form-select")}
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    {form.due_date.label(class_="form-label")}
                                    {form.due_date(class_="form-control")}
                                </div>
                                <div class="col-md-6 mb-3">
                                    {form.estimated_hours.label(class_="form-label")}
                                    {form.estimated_hours(class_="form-control")}
                                </div>
                            </div>
                            <div class="d-grid">
                                {form.submit(class_="btn btn-primary btn-lg")}
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@tasks_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit existing task"""
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = TaskForm(obj=task)
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.subject = form.subject.data
        task.priority = form.priority.data
        task.difficulty = form.difficulty.data
        task.estimated_hours = form.estimated_hours.data
        task.due_date = form.due_date.data
        task.category = form.category.data
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.index'))
    
    # Simple edit task HTML
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Edit Task - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}">StudyFlow</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{url_for('tasks.index')}">Tasks</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h3>Edit Task: {task.title}</h3>
                    </div>
                    <div class="card-body">
                        <form method="POST">
                            {form.hidden_tag()}
                            <div class="mb-3">
                                {form.title.label(class_="form-label")}
                                {form.title(class_="form-control")}
                            </div>
                            <div class="mb-3">
                                {form.description.label(class_="form-label")}
                                {form.description(class_="form-control")}
                            </div>
                            <div class="d-grid">
                                {form.submit(class_="btn btn-primary")}
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@tasks_bp.route('/complete/<int:id>', methods=['POST'])
@login_required
def complete(id):
    """Mark task as completed"""
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if task.status != 'completed':
        task.mark_completed()
        db.session.commit()
        flash(f'Task completed! You earned {task.points_awarded} points!', 'success')
    
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete task"""
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'info')
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/study-sessions')
@login_required
def study_sessions():
    """Study sessions overview"""
    sessions = StudySession.query.filter_by(
        user_id=current_user.id
    ).order_by(StudySession.created_at.desc()).all()
    
    # Simple study sessions HTML
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Study Sessions - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}">StudyFlow</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{url_for('main.dashboard')}">Dashboard</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>Study Sessions</h1>
            <a href="{url_for('tasks.add_session')}" class="btn btn-primary">Log Session</a>
        </div>
        
        <div class="row">
            {''.join([f'<div class="col-md-6 mb-3"><div class="card"><div class="card-body"><h5>{session.subject}</h5><p>Duration: {session.duration} min | Focus: {session.focus_rating}/10</p><small>{session.date}</small></div></div></div>' for session in sessions])}
        </div>
        
        {"<p class='text-center text-muted'>No study sessions yet.</p>" if not sessions else ""}
    </div>
</body>
</html>
    '''

@tasks_bp.route('/add-session', methods=['GET', 'POST'])
@login_required
def add_session():
    """Add study session"""
    form = StudySessionForm()
    
    # Populate task choices
    tasks = Task.query.filter_by(
        user_id=current_user.id,
        status__in=['pending', 'in_progress']
    ).all()
    form.task_id.choices = [(0, 'No specific task')] + [(t.id, t.title) for t in tasks]
    
    if form.validate_on_submit():
        session = StudySession(
            subject=form.subject.data,
            duration=form.duration.data,
            session_type=form.session_type.data,
            focus_rating=form.focus_rating.data,
            notes=form.notes.data,
            date=form.date.data,
            user_id=current_user.id
        )
        
        if form.task_id.data and form.task_id.data != 0:
            session.task_id = form.task_id.data
        
        session.calculate_points()
        db.session.add(session)
        db.session.commit()
        
        flash(f'Study session logged! You earned {session.points_earned} points!', 'success')
        return redirect(url_for('tasks.study_sessions'))
    
    # Simple add session HTML
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Log Study Session - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}">StudyFlow</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h3>Log Study Session</h3>
                    </div>
                    <div class="card-body">
                        <form method="POST">
                            {form.hidden_tag()}
                            <div class="mb-3">
                                {form.subject.label(class_="form-label")}
                                {form.subject(class_="form-control")}
                            </div>
                            <div class="mb-3">
                                {form.duration.label(class_="form-label")}
                                {form.duration(class_="form-control")}
                            </div>
                            <div class="mb-3">
                                {form.focus_rating.label(class_="form-label")}
                                {form.focus_rating(class_="form-control")}
                            </div>
                            <div class="d-grid">
                                {form.submit(class_="btn btn-primary")}
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@tasks_bp.route('/api/tasks')
@login_required
def api_tasks():
    """API endpoint for tasks (for calendar view)"""
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    events = []
    for task in tasks:
        events.append({
            'id': task.id,
            'title': task.title,
            'start': task.due_date.isoformat(),
            'backgroundColor': f'var(--bs-{task.priority_color})',
            'borderColor': f'var(--bs-{task.priority_color})',
            'extendedProps': {
                'subject': task.subject,
                'priority': task.priority,
                'status': task.status
            }
        })
    
    return jsonify(events)

@tasks_bp.route('/calendar')
@login_required
def calendar():
    """Calendar view of tasks"""
    # Simple calendar HTML
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Task Calendar - StudyFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{url_for('main.dashboard')}">StudyFlow</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1>Task Calendar</h1>
        <div class="card">
            <div class="card-body">
                <p class="text-center text-muted">Calendar view coming soon!</p>
                <div class="text-center">
                    <a href="{url_for('tasks.index')}" class="btn btn-primary">View Tasks List</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''