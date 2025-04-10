from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('qb_trace', '0018_alter_purchaseorderitem_material_name_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                'DROP TABLE IF EXISTS serial_lot_items CASCADE;',
                'DROP TABLE IF EXISTS serial_lots CASCADE;',
                'DROP TABLE IF EXISTS qb_trace_seriallotitem CASCADE;',
                'DROP TABLE IF EXISTS qb_trace_seriallot CASCADE;',
                '''
                CREATE TABLE serial_lots (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'ordered',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    batch_id INTEGER REFERENCES batches(id) ON DELETE CASCADE
                );
                ''',
                '''
                CREATE TABLE serial_lot_items (
                    id BIGSERIAL PRIMARY KEY,
                    quantity DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    serial_lot_id INTEGER REFERENCES serial_lots(id) ON DELETE CASCADE,
                    material_id INTEGER REFERENCES materials(id) ON DELETE CASCADE,
                    inventory_id INTEGER REFERENCES inventory(id) ON DELETE CASCADE,
                    tracking_key_id INTEGER REFERENCES tracking_keys(id) ON DELETE SET NULL
                );
                '''
            ],
            reverse_sql=[
                'DROP TABLE IF EXISTS serial_lot_items;',
                'DROP TABLE IF EXISTS serial_lots;'
            ]
        )
    ] 