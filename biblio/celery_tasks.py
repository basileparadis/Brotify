from __future__ import absolute_import
from celery import Celery

app = Celery('brotify',
             broker='amqp://basile:Ddd12345@localhost/brotify_vhost',
             backend='rpc://',
             include=['test_celery.tasks'])

#@app.task