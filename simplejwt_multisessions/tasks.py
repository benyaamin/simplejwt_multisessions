from celery                                             import shared_task
from django.utils                                       import timezone
import datetime


# import json
# import requests
# from requests.models    import Response

from datetime                                           import datetime, timedelta
from multiprocessing                                    import Process
import time


# app = Celery('ProjectX')
# app.config_from_object('django.conf:settings', namespace='CELERY')


# app.autodiscover_tasks()


@shared_task(name="clean_sessions")
# @shared_task
def sample_task():
    print("hi it is just a sample task")