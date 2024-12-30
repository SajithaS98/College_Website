# Generated by Django 5.1.2 on 2024-12-19 06:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CollegeApp', '0003_attendance_hod_faculty'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='is_varified',
            new_name='is_verified',
        ),
        migrations.RemoveField(
            model_name='batch',
            name='name',
        ),
        migrations.RemoveField(
            model_name='course',
            name='name',
        ),
        migrations.RemoveField(
            model_name='department',
            name='name',
        ),
        migrations.AddField(
            model_name='batch',
            name='batch_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='course_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CollegeApp.batch'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CollegeApp.course'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CollegeApp.department'),
        ),
        migrations.AddField(
            model_name='department',
            name='department_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]