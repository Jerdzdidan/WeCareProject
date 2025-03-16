from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from .models import Medicine, MedicineStock
from datetime import datetime, date
from patientInfo.models import MedicineTracking
import re
from django.db.models import Sum
from users.decorators import role_required
from logs.models import Logs

# Helper function to update total value and total quantity
def update_medicine_totals(medicine):
    today = date.today()
    valid_stocks = medicine.stocks.filter(expiration_date__gt=today)
    
    total_qty = sum(stock.quantity for stock in valid_stocks)
    
    medicine.total_quantity = total_qty
    medicine.save(update_fields=["total_quantity"])

# Helper function to update the Date of Last Stocked
def update_medicine_date_last_stocked(medicine):
    medicine.date_last_stock = date.today()
    medicine.save(update_fields=["date_last_stock"])

# === Medicine List ===
@login_required
@role_required(['ADMIN'], 'Medicine Record')
def medicine_list(request):
    medicines = Medicine.objects.all().order_by("medicine_name")
    return render(request, "medicineMonitoring/medicine_list.html", {"medicines": medicines})

# === Medicine Detail (Stock) ===
@login_required
@role_required(['ADMIN'], 'Medicine details on the Medicine Record')
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    patient_medicine_tracking = MedicineTracking.objects.filter(medicine=medicine)

    releasedQty = patient_medicine_tracking.aggregate(total=Sum('quantity_used'))['total'] or 0

    today = date.today()
    
    valid_stocks = medicine.stocks.filter(expiration_date__gt=today)
    expired_stocks = medicine.stocks.filter(expiration_date__lte=today)
    
    available_stocks = valid_stocks.filter(quantity__gt=10)
    availableQty = available_stocks.aggregate(total=Sum('quantity'))['total'] or 0
    
    context = {
        'medicine': medicine,
        'valid_stocks': valid_stocks,
        'expired_stocks': expired_stocks,
        'expired_count': expired_stocks.count(),  
        'patient_medicine_tracking': patient_medicine_tracking,
        'releasedQty': releasedQty,
        'available_stocks': available_stocks,  
        'availableQty': availableQty,          
    }
    return render(request, 'medicineMonitoring/medicine_detail.html', context)

# === Medicine Inventory CRUD Operations ===
@login_required
@role_required(['ADMIN'], 'Add medicine records on the Medicine Record')
def medicine_add(request):
    if request.method == "POST":
        medicine_name = request.POST.get("medicine_name", "").strip()
        brand_name = request.POST.get("brand_name", "").strip()
        dosage = request.POST.get("dosage", "").strip()  
        supplier_name = request.POST.get("supplier_name", "").strip()
        notes = request.POST.get("notes", "").strip()
        date_last_stock = date.today()

        Medicine.objects.create(
            medicine_name=medicine_name,
            brand_name=brand_name,
            dosage=dosage,  
            supplier_name=supplier_name,
            date_last_stock = date_last_stock,
            notes=notes,
        )
        messages.success(request, "Medicine added successfully!")
        return redirect("medicine-list")
    return render(request, "medicineMonitoring/medicine_add.html")

@login_required
@role_required(['ADMIN'], 'Update medicine records on the Medicine Record')
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        medicine.medicine_name = request.POST.get("medicine_name", "").strip()
        medicine.brand_name = request.POST.get("brand_name", "").strip()

        medicine.supplier_name = request.POST.get("supplier_name", "").strip()
        medicine.notes = request.POST.get("notes", "").strip()
        medicine.save()

        update_medicine_totals(medicine)
        update_medicine_date_last_stocked(medicine)
        
        trackings = MedicineTracking.objects.filter(medicine=medicine)
        for tracking in trackings:
            if medicine.dosage:
                match = re.match(r"^([\d\.]+)\s*(.*)$", medicine.dosage.strip())
                if match:
                    base_value = float(match.group(1))
                    unit = match.group(2)
                    tracking.total_dosage = f"{tracking.quantity_used * base_value} {unit}".strip()
            tracking.save(update_fields=["total_dosage"])

        now = datetime.now()
        formatted_date = now.strftime("%b. %d, %Y")
        formatted_time = now.strftime("%I:%M%p")

        Logs.objects.create(
            datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
            timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
            module="Medicine Record",
            action="Update Medicine",
            performed_to=f"Medicine ID - {medicine.id}: {medicine.medicine_name}",
            performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
        )
        
        messages.success(request, "Medicine updated successfully, and tracking records have been updated!")
        return redirect("medicine-list")
    return render(request, "medicineMonitoring/medicine_update.html", {"medicine": medicine})

