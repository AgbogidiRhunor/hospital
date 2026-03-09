from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from .models import User, ConsultingRoom, SPECIALIZATIONS


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_approved and not user.is_staff:
                messages.error(request, 'Your account is pending approval.')
                return render(request, 'login.html')

            login(request, user)
            request.session.cycle_key()
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def signup_view(request):
    if request.method == 'POST':
        d = request.POST
        username = d.get('username', '').strip()
        password = d.get('password', '')
        password2 = d.get('password2', '')
        role = d.get('role', 'patient')
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html', {'specializations': SPECIALIZATIONS})
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'signup.html', {'specializations': SPECIALIZATIONS})
        user = User.objects.create_user(
            username=username, password=password,
            first_name=d.get('first_name', ''),
            last_name=d.get('last_name', ''),
            email=d.get('email', ''),
            role=role,
            phone=d.get('phone', ''),
            preferred_name=d.get('preferred_name', ''),
        )
        if role == 'doctor':
            user.doctor_type = d.get('doctor_type', 'general')
            user.specialization = d.get('specialization', '')
            user.license_number = d.get('license_number', '')
        if role == 'patient':
            user.is_approved = True
        user.save()
        # Bug fix: DON'T auto-login patients, redirect to login with success message
        messages.success(request, 'Account created successfully! Please sign in.')
        return redirect('login')
    return render(request, 'signup.html', {'specializations': SPECIALIZATIONS})


@login_required
def dashboard(request):
    role = request.user.role
    if role == 'patient': return redirect('patient_dashboard')
    elif role == 'doctor': return redirect('doctor_dashboard')
    elif role == 'nurse': return redirect('nurse_dashboard')
    elif role == 'pharmacist': return redirect('pharmacist_dashboard')
    elif role == 'lab_attendant': return redirect('lab_dashboard')
    elif role == 'receptionist': return redirect('receptionist_dashboard')
    elif role == 'accountant': return redirect('accountant_dashboard')
    elif request.user.is_staff: return redirect('/admin/')
    return redirect('login')


# DOCTOR DASHBOARD
@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        return redirect('dashboard')
    from records.models import PatientVisit
    doctor = request.user
    # Show visits that are active, exclude completed AND visits with active admissions
    from records.models import WardAdmission as _WA
    admitted_visit_ids = _WA.objects.filter(
        doctor=doctor, status__in=['pending_payment', 'paid', 'admitted']
    ).values_list('visit_id', flat=True)

    visits = PatientVisit.objects.filter(
        doctor=doctor
    ).exclude(
        status__in=['pending_payment', 'completed']
    ).exclude(
        id__in=admitted_visit_ids
    ).prefetch_related(
        'vitals', 'prescriptions__drugs__drug', 'lab_requests__tests__test',
        'doctor_notes', 'payments',
        'surgeries__surgery_drugs__drug',
        'surgeries__surgery_labs__test',
        'surgeries__admission',
    ).select_related('patient', 'nurse').order_by('queue_number', 'created_at')

    rooms = ConsultingRoom.objects.filter(is_active=True)
    for room in rooms:
        room.current_doc = User.objects.filter(
            consulting_room=room, role='doctor', is_available=True
        ).exclude(pk=doctor.pk).first()

    available_pharmacists = User.objects.filter(role='pharmacist', is_approved=True, is_available=True)
    available_lab_attendants = User.objects.filter(role='lab_attendant', is_approved=True, is_available=True)
    # Count waiting patients (exclude admitted ones)
    waiting_count = PatientVisit.objects.filter(doctor=doctor).exclude(
        status__in=['pending_payment', 'completed']
    ).exclude(
        id__in=admitted_visit_ids
    ).count()

    from records.models import WardAdmission
    doctor_admissions = WardAdmission.objects.filter(
        doctor=doctor, status__in=['paid', 'admitted']
    ).select_related('patient', 'nurse').prefetch_related('prescriptions__items__drug').order_by('ward', 'bed_number')

    ctx = {
        'visits': visits,
        'rooms': rooms,
        'available_pharmacists': available_pharmacists,
        'available_lab_attendants': available_lab_attendants,
        'doctor': doctor,
        'waiting_count': waiting_count,
        'doctor_admissions': doctor_admissions,
    }
    return render(request, 'doctor.html', ctx)


