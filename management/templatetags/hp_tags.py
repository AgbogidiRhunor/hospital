from django import template
register = template.Library()

@register.filter
def currency(value):
    try:
        return f'₦{float(value):,.2f}'
    except:
        return value

@register.filter
def status_color(status):
    colors = {
        'pending_payment': '#f59e0b',
        'paid': '#10b981',
        'vitals': '#6366f1',
        'with_doctor': '#3b82f6',
        'lab_pending': '#f97316',
        'lab_paid': '#14b8a6',
        'lab_processing': '#8b5cf6',
        'rx_pending': '#f97316',
        'rx_paid': '#14b8a6',
        'pharmacy': '#06b6d4',
        'completed': '#22c55e',
        'pending': '#f59e0b',
        'dispensed': '#22c55e',
        'rejected': '#ef4444',
        'in_progress': '#8b5cf6',
    }
    return colors.get(status, '#6b7280')


@register.filter
def make_list(value):
    """Returns range(value) for use in templates."""
    try:
        return range(int(value))
    except (TypeError, ValueError):
        return []

@register.filter  
def split(value, delimiter=','):
    return value.split(delimiter)

@register.filter
def make_range(value):
    try:
        return range(1, int(value)+1)
    except (TypeError, ValueError):
        return []

@register.filter
def ward_filter(admissions, ward_key):
    return [a for a in admissions if a.ward == ward_key]

@register.filter
def age(dob):
    if not dob:
        return ''
    from django.utils import timezone
    today = timezone.now().date()
    return (today - dob).days // 365

@register.filter
def replace(value, args):
    try:
        old, new = args.split(',')
        return str(value).replace(old.strip(), new.strip())
    except:
        return value
