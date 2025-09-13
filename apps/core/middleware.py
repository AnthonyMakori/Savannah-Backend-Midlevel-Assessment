from django.http import JsonResponse
from django.urls import resolve
import logging

logger = logging.getLogger(__name__)

class HealthCheckMiddleware:
    """Middleware for health checks and monitoring"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/health/':
            return JsonResponse({
                'status': 'healthy',
                'service': 'Anthony Store API',
                'version': '1.0.0'
            })
        
        response = self.get_response(request)
        return response