# Generated by Django 4.1.6 on 2023-02-21 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("summIApp", "0002_useruploadedfiles_is this file public"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="useruploadedfiles",
            name="is this file public",
        ),
        migrations.AddField(
            model_name="useruploadedfiles",
            name="is_public_file",
            field=models.BooleanField(default=False, help_text="is this file public"),
        ),
    ]
