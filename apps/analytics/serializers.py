from rest_framework import serializers
from .models import ProductView, SalesReport

class ProductViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductView
        fields = ['id', 'product', 'customer', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']

class SalesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReport
        fields = ['id', 'date', 'total_orders', 'total_revenue', 'total_customers', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']