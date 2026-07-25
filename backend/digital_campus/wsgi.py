"""
WSGI config for digital_campus project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

# Ensure both backend and root directories are in the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)
for p in (backend_dir, root_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_campus.settings')

application = get_wsgi_application()

# Vercel needs "app" variable
app = application
