# myproject/myapp/celery.py

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VideoProcessor.settings')

# Initialize Celery application
app = Celery('SubtitleProcess')

# Using Django settings for Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all apps, must be done after app is created
app.autodiscover_tasks()
