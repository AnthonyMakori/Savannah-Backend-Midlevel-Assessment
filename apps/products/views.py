from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get products filtered by category slug
        """
        category_slug = request.query_params.get('slug', None)
        if not category_slug:
            return Response({"error": "Category slug is required"}, status=400)
        
        from apps.categories.models import Category
        try:
            category = Category.objects.get(slug=category_slug)
            descendants = category.get_descendants()
            category_ids = [category.id] + [desc.id for desc in descendants]
            products = Product.objects.filter(category_id__in=category_ids)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)