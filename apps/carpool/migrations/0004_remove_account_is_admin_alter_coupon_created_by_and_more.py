# Generated by Django 4.2.20 on 2025-04-29 13:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("carpool", "0003_account_groups_account_user_permissions"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="account",
            name="is_admin",
        ),
        migrations.AlterField(
            model_name="coupon",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.DeleteModel(
            name="Admin",
        ),
    ]
