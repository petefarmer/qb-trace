from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Supplier, Material, Inventory, PurchaseOrder, PurchaseOrderItem, Batch, BatchItem, generate_tracking_key, TrackingKey, SerialLot, SerialLotItem, Customer, SalesOrder, SalesOrderItem
from .forms import SupplierForm, MaterialForm, InventoryForm, PurchaseOrderForm, PurchaseOrderItemForm, BatchForm, BatchItemForm, SerialLotForm, CustomerForm, SalesOrderForm
from django.db import models
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

def home(request):
    return redirect('seriallots')

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'qb_trace/supplier_list.html', {'suppliers': suppliers})

def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier created successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'qb_trace/supplier_form.html', {'form': form, 'title': 'Create Supplier'})

def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'qb_trace/supplier_form.html', {'form': form, 'title': 'Update Supplier'})

def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('suppliers')
    return render(request, 'qb_trace/supplier_confirm_delete.html', {'supplier': supplier})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'qb_trace/customer_list.html', {'customers': customers})

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully.')
            return redirect('customers')
    else:
        form = CustomerForm()
    return render(request, 'qb_trace/customer_form.html', {'form': form, 'title': 'Create Customer'})

def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('customers')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'qb_trace/customer_form.html', {'form': form, 'title': 'Update Customer'})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customers')
    return render(request, 'qb_trace/customer_confirm_delete.html', {'customer': customer})

def material_list(request):
    materials = Material.objects.all()
    return render(request, 'qb_trace/material_list.html', {'materials': materials})

