import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Family, Resident
from datetime import datetime
from django.contrib.auth.decorators import login_required
from users.decorators import role_required

@login_required
@role_required(['ADMIN', 'BRGY-STAFF', 'BHW', 'DOCTOR'], 'Resident Info')
def family_resident_list(request):
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

    return render(request, 'residentInfo/resident_list.html', {'residents': residents})

@login_required
@role_required(['BRGY-STAFF'], 'Resident Info')
def family_resident_create(request):
    if request.method == "POST":
        head_data = {
            'last_name': request.POST.get('head_last_name', '').strip(),
            'first_name': request.POST.get('head_first_name', '').strip(),
            'middle_name': request.POST.get('head_middle_name', '').strip(),
            'birthdate': request.POST.get('head_birthdate', 'Jan 01, 2000').strip(),
            'age': request.POST.get('head_age', 0),
            'gender': request.POST.get('head_gender', '').strip(),
            'civil_status': request.POST.get('head_civil_status', '').strip(),
            'category': request.POST.get('head_category', '').strip(),
            'present_address': request.POST.get('head_present_address', '').strip(),
            'contact_number': request.POST.get('head_contact_number', '').strip()
        }
        
        try:
            head_data['birthdate'] = datetime.strptime(head_data['birthdate'], "%b %d, %Y").date()
        except ValueError:
            head_data['birthdate'] = datetime(2000, 1, 1).date()
        
        family = Family.objects.create()
        
        Resident.objects.create(
            family=family,
            relationship_to_head='Head of the Family',
            **head_data
        )
        
        members = {}
        for key, value in request.POST.items():
            match = re.match(r'members\[(\d+)\]\[(\w+)\]', key)
            if match:
                idx, field = match.groups()
                if idx not in members:
                    members[idx] = {}
                members[idx][field] = value.strip()
        
        for member in members.values():
            try:
                member['birthdate'] = datetime.strptime(member.get('birthdate', 'Jan 01, 2000'), "%b %d, %Y").date()
            except ValueError:
                member['birthdate'] = datetime(2000, 1, 1).date()
            
            member['present_address'] = head_data['present_address']
            
            Resident.objects.create(
                family=family,
                last_name=member.get('last_name', ''),
                first_name=member.get('first_name', ''),
                middle_name=member.get('middle_name', ''),
                relationship_to_head=member.get('relationship', ''),
                birthdate=member['birthdate'],
                age=member.get('age', 0),
                civil_status=member.get('civil_status', ''),
                gender=member.get('gender', ''),
                category=member.get('category', ''),
                present_address=member['present_address'],
                contact_number=member.get('contact_number', '')
            )
        
        messages.success(request, 'Family successfully registered.')
        return redirect('resident-list')
    
    return render(request, 'residentInfo/resident_create.html')

