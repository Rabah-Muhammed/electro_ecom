# Generated by Django 5.0.6 on 2024-08-04 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_auto_20240804_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='referral_code',
            field=models.CharField(blank=True, max_length=12, unique=True,null=True),
        ),
    ]