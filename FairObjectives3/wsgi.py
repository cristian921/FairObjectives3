"""
WSGI config for FairObjectives3 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FairObjectives3.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root='static/')
#application.add_files('/path/to/more/static/files', prefix='more-files/')
