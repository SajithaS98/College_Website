# Generated by Django 5.1.2 on 2024-12-27 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CollegeApp', '0005_customuser_photo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hod',
            name='faculty',
        ),
    ]