#!/bin/bash
echo "=== Health Plus Setup ==="
echo ""
echo "1. Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "2. Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "3. Creating superuser (admin)..."
echo "   You'll need an admin to approve Doctor/Pharmacist accounts."
python manage.py createsuperuser

echo ""
echo "4. (Optional) Load sample drugs..."
python manage.py shell -c "
from pharmacy.models import Drug
drugs = [
    {'name': 'Paracetamol', 'strength': '500mg', 'dosage_form': 'Tablet', 'manufacturer': 'GSK'},
    {'name': 'Amoxicillin', 'strength': '250mg', 'dosage_form': 'Capsule', 'manufacturer': 'Pfizer'},
    {'name': 'Ibuprofen', 'strength': '400mg', 'dosage_form': 'Tablet', 'manufacturer': 'Reckitt'},
    {'name': 'Metformin', 'strength': '500mg', 'dosage_form': 'Tablet', 'manufacturer': 'Accord'},
    {'name': 'Lisinopril', 'strength': '10mg', 'dosage_form': 'Tablet', 'manufacturer': 'Lupin'},
    {'name': 'Atorvastatin', 'strength': '20mg', 'dosage_form': 'Tablet', 'manufacturer': 'Teva'},
    {'name': 'Omeprazole', 'strength': '20mg', 'dosage_form': 'Capsule', 'manufacturer': 'AstraZeneca'},
    {'name': 'Azithromycin', 'strength': '500mg', 'dosage_form': 'Tablet', 'manufacturer': 'Pfizer'},
    {'name': 'Ciprofloxacin', 'strength': '500mg', 'dosage_form': 'Tablet', 'manufacturer': 'Bayer'},
    {'name': 'Metronidazole', 'strength': '400mg', 'dosage_form': 'Tablet', 'manufacturer': 'GSK'},
]
for d in drugs:
    Drug.objects.get_or_create(name=d['name'], defaults=d)
print('Sample drugs loaded!')
"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Start the server with:  python manage.py runserver"
echo "Admin panel:            http://localhost:8000/admin/"
echo "Application:            http://localhost:8000/"
