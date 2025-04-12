from django import forms
from .models import Supplier, Material, Inventory, PurchaseOrder, PurchaseOrderItem, Batch, BatchItem, SerialLot, SerialLotItem, Customer, SalesOrder, SalesOrderItem

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name']

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['material', 'quantity']

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'status']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If this is an existing PO and it's received, disable the status field
        if self.instance and self.instance.status == 'received':
            self.fields['status'].widget.attrs['disabled'] = 'disabled'
            self.fields['status'].widget.attrs['class'] = 'form-control bg-light'
            self.fields['status'].help_text = 'Status cannot be changed once received'

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['item_name', 'material', 'quantity']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'material': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'})
        }

class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['customer', 'status']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

class SalesOrderItemForm(forms.ModelForm):
    class Meta:
        model = SalesOrderItem
        fields = ['item_name', 'material', 'quantity']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'material': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'})
        }

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BatchItemForm(forms.ModelForm):
    class Meta:
        model = BatchItem
        fields = ['inventory', 'quantity']
        widgets = {
            'inventory': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SerialLotForm(forms.ModelForm):
    class Meta:
        model = SerialLot
        fields = ['name', 'batch', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'batch': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class SerialLotItemForm(forms.ModelForm):
    class Meta:
        model = SerialLotItem
        fields = ['material', 'inventory', 'quantity']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),
            'inventory': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'})
        } 