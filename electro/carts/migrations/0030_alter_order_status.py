# Generated by Django 5.0.6 on 2024-07-28 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0029_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(default='Pending', max_length=20),
        ),
    ]