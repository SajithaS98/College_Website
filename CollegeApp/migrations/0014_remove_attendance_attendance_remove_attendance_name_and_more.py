# Generated by Django 5.1.2 on 2025-01-07 09:38

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CollegeApp', '0013_remove_student_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='attendance',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='name',
        ),
        migrations.AddField(
            model_name='attendance',
            name='batch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='CollegeApp.batch'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='attendance',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='batch',
            name='end_date',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='batch',
            name='start_date',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='AttendanceReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('attendance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CollegeApp.attendance')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='CollegeApp.student')),
            ],
        ),
        migrations.CreateModel(
            name='StudentAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('attendance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_attendance', to='CollegeApp.attendance')),
                ('student', models.ForeignKey(limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CollegeApp.course')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CollegeApp.faculty')),
            ],
        ),
        migrations.AddField(
            model_name='attendance',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='CollegeApp.subject'),
        ),
    ]
