# Generated by Django 3.2.16 on 2023-04-10 18:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0011_alter_quiz_creator'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='organizated_by',
            new_name='organized_by',
        ),
    ]
