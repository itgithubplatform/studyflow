import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict

def get_study_recommendations(recent_sessions, pending_tasks) -> List[str]:
    """
    Generate AI-powered study recommendations based on user data
    Falls back to rule-based recommendations if AI is unavailable
    """
    
    # Try AI-powered recommendations first
    ai_recommendations = get_openai_recommendations(recent_sessions, pending_tasks)
    if ai_recommendations:
        return ai_recommendations
    
    # Fallback to rule-based recommendations
    return get_rule_based_recommendations(recent_sessions, pending_tasks)

def get_openai_recommendations(recent_sessions, pending_tasks) -> List[str]:
    """Get recommendations from OpenAI API"""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return None
    
    try:
        # Prepare data for AI analysis
        session_data = []
        for session in recent_sessions:
            session_data.append({
                'subject': session.subject,
                'duration': session.duration,
                'focus_rating': session.focus_rating,
                'date': session.date.isoformat()
            })
        
        task_data = []
        for task in pending_tasks:
            task_data.append({
                'title': task.title,
                'subject': task.subject,
                'priority': task.priority,
                'due_date': task.due_date.isoformat(),
                'difficulty': task.difficulty
            })
        
        # Create prompt for AI
        prompt = f"""
        Based on the following student data, provide 4-5 specific study recommendations:
        
        Recent Study Sessions: {session_data}
        Pending Tasks: {task_data}
        
        Please provide actionable recommendations focusing on:
        1. Study schedule optimization
        2. Subject prioritization
        3. Focus improvement techniques
        4. Time management strategies
        
        Return only the recommendations as a JSON array of strings.
        """
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'You are a study productivity expert helping students optimize their learning.'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 300,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse as JSON, fallback to splitting by lines
            try:
                import json
                recommendations = json.loads(content)
                return recommendations[:5]  # Limit to 5 recommendations
            except:
                # If JSON parsing fails, split by lines and clean up
                lines = content.strip().split('\n')
                recommendations = [line.strip('- ').strip() for line in lines if line.strip()]
                return recommendations[:5]
        
    except Exception as e:
        print(f"AI recommendation error: {e}")
        return None
    
    return None

def get_rule_based_recommendations(recent_sessions, pending_tasks) -> List[str]:
    """Generate rule-based study recommendations"""
    recommendations = []
    
    # Analyze recent study patterns
    if recent_sessions:
        avg_focus = sum(s.focus_rating for s in recent_sessions) / len(recent_sessions)
        total_study_time = sum(s.duration for s in recent_sessions)
        subjects_studied = set(s.subject for s in recent_sessions)
        
        # Focus-based recommendations
        if avg_focus < 6:
            recommendations.append("Try the Pomodoro technique (25min work, 5min break) to improve focus")
            recommendations.append("Consider studying in a quieter environment or using noise-canceling headphones")
        elif avg_focus > 8:
            recommendations.append("Great focus! Consider extending study sessions to 45-60 minutes")
        
        # Study time recommendations
        if total_study_time < 120:  # Less than 2 hours total
            recommendations.append("Aim to increase your daily study time gradually by 15-30 minutes")
        elif total_study_time > 480:  # More than 8 hours total
            recommendations.append("Take more breaks to avoid burnout - quality over quantity")
        
        # Subject diversity
        if len(subjects_studied) == 1:
            recommendations.append("Try alternating between different subjects to keep your mind engaged")
    
    # Task-based recommendations
    if pending_tasks:
        urgent_tasks = [t for t in pending_tasks if t.priority in ['high', 'urgent']]
        overdue_tasks = [t for t in pending_tasks if t.is_overdue()]
        
        if urgent_tasks:
            recommendations.append(f"Focus on {len(urgent_tasks)} high-priority tasks first")
        
        if overdue_tasks:
            recommendations.append("Address overdue tasks immediately to get back on track")
        
        # Due date analysis
        upcoming_tasks = [t for t in pending_tasks if t.days_until_due() <= 3]
        if upcoming_tasks:
            recommendations.append("Prioritize tasks due within the next 3 days")
    
    # General recommendations if no specific patterns found
    if not recommendations:
        recommendations = [
            "Set specific, measurable goals for each study session",
            "Use active recall techniques like flashcards or practice tests",
            "Take a 10-15 minute break every hour to maintain concentration",
            "Review material within 24 hours of first learning it",
            "Create a consistent study schedule and stick to it"
        ]
    
    return recommendations[:5]  # Return max 5 recommendations

def analyze_productivity_patterns(user_sessions) -> Dict:
    """Analyze user's productivity patterns"""
    if not user_sessions:
        return {}
    
    # Group sessions by day of week
    weekday_performance = {}
    for session in user_sessions:
        weekday = session.date.weekday()  # 0 = Monday, 6 = Sunday
        if weekday not in weekday_performance:
            weekday_performance[weekday] = []
        weekday_performance[weekday].append(session.focus_rating)
    
    # Calculate average focus by weekday
    weekday_avg = {}
    for day, ratings in weekday_performance.items():
        weekday_avg[day] = sum(ratings) / len(ratings)
    
    # Find best and worst days
    best_day = max(weekday_avg, key=weekday_avg.get) if weekday_avg else None
    worst_day = min(weekday_avg, key=weekday_avg.get) if weekday_avg else None
    
    # Time of day analysis (if we had time data)
    # This could be expanded with more detailed time tracking
    
    return {
        'weekday_performance': weekday_avg,
        'best_day': best_day,
        'worst_day': worst_day,
        'total_sessions': len(user_sessions),
        'avg_focus': sum(s.focus_rating for s in user_sessions) / len(user_sessions)
    }

def suggest_study_schedule(pending_tasks, available_hours_per_day=4) -> List[Dict]:
    """Suggest an optimal study schedule based on pending tasks"""
    if not pending_tasks:
        return []
    
    # Sort tasks by priority and due date
    sorted_tasks = sorted(pending_tasks, key=lambda t: (
        {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}[t.priority],
        t.due_date,
        -t.difficulty
    ))
    
    schedule = []
    current_date = datetime.now().date()
    
    for task in sorted_tasks[:10]:  # Limit to next 10 tasks
        # Calculate recommended study time based on difficulty and estimated hours
        recommended_time = min(task.estimated_hours, available_hours_per_day)
        
        # Suggest when to work on this task
        days_until_due = (task.due_date - current_date).days
        urgency_factor = max(1, days_until_due)
        
        schedule.append({
            'task_id': task.id,
            'task_title': task.title,
            'subject': task.subject,
            'recommended_time': recommended_time,
            'priority': task.priority,
            'due_date': task.due_date.isoformat(),
            'urgency_score': urgency_factor
        })
    
    return schedule