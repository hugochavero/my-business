# Generated by Django 4.1.5 on 2023-04-26 11:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_alter_buyoperation_source_accounts_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="external_code",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
    ]
