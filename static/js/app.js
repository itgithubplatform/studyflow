// StudyFlow Main JavaScript Application

class StudyFlowApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.loadUserStats();
        this.setupNotifications();
    }

    setupEventListeners() {
        // Global event listeners
        document.addEventListener('DOMContentLoaded', () => {
            this.animateElements();
            this.setupTooltips();
            this.setupModals();
        });

        // Task checkbox handlers
        document.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.handleTaskToggle(e.target);
            });
        });

        // Priority update handlers
        document.querySelectorAll('.priority-select').forEach(select => {
            select.addEventListener('change', (e) => {
                this.handlePriorityUpdate(e.target);
            });
        });

        // Quick actions
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    initializeComponents() {
        // Initialize charts if Chart.js is available
        if (typeof Chart !== 'undefined') {
            this.initializeCharts();
        }

        // Initialize calendar if FullCalendar is available
        if (typeof FullCalendar !== 'undefined') {
            this.initializeCalendar();
        }

        // Initialize progress bars
        this.animateProgressBars();

        // Initialize counters
        this.animateCounters();
    }

    // Task Management
    async handleTaskToggle(checkbox) {
        const taskId = checkbox.dataset.taskId;
        const isCompleted = checkbox.checked;

        try {
            this.showLoading(checkbox.parentElement);

            const response = await fetch(`/api/tasks/${taskId}/toggle-status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.updateTaskUI(checkbox, data.status);
                
                if (data.points_earned > 0) {
                    this.showPointsAnimation(data.points_earned);
                }
            } else {
                checkbox.checked = !isCompleted; // Revert checkbox
                this.showNotification('Failed to update task', 'error');
            }
        } catch (error) {
            console.error('Error toggling task:', error);
            checkbox.checked = !isCompleted; // Revert checkbox
            this.showNotification('Network error occurred', 'error');
        } finally {
            this.hideLoading(checkbox.parentElement);
        }
    }

    async handlePriorityUpdate(select) {
        const taskId = select.dataset.taskId;
        const priority = select.value;

        try {
            const response = await fetch(`/api/tasks/${taskId}/update-priority`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ priority })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Priority updated', 'success');
                this.updatePriorityUI(select, priority);
            } else {
                this.showNotification('Failed to update priority', 'error');
            }
        } catch (error) {
            console.error('Error updating priority:', error);
            this.showNotification('Network error occurred', 'error');
        }
    }

    updateTaskUI(checkbox, status) {
        const taskItem = checkbox.closest('.task-item');
        const taskTitle = taskItem.querySelector('.task-title');

        if (status === 'completed') {
            taskItem.classList.add('completed');
            taskTitle.style.textDecoration = 'line-through';
            taskTitle.style.opacity = '0.7';
        } else {
            taskItem.classList.remove('completed');
            taskTitle.style.textDecoration = 'none';
            taskTitle.style.opacity = '1';
        }
    }

    updatePriorityUI(select, priority) {
        const badge = select.parentElement.querySelector('.priority-badge');
        if (badge) {
            badge.className = `badge priority-${priority}`;
            badge.textContent = priority.charAt(0).toUpperCase() + priority.slice(1);
        }
    }

    // Charts and Analytics
    initializeCharts() {
        // Study hours chart
        const studyChartCtx = document.getElementById('studyHoursChart');
        if (studyChartCtx) {
            this.createStudyHoursChart(studyChartCtx);
        }

        // Subject distribution chart
        const subjectChartCtx = document.getElementById('subjectChart');
        if (subjectChartCtx) {
            this.createSubjectChart(subjectChartCtx);
        }

        // Progress trend chart
        const progressChartCtx = document.getElementById('progressChart');
        if (progressChartCtx) {
            this.createProgressChart(progressChartCtx);
        }
    }

    async createStudyHoursChart(ctx) {
        try {
            const response = await fetch('/api/dashboard-stats');
            const data = await response.json();

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.weekly_stats.map(d => 
                        new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' })
                    ),
                    datasets: [{
                        label: 'Study Hours',
                        data: data.weekly_stats.map(d => d.hours),
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error creating study hours chart:', error);
        }
    }

    async createSubjectChart(ctx) {
        try {
            const response = await fetch('/api/analytics/chart-data?type=subjects');
            const data = await response.json();

            const colors = [
                '#0d6efd', '#198754', '#ffc107', '#dc3545', 
                '#0dcaf0', '#6f42c1', '#fd7e14', '#20c997'
            ];

            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.map(d => d.subject),
                    datasets: [{
                        data: data.map(d => d.hours),
                        backgroundColor: colors.slice(0, data.length),
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error creating subject chart:', error);
        }
    }

    // Calendar Integration
    initializeCalendar() {
        const calendarEl = document.getElementById('calendar');
        if (!calendarEl) return;

        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,listWeek'
            },
            events: '/api/tasks',
            eventClick: (info) => {
                this.showTaskDetails(info.event);
            },
            dateClick: (info) => {
                this.showAddTaskModal(info.date);
            }
        });

        calendar.render();
    }

    // Animations and UI Effects
    animateElements() {
        // Animate cards on page load
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('fade-in');
            }, index * 100);
        });

        // Animate stats numbers
        this.animateCounters();
    }

    animateCounters() {
        const counters = document.querySelectorAll('.stats-number');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent);
            const increment = target / 50;
            let current = 0;

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = target;
                    clearInterval(timer);
                } else {
                    counter.textContent = Math.floor(current);
                }
            }, 20);
        });
    }

    animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.width = width;
            }, 500);
        });
    }

    showPointsAnimation(points) {
        const pointsEl = document.createElement('div');
        pointsEl.className = 'points-animation';
        pointsEl.textContent = `+${points} points!`;
        pointsEl.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #ffc107, #fd7e14);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1.2rem;
            z-index: 9999;
            animation: pointsBounce 2s ease-out forwards;
        `;

        document.body.appendChild(pointsEl);

        setTimeout(() => {
            pointsEl.remove();
        }, 2000);
    }

    // Notifications
    setupNotifications() {
        // Request notification permission
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }

        // Setup service worker for background notifications
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/sw.js')
                .catch(error => console.log('SW registration failed'));
        }
    }

    showNotification(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        const container = document.querySelector('.toast-container') || this.createToastContainer();
        container.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Auto remove after showing
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    }

    // Utility Functions
    showLoading(element) {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.style.marginLeft = '10px';
        element.appendChild(spinner);
    }

    hideLoading(element) {
        const spinner = element.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }

    setupTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    setupModals() {
        // Auto-focus first input in modals
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                const firstInput = modal.querySelector('input, textarea, select');
                if (firstInput) {
                    firstInput.focus();
                }
            });
        });
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K for quick task add
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const quickTaskModal = document.getElementById('quickTaskModal');
            if (quickTaskModal) {
                new bootstrap.Modal(quickTaskModal).show();
            }
        }

        // Ctrl/Cmd + P for Pomodoro
        if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
            e.preventDefault();
            window.location.href = '/pomodoro';
        }
    }

    async loadUserStats() {
        try {
            const response = await fetch('/api/user/stats');
            const data = await response.json();
            
            if (data.success) {
                this.updateUserStatsUI(data.stats);
            }
        } catch (error) {
            console.error('Error loading user stats:', error);
        }
    }

    updateUserStatsUI(stats) {
        // Update points display in navbar
        const pointsDisplay = document.querySelector('.navbar .badge');
        if (pointsDisplay) {
            pointsDisplay.innerHTML = `<i class="bi bi-star-fill me-1"></i>${stats.total_points} pts`;
        }

        // Update level progress
        const levelProgress = document.querySelector('.level-progress');
        if (levelProgress) {
            levelProgress.style.width = `${stats.progress_percentage}%`;
        }
    }
}

// Utility Functions
function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours > 0) {
        return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function getTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

// CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes pointsBounce {
        0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
        50% { transform: translate(-50%, -50%) scale(1.2); opacity: 1; }
        100% { transform: translate(-50%, -50%) scale(1) translateY(-100px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.studyFlowApp = new StudyFlowApp();
});

// Export for use in other scripts
window.StudyFlowApp = StudyFlowApp;