# Generated by Django 3.2.11 on 2024-03-06 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userPolls', '0011_auto_20240306_0334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
    ]