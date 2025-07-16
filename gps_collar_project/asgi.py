"""
ASGI config for gps_collar_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""


import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gps_collar_project.settings')

application = get_asgi_application()

'''

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import api_app.routing  # ganti sesuai nama app kamu

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gps_collar_project.settings')
django.setup()  # INI WAJIB

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api_app.routing.websocket_urlpatterns
        )
    ),
})
'''