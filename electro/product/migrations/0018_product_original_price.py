# Generated by Django 5.0.6 on 2024-07-29 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_categoryoffer_productoffer_referraloffer'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='original_price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]