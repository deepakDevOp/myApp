# Generated by Django 3.2.11 on 2024-03-09 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userPolls', '0017_auto_20240309_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='profile_pic_url',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
