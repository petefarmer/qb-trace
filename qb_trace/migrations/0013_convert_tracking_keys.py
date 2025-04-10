from django.db import migrations

def convert_tracking_keys(apps, schema_editor):
    TrackingKey = apps.get_model('qb_trace', 'TrackingKey')
    PurchaseOrderItem = apps.get_model('qb_trace', 'PurchaseOrderItem')
    Inventory = apps.get_model('qb_trace', 'Inventory')
    
    # Get all unique tracking keys
    po_tracking_keys = set(PurchaseOrderItem.objects.exclude(tracking_key='')
                          .values_list('tracking_key', flat=True))
    inv_tracking_keys = set(Inventory.objects.exclude(tracking_key='')
                          .values_list('tracking_key', flat=True))
    all_tracking_keys = po_tracking_keys.union(inv_tracking_keys)
    
    # Create TrackingKey records
    tracking_key_map = {}
    for key in all_tracking_keys:
        if key:  # Skip None or empty strings
            tracking_key = TrackingKey.objects.create(key=key)
            tracking_key_map[key] = tracking_key
    
    # Update PurchaseOrderItem records
    for po_item in PurchaseOrderItem.objects.exclude(tracking_key=''):
        if po_item.tracking_key in tracking_key_map:
            po_item.tracking_key_new = tracking_key_map[po_item.tracking_key]
            po_item.save()
    
    # Update Inventory records
    for inv_item in Inventory.objects.exclude(tracking_key=''):
        if inv_item.tracking_key in tracking_key_map:
            inv_item.tracking_key_new = tracking_key_map[inv_item.tracking_key]
            inv_item.save()

def reverse_convert_tracking_keys(apps, schema_editor):
    TrackingKey = apps.get_model('qb_trace', 'TrackingKey')
    PurchaseOrderItem = apps.get_model('qb_trace', 'PurchaseOrderItem')
    Inventory = apps.get_model('qb_trace', 'Inventory')
    
    # Restore original tracking keys
    for po_item in PurchaseOrderItem.objects.exclude(tracking_key_new__isnull=True):
        po_item.tracking_key = po_item.tracking_key_new.key
        po_item.save()
    
    for inv_item in Inventory.objects.exclude(tracking_key_new__isnull=True):
        inv_item.tracking_key = inv_item.tracking_key_new.key
        inv_item.save()

class Migration(migrations.Migration):
    dependencies = [
        ('qb_trace', '0012_trackingkey_alter_inventory_tracking_key_and_more'),
    ]

    operations = [
        migrations.RunPython(convert_tracking_keys, reverse_convert_tracking_keys),
    ] 