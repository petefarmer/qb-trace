from django.core.management.base import BaseCommand
from qb_trace.models import Inventory, PurchaseOrderItem
from django.db import transaction
from django.db.models import Q

class Command(BaseCommand):
    help = 'Updates tracking keys in PurchaseOrderItem to match those in Inventory'

    def handle(self, *args, **options):
        # Get all inventory items with tracking keys
        inventory_items = Inventory.objects.filter(tracking_key__isnull=False)
        
        updated_count = 0
        for inventory_item in inventory_items:
            # Find the corresponding PO item by material name
            po_items = PurchaseOrderItem.objects.filter(
                Q(material_name=inventory_item.material.name) &
                (Q(tracking_key__isnull=True) | ~Q(tracking_key=inventory_item.tracking_key))
            ).order_by('purchase_order__created_at')
            
            # Only update the first matching PO item (the oldest one)
            if po_items.exists():
                po_item = po_items.first()
                try:
                    # Update directly in the database to bypass any signals
                    PurchaseOrderItem.objects.filter(id=po_item.id).update(
                        tracking_key=inventory_item.tracking_key
                    )
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated tracking key for {po_item.material_name} in PO-{po_item.purchase_order.id} to {inventory_item.tracking_key}'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Could not update tracking key for {po_item.material_name} in PO-{po_item.purchase_order.id}: {str(e)}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} tracking keys')
        ) 