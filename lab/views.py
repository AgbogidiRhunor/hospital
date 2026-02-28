from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import LabRequest, LabRequestTest, LabTest


@login_required
def lab_dashboard(request):
    if request.user.role != 'lab_attendant':
        return redirect('dashboard')
    lab = request.user

    my_requests = LabRequest.objects.filter(
        lab_attendant=lab, status__in=['paid', 'in_progress']
    ).prefetch_related('tests__test').select_related('patient', 'visit', 'doctor')

    unassigned = LabRequest.objects.filter(
        lab_attendant__isnull=True, status='paid'
    ).prefetch_related('tests__test').select_related('patient')

    completed = LabRequest.objects.filter(
        lab_attendant=lab, status='completed', lab_attendant_deleted=False
    ).prefetch_related('tests__test').select_related('patient').order_by('-completed_at')[:50]

    ctx = {'my_requests': my_requests, 'unassigned': unassigned, 'completed': completed, 'lab': lab}
    return render(request, 'lab_dashboard.html', ctx)


@login_required
def submit_test_result(request, test_id):
    if request.method == 'POST' and request.user.role == 'lab_attendant':
        lt = get_object_or_404(LabRequestTest, pk=test_id, request__lab_attendant=request.user)
        lt.result_note = request.POST.get('result_note', '')
        lt.is_completed = True
        lt.save()
        # Check if all tests done
        lr = lt.request
        if lr.tests.filter(is_completed=False).count() == 0:
            lr.status = 'completed'
            lr.completed_at = timezone.now()
            lr.save()
            visit = lr.visit
            visit.status = 'with_doctor'
            visit.save()
        return JsonResponse({'status': 'ok', 'all_done': lr.status == 'completed'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def take_request(request, lr_id):
    """Lab attendant claims an unassigned request."""
    if request.method == 'POST' and request.user.role == 'lab_attendant':
        lr = get_object_or_404(LabRequest, pk=lr_id, lab_attendant__isnull=True)
        lr.lab_attendant = request.user
        lr.status = 'in_progress'
        lr.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def delete_completed(request, lr_id):
    if request.method == 'POST' and request.user.role == 'lab_attendant':
        lr = get_object_or_404(LabRequest, pk=lr_id, lab_attendant=request.user, status='completed')
        lr.lab_attendant_deleted = True
        lr.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'forbidden'}, status=403)


@login_required
def lab_tests_api(request):
    q = request.GET.get('q', '').strip()
    tests = LabTest.objects.filter(is_active=True, name__icontains=q)[:20]
    results = [{'id': t.pk, 'name': t.name, 'category': t.category, 'price': str(t.price)} for t in tests]
    return JsonResponse({'results': results})


@login_required
def submit_test_result_single(request, test_id):
    """Submit result for a single lab test."""
    if request.method == 'POST' and request.user.role == 'lab_attendant':
        from lab.models import LabRequestTest, LabRequest
        from django.utils import timezone
        t = get_object_or_404(LabRequestTest, pk=test_id, request__lab_attendant=request.user)
        t.result_note = request.POST.get('result_note', '').strip()
        t.is_completed = True
        t.save()
        # Check if all tests in this request are done
        lr = t.request
        if all(x.is_completed for x in lr.tests.all()):
            lr.status = 'completed'
            lr.completed_at = timezone.now()
            lr.save()
            # Set visit back to with_doctor
            visit = lr.visit
            if visit.status == 'lab_processing':
                visit.status = 'with_doctor'
                visit.save()
        return JsonResponse({'status': 'ok', 'all_done': lr.status == 'completed'})
    return JsonResponse({'error': 'forbidden'}, status=403)
