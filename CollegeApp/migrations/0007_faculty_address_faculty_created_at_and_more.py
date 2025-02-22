# Generated by Django 5.1.2 on 2024-12-30 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CollegeApp', '0006_remove_hod_faculty'),
    ]

    operations = [
        migrations.AddField(
            model_name='faculty',
            name='address',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='faculty',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='faculty',
            name='updated_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='faculty',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
