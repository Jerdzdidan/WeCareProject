from django.shortcuts import render
from residentInfo.models import Resident
from patientInfo.models import Patient
from django.http import HttpResponse
from django.template.loader import render_to_string
import io
import openpyxl
from io import BytesIO
from openpyxl.styles import Font, PatternFill
from django.utils import timezone
from xhtml2pdf import pisa
from users.decorators import role_required
from django.contrib.auth.decorators import login_required


# Create your views here.
def residentInfoReport(request):
    category = request.GET.get('category', '')
    gender = request.GET.get('gender', '')
    age_group = request.GET.get('age', '')

    residents = Resident.objects.select_related('family').all()

    if category:
        residents = residents.filter(category=category)
    if gender:
        residents = residents.filter(gender=gender)
    
    if age_group:
        try:
            age_group = int(age_group)
        except ValueError:
            age_group = None
        
        if age_group is not None:
            if age_group == 6:
                residents = residents.filter(age__lte=6)
            elif age_group == 18:
                residents = residents.filter(age__gte=7, age__lte=18)
            elif age_group == 59:
                residents = residents.filter(age__gte=19, age__lte=59)
            elif age_group == 150:
                residents = residents.filter(age__gte=60)

    residents = residents.order_by('family__family_no', 'id')

    return render(request, 'reports/residentInfoReport.html', {'residents': residents})

# Printing and exporting of residents
def get_filtered_residents(request):
    residents = Resident.objects.all()

    category = request.GET.get('category')
    if category:
        residents = residents.filter(category=category)
    gender = request.GET.get('gender')
    if gender:
        residents = residents.filter(gender=gender)
    age_filter = request.GET.get('age')
    if age_filter:
        try:
            age_value = int(age_filter)
            if age_value == 6:
                residents = residents.filter(age__lte=6)
            elif age_value == 18:
                residents = residents.filter(age__gte=7, age__lte=18)
            elif age_value == 59:
                residents = residents.filter(age__gte=19, age__lte=59)
            elif age_value == 150:
                residents = residents.filter(age__gte=60)
        except ValueError:
            pass
    return residents


def resident_export_xlsx(request):
    residents = get_filtered_residents(request)
    output = BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Residents Report"

    # Title styling (row 1)
    title_font = Font(bold=True, size=14)
    ws.merge_cells('A1:N1')
    ws['A1'] = "WeCare - A Resident and Patient Management System"
    ws['A1'].font = title_font

    ws.merge_cells('A2:N2')
    ws['A2'] = f"Category: {request.GET.get('category', 'All')}"
    
    ws.merge_cells('A3:N3')
    ws['A3'] = f"Gender: {request.GET.get('gender', 'All')}"
    
    ws.merge_cells('A4:N4')
    ws['A4'] = f"Age-group: {request.GET.get('age', 'All')}"
    
    headers = [
        "Family No.", "Resident ID", "Last Name", "First Name", "Middle Name",
        "Relationship to Head", "Birthdate", "Age", "Civil Status", "Gender",
        "Category", "Address", "Contact Number", "Date Updated"
    ]
    header_font = Font(bold=True)
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=6, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    
    current_row = 7
    for resident in residents:
        ws.cell(row=current_row, column=1, value=resident.family.family_no if resident.family else "")
        ws.cell(row=current_row, column=2, value=resident.id)
        ws.cell(row=current_row, column=3, value=resident.last_name)
        ws.cell(row=current_row, column=4, value=resident.first_name)
        ws.cell(row=current_row, column=5, value=resident.middle_name)
        ws.cell(row=current_row, column=6, value=resident.relationship_to_head)
        ws.cell(row=current_row, column=7, value=resident.birthdate.strftime("%b. %d, %Y") if resident.birthdate else "")
        ws.cell(row=current_row, column=8, value=resident.age)
        ws.cell(row=current_row, column=9, value=resident.civil_status)
        ws.cell(row=current_row, column=10, value=resident.gender)
        ws.cell(row=current_row, column=11, value=resident.category)
        ws.cell(row=current_row, column=12, value=resident.present_address)
        ws.cell(row=current_row, column=13, value=resident.contact_number)
        ws.cell(row=current_row, column=14, value=resident.date_updated.strftime("%b. %d, %Y") if resident.date_updated else "")
        current_row += 1

    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output, 
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="WeCare Residents Report.xlsx"'
    return response


def resident_export_pdf(request):
    residents = get_filtered_residents(request)
    context = {
        'residents': residents,
        'filter_category': request.GET.get('category', 'All'),
        'filter_gender': request.GET.get('gender', 'All'),
        'filter_age': request.GET.get('age', 'All'),
        'printed_by': request.user.get_full_name() if request.user.is_authenticated else 'Anonymous',
        'printed_on': timezone.now(),
    }
    html = render_to_string('reports/resident_pdf_template.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="WeCare Residents Report.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF <pre>' + html + '</pre>')
    
    return response


