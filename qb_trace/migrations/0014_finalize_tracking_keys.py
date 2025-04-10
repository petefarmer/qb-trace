from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('qb_trace', '0013_convert_tracking_keys'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventory',
            name='tracking_key',
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='tracking_key',
        ),
        migrations.RenameField(
            model_name='inventory',
            old_name='tracking_key_new',
            new_name='tracking_key',
        ),
        migrations.RenameField(
            model_name='purchaseorderitem',
            old_name='tracking_key_new',
            new_name='tracking_key',
        ),
    ] 