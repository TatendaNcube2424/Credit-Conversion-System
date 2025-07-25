# Generated by Django 5.0.4 on 2025-05-30 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_locationclass_registered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationclass',
            name='latitude',
            field=models.DecimalField(decimal_places=30, max_digits=50),
        ),
        migrations.AlterField(
            model_name='locationclass',
            name='longitude',
            field=models.DecimalField(decimal_places=30, max_digits=50),
        ),
    ]
