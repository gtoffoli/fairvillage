"""
WSGI config for fairvillage project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

"""
import os, sys

# see: http://stackoverflow.com/questions/10752031/django-1-4-with-apache-virtualhost-path-problems
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)
path = '/home/ubuntu/django/roma'
if path not in sys.path:
    sys.path.append(path)
path = '/home/ubuntu/django/lib/python2.7/site-packages'
if path not in sys.path:
    sys.path.append(path)
"""

import os

from django.core.wsgi import get_wsgi_application

"""
# see: http://stackoverflow.com/questions/11383176/problems-hosting-multiple-django-sites-settings-cross-over
# change the env variable where django looks for the settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fairvillage.settings")
"""
import django.conf
import fairvillage
django.conf.ENVIRONMENT_VARIABLE = "DJANGO_FV_SETTINGS_MODULE"
os.environ.setdefault("DJANGO_FV_SETTINGS_MODULE", "fairvillage.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