@login_required
def toggle_availability(request):
    if request.method == 'POST':
        user = request.user
        field = request.POST.get('field', 'is_available')
        if field not in ['is_available', 'is_on_sit', 'is_vital_signs_nurse']:
            return JsonResponse({'error': 'Invalid field'}, status=400)
        if field == 'is_vital_signs_nurse' and not user.is_vital_signs_nurse:
            count = User.objects.filter(is_vital_signs_nurse=True, role='nurse').count()
            if count >= 2:
                return JsonResponse({'error': 'Maximum 2 vital-sign nurses at once', 'max_reached': True}, status=400)
        setattr(user, field, not getattr(user, field))
        if field == 'is_available' and not user.is_available and user.role == 'doctor':
            user.consulting_room = None
        user.save()
        return JsonResponse({'status': 'ok', 'value': getattr(user, field)})
    return JsonResponse({'error': 'POST only'}, status=405)


@login_required
def select_consulting_room(request):
    if request.method == 'POST' and request.user.role == 'doctor':
        room_id = request.POST.get('room_id')
        if room_id == '':
            request.user.consulting_room = None
            request.user.save()
            return JsonResponse({'status': 'ok', 'room': None})
        room = get_object_or_404(ConsultingRoom, pk=room_id, is_active=True)
        other = User.objects.filter(consulting_room=room, is_available=True).exclude(pk=request.user.pk).first()
        if other:
            return JsonResponse({'error': f'Room taken by Dr. {other.get_full_name() or other.username}'}, status=400)
        request.user.consulting_room = room
        request.user.is_available = True
        request.user.save()
        return JsonResponse({'status': 'ok', 'room': room.display_name})
    return JsonResponse({'error': 'invalid'}, status=400)


@login_required
def end_visit(request, visit_id):
    if request.method == 'POST' and request.user.role == 'doctor':
        from records.models import PatientVisit
        from accounting.models import Payment
        visit = get_object_or_404(PatientVisit, pk=visit_id, doctor=request.user)
        pending = Payment.objects.filter(visit=visit, is_paid=False).count()
        if pending:
            return JsonResponse({'error': f'Cannot end visit: {pending} payment(s) still pending. All payments must be settled first.'}, status=400)
        visit.status = 'completed'
        visit.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def delete_lab_request(request, lr_id):
    if request.method == 'POST' and request.user.role == 'doctor':
        from lab.models import LabRequest
        lr = get_object_or_404(LabRequest, pk=lr_id, doctor=request.user)
        lr.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def delete_prescription(request, rx_id):
    if request.method == 'POST' and request.user.role == 'doctor':
        from pharmacy.models import Prescription
        rx = get_object_or_404(Prescription, pk=rx_id, doctor=request.user)
        rx.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


# ─── NURSE ──────────────────────────────────────────────────────────────────────
@login_required
def nurse_dashboard(request):
    if request.user.role != 'nurse':
        return redirect('dashboard')
    from records.models import PatientVisit
    nurse = request.user
    visits = PatientVisit.objects.filter(
        nurse=nurse, status__in=['paid', 'vitals']
    ).select_related('patient', 'doctor').order_by('queue_number', 'created_at')

    # Recent history (not hard-deleted from dashboard)
    history = PatientVisit.objects.filter(
        nurse=nurse, nurse_history_deleted=False,
        status__in=['with_doctor', 'lab_pending', 'lab_paid', 'lab_processing',
                    'rx_pending', 'rx_paid', 'pharmacy', 'completed']
    ).select_related('patient', 'doctor').order_by('-updated_at')[:30]

    ctx = {'visits': visits, 'history': history, 'nurse': nurse}
    return render(request, 'nurse_dashboard.html', ctx)


@login_required
def submit_vitals(request, visit_id):
    if request.method == 'POST' and request.user.role == 'nurse':
        from records.models import PatientVisit, VitalSigns
        visit = get_object_or_404(PatientVisit, pk=visit_id, nurse=request.user)
        d = request.POST
        VitalSigns.objects.update_or_create(visit=visit, defaults={
            'nurse': request.user,
            'blood_pressure': d.get('blood_pressure', ''),
            'pulse_rate': d.get('pulse_rate', ''),
            'temperature': d.get('temperature', ''),
            'respiratory_rate': d.get('respiratory_rate', ''),
            'oxygen_saturation': d.get('oxygen_saturation', ''),
            'weight': d.get('weight', ''),
            'height': d.get('height', ''),
            'bmi': d.get('bmi', ''),
            'pain_level': d.get('pain_level', ''),
            'nurse_note': d.get('nurse_note', ''),
        })
        visit.status = 'with_doctor'
        visit.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def nurse_delete_history(request, visit_id):
    if request.method == 'POST' and request.user.role == 'nurse':
        from records.models import PatientVisit
        visit = get_object_or_404(PatientVisit, pk=visit_id, nurse=request.user)
        visit.nurse_history_deleted = True
        visit.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def nurse_history(request):
    if request.user.role != 'nurse':
        return redirect('dashboard')
    from records.models import PatientVisit
    history = PatientVisit.objects.filter(
        nurse=request.user
    ).select_related('patient', 'doctor', 'vitals').order_by('-updated_at')
    return render(request, 'nurse_history.html', {'history': history})


