from rest_framework import serializers
from .models import Order, OrderItem
from apps.customers.serializers import CustomerSerializer
from apps.products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_details', 'quantity', 'price', 'subtotal']
        read_only_fields = ['id', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_details', 'status', 'total_amount', 
                  'shipping_address', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if items_data is not None:
            instance.items.all().delete()
            
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
        
        return instance