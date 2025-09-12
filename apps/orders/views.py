from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from apps.customers.permissions import IsCustomerOwner, IsAdminUser

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomerOwner | IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        try:
            customer = user.customer
            return Order.objects.filter(customer=customer)
        except:
            return Order.objects.none()
    
    def perform_create(self, serializer):
        try:
            customer = self.request.user.customer
            serializer.save(customer=customer)
        except:
            raise serializers.ValidationError("Customer profile not found")
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """
        Get orders for the current authenticated customer
        """
        try:
            customer = request.user.customer
            orders = Order.objects.filter(customer=customer)
            serializer = self.get_serializer(orders, many=True)
            return Response(serializer.data)
        except:
            return Response({"detail": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)
