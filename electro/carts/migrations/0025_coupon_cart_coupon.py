# Generated by Django 5.0.6 on 2024-07-27 06:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0024_remove_order_coupon_remove_cart_coupon_delete_coupon'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount', models.FloatField(help_text='Percentage discount for this coupon')),
                ('active', models.BooleanField(default=True)),
                ('minimum_amount', models.DecimalField(decimal_places=2, help_text='Minimum cart amount required to use this coupon', max_digits=10)),
                ('expiry_date', models.DateField(help_text='The date when the coupon expires')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='carts.coupon'),
        ),
    ]