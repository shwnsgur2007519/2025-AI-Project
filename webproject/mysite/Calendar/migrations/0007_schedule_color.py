# Generated by Django 5.2 on 2025-05-04 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Calendar', '0006_schedule_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='color',
            field=models.CharField(blank=True, default='#6c8df5', max_length=7),
        ),
    ]
