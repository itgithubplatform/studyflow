from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField, DateField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from datetime import date
from app.models import User

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class TaskForm(FlaskForm):
    """Task creation and editing form"""
    title = StringField('Task Title', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=1, max=100)])
    
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    
    difficulty = IntegerField('Difficulty (1-5)', validators=[
        DataRequired(), NumberRange(min=1, max=5)
    ], default=3)
    
    estimated_hours = FloatField('Estimated Hours', validators=[
        DataRequired(), NumberRange(min=0.1, max=24)
    ], default=1.0)
    
    due_date = DateField('Due Date', validators=[DataRequired()], default=date.today)
    
    category = SelectField('Category', choices=[
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('exam', 'Exam Preparation'),
        ('reading', 'Reading'),
        ('research', 'Research'),
        ('other', 'Other')
    ], default='assignment')
    
    submit = SubmitField('Save Task')
    
    def validate_due_date(self, due_date):
        if due_date.data < date.today():
            raise ValidationError('Due date cannot be in the past.')

class StudySessionForm(FlaskForm):
    """Study session logging form"""
    subject = StringField('Subject', validators=[DataRequired(), Length(min=1, max=100)])
    duration = IntegerField('Duration (minutes)', validators=[
        DataRequired(), NumberRange(min=1, max=480)  # Max 8 hours
    ])
    
    session_type = SelectField('Session Type', choices=[
        ('regular', 'Regular Study'),
        ('pomodoro', 'Pomodoro'),
        ('intensive', 'Intensive Study'),
        ('review', 'Review Session')
    ], default='regular')
    
    focus_rating = IntegerField('Focus Rating (1-10)', validators=[
        DataRequired(), NumberRange(min=1, max=10)
    ], default=5)
    
    notes = TextAreaField('Notes', validators=[Length(max=500)])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    task_id = SelectField('Related Task (Optional)', coerce=int)
    
    submit = SubmitField('Log Session')
    
    def validate_date(self, date_field):
        if date_field.data > date.today():
            raise ValidationError('Session date cannot be in the future.')

class ProfileForm(FlaskForm):
    """User profile editing form"""
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    study_goal_hours = IntegerField('Daily Study Goal (hours)', validators=[
        NumberRange(min=1, max=12)
    ], default=2)
    email_notifications = BooleanField('Email Notifications')
    submit = SubmitField('Update Profile')

class QuickTaskForm(FlaskForm):
    """Quick task addition form for dashboard"""
    title = StringField('Task Title', validators=[DataRequired(), Length(min=1, max=200)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=1, max=100)])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    due_date = DateField('Due Date', validators=[DataRequired()], default=date.today)
    submit = SubmitField('Add Task')

class PomodoroForm(FlaskForm):
    """Pomodoro session configuration form"""
    subject = StringField('Subject', validators=[DataRequired(), Length(min=1, max=100)])
    task_id = SelectField('Related Task (Optional)', coerce=int)
    work_duration = IntegerField('Work Duration (minutes)', validators=[
        NumberRange(min=15, max=60)
    ], default=25)
    break_duration = IntegerField('Break Duration (minutes)', validators=[
        NumberRange(min=5, max=30)
    ], default=5)
    cycles = IntegerField('Number of Cycles', validators=[
        NumberRange(min=1, max=8)
    ], default=4)
    submit = SubmitField('Start Pomodoro')