# Patient Report
@login_required
def patientInfoReport(request):
    category = request.GET.get('category', '')
    gender = request.GET.get('gender', '')
    street = request.GET.get('street', '')
    age_group = request.GET.get('age', '')  

    patients = Patient.objects.select_related('resident').all()

    if category:
        patients = patients.filter(resident__category=category)
    if gender:
        patients = patients.filter(resident__gender=gender)
    if street:
        patients = patients.filter(resident__present_address__icontains=street)
    
    if age_group:
        try:
            age_group = int(age_group)
        except ValueError:
            age_group = None
        
        if age_group is not None:
            if age_group == 6:
                patients = patients.filter(resident__age__lte=6)
            elif age_group == 18:
                patients = patients.filter(resident__age__gte=7, resident__age__lte=18)
            elif age_group == 59:
                patients = patients.filter(resident__age__gte=19, resident__age__lte=59)
            elif age_group == 150:
                patients = patients.filter(resident__age__gte=60)
    
    patients = patients.order_by('patientID')

    return render(request, 'reports/patientInfoReport.html', {'patients': patients})

# Add these patient export functions to your views.py

def get_filtered_patients(request):
    patients = Patient.objects.select_related('resident').all()

    category = request.GET.get('category')
    if category:
        patients = patients.filter(resident__category=category)
    
    gender = request.GET.get('gender')
    if gender:
        patients = patients.filter(resident__gender=gender)
    
    street = request.GET.get('street')
    if street:
        patients = patients.filter(resident__present_address__icontains=street)
    
    age_filter = request.GET.get('age')
    if age_filter:
        try:
            age_value = int(age_filter)
            if age_value == 6:
                patients = patients.filter(resident__age__lte=6)
            elif age_value == 18:
                patients = patients.filter(resident__age__gte=7, resident__age__lte=18)
            elif age_value == 59:
                patients = patients.filter(resident__age__gte=19, resident__age__lte=59)
            elif age_value == 150:
                patients = patients.filter(resident__age__gte=60)
        except ValueError:
            pass
    
    return patients.order_by('patientID')

@login_required
def patient_export_xlsx(request):
    patients = get_filtered_patients(request)
    output = BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Patients Report"

    # Title styling
    title_font = Font(bold=True, size=14)
    ws.merge_cells('A1:K1')
    ws['A1'] = "WeCare - Patient Medical Report"
    ws['A1'].font = title_font

    # Filter information
    ws.merge_cells('A2:K2')
    ws['A2'] = f"Category: {request.GET.get('category', 'All')}"
    ws.merge_cells('A3:K3')
    ws['A3'] = f"Gender: {request.GET.get('gender', 'All')}"
    ws.merge_cells('A4:K4')
    ws['A4'] = f"Street: {request.GET.get('street', 'All')}"
    ws.merge_cells('A5:K5')
    ws['A5'] = f"Age-group: {request.GET.get('age', 'All')}"

    # Headers
    headers = [
        "Patient ID", "Resident ID", "Full Name", "Age", "Gender",
        "Address", "Diagnosis", "Physician", "Admission Date", 
        "Discharge Date", "Status"
    ]
    
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=7, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill

    # Data rows
    current_row = 8
    for patient in patients:
        resident = patient.resident
        ws.cell(row=current_row, column=1, value=patient.patientID)
        ws.cell(row=current_row, column=2, value=resident.id)
        ws.cell(row=current_row, column=3, value=f"{resident.last_name}, {resident.first_name} {resident.middle_name}".strip())
        ws.cell(row=current_row, column=4, value=resident.age)
        ws.cell(row=current_row, column=5, value=resident.gender)
        ws.cell(row=current_row, column=6, value=resident.present_address)
        ws.cell(row=current_row, column=7, value=patient.diagnosis)
        ws.cell(row=current_row, column=8, value=patient.physician)
        ws.cell(row=current_row, column=9, value=patient.admission_date.strftime("%b. %d, %Y") if patient.admission_date else "")
        ws.cell(row=current_row, column=10, value=patient.discharge_date.strftime("%b. %d, %Y") if patient.discharge_date else "")
        ws.cell(row=current_row, column=11, value=patient.status)
        current_row += 1

    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column_letter].width = adjusted_width

    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output, 
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="WeCare Patients Report.xlsx"'
    return response

@login_required
def patient_export_pdf(request):
    patients = get_filtered_patients(request)
    context = {
        'patients': patients,
        'filter_category': request.GET.get('category', 'All'),
        'filter_gender': request.GET.get('gender', 'All'),
        'filter_street': request.GET.get('street', 'All'),
        'filter_age': request.GET.get('age', 'All'),
        'printed_by': request.user.get_full_name() if request.user.is_authenticated else 'Anonymous',
        'printed_on': timezone.now(),
    }
    html = render_to_string('reports/patient_pdf_template.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="WeCare Patients Report.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    
    return response