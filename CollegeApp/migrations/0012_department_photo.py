# Generated by Django 5.1.2 on 2025-01-02 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CollegeApp', '0011_remove_department_course_department_courses'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='department_photos/'),
        ),
    ]
