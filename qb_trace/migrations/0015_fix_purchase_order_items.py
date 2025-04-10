from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qb_trace', '0014_finalize_tracking_keys'),
    ]

    operations = [
        migrations.RunSQL(
            # Drop the existing table if it exists
            "DROP TABLE IF EXISTS purchase_order_items CASCADE;",
            # No reverse SQL needed since we're recreating the table
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.CreateModel(
            name='PurchaseOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material_name', models.CharField(blank=True, max_length=100, null=True)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('purchase_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='qb_trace.purchaseorder')),
                ('tracking_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='po_items', to='qb_trace.trackingkey', db_column='tracking_key_id')),
            ],
            options={
                'db_table': 'purchase_order_items',
                'ordering': ['id'],
            },
        ),
    ] 