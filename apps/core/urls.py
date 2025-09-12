from django.urls import path
from .views import health_check, system_info

urlpatterns = [
    path('', health_check, name='health-check'),
    path('info/', system_info, name='system-info'),
]
