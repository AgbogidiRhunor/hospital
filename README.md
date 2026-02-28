# HealthPlus V3 — Hospital Management System

## Fresh Install

```bash
pip install django pillow
python manage.py migrate
python manage.py createsuperuser
python seed.py
python manage.py runserver
```

Then visit http://127.0.0.1:8000 and log in as superuser to approve staff accounts.

---

## Complete Patient Flow

```
1. RECEPTIONIST
   → Searches for patient profile
   → Assigns: Doctor (General or Specialist), Vital-Sign Nurse, On-Sit Accountant
   → Sets consultation fee
   → Creates visit → sent to Accountant

2. ACCOUNTANT
   → Sees pending payment
   → Confirms payment → Patient's info appears on Nurse dashboard
   → Can print receipt

3. NURSE (with Vital Signs role active)
   → Sees assigned patient (PAID badge shown)
   → Records all vitals → Sends to Doctor

4. DOCTOR
   → Sees patient only AFTER nurse submits vitals
   → Can add notes, order lab tests, prescribe drugs
   → Assigns specific lab attendant + pharmacist (must be available)
   → Lab/drug orders → go to Accountant first for payment
   → Doctor can end session at any time

5. ACCOUNTANT (for Lab/Prescription payment)
   → Sees lab/drug payment request
   → Confirms → forwards to Lab Attendant or Pharmacist

6. LAB ATTENDANT
   → Sees assigned requests (PAID badge)
   → Enters results per test → sends to Doctor automatically

7. PHARMACIST
   → Sees assigned prescriptions (PAID badge)
   → Dispenses → Doctor can now end session
```

---

## New in V3

- **Accountant role** — full dashboard, receipts, payment confirmation, on-sit toggle
- **Receptionist** — completely new UI, searches patients and doctors dynamically
- **Doctor registration** — General vs Specialist + specialization picker
- **Consulting rooms** — doctor picks which room they're in (visible to everyone)
- **Vital signs nurse toggle** — max 2 nurses can hold role at once
- **Lab + prescription payments** → go through accountant before lab/pharmacy
- **Prices on lab tests and drugs** — cost overlay before doctor submits
- **Receipts** — generated and printable for every payment
- **Receipts attached to patient dashboard** — patient can view/download each receipt
- **Doctor assigns mandatory** staff (pharmacist + lab attendant must be available)
- **Soft-delete** for pharmacist dispensed tab and lab completed tab
- **Beautiful patient medical records** — progress tracker, care team display, vitals grid

---

## Roles Summary

| Role | Key Capabilities |
|------|----------------|
| Patient | View full visit history, progress tracker, receipts |
| Receptionist | Register visits, search patients & doctors |
| Accountant | Confirm payments, print receipts, on-sit toggle |
| Nurse | Vital signs (with role toggle), max 2 at once |
| Doctor | Full session management, consulting room, end session |
| Pharmacist | Dispense assigned prescriptions, availability toggle |
| Lab Attendant | Process assigned tests, availability toggle |

---

## Admin Dashboard

Visit `/admin/` to:
- Approve staff accounts
- Add/remove/rename consulting rooms (change number from 7 to any amount)
- Manage drugs and lab test prices
