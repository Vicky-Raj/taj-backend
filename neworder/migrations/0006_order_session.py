# Generated by Django 3.0.1 on 2020-02-26 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neworder', '0005_auto_20200226_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='session',
            field=models.TextField(null=True),
        ),
    ]
