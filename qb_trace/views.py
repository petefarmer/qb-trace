from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Supplier, Material, Inventory, PurchaseOrder, PurchaseOrderItem, Batch, BatchItem, generate_tracking_key, TrackingKey, SerialLot, SerialLotItem
from .forms import SupplierForm, MaterialForm, InventoryForm, PurchaseOrderForm, PurchaseOrderItemForm, BatchForm, BatchItemForm, SerialLotForm
from django.db import models
from django.utils import timezone
from django.db import transaction

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
        return redirect('supplier_list')
    return render(request, 'qb_trace/supplier_confirm_delete.html', {'supplier': supplier})

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
                material_name = request.POST.get(f'material_name_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                
                if not material_name or not quantity:
                    break
                
                # Create or get the material
                material, created = Material.objects.get_or_create(name=material_name)
                
                # Create new item
                po_item = PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    material_name=material_name,
                    quantity=quantity
                )
                
                # If PO is received, create inventory and tracking key
                if po.status == 'received':
                    # Generate tracking key
                    tracking_key = generate_tracking_key(material_name)
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
            existing_items = {item.material_name: item for item in po.items.all()}
            
            # Process submitted items
            i = 1
            while True:
                material_name = request.POST.get(f'material_name_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                
                if not material_name or not quantity:
                    break
                
                # Create or get the material
                material, created = Material.objects.get_or_create(name=material_name)
                
                if material_name in existing_items:
                    # Update existing item
                    existing_item = existing_items[material_name]
                    existing_item.quantity = quantity
                    existing_item.save()
                    # Remove from existing_items so we know it was processed
                    del existing_items[material_name]
                else:
                    # Create new item
                    po_item = PurchaseOrderItem.objects.create(
                        purchase_order=po,
                        material_name=material_name,
                        quantity=quantity
                    )
                    
                    # If PO is received, create inventory and tracking key
                    if po.status == 'received':
                        # Generate tracking key
                        tracking_key = generate_tracking_key(material_name)
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
        # First try to find the tracking key in PurchaseOrderItem
        po_item = PurchaseOrderItem.objects.filter(tracking_key__key=tracking_key).first()
        if po_item:
            po = po_item.purchase_order
            return render(request, 'qb_trace/po_details.html', {
                'po': po,
                'tracking_key': tracking_key
            })
        
        # If not found in PurchaseOrderItem, try Inventory
        inventory_item = Inventory.objects.filter(tracking_key__key=tracking_key).first()
        if inventory_item and inventory_item.tracking_key:
            po_item = PurchaseOrderItem.objects.filter(tracking_key=inventory_item.tracking_key).first()
            if po_item:
                po = po_item.purchase_order
                return render(request, 'qb_trace/po_details.html', {
                    'po': po,
                    'tracking_key': tracking_key
                })
        
        return render(request, 'qb_trace/po_details.html', {
            'error': 'Purchase order details not found'
        })
    except Exception as e:
        return render(request, 'qb_trace/po_details.html', {
            'error': str(e)
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
    if request.method == 'POST':
        name = request.POST.get('name')
        batch_id = request.POST.get('batch')
        status = request.POST.get('status')
        
        batch = get_object_or_404(Batch, pk=batch_id)
        serial_lot = SerialLot.objects.create(
            name=name,
            batch=batch,
            status=status
        )
        return redirect('seriallots')
    
    batches = Batch.objects.all()
    return render(request, 'qb_trace/serial_lot_form.html', {
        'serial_lot': None,
        'batches': batches
    })

def serial_lot_update(request, pk):
    serial_lot = get_object_or_404(SerialLot, pk=pk)
    batches = Batch.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        batch_id = request.POST.get('batch')
        status = request.POST.get('status')
        
        # Get the current status before update
        old_status = serial_lot.status
        
        # Update serial lot
        serial_lot.name = name
        serial_lot.batch_id = batch_id
        serial_lot.status = status
        
        # If status is changing to completed, handle all updates
        if status == 'completed' and old_status != 'completed':
            with transaction.atomic():
                # Create serial lot items from batch items
                batch_items = BatchItem.objects.filter(batch=serial_lot.batch)
                for batch_item in batch_items:
                    # Check if the item already exists
                    existing_item = SerialLotItem.objects.filter(
                        serial_lot=serial_lot,
                        material=batch_item.inventory.material,
                        inventory=batch_item.inventory
                    ).first()
                    
                    if not existing_item:
                        SerialLotItem.objects.create(
                            serial_lot=serial_lot,
                            material=batch_item.inventory.material,
                            inventory=batch_item.inventory,
                            quantity=batch_item.quantity,
                            tracking_key=batch_item.inventory.tracking_key
                        )
                
                # Update expiry date from inventory items
                expiry_dates = []
                for item in serial_lot.items.all():
                    if item.tracking_key:
                        inventory_items = Inventory.objects.filter(tracking_key=item.tracking_key)
                        for inv in inventory_items:
                            if inv.expiry_date:
                                expiry_dates.append(inv.expiry_date)
                
                if expiry_dates:
                    today = timezone.now().date()
                    nearest_expiry = min(expiry_dates, key=lambda x: abs((x - today).days))
                    serial_lot.expiry_date = nearest_expiry
                
                # Update inventory quantities
                for item in serial_lot.items.all():
                    if item.tracking_key:
                        inventory_items = Inventory.objects.filter(tracking_key=item.tracking_key)
                        for inv in inventory_items:
                            inv.quantity = inv.quantity - item.quantity
                            if inv.quantity < 0:
                                messages.error(request, f'Not enough quantity in inventory for {item.material.name}')
                                return redirect('serial_lot_update', pk=pk)
                            inv.save()
        
        serial_lot.save()
        return redirect('seriallots')
    
    return render(request, 'qb_trace/serial_lot_form.html', {
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
        items = serial_lot.items.select_related(
            'material', 
            'tracking_key', 
            'inventory',
            'inventory__tracking_key'
        )
        
        # Get all expiry dates from inventory items
        expiry_dates = []
        for item in items:
            if item.tracking_key:
                inventory_items = Inventory.objects.filter(tracking_key=item.tracking_key)
                for inv in inventory_items:
                    if inv.expiry_date:
                        expiry_dates.append(inv.expiry_date)
        
        # Find the nearest expiry date
        today = timezone.now().date()
        nearest_expiry = None
        if expiry_dates:
            nearest_expiry = min(expiry_dates, key=lambda x: abs((x - today).days))
        
        data = {
            'serial_lot': {
                'id': serial_lot.id,
                'name': serial_lot.name,
                'batch': serial_lot.batch.name,
                'status': serial_lot.get_status_display(),
                'created_at': serial_lot.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'expiry_date': nearest_expiry.strftime('%Y-%m-%d') if nearest_expiry else None
            },
            'items': [
                {
                    'material_name': item.material.name,
                    'quantity': str(item.quantity),
                    'tracking_key': item.tracking_key.key if item.tracking_key else None,
                    'po_id': po_item.purchase_order.id if (item.tracking_key and (po_item := PurchaseOrderItem.objects.filter(tracking_key=item.tracking_key).first())) else None,
                    'po_number': f"PO-{po_item.purchase_order.id}" if (item.tracking_key and (po_item := PurchaseOrderItem.objects.filter(tracking_key=item.tracking_key).first())) else None,
                    'supplier': po_item.purchase_order.supplier.name if (item.tracking_key and (po_item := PurchaseOrderItem.objects.filter(tracking_key=item.tracking_key).first())) else None,
                    'expiry_dates': [
                        inv.expiry_date.strftime('%Y-%m-%d') 
                        for inv in Inventory.objects.filter(tracking_key=item.tracking_key) 
                        if inv.expiry_date
                    ] if item.tracking_key else []
                }
                for item in items
            ]
        }
        return JsonResponse(data)
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