from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer, CategoryNestedSerializer
from apps.products.models import Product

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Get categories in a tree structure
        """
        root_categories = Category.objects.filter(parent=None)
        serializer = CategoryNestedSerializer(root_categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """
        Get all products in a category and its subcategories
        """
        category = self.get_object()
        descendants = category.get_descendants()
        category_ids = [category.id] + [desc.id for desc in descendants]
        products = Product.objects.filter(category_id__in=category_ids)
        
        from apps.products.serializers import ProductSerializer
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def average_price(self, request, slug=None):
        """
        Get the average price of products in a category and its subcategories
        """
        category = self.get_object()
        descendants = category.get_descendants()
        category_ids = [category.id] + [desc.id for desc in descendants]
        products = Product.objects.filter(category_id__in=category_ids)
        
        if not products.exists():
            return Response({"average_price": 0})
        
        total_price = sum(product.price for product in products)
        average_price = total_price / products.count()
        
        return Response({"average_price": average_price})