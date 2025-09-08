#!/usr/bin/env python3
"""
Simple run script for StudyFlow application
Use this for quick development testing
"""

from app import create_app

if __name__ == '__main__':
    app = create_app('development')
    print("🚀 Starting StudyFlow in Development Mode...")
    print("📊 Access the application at: http://localhost:5000")
    print("👤 Demo account: username='demo', password='demo123'")
    app.run(debug=True, host='0.0.0.0', port=5000)