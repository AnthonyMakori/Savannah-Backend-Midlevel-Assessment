import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

app = application  # For compatibility with some WSGI servers that expect 'app' to be the WSGI callable
