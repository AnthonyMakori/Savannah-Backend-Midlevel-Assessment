
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('level', models.PositiveIntegerField(default=0)),
                ('path', models.CharField(blank=True, max_length=500)),
                ('display_name', models.CharField(blank=True, max_length=100)),
                ('meta_title', models.CharField(blank=True, max_length=200)),
                ('meta_description', models.TextField(blank=True, max_length=500)),
                ('keywords', models.CharField(blank=True, max_length=500)),
                ('image', models.ImageField(blank=True, null=True, upload_to='categories/')),
                ('icon', models.CharField(blank=True, help_text='CSS class for icon', max_length=100)),
                ('banner_image', models.ImageField(blank=True, null=True, upload_to='categories/banners/')),
                ('is_active', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('show_in_menu', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('commission_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_categories', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='categories.category')),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CategoryAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('attribute_type', models.CharField(choices=[('text', 'Text'), ('number', 'Number'), ('boolean', 'Boolean'), ('date', 'Date'), ('choice', 'Choice'), ('multi_choice', 'Multiple Choice')], max_length=20)),
                ('is_required', models.BooleanField(default=False)),
                ('is_filterable', models.BooleanField(default=False)),
                ('choices', models.JSONField(blank=True, help_text='For choice type attributes', null=True)),
                ('default_value', models.CharField(blank=True, max_length=255)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='categories.category')),
            ],
            options={
                'ordering': ['sort_order', 'name'],
                'unique_together': {('category', 'name')},
            },
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['slug'], name='categories__slug_9b1a28_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['parent'], name='categories__parent__91c7d9_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['level'], name='categories__level_f4d924_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['is_active'], name='categories__is_acti_3ca3e4_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['is_featured'], name='categories__is_feat_283251_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['sort_order'], name='categories__sort_or_ac4749_idx'),
        ),
    ]