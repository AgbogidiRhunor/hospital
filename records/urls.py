from django.urls import path
from . import views

urlpatterns = [
    path('api/note/<int:visit_id>/', views.add_doctor_note, name='add_doctor_note'),
    path('api/prescribe/<int:visit_id>/', views.prescribe, name='prescribe'),
    path('api/order-lab/<int:visit_id>/', views.order_lab, name='order_lab'),
    path('api/admit/<int:visit_id>/', views.admit_patient, name='admit_patient'),
    path('api/surgery/<int:visit_id>/', views.create_surgery, name='create_surgery'),
    path('api/surgery-review/<int:surgery_id>/', views.patient_review_surgery, name='patient_review_surgery'),
    path('api/ward-occupancy/', views.ward_occupancy, name='ward_occupancy'),
    path('api/drug-search/', views.drug_search, name='drug_search'),
    path('api/lab-test-search/', views.lab_test_search, name='lab_test_search'),
    path('print/lab-results/<int:lr_id>/', views.print_lab_results, name='print_lab_results'),
]
