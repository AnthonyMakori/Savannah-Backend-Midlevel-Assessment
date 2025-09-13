
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
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('P', 'Prefer not to say')], max_length=1)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('age', models.PositiveIntegerField(blank=True, null=True)),
                ('id_number', models.CharField(max_length=20, unique=True, validators=[django.core.validators.RegexValidator('^\\d{8,20}$', 'Enter a valid ID number')])),
                ('passport_number', models.CharField(blank=True, max_length=20)),
                ('phone_number', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator('^\\+?1?\\d{9,15}$', 'Enter a valid phone number')])),
                ('alternative_phone', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('address_line_1', models.CharField(max_length=255)),
                ('address_line_2', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('state_province', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('country', models.CharField(default='Kenya', max_length=100)),
                ('company_name', models.CharField(blank=True, max_length=200)),
                ('tax_number', models.CharField(blank=True, max_length=50)),
                ('business_registration_number', models.CharField(blank=True, max_length=50)),
                ('customer_type', models.CharField(choices=[('individual', 'Individual'), ('business', 'Business'), ('premium', 'Premium'), ('vip', 'VIP')], default='individual', max_length=20)),
                ('is_verified', models.BooleanField(default=False)),
                ('verification_date', models.DateTimeField(blank=True, null=True)),
                ('preferred_language', models.CharField(default='en', max_length=10)),
                ('preferred_currency', models.CharField(default='KES', max_length=3)),
                ('marketing_consent', models.BooleanField(default=False)),
                ('sms_notifications', models.BooleanField(default=True)),
                ('email_notifications', models.BooleanField(default=True)),
                ('credit_limit', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('loyalty_points', models.PositiveIntegerField(default=0)),
                ('total_spent', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True, help_text='Internal notes about the customer')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CustomerAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_type', models.CharField(choices=[('home', 'Home'), ('work', 'Work'), ('billing', 'Billing'), ('shipping', 'Shipping'), ('other', 'Other')], max_length=20)),
                ('label', models.CharField(help_text='Custom label for this address', max_length=100)),
                ('address_line_1', models.CharField(max_length=255)),
                ('address_line_2', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('state_province', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=100)),
                ('is_default', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='customers.customer')),
            ],
            options={
                'ordering': ['-is_default', '-created_at'],
                'unique_together': {('customer', 'address_type', 'label')},
            },
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['customer_id'], name='customers_c_custome_ec5e63_idx'),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['id_number'], name='customers_c_id_numb_543491_idx'),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['phone_number'], name='customers_c_phone_n_cabfe1_idx'),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['email'], name='customers_c_email_4fdeb3_idx'),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['customer_type'], name='customers_c_custome_47da94_idx'),
        ),
    ]