# ─── RECEPTIONIST ───────────────────────────────────────────────────────────────
@login_required
def receptionist_dashboard(request):
    if request.user.role != 'receptionist':
        return redirect('dashboard')
    from records.models import PatientVisit
    accountants = User.objects.filter(role='accountant', is_approved=True)
    nurses = User.objects.filter(role='nurse', is_approved=True)
    general_doctors = User.objects.filter(role='doctor', is_approved=True, doctor_type='general')
    specialist_doctors = User.objects.filter(role='doctor', is_approved=True, doctor_type='specialist')
    recent_visits = PatientVisit.objects.filter(
        receptionist=request.user
    ).select_related('patient', 'doctor', 'nurse', 'accountant').order_by('-created_at')[:50]
    ctx = {
        'accountants': accountants, 'nurses': nurses,
        'general_doctors': general_doctors, 'specialist_doctors': specialist_doctors,
        'recent_visits': recent_visits,
        'specializations': SPECIALIZATIONS,
    }
    return render(request, 'receptionist.html', ctx)


@login_required
def search_patient(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'results': []})
    patients = User.objects.filter(role='patient', is_approved=True).filter(
        Q(username__icontains=q) | Q(first_name__icontains=q) |
        Q(last_name__icontains=q) | Q(preferred_name__icontains=q)
    )[:10]
    results = [{'id': p.pk, 'name': p.display_name, 'username': p.username} for p in patients]
    return JsonResponse({'results': results})


@login_required
def search_doctors(request):
    q = request.GET.get('q', '').strip()
    dtype = request.GET.get('type', '')
    spec = request.GET.get('specialization', '').strip()
    qs = User.objects.filter(role='doctor', is_approved=True)
    if dtype:
        qs = qs.filter(doctor_type=dtype)
    if spec:
        qs = qs.filter(specialization=spec)
    if q:
        qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(preferred_name__icontains=q))
    results = [{
        'id': d.pk,
        'name': d.get_full_name() or d.username,
        'type': d.get_doctor_type_display() if d.doctor_type else '',
        'specialization': d.get_specialization_display() if d.specialization else '',
        'available': d.is_available,
        'room': d.consulting_room.display_name if d.consulting_room else '',
    } for d in qs[:20]]
    return JsonResponse({'results': results})


@login_required
def create_visit(request):
    if request.method == 'POST' and request.user.role == 'receptionist':
        from records.models import PatientVisit
        from accounting.models import Payment
        d = request.POST
        try:
            patient = User.objects.get(pk=d.get('patient_id'), role='patient')
        except User.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=400)
        try:
            doctor = User.objects.get(pk=d.get('doctor_id'), role='doctor')
        except User.DoesNotExist:
            return JsonResponse({'error': 'Doctor not found'}, status=400)
        try:
            nurse = User.objects.get(pk=d.get('nurse_id'), role='nurse')
        except User.DoesNotExist:
            return JsonResponse({'error': 'Nurse not found'}, status=400)
        try:
            accountant = User.objects.get(pk=d.get('accountant_id'), role='accountant')
        except User.DoesNotExist:
            return JsonResponse({'error': 'Accountant not found'}, status=400)
        try:
            fee = float(d.get('consultation_fee', 0))
        except:
            fee = 0
        with transaction.atomic():
            # Assign next queue number for today
            from django.utils import timezone
            today = timezone.now().date()
            last_q = PatientVisit.objects.filter(
                created_at__date=today
            ).order_by('-queue_number').values_list('queue_number', flat=True).first()
            queue_number = (last_q or 0) + 1

            visit = PatientVisit.objects.create(
                patient=patient, receptionist=request.user,
                doctor=doctor, nurse=nurse, accountant=accountant,
                consultation_fee=fee, status='pending_payment',
                queue_number=queue_number,
            )
            Payment.objects.create(
                visit=visit, patient=patient, accountant=accountant,
                payment_type='consultation', amount=fee, is_paid=False,
            )
        return JsonResponse({'status': 'ok', 'visit_id': visit.pk})
    return JsonResponse({'error': 'forbidden'}, status=403)


