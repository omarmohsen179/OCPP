"""
ASGI config for ev_station project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from charging.consumers import OCPPConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ev_station.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([
        path('ws/ocpp/<str:charge_point_id>', OCPPConsumer.as_asgi()),
    ]),
})
