# Generated by Django 5.0.6 on 2024-07-09 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0007_cart_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='user',
        ),
    ]
