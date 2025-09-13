from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewViewSet, SalesReportViewSet

router = DefaultRouter()
router.register(r'views', ProductViewViewSet, basename='product-view')
router.register(r'reports', SalesReportViewSet, basename='sales-report')

urlpatterns = [
    path('', include(router.urls)),
]