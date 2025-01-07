# Generated by Django 5.1.2 on 2024-12-31 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CollegeApp', '0010_department_course_alter_department_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='course',
        ),
        migrations.AddField(
            model_name='department',
            name='courses',
            field=models.ManyToManyField(blank=True, to='CollegeApp.course'),
        ),
    ]
