# Generated by Django 5.0.6 on 2024-08-04 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_userprofile_referral_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='referral_code',
        ),
    ]
