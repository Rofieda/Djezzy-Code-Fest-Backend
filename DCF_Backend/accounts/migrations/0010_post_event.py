# Generated by Django 5.0.2 on 2025-03-14 23:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_product_seil'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='event',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.event'),
            preserve_default=False,
        ),
    ]
