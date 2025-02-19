import re
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Family, Resident

def family_resident_list(request):
    families = Family.objects.all().order_by('family_no')
    return render(request, 'residentInfo/resident_list.html', {'families': families})

def family_resident_create(request):
    if request.method == "POST":
        head_last_name       = request.POST.get('head_last_name')
        head_first_name      = request.POST.get('head_first_name')
        head_middle_name     = request.POST.get('head_middle_name')
        head_birthdate       = request.POST.get('head_birthdate')
        head_age             = request.POST.get('head_age')
        head_gender          = request.POST.get('head_gender')
        head_civil_status    = request.POST.get('head_civil_status')
        head_category        = request.POST.get('head_category')
        head_present_address = request.POST.get('head_present_address')
        head_contact_number  = request.POST.get('head_contact_number')

        family = Family.objects.create()

        Resident.objects.create(
            family=family,
            last_name=head_last_name,
            first_name=head_first_name,
            middle_name=head_middle_name,
            relationship_to_head='Head',  
            birthdate=head_birthdate,
            age=head_age,
            civil_status=head_civil_status,
            gender=head_gender,
            category=head_category,
            present_address=head_present_address,
            contact_number=head_contact_number
        )

        members = {}
        for key, value in request.POST.items():
            if key.startswith('members'):
                match = re.match(r'members\[(\d+)\]\[(\w+)\]', key)
                if match:
                    idx, field = match.groups()
                    if idx not in members:
                        members[idx] = {}
                    members[idx][field] = value

        for member in members.values():
            Resident.objects.create(
                family=family,
                last_name=member.get('last_name'),
                first_name=member.get('first_name'),
                middle_name=member.get('middle_name'),
                relationship_to_head=member.get('relationship'),
                birthdate=member.get('birthdate'),
                age=member.get('age'),
                civil_status=member.get('civil_status'),
                gender=member.get('gender'),
                category=member.get('category'),
                present_address=member.get('present_address'),
                contact_number=member.get('contact_number')
            )
        
        messages.sucess(request, 'Family successfully registered.')
        return redirect('resident-list')  
    
    return render(request, 'family_registration.html')

# views.py
import re
from django.shortcuts import render, redirect, get_object_or_404
from .models import Family, Resident

def family_resident_update(request, family_no):

    family = get_object_or_404(Family, pk=family_no)

    head = family.residents.filter(relationship_to_head='Head').first()

    members_qs = family.residents.exclude(relationship_to_head='Head')
    
    if request.method == "POST":
        head.last_name       = request.POST.get('head_last_name')
        head.first_name      = request.POST.get('head_first_name')
        head.middle_name     = request.POST.get('head_middle_name')
        head.birthdate       = request.POST.get('head_birthdate')
        head.age             = request.POST.get('head_age')
        head.gender          = request.POST.get('head_gender')
        head.civil_status    = request.POST.get('head_civil_status')
        head.category        = request.POST.get('head_category')
        head.present_address = request.POST.get('head_present_address')
        head.contact_number  = request.POST.get('head_contact_number')
        head.save()

        submitted_members = {}
        for key, value in request.POST.items():
            if key.startswith('members'):
                match = re.match(r'members\[(\d+)\]\[(\w+)\]', key)
                if match:
                    idx, field = match.groups()
                    submitted_members.setdefault(idx, {})[field] = value

        submitted_member_ids = []

        for member_data in submitted_members.values():
            member_id = member_data.get('member_id')
            if member_id:  
                submitted_member_ids.append(int(member_id))
                try:
                    resident = Resident.objects.get(id=member_id, family=family)
                    resident.last_name       = member_data.get('last_name')
                    resident.first_name      = member_data.get('first_name')
                    resident.middle_name     = member_data.get('middle_name')
                    resident.relationship_to_head = member_data.get('relationship')
                    resident.birthdate       = member_data.get('birthdate')
                    resident.age             = member_data.get('age')
                    resident.civil_status    = member_data.get('civil_status')
                    resident.gender          = member_data.get('gender')
                    resident.category        = member_data.get('category')
                    resident.present_address = member_data.get('present_address')
                    resident.contact_number  = member_data.get('contact_number')
                    resident.save()
                except Resident.DoesNotExist:
                    new_resident = Resident.objects.create(
                        family=family,
                        last_name=member_data.get('last_name'),
                        first_name=member_data.get('first_name'),
                        middle_name=member_data.get('middle_name'),
                        relationship_to_head=member_data.get('relationship'),
                        birthdate=member_data.get('birthdate'),
                        age=member_data.get('age'),
                        civil_status=member_data.get('civil_status'),
                        gender=member_data.get('gender'),
                        category=member_data.get('category'),
                        present_address=member_data.get('present_address'),
                        contact_number=member_data.get('contact_number')
                    )
                    submitted_member_ids.append(new_resident.id)
            else:
                new_resident = Resident.objects.create(
                    family=family,
                    last_name=member_data.get('last_name'),
                    first_name=member_data.get('first_name'),
                    middle_name=member_data.get('middle_name'),
                    relationship_to_head=member_data.get('relationship'),
                    birthdate=member_data.get('birthdate'),
                    age=member_data.get('age'),
                    civil_status=member_data.get('civil_status'),
                    gender=member_data.get('gender'),
                    category=member_data.get('category'),
                    present_address=member_data.get('present_address'),
                    contact_number=member_data.get('contact_number')
                )
                submitted_member_ids.append(new_resident.id)
        
        for member in members_qs:
            if member.id not in submitted_member_ids:
                member.delete()

        return redirect('success')  
    
    context = {
        'family': family,
        'head': head,
        'members': list(members_qs.values()),  
    }
    return render(request, 'family_update.html', context)