@login_required
@role_required(['ADMIN'], 'Delete medicine records on the Medicine Record')
def medicine_delete(request, pk):
    try:
        medicine = Medicine.objects.get(pk=pk)
    except Medicine.DoesNotExist:
        messages.warning(request, "No medicine records found!")
        return redirect('medicine-list')

    now = datetime.now()
    formatted_date = now.strftime("%b. %d, %Y")
    formatted_time = now.strftime("%I:%M%p")

    Logs.objects.create(
        datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
        timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
        module="Medicine Record",
        action="Delete Medicine",
        performed_to=f"Medicine ID - {medicine.id}: {medicine.medicine_name}",
        performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
    )

    medicine.delete()
    messages.success(request, "Medicine deleted successfully!")
    return redirect("medicine-list")


# === MEDICINE STOCK CRUD OPERATIONS ===
@login_required
@role_required(['ADMIN'], 'Add medicine stock on the Medicine Record')
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
@role_required(['ADMIN'], 'Update medicine stock on the Medicine Record')
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

        now = datetime.now()
        formatted_date = now.strftime("%b. %d, %Y")
        formatted_time = now.strftime("%I:%M%p")

        Logs.objects.create(
            datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
            timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
            module="Medicine Record",
            action="Update Medicine Stock",
            performed_to=f"Medicine Stock for Medicine ID - {stock.medicine.id}: {stock.medicine.medicine_name}",
            performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
        )

        messages.success(request, "Stock updated successfully!")
        return redirect("medicine-detail", pk=stock.medicine.pk)
    return render(request, "medicineMonitoring/medicine_stock_update.html", {"stock": stock})


@login_required
@role_required(['ADMIN'], 'Delete medicine stock on the Medicine Record')
def medicine_stock_delete(request, medicine_pk, stock_pk):
    try:
        stock = MedicineStock.objects.get(pk=stock_pk)
    except MedicineStock.DoesNotExist:
        messages.warning(request, "No stock records found!")
        return redirect("medicine-detail", pk=medicine_pk)
    
    now = datetime.now()
    formatted_date = now.strftime("%b. %d, %Y")
    formatted_time = now.strftime("%I:%M%p")

    Logs.objects.create(
        datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
        timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
        module="Medicine",
        action="Delete Medicine Stock",
        performed_to=f"Medicine Stock for Medicine ID - {stock.medicine.id}: {stock.medicine.medicine_name}",
        performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
    )

    stock.delete()
    update_medicine_totals(stock.medicine)
    update_medicine_date_last_stocked(stock.medicine)
    messages.success(request, f"Stock deleted for {stock.medicine.medicine_name} successfully!")
    return redirect("medicine-detail", pk=medicine_pk)


@login_required
@role_required(['ADMIN'], 'Delete all expired medicine stock on the Medicine Record')
def medicine_stock_delete_all_expired(request, medicine_pk):
    medicine = get_object_or_404(Medicine, pk=medicine_pk)
    expired_stocks = medicine.stocks.filter(expiration_date__lte=date.today())

    now = datetime.now()
    formatted_date = now.strftime("%b. %d, %Y")
    formatted_time = now.strftime("%I:%M%p")

    Logs.objects.create(
        datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
        timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
        module="Medicine Record",
        action="Delete Expired Medicine Stock",
        performed_to=f"Expired stocks for Medicine ID - {medicine.id}: {medicine.medicine_name}",
        performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
    )

    if not expired_stocks.exists():
        messages.warning(request, f"No expired stocks found for {medicine.medicine_name}!")
    else:
        expired_stocks.delete()
        update_medicine_totals(medicine)
        update_medicine_date_last_stocked(medicine)
        messages.success(request, f"All expired stocks have been deleted for {medicine.medicine_name} successfully!")
    return redirect("medicine-detail", pk=medicine.pk)


# Medicine Tracking DELETE ALL
@login_required
@role_required(['ADMIN'], 'Delete all released_qty medicine stock on the Medicine Record')
def medicine_tracking_delete_all_records(request, medicine_pk):
    medicine = get_object_or_404(Medicine, pk=medicine_pk)
    medicine_patient_records = MedicineTracking.objects.filter(medicine=medicine)

    if not medicine_patient_records.exists():
        messages.warning(request, f"No patient entry of stocks found for {medicine.medicine_name}!")
    else:
        medicine_patient_records.delete()
        messages.success(request, f"All patient entry of stocks have been deleted for {medicine.medicine_name} successfully!")
    
    return redirect("medicine-detail", pk=medicine.pk)
