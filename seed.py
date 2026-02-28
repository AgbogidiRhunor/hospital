#!/usr/bin/env python
"""
Run after migrations: python seed.py
Seeds consulting rooms, lab tests, and drugs.
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from management.models import ConsultingRoom
from lab.models import LabTest
from pharmacy.models import Drug

# Consulting Rooms
print("Creating consulting rooms...")
for i in range(1, 8):
    ConsultingRoom.objects.get_or_create(number=i, defaults={'name': f'Consulting Room {i}'})
print(f"  Created 7 consulting rooms")

# Lab Tests
print("Creating lab tests...")
LAB_TESTS = [
    ('Full Blood Count', 'Haematology', 3500),
    ('Erythrocyte Sedimentation Rate (ESR)', 'Haematology', 2500),
    ('Blood Group & Genotype', 'Haematology', 2000),
    ('Malaria Parasite (MP)', 'Parasitology', 2000),
    ('Widal Test', 'Serology', 2500),
    ('Hepatitis B Surface Antigen', 'Serology', 3000),
    ('HIV Screening', 'Serology', 3000),
    ('Fasting Blood Sugar', 'Biochemistry', 2000),
    ('Random Blood Sugar', 'Biochemistry', 1500),
    ('HbA1c', 'Biochemistry', 5000),
    ('Urea, Electrolytes & Creatinine', 'Biochemistry', 5000),
    ('Liver Function Test', 'Biochemistry', 5500),
    ('Lipid Profile', 'Biochemistry', 6000),
    ('Thyroid Function Test', 'Endocrinology', 8000),
    ('Urinalysis (Routine)', 'Microbiology', 1500),
    ('Urine Culture & Sensitivity', 'Microbiology', 4500),
    ('Stool Analysis', 'Microbiology', 2000),
    ('Pregnancy Test', 'Serology', 1500),
    ('Prostate Specific Antigen (PSA)', 'Oncology', 7000),
    ('Chest X-Ray', 'Radiology', 8000),
    ('Abdominal Ultrasound', 'Radiology', 12000),
    ('ECG', 'Cardiology', 5000),
    ('APTT / PT / INR', 'Haematology', 4000),
    ('Rheumatoid Factor', 'Serology', 3500),
    ('Sputum AFB', 'Microbiology', 3000),
]
for name, category, price in LAB_TESTS:
    LabTest.objects.get_or_create(name=name, defaults={'category': category, 'price': price})
print(f"  Created {len(LAB_TESTS)} lab tests")

# Drugs
print("Creating drugs...")
DRUGS = [
    ('Paracetamol', 'Tablet', '500mg', 50),
    ('Ibuprofen', 'Tablet', '400mg', 80),
    ('Amoxicillin', 'Capsule', '500mg', 150),
    ('Amoxicillin-Clavulanate', 'Tablet', '625mg', 350),
    ('Ciprofloxacin', 'Tablet', '500mg', 200),
    ('Metronidazole', 'Tablet', '400mg', 100),
    ('Azithromycin', 'Tablet', '500mg', 250),
    ('Doxycycline', 'Capsule', '100mg', 120),
    ('Ceftriaxone', 'Injection', '1g', 800),
    ('Artemether-Lumefantrine', 'Tablet', '20/120mg', 1200),
    ('Coartem', 'Tablet', '80/480mg', 2500),
    ('Amlodipine', 'Tablet', '5mg', 100),
    ('Lisinopril', 'Tablet', '10mg', 120),
    ('Atenolol', 'Tablet', '50mg', 80),
    ('Hydrochlorothiazide', 'Tablet', '25mg', 60),
    ('Metformin', 'Tablet', '500mg', 80),
    ('Glibenclamide', 'Tablet', '5mg', 60),
    ('Insulin Glargine', 'Injection', '100IU/ml', 5000),
    ('Omeprazole', 'Capsule', '20mg', 100),
    ('Ranitidine', 'Tablet', '150mg', 80),
    ('Metoclopramide', 'Tablet', '10mg', 60),
    ('Oral Rehydration Salts', 'Sachet', '1 sachet', 50),
    ('Diazepam', 'Tablet', '5mg', 80),
    ('Loratadine', 'Tablet', '10mg', 80),
    ('Prednisolone', 'Tablet', '5mg', 60),
    ('Dexamethasone', 'Injection', '8mg/2ml', 300),
    ('Tramadol', 'Capsule', '50mg', 150),
    ('Morphine', 'Injection', '10mg/ml', 500),
    ('Ferrous Sulphate', 'Tablet', '200mg', 50),
    ('Folic Acid', 'Tablet', '5mg', 30),
    ('Vitamin C', 'Tablet', '500mg', 50),
    ('Zinc Sulphate', 'Tablet', '20mg', 60),
    ('Salbutamol', 'Inhaler', '100mcg', 1500),
    ('Fluticasone', 'Inhaler', '250mcg', 3500),
    ('Atorvastatin', 'Tablet', '20mg', 150),
    ('Aspirin (low dose)', 'Tablet', '75mg', 50),
    ('Warfarin', 'Tablet', '5mg', 100),
    ('Phenytoin', 'Capsule', '100mg', 100),
    ('Carbamazepine', 'Tablet', '200mg', 100),
    ('Haloperidol', 'Tablet', '5mg', 100),
]
for name, form, strength, price in DRUGS:
    Drug.objects.get_or_create(name=name, defaults={'dosage_form': form, 'strength': strength, 'price': price})
print(f"  Created {len(DRUGS)} drugs")

print("\n✅ Seed complete!")
print("\nNext steps:")
print("  python manage.py createsuperuser")
print("  python manage.py runserver")
