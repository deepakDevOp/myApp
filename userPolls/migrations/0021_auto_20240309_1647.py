# Generated by Django 3.2.11 on 2024-03-09 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userPolls', '0020_alter_eventlist_event_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventlist',
            name='event_id',
        ),
        migrations.AddField(
            model_name='eventlist',
            name='id',
            field=models.BigAutoField(auto_created=True, default=None, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]