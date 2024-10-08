# Generated by Django 5.1.1 on 2024-10-02 17:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0003_alter_consultation_consultation_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultation',
            name='consultation_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 2, 11, 34, 44, 737338, tzinfo=datetime.timezone.utc), help_text='Consultation current time'),
        ),
    ]