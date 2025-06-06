# Generated by Django 5.1.7 on 2025-04-11 08:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qb_trace', '0022_customer_alter_supplier_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchaseorderitem',
            options={},
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('received', 'Received')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='material_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
        migrations.CreateModel(
            name='SalesOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_orders', to='qb_trace.customer')),
            ],
            options={
                'db_table': 'sales_orders',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SalesOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material_name', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField()),
                ('sales_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='qb_trace.salesorder')),
            ],
            options={
                'db_table': 'sales_order_items',
            },
        ),
    ]
