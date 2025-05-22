from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optalim.settings')

from django.conf import settings

app = Celery('optalim')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "celery_alive": {"task": "common.tasks.celery_alive", "schedule": crontab(minute="*")},
    "update_metabolisms": {"task": "diet_mgr.tasks.update_metabolisms", "schedule": crontab(minute=0, hour=9)},
    "remind_weight_update": {"task": "diet_mgr.tasks.remind_weight_update", "schedule": crontab(minute=0, hour=10)},
    "remove_old_logs": {"task": "hippocrate.tasks.remove_old_logs", "schedule": crontab(hour=5, minute=42)},
    "send_planning_reminder": {"task": "planning_mgr.tasks.send_planning_reminder", "schedule": crontab(minute=0, hour=18)},
    "send_meals_suggestion": {"task": "planning_mgr.tasks.send_meals_suggestion", "schedule": crontab(minute=30, hour=5, day_of_month='7,21')},
    "send_meals_reminder": {"task": "planning_mgr.tasks.send_meals_reminder", "schedule": crontab(minute=0, hour=5)},
    "delete_old_plannings": {"task": "planning_mgr.tasks.delete_old_plannings", "schedule": crontab(minute=0, hour=2)},
    "update_seasonality": {"task": "recipe_mgr.tasks.update_seasonality", "schedule": crontab(minute=0, hour=5)},
    "update_recipe_ratings": {"task": "recipe_mgr.tasks.update_recipe_ratings", "schedule": crontab(minute=10, hour=5)},
    "delete_expired_tokens": {"task": "user_mgr.tasks.delete_expired_tokens", "schedule": crontab(minute=20, hour=12)},
    "expired_subscription_email": {"task": "user_mgr.tasks.expired_subscription_email", "schedule": crontab(minute=0, hour=1)},
}
