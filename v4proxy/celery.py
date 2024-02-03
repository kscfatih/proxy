import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'v4proxy.settings')

app = Celery('v4proxy')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
