# Generated by Django 5.0.6 on 2024-08-04 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_userprofile_referral_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='referral_code',
        ),
    ]
