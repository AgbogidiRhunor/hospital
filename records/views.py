from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from .models import PatientVisit, VitalSigns, DoctorNote
from pharmacy.models import Prescription, PrescriptionDrug, Drug
from lab.models import LabRequest, LabRequestTest, LabTest
from accounting.models import Payment
from management.models import User


@login_required
def add_doctor_note(request, visit_id):
    if request.method == 'POST' and request.user.role == 'doctor':
        visit = get_object_or_404(PatientVisit, pk=visit_id, doctor=request.user)
        note = request.POST.get('note', '').strip()
        if note:
            DoctorNote.objects.create(visit=visit, doctor=request.user, note=note)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def prescribe(request, visit_id):
    """Doctor submits prescription → creates Prescription + sends to accountant for payment."""
    if request.method == 'POST' and request.user.role == 'doctor':
        visit = get_object_or_404(PatientVisit, pk=visit_id, doctor=request.user)
        d = request.POST

        pharmacist_id = d.get('pharmacist_id')
        pharmacist = None
        if pharmacist_id:
            pharmacist = User.objects.filter(pk=pharmacist_id, role='pharmacist').first()

        accountant_id = d.get('accountant_id')
        accountant = None
        if accountant_id:
            accountant = User.objects.filter(pk=accountant_id, role='accountant').first()
        if not accountant:
            accountant = visit.accountant  # fall back to visit's accountant

        drug_ids = d.getlist('drug_ids[]')
        dosages = d.getlist('dosages[]')
        quantities = d.getlist('quantities[]')

        if not drug_ids:
            return JsonResponse({'error': 'No drugs selected'}, status=400)

        with transaction.atomic():
            rx = Prescription.objects.create(
                visit=visit,
                patient=visit.patient,
                doctor=request.user,
                pharmacist=pharmacist,
                accountant=accountant,
                doctor_note=d.get('note', ''),
                status='pending_payment',
            )
            total = 0
            for drug_id, dosage, qty in zip(drug_ids, dosages, quantities):
                try:
                    drug = Drug.objects.get(pk=drug_id)
                    qty = int(qty) if qty else 1
                    price = drug.price * qty
                    inj_days = request.POST.getlist('injection_days[]')
                    inj_times = request.POST.getlist('injection_times[]')
                    inj_d = int(inj_days[list(drug_ids).index(drug_id)]) if inj_days and list(drug_ids).index(drug_id) < len(inj_days) and inj_days[list(drug_ids).index(drug_id)] else None
                    inj_t = int(inj_times[list(drug_ids).index(drug_id)]) if inj_times and list(drug_ids).index(drug_id) < len(inj_times) and inj_times[list(drug_ids).index(drug_id)] else None
                    PrescriptionDrug.objects.create(
                        prescription=rx, drug=drug,
                        dosage=dosage, quantity=qty,
                        price_at_time=drug.price,
                        injection_days=inj_d,
                        injection_times_per_day=inj_t,
                    )
                    total += price
                except Drug.DoesNotExist:
                    pass
            rx.total_price = total
            rx.save()

            # Create payment for accountant
            Payment.objects.create(
                visit=visit,
                patient=visit.patient,
                accountant=accountant,
                payment_type='prescription',
                amount=total,
                prescription=rx,
            )
            visit.status = 'rx_pending'
            visit.save()

        return JsonResponse({'status': 'ok', 'rx_id': rx.pk})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def order_lab(request, visit_id):
    """Doctor orders lab tests → sends to accountant first."""
    if request.method == 'POST' and request.user.role == 'doctor':
        visit = get_object_or_404(PatientVisit, pk=visit_id, doctor=request.user)
        d = request.POST

        lab_attendant_id = d.get('lab_attendant_id')
        lab_attendant = None
        if lab_attendant_id:
            lab_attendant = User.objects.filter(pk=lab_attendant_id, role='lab_attendant').first()

        accountant_id = d.get('accountant_id')
        accountant = None
        if accountant_id:
            accountant = User.objects.filter(pk=accountant_id, role='accountant').first()
        if not accountant:
            accountant = visit.accountant

        test_ids = d.getlist('test_ids[]')
        test_notes = d.getlist('test_notes[]')

        if not test_ids:
            return JsonResponse({'error': 'No tests selected'}, status=400)

        with transaction.atomic():
            lr = LabRequest.objects.create(
                visit=visit,
                patient=visit.patient,
                doctor=request.user,
                lab_attendant=lab_attendant,
                accountant=accountant,
                doctor_note=d.get('note', ''),
                status='pending_payment',
            )
            total = 0
            for test_id, note in zip(test_ids, test_notes):
                try:
                    test = LabTest.objects.get(pk=test_id)
                    LabRequestTest.objects.create(
                        request=lr, test=test,
                        doctor_note=note,
                        price_at_time=test.price,
                    )
                    total += test.price
                except LabTest.DoesNotExist:
                    pass
            lr.total_price = total
            lr.save()

            Payment.objects.create(
                visit=visit,
                patient=visit.patient,
                accountant=accountant,
                payment_type='lab',
                amount=total,
                lab_request=lr,
            )
            visit.status = 'lab_pending'
            visit.save()

        return JsonResponse({'status': 'ok', 'lr_id': lr.pk})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def admit_patient(request, visit_id):
    """Doctor submits admission form."""
    if request.method == 'POST' and request.user.role == 'doctor':
        from records.models import WardAdmission, WARD_CAPACITY
        visit = get_object_or_404(PatientVisit, pk=visit_id, doctor=request.user)
        d = request.POST
        ward = d.get('ward')
        bed_number = int(d.get('bed_number', 1))
        daily_fee = float(d.get('daily_ward_fee', 0))
        total_fee = float(d.get('total_admission_fee', 0))

        # Check bed availability
        occupied = WardAdmission.objects.filter(ward=ward, bed_number=bed_number, status__in=['paid','admitted']).count()
        if occupied:
            return JsonResponse({'error': f'Bed {bed_number} in {ward} is already occupied'}, status=400)

        drug_ids = d.getlist('drug_ids[]')
        dosages = d.getlist('dosages[]')
        quantities = d.getlist('quantities[]')

        with transaction.atomic():
            admission = WardAdmission.objects.create(
                visit=visit, patient=visit.patient, doctor=request.user,
                nurse=visit.nurse, accountant=visit.accountant,
                ward=ward, bed_number=bed_number,
                admission_reason=d.get('admission_reason', ''),
                daily_ward_fee=daily_fee, total_admission_fee=total_fee,
                status='pending_payment',
            )
            Payment.objects.create(
                visit=visit, patient=visit.patient, accountant=visit.accountant,
                payment_type='admission', amount=total_fee,
                admission=admission,
            )
            # Create initial admission prescription if drugs provided
            if drug_ids:
                from records.models import AdmissionPrescription, AdmissionPrescriptionItem
                rx = AdmissionPrescription.objects.create(
                    admission=admission, doctor=request.user,
                    notes='Initial admission medication', status='active',
                )
                med_total = 0
                for drug_id, dosage, qty in zip(drug_ids, dosages, quantities):
                    try:
                        drug = Drug.objects.get(pk=drug_id)
                        qty_int = int(qty) if qty else 1
                        item_price = drug.price * qty_int
                        AdmissionPrescriptionItem.objects.create(
                            prescription=rx, drug=drug,
                            drug_name=drug.name, dosage=dosage, quantity=qty_int,
                            price=item_price,
                        )
                        med_total += item_price
                    except Drug.DoesNotExist:
                        pass
                if med_total > 0:
                    Payment.objects.create(
                        visit=visit, patient=visit.patient, accountant=visit.accountant,
                        payment_type='admission_medication', amount=med_total,
                        admission=admission,
                    )
        return JsonResponse({'status': 'ok', 'admission_id': admission.pk})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def create_surgery(request, visit_id):
    """Doctor submits surgery consent form."""
    if request.method == 'POST' and request.user.role == 'doctor':
        from records.models import Surgery, WardAdmission, WARD_CAPACITY
        visit = get_object_or_404(PatientVisit, pk=visit_id, doctor=request.user)
        d = request.POST

        with transaction.atomic():
            surgery = Surgery.objects.create(
                visit=visit, patient=visit.patient, doctor=request.user,
                procedure_name=d.get('procedure_name', ''),
                purpose_and_benefits=d.get('purpose_and_benefits', ''),
                known_risks=d.get('known_risks', ''),
                alternative_treatments=d.get('alternative_treatments', ''),
                anesthesia_type=d.get('anesthesia_type', ''),
                additional_procedures_auth=d.get('additional_procedures_auth') == '1',
                tissue_disposal_auth=d.get('tissue_disposal_auth') == '1',
                residents_involved=d.get('residents_involved') == '1',
                observers_permitted=d.get('observers_permitted') == '1',
                photography_permitted=d.get('photography_permitted') == '1',
                blood_transfusion_consent=d.get('blood_transfusion_consent', 'na'),
                financial_disclosure=d.get('financial_disclosure', ''),
                advance_directives=d.get('advance_directives', ''),
                postop_instructions=d.get('postop_instructions', ''),
                patient_acknowledged=d.get('patient_acknowledged') == '1',
                witness_name=d.get('witness_name', ''),
                surgery_fee=float(d.get('surgery_fee', 0) or 0),
                admit_after_surgery=d.get('admit_after_surgery') == '1',
                status='draft',
            )
            # If post-op admission is required
            if surgery.admit_after_surgery and d.get('ward'):
                ward = d.get('ward')
                bed_number = int(d.get('bed_number', 1))
                daily_fee = float(d.get('daily_ward_fee', 0))
                total_fee = float(d.get('total_admission_fee', 0))
                admission = WardAdmission.objects.create(
                    visit=visit, patient=visit.patient, doctor=request.user,
                    ward=ward, bed_number=bed_number,
                    admission_reason=f'Post-surgery: {surgery.procedure_name}',
                    daily_ward_fee=daily_fee, total_admission_fee=total_fee,
                    status='pending_payment',
                )
                surgery.admission = admission
                surgery.save()
                if total_fee:
                    Payment.objects.create(
                        visit=visit, patient=visit.patient, accountant=visit.accountant,
                        payment_type='admission', amount=total_fee,
                    )
        return JsonResponse({'status': 'ok', 'surgery_id': surgery.pk})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def ward_occupancy(request):
    """Returns current bed occupancy per ward."""
    from records.models import WardAdmission, WARD_CHOICES, WARD_CAPACITY
    result = {}
    for ward_key, ward_label in WARD_CHOICES:
        capacity = WARD_CAPACITY[ward_key]
        occupied_beds = list(WardAdmission.objects.filter(
            ward=ward_key, status__in=['paid', 'admitted']
        ).values_list('bed_number', flat=True))
        result[ward_key] = {
            'label': ward_label,
            'capacity': capacity,
            'occupied': occupied_beds,
            'available': [b for b in range(1, capacity + 1) if b not in occupied_beds],
        }
    return JsonResponse(result)


