# Generated by Django 3.2.16 on 2023-04-17 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230405_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, help_text='Электронная почта пользователя', max_length=100, unique=True, verbose_name='почта'),
        ),
    ]
