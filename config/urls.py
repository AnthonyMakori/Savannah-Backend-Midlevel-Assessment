from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Anthony Store API",
        default_version='v1',
        description="""
        
        A comprehensive e-commerce backend service built with Django REST Framework.
        
        Your one-stop shop for quality products with excellent customer service.
        
        **Contact Information:**
        - Email: anthonymakori2@gmail.com
        - Phone: +254707497200
        - Location: Nairobi, Kenya
        
        - User authentication and authorization (OAuth2/OpenID Connect)
        - Customer management with detailed profiles
        - Hierarchical product categories (unlimited depth)
        - Product management with inventory tracking
        - Order processing with SMS and email notifications
        - Analytics and reporting
        - RESTful API with comprehensive documentation
        
        This API supports multiple authentication methods:
        - **Token Authentication**: Use `Authorization: Token <your-token>` header
        - **Session Authentication**: Login through the browsable API
        - **OAuth2/OpenID Connect**: For third-party integrations
        
        You can test the API using:
        - This Swagger UI interface
        - Postman collection (available in the repository)
        - cURL commands
        - Python requests library
        
        For support, please contact: anthonymakori2@gmail.com
        """,
        terms_of_service="https://Anthony-store.com/terms/",
        contact=openapi.Contact(email="anthonymakori2@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', RedirectView.as_view(url='/swagger/', permanent=False), name='index'),
    
    path('health/', include('apps.core.urls')),
    
    path('api/', include(router.urls)),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Anthony Store Administration"
admin.site.site_title = "Anthony Store Admin"
admin.site.index_title = "Welcome to Anthony Store Administration"