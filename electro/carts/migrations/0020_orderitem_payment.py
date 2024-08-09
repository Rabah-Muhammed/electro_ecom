# Generated by Django 5.0.6 on 2024-07-26 13:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0019_order_is_ordered'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='carts.payment'),
        ),
    ]
