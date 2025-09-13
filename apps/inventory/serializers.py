from rest_framework import serializers
from .models import InventoryTransaction, StockAlert
from apps.products.serializers import ProductSerializer

class InventoryTransactionSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = ['id', 'product', 'product_details', 'transaction_type', 'quantity', 
                  'reference_number', 'notes', 'created_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'created_by']

class StockAlertSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = StockAlert
        fields = ['id', 'product', 'product_details', 'alert_type', 'threshold', 
                  'is_active', 'last_triggered', 'created_at']
        read_only_fields = ['id', 'last_triggered', 'created_at']