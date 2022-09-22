# Generated by Django 4.0.7 on 2022-09-20 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order_history',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('total_amount', models.FloatField(blank=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now_add=True, null=True)),
                ('time_created', models.TimeField(auto_now_add=True, null=True)),
                ('date_created', models.DateField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sku', models.TextField(blank=True, max_length=255, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('product_status', models.BooleanField(default=False)),
                ('product_left', models.IntegerField()),
                ('price', models.FloatField(default=0.0)),
                ('last_modified', models.DateTimeField(auto_now_add=True, null=True)),
                ('time_created', models.TimeField(auto_now_add=True, null=True)),
                ('date_created', models.DateField(auto_now_add=True, null=True)),
            ],
        ),
    ]
