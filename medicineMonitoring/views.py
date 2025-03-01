from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from .models import Medicine, MedicineStock
from datetime import datetime, date

# Helper function to update total value and total quantity
def update_medicine_totals(medicine):
    today = date.today()
    valid_stocks = medicine.stocks.filter(expiration_date__gt=today)
    
    total_value = sum(stock.quantity * medicine.unit_price for stock in valid_stocks)
    total_qty = sum(stock.quantity for stock in valid_stocks)
    
    medicine.total_value = total_value
    medicine.total_quantity = total_qty
    medicine.save(update_fields=["total_value", "total_quantity"])

# Helper function to update the Date of Last Stocked
def update_medicine_date_last_stocked(medicine):
    # Simply set the last stocked date to today's date
    medicine.date_last_stock = date.today()
    medicine.save(update_fields=["date_last_stock"])

# === Medicine List ===
@login_required
def medicine_list(request):
    medicines = Medicine.objects.all().order_by("medicine_name")
    return render(request, "medicineMonitoring/medicine_list.html", {"medicines": medicines})

# === Medicine Detail (Stock) ===
@login_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    today = date.today()
    
    valid_stocks = medicine.stocks.filter(expiration_date__gt=today)
    expired_stocks = medicine.stocks.filter(expiration_date__lte=today)
    
    context = {
        'medicine': medicine,
        'valid_stocks': valid_stocks,
        'expired_stocks': expired_stocks,
        'expired_count': expired_stocks.count(),  
    }
    return render(request, 'medicineMonitoring/medicine_detail.html', context)

# === Medicine Inventory CRUD Operations ===
@login_required
def medicine_add(request):
    if request.method == "POST":
        medicine_name = request.POST.get("medicine_name", "").strip()
        generic_name = request.POST.get("generic_name", "").strip()
        brand_name = request.POST.get("brand_name", "").strip()
        dosage = request.POST.get("dosage", "").strip()  # Retrieve dosage
        unit_price = request.POST.get("unit_price", "").strip()
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
            dosage=dosage,  
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
        unit_price = request.POST.get("unit_price", "").strip()
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
        quantity = request.POST.get("quantity", "").strip()
        notes = request.POST.get("notes", "").strip() 
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
        
        if expiration_date:
            medicine.stocks.create(
                quantity=quantity,
                expiration_date=expiration_date,
                notes=notes  
            )
            update_medicine_totals(medicine) 
            update_medicine_date_last_stocked(medicine)
            messages.success(request, "Stock added successfully!")
            return redirect("medicine-detail", pk=medicine.pk)
        else:
            messages.error(request, "Please provide a valid expiration date.")
    return render(request, "medicineMonitoring/medicine_stock_add.html", {"medicine": medicine})


@login_required
def medicine_stock_update(request, stock_pk):
    stock = get_object_or_404(MedicineStock, pk=stock_pk)
    if request.method == "POST":
        notes = request.POST.get("notes", "").strip() 
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
        stock.notes = notes  
        stock.save()
        update_medicine_totals(stock.medicine)
        update_medicine_date_last_stocked(stock.medicine)
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
        update_medicine_date_last_stocked(stock.medicine)
        messages.success(request, "Stock deleted successfully!")
        return redirect("medicine-detail", pk=medicine_pk)
    return render(request, "medicineMonitoring/medicine_stock_delete.html", {"stock": stock})

@login_required
def medicine_stock_delete_all_expired(request, medicine_pk):
    medicine = get_object_or_404(Medicine, pk=medicine_pk)
    expired_stocks = medicine.stocks.filter(expiration_date__lte=date.today())
    if request.method == "POST":
        expired_stocks.delete()
        update_medicine_totals(medicine)
        update_medicine_date_last_stocked(medicine)
        messages.success(request, "All expired stocks have been deleted successfully!")
        return redirect("medicine-detail", pk=medicine.pk)
    return render(request, "medicineMonitoring/medicine_stock_delete_all_expired.html", {"expired_stocks": expired_stocks})