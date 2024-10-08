# Generated by Django 5.0.6 on 2024-08-03 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_product_current_price_alter_product_original_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productoffer',
            name='product',
        ),
        migrations.RemoveField(
            model_name='product',
            name='current_price',
        ),
        migrations.AddField(
            model_name='product',
            name='offer_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='original_price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='CategoryOffer',
        ),
        migrations.DeleteModel(
            name='ProductOffer',
        ),
    ]
