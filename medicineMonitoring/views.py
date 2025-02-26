from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from .models import Medicine, MedicineStock
from datetime import datetime, date

# Helper function to update total value and total quantity
def update_medicine_totals(medicine):
    total_value = Decimal("0.00")
    total_qty = 0
    for stock in medicine.stocks.all():
        total_value += stock.quantity * medicine.unit_price
        total_qty += stock.quantity
    medicine.total_value = total_value
    medicine.total_quantity = total_qty
    medicine.save(update_fields=["total_value", "total_quantity"])

# === Medicine List ===
@login_required
def medicine_list(request):
    medicines = Medicine.objects.all().order_by("medicine_name")
    return render(request, "medicineMonitoring/medicine_list.html", {"medicines": medicines})

# === Medicine Detail (Stock) ===
@login_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    stocks = medicine.stocks.all().order_by("expiration_date")
    valid_stocks = stocks.filter(expiration_date__gte=date.today())
    expired_stocks = stocks.filter(expiration_date__lt=date.today())
    
    valid_total_qty = sum(stock.quantity for stock in valid_stocks)
    expired_total_qty = sum(stock.quantity for stock in expired_stocks)
    
    return render(request, 'medicineMonitoring/medicine_detail.html', {
        'medicine': medicine,
        'valid_stocks': valid_stocks,
        'expired_stocks': expired_stocks,
        'valid_total_qty': valid_total_qty,
        'expired_total_qty': expired_total_qty,
    })

# === Medicine Inventory CRUD Operations ===
@login_required
def medicine_add(request):
    if request.method == "POST":
        medicine_name = request.POST.get("medicine_name", "").strip()
        generic_name = request.POST.get("generic_name", "").strip()
        brand_name = request.POST.get("brand_name", "").strip()
        unit_price = request.POST.get("unit_price", "").strip()  # NEW
        supplier_name = request.POST.get("supplier_name", "").strip()
        notes = request.POST.get("notes", "").strip()

        try:
            unit_price = Decimal(unit_price)
        except (InvalidOperation, ValueError):
            unit_price = Decimal("0.00")

        Medicine.objects.create(
            medicine_name=medicine_name,
            generic_name=generic_name,
            brand_name=brand_name,
            unit_price=unit_price,  
            supplier_name=supplier_name,
            notes=notes,
        )
        messages.success(request, "Medicine added successfully!")
        return redirect("medicine-list")
    return render(request, "medicineMonitoring/medicine_add.html")

@login_required
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        medicine.medicine_name = request.POST.get("medicine_name", "").strip()
        medicine.generic_name = request.POST.get("generic_name", "").strip()
        medicine.brand_name = request.POST.get("brand_name", "").strip()
        unit_price = request.POST.get("unit_price", "").strip()  # NEW
        try:
            medicine.unit_price = Decimal(unit_price)
        except (InvalidOperation, ValueError):
            medicine.unit_price = Decimal("0.00")
        medicine.supplier_name = request.POST.get("supplier_name", "").strip()
        medicine.notes = request.POST.get("notes", "").strip()
        medicine.save()
        messages.success(request, "Medicine updated successfully!")
        return redirect("medicine-list")
    return render(request, "medicineMonitoring/medicine_update.html", {"medicine": medicine})

@login_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        medicine.delete()
        messages.success(request, "Medicine deleted successfully!")
        return redirect("medicine-list")
    return render(request, "medicineMonitoring/medicine_delete.html", {"medicine": medicine})

# === MEDICINE STOCK CRUD OPERATIONS ===
@login_required
def medicine_stock_add(request, medicine_pk):
    medicine = get_object_or_404(Medicine, pk=medicine_pk)
    if request.method == "POST":
        dosage = request.POST.get("dosage", "").strip()
        quantity = request.POST.get("quantity", "").strip()
        expiration_date_str = request.POST.get("expiration_date", "").strip()
        try:
            quantity = int(quantity)
        except ValueError:
            quantity = 0
        
        expiration_date = None
        for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"):
            try:
                expiration_date = datetime.strptime(expiration_date_str, fmt).date()
                break
            except ValueError:
                continue
        
        if dosage and expiration_date:
            medicine.stocks.create(
                dosage=dosage,
                quantity=quantity,
                expiration_date=expiration_date
            )
            update_medicine_totals(medicine)  # Update total value and quantity
            messages.success(request, "Stock added successfully!")
            return redirect("medicine-detail", pk=medicine.pk)
        else:
            messages.error(request, "Please provide valid dosage and expiration date.")
    return render(request, "medicineMonitoring/medicine_stock_add.html", {"medicine": medicine})

@login_required
def medicine_stock_update(request, stock_pk):
    stock = get_object_or_404(MedicineStock, pk=stock_pk)
    if request.method == "POST":
        stock.dosage = request.POST.get("dosage", "").strip()
        quantity = request.POST.get("quantity", "").strip()
        expiration_date_str = request.POST.get("expiration_date", "").strip()
        try:
            stock.quantity = int(quantity)
        except ValueError:
            stock.quantity = 0
        for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"):
            try:
                stock.expiration_date = datetime.strptime(expiration_date_str, fmt).date()
                break
            except ValueError:
                continue
        stock.save()
        update_medicine_totals(stock.medicine)
        messages.success(request, "Stock updated successfully!")
        return redirect("medicine-detail", pk=stock.medicine.pk)
    return render(request, "medicineMonitoring/medicine_stock_update.html", {"stock": stock})

@login_required
def medicine_stock_delete(request, stock_pk):
    stock = get_object_or_404(MedicineStock, pk=stock_pk)
    if request.method == 'POST':
        medicine_pk = stock.medicine.pk
        stock.delete()
        update_medicine_totals(stock.medicine)
        messages.success(request, "Stock deleted successfully!")
        return redirect("medicine-detail", pk=medicine_pk)
    return render(request, "medicineMonitoring/medicine_stock_delete.html", {"stock": stock})
