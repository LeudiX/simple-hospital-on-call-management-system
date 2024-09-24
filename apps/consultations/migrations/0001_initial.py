# Generated by Django 5.1.1 on 2024-09-22 09:05

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consultation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consultation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True, max_length=200, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultations_doctor', to='users.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultations_patient', to='users.patient')),
            ],
            options={
                'verbose_name': 'Consultation',
                'verbose_name_plural': 'Consultations',
                'constraints': [models.UniqueConstraint(fields=('doctor', 'patient', 'consultation_date'), name='unique_consultation')],
            },
        ),
    ]