from django.db import models, transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import random
import string
from django.db import connection
from django.core.exceptions import ValidationError

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'suppliers'
        ordering = ['name']

class Customer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'customers'
        ordering = ['name']

class Material(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'materials'
        ordering = ['name']

class TrackingKey(models.Model):
    key = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        db_table = 'tracking_keys'
        ordering = ['-created_at']

class Inventory(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True)
    serial_lot = models.ForeignKey('SerialLot', on_delete=models.CASCADE, null=True, blank=True, related_name='inventory_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default='pcs')
    location = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('in_stock', 'In Stock'),
        ('reserved', 'Reserved'),
        ('shipped', 'Shipped')
    ], default='in_stock')
    tracking_key = models.ForeignKey(TrackingKey, on_delete=models.SET_NULL, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory'
        ordering = ['-created_at']

    def __str__(self):
        if self.material:
            return f"{self.material.name} - {self.quantity} {self.unit}"
        elif self.serial_lot:
            return f"{self.serial_lot.name} - {self.quantity} {self.unit}"
        return f"Inventory Item {self.id}"

    def clean(self):
        if not self.material and not self.serial_lot:
            raise ValidationError("Either material or serial lot must be specified")
        if self.material and self.serial_lot:
            raise ValidationError("Cannot specify both material and serial lot")

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = generate_expiry_date()
        super().save(*args, **kwargs)

class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('received', 'Received')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"PO-{self.id}"

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_order_items')
    quantity = models.PositiveIntegerField()
    tracking_key = models.ForeignKey(TrackingKey, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'purchase_order_items'

    def __str__(self):
        return f"{self.item_name} - {self.quantity}"

class SalesOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales_orders')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales_orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"SO-{self.id}"

class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_order_items')
    quantity = models.PositiveIntegerField()
    serial_lot = models.ForeignKey('SerialLot', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_order_items')
    tracking_key = models.ForeignKey(TrackingKey, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_order_items')

    class Meta:
        db_table = 'sales_order_items'

    def __str__(self):
        return f"{self.item_name} - {self.quantity}"

class Batch(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'batches'
        ordering = ['-created_at']

class BatchItem(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='items')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'batch_items'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.batch.name} - {self.inventory.material.name} ({self.quantity})"

def generate_tracking_key(prefix):
    """Generate a unique tracking key with format: PREFIX-XXXXXXX"""
    # Take first 3 letters of prefix, uppercase
    prefix = prefix[:3].upper()
    # Generate 7 random alphanumeric characters
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    return f"{prefix}-{random_part}"

def generate_expiry_date():
    """Generate a random expiry date between 6 months and 2 years from now"""
    today = timezone.now()
    six_months = today + timedelta(days=180)
    two_years = today + timedelta(days=730)
    return today + timedelta(days=random.randint(180, 730))

@receiver(post_save, sender=PurchaseOrder)
def handle_po_received(sender, instance, **kwargs):
    if instance.status == 'received':
        with transaction.atomic():
            for item in instance.items.all():
                if item.material:
                    tracking_key = TrackingKey.objects.create(
                        key=generate_tracking_key(item.material.name)
                    )
                    # Only update the tracking_key field
                    PurchaseOrderItem.objects.filter(id=item.id).update(tracking_key=tracking_key)
                    
                    # Create inventory record
                    Inventory.objects.create(
                        material=item.material,
                        quantity=item.quantity,
                        tracking_key=tracking_key
                    )

class SerialLot(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]
    
    name = models.CharField(max_length=100)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='serial_lots')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.batch.name}"

    class Meta:
        db_table = 'serial_lots'
        ordering = ['-created_at']

class SerialLotItem(models.Model):
    serial_lot = models.ForeignKey(SerialLot, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_key = models.ForeignKey(TrackingKey, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'serial_lot_items'
        managed = True
        app_label = 'qb_trace'

    def __str__(self):
        return f"{self.material.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        # Get the tracking key from the inventory item
        if self.inventory and self.inventory.tracking_key:
            self.tracking_key = self.inventory.tracking_key
        super().save(*args, **kwargs) 