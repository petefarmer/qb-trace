"""
URL configuration for qb_trace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from . import views

def redirect_to_suppliers(request):
    return redirect('supplier_list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/update/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # Material URLs
    path('materials/', views.material_list, name='material_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/<int:pk>/update/', views.material_update, name='material_update'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    
    # Inventory URLs
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/create/', views.inventory_create, name='inventory_create'),
    path('inventory/<int:pk>/update/', views.inventory_update, name='inventory_update'),
    path('inventory/<int:pk>/delete/', views.inventory_delete, name='inventory_delete'),
    
    # Purchase Order URLs
    path('purchase-orders/', views.po_list, name='po_list'),
    path('purchase-orders/create/', views.po_create, name='po_create'),
    path('purchase-orders/<int:pk>/update/', views.po_update, name='po_update'),
    path('purchase-orders/<int:pk>/delete/', views.po_delete, name='po_delete'),
    path('purchase-orders/<str:tracking_key>/details/', views.po_details, name='po_details'),
    
    # Batch URLs
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/create/', views.batch_create, name='batch_create'),
    path('batches/<int:pk>/update/', views.batch_update, name='batch_update'),
    path('batches/<int:pk>/delete/', views.batch_delete, name='batch_delete'),
    
    # Serial Lot URLs
    path('seriallots/', views.serial_lot_list, name='seriallots'),
    path('seriallots/create/', views.serial_lot_create, name='serial_lot_create'),
    path('seriallots/<int:pk>/update/', views.serial_lot_update, name='serial_lot_update'),
    path('seriallots/<int:pk>/delete/', views.serial_lot_delete, name='serial_lot_delete'),
    path('seriallots/<int:pk>/details/', views.serial_lot_details, name='serial_lot_details'),
]
