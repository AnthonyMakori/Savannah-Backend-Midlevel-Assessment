from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum
from .models import ProductView, SalesReport
from .serializers import ProductViewSerializer, SalesReportSerializer
from apps.orders.models import Order
from apps.products.models import Product

class ProductViewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductView.objects.all()
    serializer_class = ProductViewSerializer
    permission_classes = [permissions.IsAdminUser]

class SalesReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        total_products = Product.objects.filter(is_active=True).count()
        
        return Response({
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_products': total_products,
            'business_info': {
                'name': 'Anthony Store',
                'contact': '+2547707497200',
                'email': 'anthonymakori2@gmail.com'
            }
        })