# Generated by Django 5.0.4 on 2025-05-20 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_remove_locationclass_ends_at_locationclass_venue'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationclass',
            name='full_name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