# ─── PATIENT ────────────────────────────────────────────────────────────────────
@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return redirect('dashboard')
    from records.models import PatientVisit
    # Current active visit (most recent non-completed)
    active_visit = PatientVisit.objects.filter(
        patient=request.user
    ).exclude(status='completed').select_related('doctor', 'nurse', 'accountant').prefetch_related(
        'vitals', 'prescriptions__drugs__drug',
        'lab_requests__tests__test',
        'payments', 'doctor_notes',
        'surgeries__surgery_drugs__drug',
        'surgeries__surgery_labs__test',
        'surgeries__admission',
        'surgeries__payments',
        'admissions__prescriptions__items__drug',
        'admissions__visit__lab_requests__tests__test',
        'admissions__payments',
    ).first()
    from records.models import Surgery
    pending_surgery_reviews = Surgery.objects.filter(
        patient=request.user, status='draft'
    ).select_related('doctor', 'visit').prefetch_related(
        'surgery_drugs__drug', 'surgery_labs__test', 'admission'
    )
    ctx = {
        'user': request.user,
        'active_visit': active_visit,
        'pending_surgery_reviews': pending_surgery_reviews,
    }
    return render(request, 'patient.html', ctx)


@login_required
def patient_records(request):
    if request.user.role != 'patient':
        return redirect('dashboard')
    from records.models import PatientVisit
    visits = PatientVisit.objects.filter(
        patient=request.user
    ).prefetch_related(
        'vitals', 'prescriptions__drugs__drug', 'lab_requests__tests__test',
        'doctor_notes', 'payments'
    ).select_related('doctor', 'nurse', 'accountant')
    ctx = {'visits': visits, 'user': request.user}
    return render(request, 'patient_records.html', ctx)


@login_required
def patient_profile(request):
    if request.user.role != 'patient':
        return redirect('dashboard')
    if request.method == 'POST':
        u = request.user
        d = request.POST
        u.first_name = d.get('first_name', u.first_name)
        u.last_name = d.get('last_name', u.last_name)
        u.preferred_name = d.get('preferred_name', u.preferred_name)
        u.email = d.get('email', u.email)
        u.phone = d.get('phone', u.phone)
        u.address = d.get('address', u.address)
        u.gender = d.get('gender', u.gender)
        if d.get('date_of_birth'):
            from datetime import datetime
            try:
                u.date_of_birth = datetime.strptime(d.get('date_of_birth'), '%Y-%m-%d').date()
            except:
                pass
        u.blood_group = d.get('blood_group', u.blood_group)
        u.genotype = d.get('genotype', u.genotype)
        u.allergies = d.get('allergies', u.allergies)
        u.medical_history = d.get('medical_history', u.medical_history)
        u.current_medications = d.get('current_medications', u.current_medications)
        u.family_history = d.get('family_history', u.family_history)
        u.surgical_history = d.get('surgical_history', u.surgical_history)
        u.immunizations = d.get('immunizations', u.immunizations)
        u.occupation = d.get('occupation', u.occupation)
        u.marital_status = d.get('marital_status', u.marital_status)
        u.nationality = d.get('nationality', u.nationality)
        u.religion = d.get('religion', u.religion)
        u.next_of_kin_name = d.get('next_of_kin_name', u.next_of_kin_name)
        u.next_of_kin_phone = d.get('next_of_kin_phone', u.next_of_kin_phone)
        u.next_of_kin_relationship = d.get('next_of_kin_relationship', u.next_of_kin_relationship)
        u.emergency_contact_name = d.get('emergency_contact_name', u.emergency_contact_name)
        u.emergency_contact_phone = d.get('emergency_contact_phone', u.emergency_contact_phone)
        u.emergency_contact_relationship = d.get('emergency_contact_relationship', u.emergency_contact_relationship)
        u.disabilities = d.get('disabilities', u.disabilities)
        u.home_phone = d.get('home_phone', u.home_phone)
        u.work_phone = d.get('work_phone', u.work_phone)
        u.temporary_address = d.get('temporary_address', u.temporary_address)
        u.employer = d.get('employer', u.employer)
        u.sex_at_birth = d.get('sex_at_birth', u.sex_at_birth)
        u.has_support_person = d.get('has_support_person') == 'yes'
        u.has_legal_guardian = d.get('has_legal_guardian') == 'yes'
        u.save()
        return JsonResponse({'status': 'ok'})
    from management.models import BLOOD_GROUPS, GENOTYPES
    return render(request, 'patient_profile.html', {'u': request.user, 'blood_groups': BLOOD_GROUPS, 'genotypes': GENOTYPES})