def material_create(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('material_list')
    else:
        form = MaterialForm()
    return render(request, 'qb_trace/material_form.html', {'form': form, 'title': 'Create Material'})

def material_update(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            return redirect('material_list')
    else:
        form = MaterialForm(instance=material)
    return render(request, 'qb_trace/material_form.html', {'form': form, 'title': 'Update Material'})

def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        material.delete()
        return redirect('material_list')
    return render(request, 'qb_trace/material_confirm_delete.html', {'material': material})

def inventory_list(request):
    inventory_items = Inventory.objects.all()
    return render(request, 'qb_trace/inventory_list.html', {'inventory_items': inventory_items})

def inventory_create(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = InventoryForm()
    return render(request, 'qb_trace/inventory_form.html', {'form': form, 'title': 'Create Inventory Item'})

def inventory_update(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = InventoryForm(instance=inventory)
    return render(request, 'qb_trace/inventory_form.html', {'form': form, 'title': 'Update Inventory Item'})

def inventory_delete(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        inventory.delete()
        return redirect('inventory_list')
    return render(request, 'qb_trace/inventory_confirm_delete.html', {'inventory': inventory})

def po_list(request):
    purchase_orders = PurchaseOrder.objects.all()
    return render(request, 'qb_trace/po_list.html', {'purchase_orders': purchase_orders})

def po_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            po = form.save(commit=False)
            
            # If PO is received, prevent status changes
            if po.status == 'received':
                po.status = 'received'  # Force status to remain 'received'
            
            po.save()
            
            # Process submitted items
            i = 1
            while True:
                item_name = request.POST.get(f'item_name_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                
                if not item_name or not quantity:
                    break
                
                # Create or get the material
                material, created = Material.objects.get_or_create(name=item_name)
                
                # Create new item
                po_item = PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    item_name=item_name,
                    material=material,
                    quantity=quantity
                )
                
                # If PO is received, create inventory and tracking key
                if po.status == 'received':
                    # Generate tracking key
                    tracking_key = generate_tracking_key(item_name)
                    tracking_key_obj = TrackingKey.objects.create(key=tracking_key)
                    
                    # Update PO item with tracking key
                    po_item.tracking_key = tracking_key_obj
                    po_item.save()
                    
                    # Create inventory record
                    Inventory.objects.create(
                        material=material,
                        quantity=quantity,
                        tracking_key=tracking_key_obj
                    )
                
                i += 1
            
            return redirect('po_list')
    else:
        form = PurchaseOrderForm()
    
    suppliers = Supplier.objects.all()
    materials = Material.objects.all()
    return render(request, 'qb_trace/po_form.html', {
        'form': form,
        'title': 'Create Purchase Order',
        'suppliers': suppliers,
        'materials': materials
    })

def po_update(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=po)
        if form.is_valid():
            po = form.save(commit=False)
            
            # If PO is received, prevent status changes
            if po.status == 'received':
                po.status = 'received'  # Force status to remain 'received'
            
            po.save()
            
            # Get existing items
            existing_items = {item.item_name: item for item in po.items.all()}
            
            # Process submitted items
            i = 1
            while True:
                item_name = request.POST.get(f'item_name_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                
                if not item_name or not quantity:
                    break
                
                # Create or get the material
                material, created = Material.objects.get_or_create(name=item_name)
                
                if item_name in existing_items:
                    # Update existing item
                    existing_item = existing_items[item_name]
                    existing_item.quantity = quantity
                    existing_item.save()
                    # Remove from existing_items so we know it was processed
                    del existing_items[item_name]
                else:
                    # Create new item
                    po_item = PurchaseOrderItem.objects.create(
                        purchase_order=po,
                        item_name=item_name,
                        material=material,
                        quantity=quantity
                    )
                    
                    # If PO is received, create inventory and tracking key
                    if po.status == 'received':
                        # Generate tracking key
                        tracking_key = generate_tracking_key(item_name)
                        tracking_key_obj = TrackingKey.objects.create(key=tracking_key)
                        
                        # Update PO item with tracking key
                        po_item.tracking_key = tracking_key_obj
                        po_item.save()
                        
                        # Create inventory record
                        Inventory.objects.create(
                            material=material,
                            quantity=quantity,
                            tracking_key=tracking_key_obj
                        )
                
                i += 1
            
            # Only delete items that weren't in the submitted form
            # and don't have tracking keys (to preserve received items)
            for item in existing_items.values():
                if not item.tracking_key:
                    item.delete()
            
            return redirect('po_list')
    else:
        form = PurchaseOrderForm(instance=po)
    
    suppliers = Supplier.objects.all()
    materials = Material.objects.all()
    return render(request, 'qb_trace/po_form.html', {
        'form': form,
        'title': 'Update Purchase Order',
        'po': po,
        'suppliers': suppliers,
        'materials': materials
    })

def po_delete(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        po.delete()
        messages.success(request, 'Purchase Order deleted successfully.')
        return redirect('po_list')
    return render(request, 'qb_trace/po_confirm_delete.html', {'po': po})

def po_details(request, tracking_key):
    try:
        # Get the tracking key object
        tracking_key_obj = TrackingKey.objects.get(key=tracking_key)
        print(f"\nDebug: Tracking Key Object:")
        print(f"  - Key: {tracking_key_obj.key}")
        print(f"  - ID: {tracking_key_obj.id}")
        
        # Get all purchase order items with this tracking key
        po_items = PurchaseOrderItem.objects.filter(tracking_key=tracking_key_obj).select_related(
            'purchase_order',
            'purchase_order__supplier',
            'material'
        )
        
        if not po_items.exists():
            return render(request, 'qb_trace/po_modal_details.html', {
                'error': 'No purchase order found for this tracking key'
            })
            
        # Get the first purchase order (they should all be the same)
        po = po_items.first().purchase_order
        
        # Get all sales order items that reference this tracking key
        sales_order_items = SalesOrderItem.objects.filter(tracking_key=tracking_key_obj).select_related(
            'sales_order',
            'sales_order__customer',
            'material',
            'serial_lot'
        )
        
        # Debug: Print inventory items with this tracking key
        inventory_items = Inventory.objects.filter(tracking_key=tracking_key_obj)
        print(f"\nDebug: Inventory Items with tracking key {tracking_key}:")
        for inv in inventory_items:
            print(f"  - ID: {inv.id}")
            print(f"    Material: {inv.material.name if inv.material else 'None'}")
            print(f"    Serial Lot: {inv.serial_lot.name if inv.serial_lot else 'None'}")
            print(f"    Quantity: {inv.quantity}")
        
        # Get the material and inventory item from the inventory item with this tracking key
        material = inventory_items.first().material if inventory_items.exists() else None
        inventory = inventory_items.first() if inventory_items.exists() else None
        
        # Get all serial lot items that use this tracking key either directly or through their inventory
        # OR have the same material and inventory item as the inventory item with this tracking key
        serial_lot_items = SerialLotItem.objects.filter(
            models.Q(tracking_key=tracking_key_obj) | 
            models.Q(inventory__tracking_key=tracking_key_obj) |
            models.Q(material=material, inventory=inventory)
        ).select_related(
            'serial_lot',
            'material',
            'inventory'
        )
        
        # Debug: Print serial lot items
        print(f"\nDebug: Serial Lot Items for tracking key {tracking_key}:")
        for item in serial_lot_items:
            print(f"  - Serial Lot: {item.serial_lot.name}")
            print(f"    Material: {item.material.name}")
            print(f"    Quantity: {item.quantity}")
            print(f"    Tracking Key: {item.tracking_key.key if item.tracking_key else 'None'}")
            print(f"    Inventory Tracking Key: {item.inventory.tracking_key.key if item.inventory.tracking_key else 'None'}")
        
        # Group sales order items by their sales order
        sales_orders = {}
        for item in sales_order_items:
            if item.sales_order not in sales_orders:
                sales_orders[item.sales_order] = []
            sales_orders[item.sales_order].append(item)
        
        return render(request, 'qb_trace/po_modal_details.html', {
            'po': po,
            'tracking_key': tracking_key,
            'po_items': po_items,
            'sales_orders': sales_orders,
            'serial_lot_items': serial_lot_items
        })
    except TrackingKey.DoesNotExist:
        return render(request, 'qb_trace/po_modal_details.html', {
            'error': 'Tracking key not found'
        })

def batch_list(request):
    batches = Batch.objects.all()
    return render(request, 'qb_trace/batch_list.html', {'batches': batches})

def batch_create(request):
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            batch = form.save()
            
            # Process batch items
            inventory_ids = request.POST.getlist('inventory')
            quantities = request.POST.getlist('quantity')
            
            for inv_id, qty in zip(inventory_ids, quantities):
                if inv_id and qty:
                    inventory = Inventory.objects.get(id=inv_id)
                    BatchItem.objects.create(
                        batch=batch,
                        inventory=inventory,
                        quantity=qty
                    )
            
            messages.success(request, 'Batch created successfully.')
            return redirect('batch_list')
    else:
        form = BatchForm()
    
    # Get unique materials with their earliest expiring inventory item
    inventory_items = Inventory.objects.order_by(
        'material__name',
        models.F('expiry_date').asc(nulls_last=True)
    ).distinct('material__name')

    return render(request, 'qb_trace/batch_form.html', {
        'form': form,
        'title': 'Create Batch',
        'inventory_items': inventory_items
    })

def batch_update(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            batch = form.save()
            # Clear existing items
            batch.items.all().delete()
            
            # Handle multiple items
            inventory_ids = request.POST.getlist('inventory')
            quantities = request.POST.getlist('quantity')
            
            for inventory_id, quantity in zip(inventory_ids, quantities):
                if inventory_id and quantity:
                    inventory = get_object_or_404(Inventory, pk=inventory_id)
                    BatchItem.objects.create(
                        batch=batch,
                        inventory=inventory,
                        quantity=quantity
                    )
            
            messages.success(request, 'Batch updated successfully.')
            return redirect('batch_list')
    else:
        form = BatchForm(instance=batch)
    
    # Get unique materials with their earliest expiring inventory item
    inventory_items = Inventory.objects.order_by(
        'material__name',
        models.F('expiry_date').asc(nulls_last=True)
    ).distinct('material__name')

    return render(request, 'qb_trace/batch_form.html', {
        'form': form,
        'title': 'Update Batch',
        'batch': batch,
        'inventory_items': inventory_items
    })

def batch_delete(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        batch.delete()
        messages.success(request, 'Batch deleted successfully.')
        return redirect('batch_list')
    return render(request, 'qb_trace/batch_confirm_delete.html', {'batch': batch})

def serial_lot_list(request):
    serial_lots = SerialLot.objects.select_related('batch').all()
    today = timezone.now().date()
    soon = today + timezone.timedelta(days=30)  # 30 days from now
    
    # Calculate expiry dates for each serial lot
    for serial_lot in serial_lots:
        if not serial_lot.expiry_date and serial_lot.status == 'completed':
            # Get all expiry dates from inventory items
            expiry_dates = []
            for item in serial_lot.items.all():
                if item.tracking_key:
                    inventory_items = Inventory.objects.filter(tracking_key=item.tracking_key)
                    for inv in inventory_items:
                        if inv.expiry_date:
                            expiry_dates.append(inv.expiry_date)
            
            # Find the nearest expiry date
            if expiry_dates:
                nearest_expiry = min(expiry_dates, key=lambda x: abs((x - today).days))
                serial_lot.expiry_date = nearest_expiry
                serial_lot.save()
    
    return render(request, 'qb_trace/serial_lot_list.html', {
        'serial_lots': serial_lots,
        'today': today,
        'soon': soon
    })

def serial_lot_create(request):
    batches = Batch.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        batch_id = request.POST.get('batch')
        status = request.POST.get('status')
        
        # Get the batch
        batch = get_object_or_404(Batch, pk=batch_id)
        
        # Check inventory availability against BOM
        insufficient_materials = []
        with transaction.atomic():
            # Get all batch items (BOM)
            batch_items = BatchItem.objects.filter(batch=batch)
            
            # Check each material's availability
            for batch_item in batch_items:
                material = batch_item.inventory.material
                required_quantity = batch_item.quantity
                
                # Get available inventory items for this material with sufficient quantity
                available_inventory = Inventory.objects.filter(
                    material=material,
                    quantity__gte=required_quantity
                ).order_by('expiry_date')  # Order by expiry date to use earliest expiring first
                
                if not available_inventory.exists():
                    insufficient_materials.append({
                        'material': material.name,
                        'required': required_quantity,
                        'available': 0
                    })
        
        # If any materials are insufficient, set status to pending and show alert
        if insufficient_materials:
            status = 'pending'
            messages.warning(request, 'Insufficient inventory for the following materials:')
            for material in insufficient_materials:
                messages.warning(request, 
                    f"{material['material']}: Required {material['required']}, Available {material['available']}")
        
        # Create the serial lot
        serial_lot = SerialLot.objects.create(
            name=name,
            batch_id=batch_id,
            status=status
        )
        
        # If status is completed, create serial lot items and update inventory
        if status == 'completed':
            with transaction.atomic():
                # Create serial lot items from batch items
                for batch_item in batch_items:
                    material = batch_item.inventory.material
                    required_quantity = batch_item.quantity
                    
                    # Get available inventory items for this material with sufficient quantity
                    available_inventory = Inventory.objects.filter(
                        material=material,
                        quantity__gte=required_quantity
                    ).order_by('expiry_date')  # Order by expiry date to use earliest expiring first
                    
                    # Use the earliest expiring inventory item that has sufficient quantity
                    inventory = available_inventory.first()
                    
                    if inventory:
                        # Create serial lot item with the tracking key from the inventory item
                        serial_lot_item = SerialLotItem.objects.create(
                            serial_lot=serial_lot,
                            material=material,
                            inventory=inventory,
                            quantity=required_quantity,
                            tracking_key=inventory.tracking_key
                        )
                        
                        # Update inventory quantity
                        inventory.quantity -= required_quantity
                        inventory.save()
                        
                        # Create a new inventory item for the serial lot with the same tracking key
                        new_inventory = Inventory.objects.create(
                            serial_lot=serial_lot,
                            material=material,
                            quantity=required_quantity,
                            tracking_key=inventory.tracking_key,
                            expiry_date=inventory.expiry_date,
                            unit=inventory.unit,
                            status='in_stock'
                        )
                        
                        # Update the serial lot item to reference the new inventory item
                        serial_lot_item.inventory = new_inventory
                        serial_lot_item.save()
                
                # Update expiry date from inventory items
                expiry_dates = []
                for item in serial_lot.items.all():
                    if item.inventory.expiry_date:
                        expiry_dates.append(item.inventory.expiry_date)
                
                if expiry_dates:
                    serial_lot.expiry_date = min(expiry_dates)
                    serial_lot.save()
        
        return redirect('seriallots')
    
    return render(request, 'qb_trace/serial_lot_form.html', {
        'batches': batches,
        'title': 'Create Serial Lot'
    })

def serial_lot_update(request, pk):
    print(f"\n=== Starting serial_lot_update for pk={pk} ===")
    serial_lot = get_object_or_404(SerialLot, pk=pk)
    batches = Batch.objects.all()
    print(f"Found serial lot: {serial_lot.name} (status: {serial_lot.status})")
    
    if request.method == 'POST':
        print("\nProcessing POST request")
        print(f"POST data: {request.POST}")
        form = SerialLotForm(request.POST, instance=serial_lot)
        if form.is_valid():
            print("Form is valid")
            with transaction.atomic():
                # Get the current status before saving
                current_status = serial_lot.status
                new_status = form.cleaned_data['status']
                print(f"Status change: {current_status} -> {new_status}")
                
                # If status is completed (either changing to or already completed)
                if new_status == 'completed':
                    print("\n=== Processing completed status ===")
                    print(f"Checking if inventory item exists for serial lot: {serial_lot.name}")
                    
                    # Check if inventory item already exists
                    existing_inventory = Inventory.objects.filter(serial_lot=serial_lot).first()
                    if not existing_inventory:
                        print("No existing inventory item found, creating new one")
                        
                        # Get all batch items for this serial lot
                        batch_items = serial_lot.batch.items.select_related(
                            'inventory',
                            'inventory__material',
                            'inventory__tracking_key'
                        ).all()
                        
                        # Check if we have sufficient inventory for all materials
                        insufficient_materials = []
                        for batch_item in batch_items:
                            material = batch_item.inventory.material
                            required_quantity = batch_item.quantity
                            
                            # Get available inventory items for this material with sufficient quantity
                            available_inventory = Inventory.objects.filter(
                                material=material,
                                quantity__gte=required_quantity
                            ).order_by('expiry_date')
                            
                            if not available_inventory.exists():
                                insufficient_materials.append({
                                    'material': material.name,
                                    'required': required_quantity,
                                    'available': 0
                                })
                        
                        if insufficient_materials:
                            messages.warning(request, 'Insufficient inventory for the following materials:')
                            for material in insufficient_materials:
                                messages.warning(request, 
                                    f"{material['material']}: Required {material['required']}, Available {material['available']}")
                            return redirect('seriallots')
                        
                        # Create serial lot items and update inventory
                        for batch_item in batch_items:
                            material = batch_item.inventory.material
                            required_quantity = batch_item.quantity
                            
                            # Get available inventory items for this material with sufficient quantity
                            available_inventory = Inventory.objects.filter(
                                material=material,
                                quantity__gte=required_quantity
                            ).order_by('expiry_date')
                            
                            # Use the earliest expiring inventory item that has sufficient quantity
                            inventory = available_inventory.first()
                            
                            if inventory:
                                # Create serial lot item with the tracking key from the inventory item
                                serial_lot_item = SerialLotItem.objects.create(
                                    serial_lot=serial_lot,
                                    material=material,
                                    inventory=inventory,
                                    quantity=required_quantity,
                                    tracking_key=inventory.tracking_key
                                )
                                
                                # Update inventory quantity
                                inventory.quantity -= required_quantity
                                inventory.save()
                        
                        # Set the expiry date based on the earliest expiry date from batch items
                        print("\nSetting expiry date from batch items")
                        earliest_expiry = None
                        for batch_item in batch_items:
                            if batch_item.inventory.expiry_date:
                                if earliest_expiry is None or batch_item.inventory.expiry_date < earliest_expiry:
                                    earliest_expiry = batch_item.inventory.expiry_date
                        
                        if earliest_expiry:
                            serial_lot.expiry_date = earliest_expiry
                            print(f"Updated serial lot expiry date to: {earliest_expiry}")
                    else:
                        print(f"Inventory item already exists with ID: {existing_inventory.id}")
                
                # Save the serial lot
                print("\nSaving serial lot")
                serial_lot = form.save()
                print(f"Serial lot saved with status: {serial_lot.status}")
                
                messages.success(request, 'Serial lot updated successfully.')
                print("=== Completed serial_lot_update ===")
                return redirect('seriallots')
        else:
            print("Form is invalid")
            print(f"Form errors: {form.errors}")
    else:
        print("Processing GET request")
        form = SerialLotForm(instance=serial_lot)
    
    return render(request, 'qb_trace/serial_lot_form.html', {
        'form': form,
        'serial_lot': serial_lot,
        'batches': batches,
        'title': 'Update Serial Lot'
    })

def serial_lot_delete(request, pk):
    serial_lot = get_object_or_404(SerialLot, pk=pk)
    if request.method == 'POST':
        serial_lot.delete()
        messages.success(request, 'Serial Lot deleted successfully.')
        return redirect('seriallots')
    return render(request, 'qb_trace/serial_lot_confirm_delete.html', {'serial_lot': serial_lot})

def serial_lot_details(request, pk):
    try:
        serial_lot = get_object_or_404(SerialLot, pk=pk)
        
        # Get batch items with their inventory and materials
        batch_items = serial_lot.batch.items.select_related(
            'inventory',
            'inventory__material',
            'inventory__serial_lot',
            'inventory__tracking_key'
        ).all()
        
        # Get all sales order items that reference this serial lot
        sales_orders = SalesOrderItem.objects.filter(serial_lot=serial_lot)
        
        context = {
            'serial_lot': serial_lot,
            'items': batch_items,
            'sales_orders': sales_orders
        }
        
        return render(request, 'qb_trace/serial_lot_modal_details.html', context)
    except SerialLot.DoesNotExist:
        return JsonResponse({'error': 'Serial lot not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def handle_po_received(po):
    """Handle the logic when a PO is received"""
    # Get all items for this PO
    items = PurchaseOrderItem.objects.filter(purchase_order=po)
    
    # Create inventory records for each item
    for item in items:
        # Create a new inventory record
        inventory = Inventory.objects.create(
            material=item.material,
            quantity=item.quantity,
            unit=item.unit,
            location=po.supplier.name,  # Use supplier name as initial location
            status='in_stock',
            tracking_key=item.tracking_key
        )
    
    # Update PO status to received
    po.status = 'received'
    po.save()

def sales_order_list(request):
    sales_orders = SalesOrder.objects.all()
    return render(request, 'qb_trace/sales_order_list.html', {'sales_orders': sales_orders})

def sales_order_create(request):
    if request.method == 'POST':
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            sales_order = form.save()
            # Process submitted items
            i = 1
            while True:
                item_name = request.POST.get(f'item_name_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                
                if not item_name or not quantity:
                    break
                
                # Find inventory items ordered by expiry date (FIFO)
                inventory_items = Inventory.objects.filter(
                    models.Q(material__name=item_name) | models.Q(serial_lot__name=item_name)
                ).order_by('expiry_date')
                
                # Calculate total available quantity
                total_available = inventory_items.aggregate(total=models.Sum('quantity'))['total'] or 0
                
                # Validate quantity before proceeding
                requested_quantity = int(quantity)
                if requested_quantity <= 0:
                    messages.warning(request, f'Quantity must be greater than 0 for {item_name}.')
                    i += 1
                    continue
                
                if requested_quantity > total_available:
                    messages.warning(request, f'Not enough inventory available for {item_name}. Requested: {requested_quantity}, Available: {total_available}')
                    i += 1
                    continue
                
                remaining_quantity = requested_quantity
                
                # Create sales order items for each inventory item until we fulfill the quantity
                for inventory_item in inventory_items:
                    if remaining_quantity <= 0:
                        break
                        
                    # Use the minimum of remaining quantity and available inventory
                    item_quantity = min(remaining_quantity, inventory_item.quantity)
                    
                    if item_quantity > 0:  # Only create items with positive quantities
                        # Create sales order item
                        SalesOrderItem.objects.create(
                            sales_order=sales_order,
                            item_name=item_name,
                            material=inventory_item.material,
                            serial_lot=inventory_item.serial_lot,
                            tracking_key=inventory_item.tracking_key,
                            quantity=item_quantity
                        )
                        
                        remaining_quantity -= item_quantity
                
                if remaining_quantity > 0:
                    messages.warning(request, f'Not enough inventory available for {item_name}. Remaining quantity: {remaining_quantity}')
                
                i += 1
            messages.success(request, 'Sales Order created successfully.')
            return redirect('sales_orders')
    else:
        form = SalesOrderForm()
    
    # Get unique inventory items ordered by expiry date
    inventory_items = Inventory.objects.filter(
        models.Q(material__isnull=False) | models.Q(serial_lot__isnull=False)
    ).order_by('expiry_date')
    
    # Create a set to track unique item names
    unique_items = set()
    filtered_items = []
    
    for item in inventory_items:
        item_name = item.material.name if item.material else item.serial_lot.name
        if item_name not in unique_items:
            unique_items.add(item_name)
            filtered_items.append(item)
    
    return render(request, 'qb_trace/sales_order_form.html', {
        'form': form,
        'title': 'Create Sales Order',
        'inventory_items': filtered_items
    })

def sales_order_update(request, pk):
    sales_order = get_object_or_404(SalesOrder, pk=pk)
    if request.method == 'POST':
        form = SalesOrderForm(request.POST, instance=sales_order)
        if form.is_valid():
            sales_order = form.save()
            # Clear existing items
            sales_order.items.all().delete()
            
            # Process submitted items
            i = 1
            while True:
                item_name = request.POST.get(f'item_name_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                
                if not item_name or not quantity:
                    break
                
                # Find inventory items ordered by expiry date (FIFO)
                inventory_items = Inventory.objects.filter(
                    models.Q(material__name=item_name) | models.Q(serial_lot__name=item_name)
                ).order_by('expiry_date')
                
                # Calculate total available quantity
                total_available = inventory_items.aggregate(total=models.Sum('quantity'))['total'] or 0
                
                # Validate quantity before proceeding
                requested_quantity = int(quantity)
                if requested_quantity <= 0:
                    messages.warning(request, f'Quantity must be greater than 0 for {item_name}.')
                    i += 1
                    continue
                
                if requested_quantity > total_available:
                    messages.warning(request, f'Not enough inventory available for {item_name}. Requested: {requested_quantity}, Available: {total_available}')
                    i += 1
                    continue
                
                remaining_quantity = requested_quantity
                
                # Create sales order items for each inventory item until we fulfill the quantity
                for inventory_item in inventory_items:
                    if remaining_quantity <= 0:
                        break
                        
                    # Use the minimum of remaining quantity and available inventory
                    item_quantity = min(remaining_quantity, inventory_item.quantity)
                    
                    if item_quantity > 0:  # Only create items with positive quantities
                        # Create sales order item
                        SalesOrderItem.objects.create(
                            sales_order=sales_order,
                            item_name=item_name,
                            material=inventory_item.material,
                            serial_lot=inventory_item.serial_lot,
                            tracking_key=inventory_item.tracking_key,
                            quantity=item_quantity
                        )
                        
                        # If sales order is completed, reduce inventory quantity
                        if sales_order.status == 'completed':
                            inventory_item.quantity -= item_quantity
                            inventory_item.save()
                        
                        remaining_quantity -= item_quantity
                
                if remaining_quantity > 0:
                    messages.warning(request, f'Not enough inventory available for {item_name}. Remaining quantity: {remaining_quantity}')
                
                i += 1
            messages.success(request, 'Sales Order updated successfully.')
            return redirect('sales_orders')
    else:
        form = SalesOrderForm(instance=sales_order)
    
    # Get unique inventory items ordered by expiry date
    inventory_items = Inventory.objects.filter(
        models.Q(material__isnull=False) | models.Q(serial_lot__isnull=False)
    ).order_by('expiry_date')
    
    # Create a set to track unique item names
    unique_items = set()
    filtered_items = []
    
    for item in inventory_items:
        item_name = item.material.name if item.material else item.serial_lot.name
        if item_name not in unique_items:
            unique_items.add(item_name)
            filtered_items.append(item)
    
    return render(request, 'qb_trace/sales_order_form.html', {
        'form': form,
        'title': 'Update Sales Order',
        'inventory_items': filtered_items,
        'sales_order': sales_order
    })

def sales_order_delete(request, pk):
    sales_order = get_object_or_404(SalesOrder, pk=pk)
    if request.method == 'POST':
        sales_order.delete()
        messages.success(request, 'Sales Order deleted successfully.')
        return redirect('sales_orders')
    return render(request, 'qb_trace/sales_order_confirm_delete.html', {'sales_order': sales_order}) 