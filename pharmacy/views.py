from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from .models import Drug, Prescription, PrescriptionDrug
from management.models import User


@login_required
def pharmacist_dashboard(request):
    if request.user.role != 'pharmacist':
        return redirect('dashboard')
    pharmacist = request.user

    # Assigned to me, paid, not dispensed
    my_pending = Prescription.objects.filter(
        pharmacist=pharmacist, status='paid'
    ).prefetch_related('drugs__drug').select_related('patient', 'visit', 'doctor')

    # Unassigned paid (any pharmacist can take)
    unassigned = Prescription.objects.filter(
        pharmacist__isnull=True, status='paid'
    ).prefetch_related('drugs__drug').select_related('patient', 'visit')

    # Dispensed (not soft-deleted)
    dispensed = Prescription.objects.filter(
        pharmacist=pharmacist, status='dispensed', pharmacist_deleted=False
    ).prefetch_related('drugs__drug').select_related('patient').order_by('-dispensed_at')[:50]

    drugs = Drug.objects.filter(is_active=True)

    ctx = {
        'my_pending': my_pending,
        'unassigned': unassigned,
        'dispensed': dispensed,
        'drugs': drugs,
        'pharmacist': pharmacist,
    }
    return render(request, 'pharmacist.html', ctx)


@login_required
def dispense_prescription(request, rx_id):
    if request.method == 'POST' and request.user.role == 'pharmacist':
        rx = get_object_or_404(Prescription, pk=rx_id)
        with transaction.atomic():
            rx.status = 'dispensed'
            rx.pharmacist = request.user
            rx.dispensed_at = timezone.now()
            rx.pharmacist_note = request.POST.get('note', '')
            rx.save()
            # Update visit status back to with_doctor so doctor can end session
            visit = rx.visit
            visit.status = 'with_doctor'
            visit.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def reject_prescription(request, rx_id):
    if request.method == 'POST' and request.user.role == 'pharmacist':
        rx = get_object_or_404(Prescription, pk=rx_id)
        rx.status = 'rejected'
        rx.pharmacist = request.user
        rx.pharmacist_note = request.POST.get('note', '')
        rx.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def delete_dispensed(request, rx_id):
    if request.method == 'POST' and request.user.role == 'pharmacist':
        rx = get_object_or_404(Prescription, pk=rx_id, pharmacist=request.user, status='dispensed')
        rx.pharmacist_deleted = True
        rx.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def print_prescription(request, rx_id):
    rx = get_object_or_404(Prescription, pk=rx_id)
    if request.user not in [rx.patient, rx.pharmacist, rx.doctor] and request.user.role not in ['accountant']:
        if not request.user.is_staff:
            return redirect('dashboard')
    return render(request, 'prescription_print.html', {'rx': rx})


@login_required
def drug_search(request):
    q = request.GET.get('q', '').strip()
    drugs = Drug.objects.filter(is_active=True, name__icontains=q)[:15]
    results = [{'id': d.pk, 'name': str(d), 'price': str(d.price)} for d in drugs]
    return JsonResponse({'results': results})


@login_required
def take_prescription(request, rx_id):
    """Pharmacist claims an unassigned prescription."""
    if request.method == 'POST' and request.user.role == 'pharmacist':
        rx = get_object_or_404(Prescription, pk=rx_id, pharmacist__isnull=True, status='paid')
        rx.pharmacist = request.user
        rx.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def add_drug(request):
    """Pharmacist adds a new drug to the database."""
    if request.method == 'POST' and request.user.role == 'pharmacist':
        from django.db import transaction
        d = request.POST
        name = d.get('name', '').strip()
        if not name:
            return JsonResponse({'error': 'Drug name is required'}, status=400)
        try:
            price = float(d.get('price', 0))
        except:
            price = 0
        drug = Drug.objects.create(
            name=name,
            dosage_form=d.get('dosage_form', ''),
            strength=d.get('strength', ''),
            price=price,
            is_active=True,
            is_injection=d.get('is_injection') == '1',
        )
        return JsonResponse({'status': 'ok', 'id': drug.pk, 'name': str(drug)})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def delete_drug(request, drug_id):
    """Pharmacist soft-deletes (deactivates) a drug."""
    if request.method == 'POST' and request.user.role == 'pharmacist':
        drug = get_object_or_404(Drug, pk=drug_id)
        drug.is_active = False
        drug.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def edit_drug(request, drug_id):
    """Pharmacist edits a drug."""
    if request.method == 'POST' and request.user.role == 'pharmacist':
        drug = get_object_or_404(Drug, pk=drug_id)
        d = request.POST
        drug.name = d.get('name', drug.name).strip() or drug.name
        drug.dosage_form = d.get('dosage_form', drug.dosage_form)
        drug.strength = d.get('strength', drug.strength)
        drug.is_injection = d.get('is_injection') == '1'
        try:
            drug.price = float(d.get('price', drug.price))
        except:
            pass
        drug.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)
