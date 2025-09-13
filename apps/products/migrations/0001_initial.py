
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('categories', '0001_initial'),
        ('customers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='brands/')),
                ('website', models.URLField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('short_description', models.TextField(blank=True, max_length=500)),
                ('description', models.TextField()),
                ('product_type', models.CharField(choices=[('simple', 'Simple Product'), ('variable', 'Variable Product'), ('grouped', 'Grouped Product'), ('external', 'External Product'), ('digital', 'Digital Product')], default='simple', max_length=20)),
                ('sku', models.CharField(max_length=100, unique=True)),
                ('barcode', models.CharField(blank=True, max_length=50)),
                ('upc', models.CharField(blank=True, max_length=20)),
                ('isbn', models.CharField(blank=True, max_length=20)),
                ('mpn', models.CharField(blank=True, help_text='Manufacturer Part Number', max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('cost_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('compare_at_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('wholesale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('track_inventory', models.BooleanField(default=True)),
                ('stock_quantity', models.PositiveIntegerField(default=0)),
                ('low_stock_threshold', models.PositiveIntegerField(default=5)),
                ('allow_backorders', models.BooleanField(default=False)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('length', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('width', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('condition', models.CharField(choices=[('new', 'New'), ('used', 'Used'), ('refurbished', 'Refurbished'), ('damaged', 'Damaged')], default='new', max_length=20)),
                ('warranty_period', models.PositiveIntegerField(blank=True, help_text='Warranty in months', null=True)),
                ('meta_title', models.CharField(blank=True, max_length=200)),
                ('meta_description', models.TextField(blank=True, max_length=500)),
                ('keywords', models.CharField(blank=True, max_length=500)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending Review'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_digital', models.BooleanField(default=False)),
                ('requires_shipping', models.BooleanField(default=True)),
                ('average_rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('review_count', models.PositiveIntegerField(default=0)),
                ('total_sales', models.PositiveIntegerField(default=0)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.brand')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='categories.category')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_products', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/')),
                ('alt_text', models.CharField(blank=True, max_length=200)),
                ('is_primary', models.BooleanField(default=False)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product')),
            ],
            options={
                'ordering': ['sort_order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('sku', models.CharField(max_length=100, unique=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('compare_at_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('stock_quantity', models.PositiveIntegerField(default=0)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='products.product')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('product', 'name')},
            },
        ),
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('title', models.CharField(max_length=200)),
                ('comment', models.TextField()),
                ('is_verified_purchase', models.BooleanField(default=False)),
                ('is_approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='products.product')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('product', 'customer')},
            },
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='products.product')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('product', 'name')},
            },
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['sku'], name='products_pr_sku_ca0cdc_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['slug'], name='products_pr_slug_3edc0c_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category'], name='products_pr_categor_9edb3d_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['brand'], name='products_pr_brand_i_dc6890_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['status'], name='products_pr_status_041708_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_active'], name='products_pr_is_acti_ca4d9a_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_featured'], name='products_pr_is_feat_a5d7cd_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['price'], name='products_pr_price_9b1a5f_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['created_at'], name='products_pr_created_52f0d7_idx'),
        ),
    ]