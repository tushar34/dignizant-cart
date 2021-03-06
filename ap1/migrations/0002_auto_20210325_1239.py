# Generated by Django 3.1.7 on 2021-03-25 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ap1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('S', 'Shirt'), ('SW', 'Sport wear'), ('OW', 'Outwear')], default='s', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='label',
            field=models.CharField(choices=[('P', 'primary'), ('S', 'secondary'), ('D', 'danger')], default='p', max_length=1),
            preserve_default=False,
        ),
    ]