@login_required
def update_visit_summary(request, visit_id):
    if request.method == 'POST' and request.user.role == 'patient':
        from records.models import PatientVisit
        visit = get_object_or_404(PatientVisit, pk=visit_id, patient=request.user)
        visit.visit_summary = request.POST.get('summary', '')
        visit.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


# ─── HISTORY PAGES ──────────────────────────────────────────────────────────────
@login_required
def doctor_history(request):
    if request.user.role != 'doctor':
        return redirect('dashboard')
    from records.models import PatientVisit
    visits = PatientVisit.objects.filter(doctor=request.user).prefetch_related(
        'vitals', 'prescriptions__drugs__drug', 'lab_requests__tests__test',
        'payments', 'doctor_notes'
    ).select_related('patient', 'nurse')
    return render(request, 'doctor_history.html', {'visits': visits})


@login_required
def pharmacist_history(request):
    if request.user.role != 'pharmacist':
        return redirect('dashboard')
    from pharmacy.models import Prescription
    rxs = Prescription.objects.filter(pharmacist=request.user).prefetch_related(
        'drugs__drug'
    ).select_related('patient', 'visit', 'doctor')
    return render(request, 'pharmacist_history.html', {'rxs': rxs})


@login_required
def lab_attendant_history(request):
    if request.user.role != 'lab_attendant':
        return redirect('dashboard')
    from lab.models import LabRequest
    requests = LabRequest.objects.filter(lab_attendant=request.user).prefetch_related(
        'tests__test'
    ).select_related('patient', 'visit', 'doctor')
    return render(request, 'lab_history.html', {'requests': requests})


@login_required
def accountant_history(request):
    if request.user.role != 'accountant':
        return redirect('dashboard')
    from accounting.models import Payment
    payments = Payment.objects.filter(accountant=request.user, is_paid=True).select_related(
        'patient', 'visit'
    ).order_by('-paid_at')
    return render(request, 'accountant_history.html', {'payments': payments})


@login_required
def ward_dashboard(request):
    """Ward dashboard for nurses and doctors showing all admitted patients."""
    if request.user.role not in ['nurse', 'doctor']:
        return redirect('dashboard')
    from records.models import WardAdmission, AdmissionPrescription, AdmissionPrescriptionItem, WARD_CHOICES

    admissions = WardAdmission.objects.filter(
        status__in=['paid', 'admitted']
    ).select_related('patient', 'doctor', 'nurse', 'visit').prefetch_related(
        'prescriptions__items__drug',
        'visit__lab_requests__tests__test',
        'visit__surgeries__surgery_drugs__drug',
        'visit__surgeries__surgery_labs__test',
        'visit__surgeries__payments',
        'payments',
    ).order_by('ward', 'bed_number')

    available_lab_attendants = User.objects.filter(role='lab_attendant', is_approved=True, is_available=True)
    available_pharmacists = User.objects.filter(role='pharmacist', is_approved=True, is_available=True)

    ctx = {
        'nurse': request.user,
        'user': request.user,
        'admissions': admissions,
        'ward_choices': WARD_CHOICES,
        'available_lab_attendants': available_lab_attendants,
        'available_pharmacists': available_pharmacists,
    }
    return render(request, 'ward_dashboard.html', ctx)


