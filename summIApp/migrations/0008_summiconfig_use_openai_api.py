# Generated by Django 4.1.7 on 2023-05-13 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("summIApp", "0007_summiconfig"),
    ]

    operations = [
        migrations.AddField(
            model_name="summiconfig",
            name="USE_OPENAI_API",
            field=models.BooleanField(default=False, help_text="Use OpenAI APIs?"),
        ),
    ]
