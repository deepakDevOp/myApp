# Generated by Django 3.2.11 on 2024-03-09 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userPolls', '0014_alter_customuser_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_picture',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]