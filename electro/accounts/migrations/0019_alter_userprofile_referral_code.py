# Generated by Django 5.0.6 on 2024-08-04 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_userprofile_referral_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='referral_code',
            field=models.CharField(blank=True, max_length=12, null=True, unique=True),
        ),
    ]
