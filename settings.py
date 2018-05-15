import os

"""
import sys

PROJECT_ROOT = os.path.dirname(__file__)
PARENT_ROOT = os.path.dirname(PROJECT_ROOT)

sys.path.insert(0, os.path.join(PARENT_ROOT, '..', 'roma'))
sys.path.insert(0, PARENT_ROOT)
"""

from roma import settings
from settings import *
PROJECT_ROOT = os.path.dirname(__file__)
PARENT_ROOT = os.path.dirname(PROJECT_ROOT)

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append('fairvillage')

ONLINE_DOMAIN = 'www.fairvillage.eu'
SITE_NAME = 'FairVillage'
DEFAULT_FROM_EMAIL = 'FairVillage <noreply@linkroma.it>'
ROOT_URLCONF = 'fairvillage.urls'

# WSGI_APPLICATION = 'fairvillage.wsgi.application'

STATIC_ROOT = os.path.join(PARENT_ROOT, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(PARENT_ROOT, 'media')
MEDIA_URL = '/media/'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            # sys.platform.count('linux') and '/home/ubuntu/django/fairvillage/fairvillage/templates' or '/django/fairvillage/fairvillage/templates',
            os.path.join(PROJECT_ROOT, 'templates'),
        ),
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug', # MMR added
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.csrf',
                'django.contrib.messages.context_processors.messages',
                # 'richtext_blog.context_processors.blog_global',
                'roma.context_processors.context_processor',
                # "allauth.account.context_processors.account",
                # "allauth.socialaccount.context_processors.socialaccount",
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

if SEARCH_BACKEND == 'whoosh':
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': os.path.join(PARENT_ROOT, 'whoosh_index'),
        },
    }
elif SEARCH_BACKEND == 'solr':
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://localhost:8080/solr',
        },
    }

# Cache backend is optional, but recommended to speed up user agent parsing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    },
    'custom': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(PARENT_ROOT, 'cache/base'),
        'TIMEOUT': 24*60*60,
        'MAX_ENTRIES': 10,
    },
    'pois': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(PARENT_ROOT, 'cache/pois'),
        'TIMEOUT': 7*24*60*60,
        'MAX_ENTRIES': 1000,
    },
    'themes': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(PARENT_ROOT, 'cache/themes'),
        'TIMEOUT': 7*24*60*60,
        'MAX_ENTRIES': 50,
    },
    'categories': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(PARENT_ROOT, 'cache/categories'),
        'TIMEOUT': 7*24*60*60,
        'MAX_ENTRIES': 500,
    },
    'zones': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(PARENT_ROOT, 'cache/zones'),
        'TIMEOUT': 7*24*60*60,
        'MAX_ENTRIES': 500,
    },
    'zonemaps': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(PARENT_ROOT, 'cache/zonemaps'),
        'TIMEOUT': 7*24*60*60,
        'MAX_ENTRIES': 500,
    },
    'catzones': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(PARENT_ROOT, 'cache/catzones'),
        'TIMEOUT': 7*24*60*60,
        'MAX_ENTRIES': 2000,
    },
    'streets': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(PARENT_ROOT, 'cache/streets'),
        'TIMEOUT': 7*24*60*60,
        'MAX_ENTRIES': 1000,
    },
}

# POITYPE_SLUGS = ['assistenza-a-stranieri-e-immigrati', 'biblioteche-comunali', 'rilascio-tessera-sanitaria-stp', 'case-della-salute', 'consultori-familiari', 'italiano-per-stranieri', 'uffici-di-collocamento', 'centri-per-limmigrazione', 'ethnic-communities',]
POITYPE_SLUGS = ['assistenza-a-stranieri-e-immigrati', 'biblioteche', 'rilascio-tessera-sanitaria-stp', 'case-della-salute', 'consultori-familiari', 'italiano-per-stranieri', 'asili-nido-spazi-bebi', 'scuole-dell-infanzia','scuole-primarie-elementari',]