@login_required
@role_required(['BRGY-STAFF'], 'Resident Info')
def family_resident_update(request, pk):
    family = get_object_or_404(Family, pk=pk)
    head = family.residents.filter(relationship_to_head__iexact='head of the family').first()
    members_qs = family.residents.exclude(relationship_to_head__iexact='head of the family')

    if request.method == "POST":
        head.last_name = request.POST.get('head_last_name', '').strip()
        head.first_name = request.POST.get('head_first_name', '').strip()
        head.middle_name = request.POST.get('head_middle_name', '').strip()

        head_birthdate_str = request.POST.get('head_birthdate', '')
        try:
            head.birthdate = datetime.strptime(head_birthdate_str, "%b %d, %Y").date()
        except ValueError:
            head.birthdate = datetime(2000, 1, 1).date()  
        
        head.age = request.POST.get('head_age', '').strip()
        head.gender = request.POST.get('head_gender', '').strip()
        head.civil_status = request.POST.get('head_civil_status', '').strip()
        head.category = request.POST.get('head_category', '').strip()
        head.present_address = request.POST.get('head_present_address', '').strip()
        head.contact_number = request.POST.get('head_contact_number', '').strip()
        head.save()

        submitted_members = {}
        for key, value in request.POST.items():
            match = re.match(r'members\[(\d+)\]\[(\w+)\]', key)
            if match:
                idx, field = match.groups()
                submitted_members.setdefault(idx, {})[field] = value.strip()

        submitted_member_ids = []
        for member_data in submitted_members.values():
            member_birthdate_str = member_data.get('birthdate', '')
            try:
                member_birthdate = datetime.strptime(member_birthdate_str, "%b %d, %Y").date()
            except ValueError:
                member_birthdate = datetime(2000, 1, 1).date()  
            
            member_id = member_data.get('member_id')
            if member_id:
                resident, created = Resident.objects.update_or_create(
                    id=member_id, family=family,
                    defaults={
                        'last_name': member_data.get('last_name', ''),
                        'first_name': member_data.get('first_name', ''),
                        'middle_name': member_data.get('middle_name', ''),
                        'relationship_to_head': member_data.get('relationship', ''),
                        'birthdate': member_birthdate,
                        'age': member_data.get('age', ''),
                        'civil_status': member_data.get('civil_status', ''),
                        'gender': member_data.get('gender', ''),
                        'category': member_data.get('category', ''),
                        'present_address': member_data.get('present_address', head.present_address),
                        'contact_number': member_data.get('contact_number', ''),
                    }
                )
                submitted_member_ids.append(resident.id)
            else:
                new_resident = Resident.objects.create(
                    family=family,
                    last_name=member_data.get('last_name', ''),
                    first_name=member_data.get('first_name', ''),
                    middle_name=member_data.get('middle_name', ''),
                    relationship_to_head=member_data.get('relationship', ''),
                    birthdate=member_birthdate,
                    age=member_data.get('age', ''),
                    civil_status=member_data.get('civil_status', ''),
                    gender=member_data.get('gender', ''),
                    category=member_data.get('category', ''),
                    present_address=member_data.get('present_address', head.present_address),
                    contact_number=member_data.get('contact_number', ''),
                )
                submitted_member_ids.append(new_resident.id)

        members_qs.exclude(id__in=submitted_member_ids).delete()

        messages.success(request, "Family updated successfully!")
        return redirect('resident-list')

    context = {
        'family': family,
        'head': head,
        'members': list(members_qs.values()),
    }
    return render(request, 'residentInfo/family_update.html', context)

@login_required
@role_required(['BRGY-STAFF'], 'Resident Info')
def family_delete_confirm(request, pk):
    family = get_object_or_404(Family, pk=pk)

    residents = family.residents.all()
    if request.method == 'POST':
        family.delete()
        messages.success(request, "Family record deleted successfully!")
        return redirect('resident-list')
    return render(request, 'residentInfo/family_delete.html', {'family': family, 'residents': residents})

@login_required
@role_required(['BRGY-STAFF'], 'Resident Info')
def resident_update(request, pk):
    resident = get_object_or_404(Resident, pk=pk)
    
    if request.method == "POST":
        resident.last_name = request.POST.get('last_name', '').strip()
        resident.first_name = request.POST.get('first_name', '').strip()
        resident.middle_name = request.POST.get('middle_name', '').strip()
        
        birthdate_str = request.POST.get('birthdate', '')
        try:
            resident.birthdate = datetime.strptime(birthdate_str, "%b %d, %Y").date()
        except ValueError:
            resident.birthdate = datetime(2000, 1, 1).date()
        
        resident.age = request.POST.get('age', '').strip()
        resident.gender = request.POST.get('gender', '').strip()
        resident.civil_status = request.POST.get('civil_status', '').strip()
        resident.category = request.POST.get('category', '').strip()
        resident.present_address = request.POST.get('present_address', '').strip()
        resident.contact_number = request.POST.get('contact_number', '').strip()
        resident.save()
        
        messages.success(request, "Resident updated successfully!")
        return redirect('resident-list')
    
    return render(request, 'residentInfo/resident_update.html', {'resident': resident})

@login_required
@role_required(['BRGY-STAFF'], 'Resident Info')
def resident_delete_confirm(request, pk):
    try:
        resident = Resident.objects.get(pk=pk)
    except Resident.DoesNotExist:
        messages.warning(request, "No resident records found!")
        return redirect('resident-list')
    
    resident.delete()
    messages.success(
        request,
        f"Resident record deleted for: {resident.last_name}, {resident.first_name} successfully!"
    )
    return redirect('resident-list')