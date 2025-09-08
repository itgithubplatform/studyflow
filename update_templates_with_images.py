#!/usr/bin/env python3
"""
Update StudyFlow templates to use proper image paths and optimize for images
"""

import os
import re

def update_base_template():
    """Update base template with proper favicon and meta tags"""
    base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="StudyFlow - Smart Student Productivity Tracker. Manage tasks, track study sessions, and boost your academic performance with gamification.">
    <meta name="keywords" content="student, productivity, tasks, study, pomodoro, education, tracking">
    <meta name="author" content="StudyFlow Team">
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:title" content="{% if title %}{{ title }} - StudyFlow{% else %}StudyFlow - Smart Student Productivity{% endif %}">
    <meta property="og:description" content="Transform your study habits with our comprehensive productivity tracker designed for students.">
    <meta property="og:image" content="{{ url_for('static', filename='img/placeholder.svg', _external=True) }}">
    <meta property="og:url" content="{{ request.url }}">
    <meta property="og:type" content="website">
    
    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{% if title %}{{ title }} - StudyFlow{% else %}StudyFlow - Smart Student Productivity{% endif %}">
    <meta name="twitter:description" content="Transform your study habits with our comprehensive productivity tracker.">
    <meta name="twitter:image" content="{{ url_for('static', filename='img/placeholder.svg', _external=True) }}">
    
    <title>{% if title %}{{ title }} - StudyFlow{% else %}StudyFlow - Smart Student Productivity{% endif %}</title>
    
    <!-- Favicon and App Icons -->
    <link rel="icon" type="image/svg+xml" href="{{ url_for('static', filename='img/placeholder.svg') }}">
    <link rel="alternate icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/placeholder.svg') }}">
    
    <!-- Preload Critical Resources -->
    <link rel="preload" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" as="style">
    <link rel="preload" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" as="style">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- FullCalendar -->
    <link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.css' rel='stylesheet' />
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.js'></script>
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
        <div class="container">
            <a class="navbar-brand fw-bold d-flex align-items-center" href="{{ url_for('main.index') }}">
                <img src="{{ url_for('static', filename='img/placeholder.svg') }}" 
                     alt="StudyFlow Logo" height="32" width="32" class="me-2">
                StudyFlow
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                {% if current_user.is_authenticated %}
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.dashboard') }}">
                            <i class="bi bi-speedometer2 me-1"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('tasks.index') }}">
                            <i class="bi bi-list-task me-1"></i>Tasks
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.pomodoro') }}">
                            <i class="bi bi-stopwatch me-1"></i>Pomodoro
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('analytics.index') }}">
                            <i class="bi bi-graph-up me-1"></i>Analytics
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.leaderboard') }}">
                            <i class="bi bi-trophy me-1"></i>Leaderboard
                        </a>
                    </li>
                </ul>
                
                <ul class="navbar-nav">
                    <!-- User Points Display -->
                    <li class="nav-item d-flex align-items-center me-3">
                        <span class="badge bg-warning text-dark">
                            <i class="bi bi-star-fill me-1"></i>{{ current_user.get_total_points() }} pts
                        </span>
                    </li>
                    
                    <!-- User Dropdown -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button" data-bs-toggle="dropdown">
                            <img src="https://ui-avatars.com/api/?name={{ current_user.first_name }}+{{ current_user.last_name }}&background=0d6efd&color=fff&size=32" 
                                 alt="User Avatar" class="rounded-circle me-2" width="32" height="32">
                            {{ current_user.first_name }}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('auth.profile') }}">
                                <i class="bi bi-person me-2"></i>Profile
                            </a></li>
                            <li><a class="dropdown-item" href="{{ url_for('main.achievements') }}">
                                <i class="bi bi-award me-2"></i>Achievements
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}">
                                <i class="bi bi-box-arrow-right me-2"></i>Logout
                            </a></li>
                        </ul>
                    </li>
                </ul>
                {% else %}
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.register') }}">Register</a>
                    </li>
                </ul>
                {% endif %}
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mt-3">
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Main Content -->
    <main class="container-fluid py-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <div class="d-flex align-items-center mb-2">
                        <img src="{{ url_for('static', filename='img/placeholder.svg') }}" 
                             alt="StudyFlow Logo" height="24" width="24" class="me-2">
                        <h5 class="mb-0">StudyFlow</h5>
                    </div>
                    <p class="mb-0">Smart Student Productivity Tracker</p>
                    <small class="text-muted">Empowering students to achieve their academic goals</small>
                </div>
                <div class="col-md-6 text-md-end">
                    <p class="mb-0">&copy; 2024 StudyFlow. All rights reserved.</p>
                    <small class="text-muted">Built with Flask, Bootstrap & Chart.js</small>
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JavaScript -->
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    
    <!-- Page-specific JavaScript -->
    {% block scripts %}{% endblock %}
</body>
</html>"""
    
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(base_template)
    
    print("✓ Updated base.html with proper image integration")

def update_main_index():
    """Update main index with hero background"""
    index_content = """{% extends "base.html" %}

