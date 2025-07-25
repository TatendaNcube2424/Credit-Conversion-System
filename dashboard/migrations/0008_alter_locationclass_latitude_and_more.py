# Generated by Django 5.0.4 on 2025-05-30 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_alter_locationclass_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationclass',
            name='latitude',
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
        migrations.AlterField(
            model_name='locationclass',
            name='longitude',
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
    ]