@login_required
def admit_ward_patient(request, admission_id):
    """Nurse confirms patient is physically in the ward."""
    if request.method == 'POST' and request.user.role == 'nurse':
        from records.models import WardAdmission
        admission = get_object_or_404(WardAdmission, pk=admission_id, status='paid')
        admission.status = 'admitted'
        from django.utils import timezone
        admission.admitted_at = timezone.now()
        admission.nurse = request.user
        admission.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def discharge_patient(request, admission_id):
    """Nurse or doctor discharges a patient — blocked if any payments outstanding."""
    if request.method == 'POST' and request.user.role in ['nurse', 'doctor']:
        from records.models import WardAdmission
        from accounting.models import Payment
        admission = get_object_or_404(WardAdmission, pk=admission_id, status='admitted')
        # Block discharge if any payments on this visit are still outstanding
        outstanding = Payment.objects.filter(
            visit=admission.visit, is_paid=False
        ).count()
        if outstanding:
            return JsonResponse({'error': f'Cannot discharge: {outstanding} payment(s) still outstanding (including surgery). All payments must be cleared before discharge.'}, status=400)
        admission.status = 'discharged'
        from django.utils import timezone
        admission.discharged_at = timezone.now()
        admission.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def add_admission_prescription(request, admission_id):
    """Doctor adds or updates medication for admitted patient."""
    if request.method == 'POST' and request.user.role == 'doctor':
        from records.models import WardAdmission, AdmissionPrescription, AdmissionPrescriptionItem
        from pharmacy.models import Drug
        admission = get_object_or_404(WardAdmission, pk=admission_id, status__in=['paid', 'admitted'])
        d = request.POST
        drug_ids = d.getlist('drug_ids[]')
        dosages = d.getlist('dosages[]')
        quantities = d.getlist('quantities[]')
        if not drug_ids:
            return JsonResponse({'error': 'No drugs selected'}, status=400)
        from django.db import transaction
        with transaction.atomic():
            rx = AdmissionPrescription.objects.create(
                admission=admission, doctor=request.user,
                notes=d.get('notes', ''), status='active',
            )
            total = 0
            for drug_id, dosage, qty in zip(drug_ids, dosages, quantities):
                try:
                    drug = Drug.objects.get(pk=drug_id)
                    qty_int = int(qty) if qty else 1
                    AdmissionPrescriptionItem.objects.create(
                        prescription=rx, drug=drug,
                        drug_name=drug.name, dosage=dosage, quantity=qty_int,
                        price=drug.price * qty_int,
                    )
                    total += drug.price * qty_int
                except Drug.DoesNotExist:
                    pass
            # Send to accountant
            from accounting.models import Payment
            if total > 0:
                Payment.objects.create(
                    visit=admission.visit, patient=admission.patient,
                    accountant=admission.accountant,
                    payment_type='admission_medication',
                    amount=total, admission=admission,
                )
        return JsonResponse({'status': 'ok', 'rx_id': rx.pk})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def void_admission_prescription(request, rx_id):
    """Doctor voids an admission prescription."""
    if request.method == 'POST' and request.user.role == 'doctor':
        from records.models import AdmissionPrescription
        from django.utils import timezone
        rx = get_object_or_404(AdmissionPrescription, pk=rx_id, status='active')
        rx.status = 'voided'
        rx.voided_at = timezone.now()
        rx.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def download_visit_summary(request, visit_id):
    """Renders a printable HTML page for patient visit summary."""
    if request.user.role != 'patient':
        return redirect('dashboard')
    from records.models import PatientVisit
    visit = get_object_or_404(
        PatientVisit.objects.prefetch_related(
            'vitals', 'doctor_notes', 'prescriptions__drugs__drug',
            'lab_requests__tests__test', 'payments',
            'admissions', 'surgeries',
        ).select_related('doctor', 'nurse', 'accountant'),
        pk=visit_id, patient=request.user
    )
    return render(request, 'visit_summary_print.html', {'visit': visit, 'patient': request.user})


@login_required
def doctor_view_patient(request, patient_id):
    """Doctor views a patient's full profile and medical history."""
    if request.user.role != 'doctor':
        return JsonResponse({'error': 'forbidden'}, status=403)
    from records.models import PatientVisit
    patient = get_object_or_404(User, pk=patient_id, role='patient')
    visits = PatientVisit.objects.filter(patient=patient).prefetch_related(
        'vitals', 'prescriptions__drugs__drug', 'lab_requests__tests__test',
        'doctor_notes',
    ).select_related('doctor').order_by('-created_at')[:20]
    data = {
        'id': patient.pk,
        'name': patient.display_name,
        'username': patient.username,
        'gender': patient.gender or '',
        'dob': str(patient.date_of_birth) if patient.date_of_birth else '',
        'phone': patient.phone or '',
        'blood_group': patient.blood_group or '',
        'genotype': patient.genotype or '',
        'allergies': patient.allergies or '',
        'medical_history': patient.medical_history or '',
        'current_medications': patient.current_medications or '',
        'family_history': patient.family_history or '',
        'surgical_history': patient.surgical_history or '',
        'emergency_contact': patient.emergency_contact_name or '',
        'emergency_phone': patient.emergency_contact_phone or '',
        'emergency_rel': patient.emergency_contact_relationship or '',
    }
    return JsonResponse({'status': 'ok', 'patient': data})
