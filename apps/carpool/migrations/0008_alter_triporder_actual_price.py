# Generated by Django 4.2.20 on 2025-05-24 08:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("carpool", "0007_alter_coupon_discount_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="triporder",
            name="actual_price",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