@login_required
def print_lab_results(request, lr_id):
    from lab.models import LabRequest
    lr = get_object_or_404(LabRequest, pk=lr_id)
    # Allow patient, doctor, lab attendant
    if request.user not in [lr.patient, lr.doctor, lr.lab_attendant] and not request.user.is_staff:
        if request.user.role not in ['lab_attendant', 'doctor']:
            return redirect('dashboard')
    return render(request, 'lab_results_print.html', {'lr': lr})


@login_required
def patient_review_surgery(request, surgery_id):
    """Patient reviews and signs the surgery consent form."""
    from records.models import Surgery
    if request.method == 'POST' and request.user.role == 'patient':
        surgery = get_object_or_404(Surgery, pk=surgery_id, patient=request.user, status='draft')
        d = request.POST
        surgery.patient_full_name_signed = d.get('patient_full_name_signed', '').strip()
        surgery.patient_questions = d.get('patient_questions', '')
        surgery.patient_understanding = d.get('patient_understanding') == '1'
        surgery.patient_voluntary = d.get('patient_voluntary') == '1'
        surgery.patient_acknowledged = d.get('patient_acknowledged') == '1'
        surgery.patient_signed_at = timezone.now()
        surgery.status = 'patient_reviewed'
        surgery.save()
        # Create payment to accountant
        if surgery.surgery_fee > 0:
            Payment.objects.create(
                visit=surgery.visit, patient=surgery.patient,
                accountant=surgery.visit.accountant,
                payment_type='surgery', amount=surgery.surgery_fee,
                surgery=surgery,
            )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def drug_search(request):
    """Search drugs for doctor prescription modal."""
    from pharmacy.models import Drug
    q = request.GET.get('q', '').strip()
    if not q:
        drugs = Drug.objects.filter(is_active=True)[:30]
    else:
        from django.db.models import Q
        drugs = Drug.objects.filter(is_active=True).filter(
            Q(name__icontains=q) | Q(strength__icontains=q) | Q(dosage_form__icontains=q)
        )[:30]
    results = [{
        'id': d.pk, 'name': d.name, 'strength': d.strength,
        'form': d.dosage_form, 'price': float(d.price),
        'is_injection': getattr(d, 'is_injection', False),
    } for d in drugs]
    return JsonResponse({'results': results})


@login_required
def lab_test_search(request):
    """Search lab tests for doctor lab order modal."""
    q = request.GET.get('q', '').strip()
    if not q:
        tests = LabTest.objects.all()[:30]
    else:
        from django.db.models import Q
        tests = LabTest.objects.filter(
            Q(name__icontains=q) | Q(category__icontains=q)
        )[:30]
    results = [{'id': t.pk, 'name': t.name, 'category': t.category, 'price': float(t.price)} for t in tests]
    return JsonResponse({'results': results})
