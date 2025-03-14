# Generated by Django 5.0.2 on 2025-03-13 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_charity_latitude_charity_longitude_event_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(blank=True, choices=[('aliments_de_base', 'Aliments de base'), ('produits_laitiers', 'Produits laitiers'), ('boissons', 'Boissons'), ('viandes_proteines', 'Viandes & Protéines'), ('cereales_legumineuses', 'Céréales & Légumineuses'), ('fruits_legumes', 'Fruits & Légumes'), ('epices_condiments', 'Épices & Condiments'), ('hygiene_nettoyage', 'Hygiène & Nettoyage'), ('huiles_cuisson', 'Huiles & Matières grasses'), ('pain_patisseries', 'Pain & Pâtisseries'), ('desserts_sucreries', 'Desserts & Sucreries'), ('autre', 'Autre')], max_length=255, null=True),
        ),
    ]
