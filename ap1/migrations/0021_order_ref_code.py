# Generated by Django 3.1.7 on 2021-04-06 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ap1', '0020_auto_20210406_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ref_code',
            field=models.CharField(default=123, max_length=20),
            preserve_default=False,
        ),
    ]