{% block content %}
<!-- Hero Section with Background Image -->
<div class="hero-section text-white py-5 mb-5" style="background: linear-gradient(rgba(102, 126, 234, 0.8), rgba(118, 75, 162, 0.8)), url('{{ url_for('static', filename='img/hero-bg.jpg') }}') center/cover;">
    <div class="container">
        <div class="row align-items-center min-vh-50">
            <div class="col-lg-6">
                <h1 class="display-4 fw-bold mb-4">
                    <img src="{{ url_for('static', filename='img/placeholder.svg') }}" 
                         alt="StudyFlow" height="60" class="me-3">
                    Welcome to StudyFlow
                </h1>
                <p class="lead mb-4">
                    The ultimate productivity tracker designed specifically for students. 
                    Manage tasks, track study sessions, and boost your academic performance with gamification.
                </p>
                <div class="d-grid gap-2 d-md-flex">
                    <a href="{{ url_for('auth.register') }}" class="btn btn-warning btn-lg px-4 me-md-2">
                        <i class="bi bi-person-plus me-2"></i>Get Started Free
                    </a>
                    <a href="{{ url_for('auth.login') }}" class="btn btn-outline-light btn-lg px-4">
                        <i class="bi bi-box-arrow-in-right me-2"></i>Sign In
                    </a>
                </div>
            </div>
            <div class="col-lg-6 text-center">
                <div class="hero-image">
                    <i class="bi bi-graph-up-arrow display-1 text-warning opacity-75 animate-float"></i>
                    <i class="bi bi-list-check display-1 text-info opacity-75 ms-3 animate-float-delay-1"></i>
                    <i class="bi bi-trophy display-1 text-success opacity-75 ms-3 animate-float-delay-2"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Features Section -->
<div class="container">
    <div class="row text-center mb-5">
        <div class="col-12">
            <h2 class="display-5 fw-bold mb-3">Why Choose StudyFlow?</h2>
            <p class="lead text-muted">Comprehensive tools to transform your study habits</p>
        </div>
    </div>
    
    <div class="row g-4 mb-5">
        <!-- Task Management -->
        <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm feature-card">
                <div class="card-body text-center p-4">
                    <div class="feature-icon bg-primary text-white rounded-circle mx-auto mb-3">
                        <i class="bi bi-list-task display-6"></i>
                    </div>
                    <h4 class="card-title">Smart Task Management</h4>
                    <p class="card-text text-muted">
                        Organize assignments, set priorities, track deadlines, and never miss important due dates again.
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Pomodoro Timer -->
        <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm feature-card">
                <div class="card-body text-center p-4">
                    <div class="feature-icon bg-success text-white rounded-circle mx-auto mb-3">
                        <i class="bi bi-stopwatch display-6"></i>
                    </div>
                    <h4 class="card-title">Pomodoro Timer</h4>
                    <p class="card-text text-muted">
                        Built-in Pomodoro technique with customizable work/break intervals to maximize focus and productivity.
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Analytics -->
        <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm feature-card">
                <div class="card-body text-center p-4">
                    <div class="feature-icon bg-info text-white rounded-circle mx-auto mb-3">
                        <i class="bi bi-graph-up display-6"></i>
                    </div>
                    <h4 class="card-title">Detailed Analytics</h4>
                    <p class="card-text text-muted">
                        Visualize your progress with charts, track study patterns, and identify areas for improvement.
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Gamification -->
        <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm feature-card">
                <div class="card-body text-center p-4">
                    <div class="feature-icon bg-warning text-white rounded-circle mx-auto mb-3">
                        <i class="bi bi-trophy display-6"></i>
                    </div>
                    <h4 class="card-title">Gamification System</h4>
                    <p class="card-text text-muted">
                        Earn points, unlock achievements, level up, and compete with friends on the leaderboard.
                    </p>
                </div>
            </div>
        </div>
        
        <!-- AI Recommendations -->
        <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm feature-card">
                <div class="card-body text-center p-4">
                    <div class="feature-icon bg-danger text-white rounded-circle mx-auto mb-3">
                        <i class="bi bi-robot display-6"></i>
                    </div>
                    <h4 class="card-title">AI Study Coach</h4>
                    <p class="card-text text-muted">
                        Get personalized study recommendations based on your habits and performance patterns.
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Email Notifications -->
        <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm feature-card">
                <div class="card-body text-center p-4">
                    <div class="feature-icon bg-secondary text-white rounded-circle mx-auto mb-3">
                        <i class="bi bi-envelope display-6"></i>
                    </div>
                    <h4 class="card-title">Smart Notifications</h4>
                    <p class="card-text text-muted">
                        Receive email reminders for upcoming deadlines and weekly progress summaries.
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- CTA Section -->
    <div class="row text-center">
        <div class="col-12">
            <div class="cta-section bg-gradient-primary text-white rounded-3 p-5">
                <h3 class="fw-bold mb-3">Ready to Transform Your Study Habits?</h3>
                <p class="lead mb-4">Join StudyFlow today and start your journey to academic excellence!</p>
                <a href="{{ url_for('auth.register') }}" class="btn btn-warning btn-lg px-5">
                    <i class="bi bi-rocket-takeoff me-2"></i>Start Your Free Account
                </a>
            </div>
        </div>
    </div>
</div>

<style>
.min-vh-50 {
    min-height: 50vh;
}

.feature-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
}

.feature-icon {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.animate-float {
    animation: float 3s ease-in-out infinite;
}

.animate-float-delay-1 {
    animation: float 3s ease-in-out infinite;
    animation-delay: 1s;
}

.animate-float-delay-2 {
    animation: float 3s ease-in-out infinite;
    animation-delay: 2s;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
</style>
{% endblock %}"""
    
    with open('templates/main/index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print("✓ Updated main/index.html with hero background")

def main():
    """Update all templates with proper image integration"""
    print("🖼️ Updating StudyFlow templates with image optimization...")
    
    update_base_template()
    update_main_index()
    
    print("\n✅ Template updates completed!")
    print("\n📋 Next steps:")
    print("1. Run: python create_placeholder_images.py")
    print("2. Replace placeholder images with custom designs")
    print("3. Optimize images for web (compress, resize)")
    print("4. Test the application with new images")

if __name__ == "__main__":
    main()