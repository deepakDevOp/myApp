# Generated by Django 3.2.11 on 2024-05-11 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=50)),
                ('host_name', models.CharField(blank=True, max_length=50)),
                ('event_type', models.CharField(blank=True, max_length=50)),
                ('event_host_day', models.CharField(max_length=50)),
                ('event_subtext', models.TextField(blank=True)),
                ('event_description', models.TextField(blank=True)),
                ('eventid', models.CharField(blank=True, max_length=100)),
                ('phone_number', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='EventList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=100)),
            ],
        ),
    ]