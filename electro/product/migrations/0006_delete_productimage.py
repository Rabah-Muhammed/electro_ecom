# Generated by Django 5.0.6 on 2024-06-30 18:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_productimage'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductImage',
        ),
    ]