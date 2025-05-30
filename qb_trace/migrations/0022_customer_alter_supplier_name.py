# Generated by Django 5.1.7 on 2025-04-11 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qb_trace', '0021_alter_seriallot_options_alter_seriallotitem_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'customers',
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='supplier',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
