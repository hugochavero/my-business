# Generated by Django 4.1.5 on 2023-04-30 04:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_alter_product_options_alter_service_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="box_size",
            field=models.PositiveIntegerField(
                null=True, verbose_name="Unidades por Caja"
            ),
        ),
        migrations.AlterField(
            model_name="account",
            name="kind",
            field=models.CharField(
                choices=[("cash", "Efectivo"), ("bank", "Transferencia")],
                default="Efectivo",
                max_length=255,
            ),
        ),
    ]
