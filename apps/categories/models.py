from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    level = models.PositiveIntegerField(default=0)
    path = models.CharField(max_length=500, blank=True)
    
    display_name = models.CharField(max_length=100, blank=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, help_text="CSS class for icon")
    banner_image = models.ImageField(upload_to='categories/banners/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    show_in_menu = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_categories'
    )
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
            models.Index(fields=['level']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        if not self.display_name:
            self.display_name = self.name
        
        if self.parent:
            self.level = self.parent.level + 1
            self.path = f"{self.parent.path}/{self.slug}" if self.parent.path else self.slug
        else:
            self.level = 0
            self.path = self.slug
        
        super().save(*args, **kwargs)
    
    def get_ancestors(self):
        """Get all ancestors of this category"""
        ancestors = []
        category = self.parent
        while category:
            ancestors.append(category)
            category = category.parent
        return ancestors
    
    def get_descendants(self):
        """Get all descendants of this category"""
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_all_children_ids(self):
        """Get IDs of all descendant categories"""
        children_ids = [self.id]
        for child in self.children.all():
            children_ids.extend(child.get_all_children_ids())
        return children_ids
    
    def get_breadcrumb(self):
        """Get breadcrumb path"""
        breadcrumb = []
        for ancestor in reversed(self.get_ancestors()):
            breadcrumb.append(ancestor)
        breadcrumb.append(self)
        return breadcrumb
    
    @property
    def product_count(self):
        """Count of products in this category and all subcategories"""
        from apps.products.models import Product
        category_ids = self.get_all_children_ids()
        return Product.objects.filter(category_id__in=category_ids, is_active=True).count()

class CategoryAttribute(models.Model):
    """Attributes that can be associated with categories"""
    ATTRIBUTE_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('choice', 'Choice'),
        ('multi_choice', 'Multiple Choice'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100)
    attribute_type = models.CharField(max_length=20, choices=ATTRIBUTE_TYPES)
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)
    choices = models.JSONField(blank=True, null=True, help_text="For choice type attributes")
    default_value = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['category', 'name']
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"