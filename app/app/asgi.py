"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

django_asgi_app = get_asgi_application()

class ASGIMediaFilesHandler(ASGIStaticFilesHandler):
    def get_base_url(self):
        return settings.MEDIA_URL

    def _should_handle(self, path):
        return path.startswith(self.get_base_url())

if settings.DEBUG:
    django_asgi_app = ASGIStaticFilesHandler(ASGIMediaFilesHandler(django_asgi_app))

# Import routing after Django setup to avoid AppRegistryNotReady
from .routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
