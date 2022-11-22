# Generated by Django 4.1.3 on 2022-11-22 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='user_like',
            new_name='users_like',
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='images_data/%Y/%m/%d'),
        ),
    ]
