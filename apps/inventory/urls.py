from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryTransactionViewSet, StockAlertViewSet

router = DefaultRouter()
router.register(r'transactions', InventoryTransactionViewSet, basename='inventory-transaction')
router.register(r'alerts', StockAlertViewSet, basename='stock-alert')

urlpatterns = [
    path('', include(router.urls)),
]
