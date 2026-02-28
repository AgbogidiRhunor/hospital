from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from .models import Payment
from management.models import User


@login_required
def accountant_dashboard(request):
    if request.user.role != 'accountant':
        return redirect('dashboard')
    pending = Payment.objects.filter(
        accountant=request.user, is_paid=False
    ).select_related('patient', 'visit', 'lab_request', 'prescription').order_by('-created_at')
    processed = Payment.objects.filter(
        accountant=request.user, is_paid=True, accountant_dashboard_deleted=False
    ).select_related('patient', 'visit').order_by('-paid_at')[:50]
    ctx = {'pending': pending, 'processed': processed, 'accountant': request.user}
    return render(request, 'accountant.html', ctx)


@login_required
def confirm_payment(request, payment_id):
    if request.method == 'POST' and request.user.role == 'accountant':
        payment = get_object_or_404(Payment, pk=payment_id, accountant=request.user)
        with transaction.atomic():
            payment.is_paid = True
            payment.paid_at = timezone.now()
            payment.save()
            visit = payment.visit

            if payment.payment_type == 'consultation':
                visit.consultation_paid_at = timezone.now()
                visit.status = 'paid'
                # Assign queue number based on doctor's current queue
                from records.models import PatientVisit
                from django.db.models import Max
                max_q = PatientVisit.objects.filter(
                    doctor=visit.doctor, queue_number__isnull=False
                ).aggregate(Max('queue_number'))['queue_number__max'] or 0
                visit.queue_number = max_q + 1
                visit.save()

            elif payment.payment_type == 'lab':
                lr = payment.lab_request
                if lr:
                    lr.status = 'paid'
                    lr.paid_at = timezone.now()
                    lr.save()
                visit.status = 'lab_processing'
                visit.save()

            elif payment.payment_type == 'surgery':
                if payment.surgery:
                    payment.surgery.status = 'paid'
                    payment.surgery.save()
                    # If surgery has a linked admission, mark it paid too
                    if payment.surgery.admission:
                        adm = payment.surgery.admission
                        if adm.status == 'pending_payment':
                            adm.status = 'paid'
                            adm.save()
                    # Also mark linked post-surgery admission as paid
                    if payment.surgery.admission:
                        adm = payment.surgery.admission
                        if adm.status == 'pending_payment':
                            adm.status = 'paid'
                            adm.save()
            elif payment.payment_type in ('admission', 'admission_medication'):
                from records.models import WardAdmission
                # Use FK if available, else fallback
                if payment.admission:
                    admit = payment.admission
                else:
                    admit = WardAdmission.objects.filter(visit=payment.visit, status='pending_payment').first()
                if admit and payment.payment_type == 'admission':
                    admit.status = 'paid'
                    admit.save()
            elif payment.payment_type == 'prescription':
                rx = payment.prescription
                if rx:
                    rx.status = 'paid'
                    rx.paid_at = timezone.now()
                    rx.save()
                visit.status = 'pharmacy'
                visit.save()

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def delete_processed(request, payment_id):
    if request.method == 'POST' and request.user.role == 'accountant':
        pay = get_object_or_404(Payment, pk=payment_id, accountant=request.user, is_paid=True)
        pay.accountant_dashboard_deleted = True
        pay.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def print_receipt(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    if request.user.role not in ['accountant'] and request.user != payment.patient:
        if not request.user.is_staff:
            return redirect('dashboard')
    return render(request, 'receipt_print.html', {'payment': payment})
