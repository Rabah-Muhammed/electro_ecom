# Generated by Django 5.0.6 on 2024-08-04 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_remove_userprofile_referral_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='referral_code',
            field=models.CharField(null=True, max_length=12, unique=True),
        ),
    ]
