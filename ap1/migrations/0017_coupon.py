# Generated by Django 3.1.7 on 2021-04-05 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ap1', '0016_auto_20210405_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
            ],
        ),
    ]
