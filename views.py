"""
FPMS Views
All API endpoints (JSON) + HTML page serving views
"""

import json
from datetime import date, datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.db.models import Sum, Count, Q

from .models import (User, Farmer, Credit, Delivery,
                     MachineryBooking, Payment, SeedDistribution, SoilHealthLog)

PRICE_PER_KG = 40  # KES per kg paddy

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def json_response(data, status=200):
    return JsonResponse(data, status=status, safe=isinstance(data, dict))

def error(msg, status=400):
    return JsonResponse({'success': False, 'error': msg}, status=status)

def ok(data=None, msg='OK'):
    resp = {'success': True, 'message': msg}
    if data is not None:
        resp['data'] = data
    return JsonResponse(resp)

def get_session_user(request):
    uid = request.session.get('user_id')
    if not uid:
        return None
    try:
        return User.objects.get(pk=uid)
    except User.DoesNotExist:
        return None

def require_login(func):
    def wrapper(request, *args, **kwargs):
        if not get_session_user(request):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
               request.content_type == 'application/json':
                return error('Not authenticated', 401)
            return redirect('/')
        return func(request, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def require_admin(func):
    def wrapper(request, *args, **kwargs):
        user = get_session_user(request)
        if not user or user.role != 'admin':
            return error('Admin access required', 403)
        return func(request, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def next_id(prefix, model, field):
    """Generate sequential IDs like FRM0001, CRD0042 …"""
    last = model.objects.order_by(f'-{field}').first()
    if last:
        num = int(getattr(last, field)[len(prefix):]) + 1
    else:
        num = 1
    return f"{prefix}{num:04d}"

def farmer_to_dict(f):
    return {
        'id': f.id,
        'farmer_id': f.farmer_id,
        'full_name': f.full_name,
        'id_number': f.id_number,
        'phone': f.phone,
        'location': f.location,
        'farm_size': float(f.farm_size),
        'plot_number': f.plot_number,
        'status': f.status,
        'join_date': str(f.join_date),
    }

def credit_to_dict(c):
    return {
        'id': c.id,
        'credit_id': c.credit_id,
        'farmer_id': c.farmer.farmer_id,
        'farmer_name': c.farmer.full_name,
        'credit_type': c.credit_type,
        'amount': float(c.amount),
        'outstanding': float(c.outstanding),
        'description': c.description,
        'status': c.status,
        'date_issued': str(c.date_issued),
    }

def delivery_to_dict(d):
    return {
        'id': d.id,
        'delivery_id': d.delivery_id,
        'farmer_id': d.farmer.farmer_id,
        'farmer_name': d.farmer.full_name,
        'delivery_date': str(d.delivery_date),
        'weight': float(d.weight),
        'variety': d.variety,
        'milling_status': d.milling_status,
    }

def booking_to_dict(b):
    return {
        'id': b.id,
        'booking_id': b.booking_id,
        'farmer_id': b.farmer.farmer_id,
        'farmer_name': b.farmer.full_name,
        'machinery_type': b.machinery_type,
        'requested_date': str(b.requested_date),
        'plot_number': b.plot_number,
        'notes': b.notes,
        'status': b.status,
        'submitted_on': str(b.submitted_on),
    }

def payment_to_dict(p):
    return {
        'id': p.id,
        'payment_id': p.payment_id,
        'farmer_id': p.farmer.farmer_id,
        'farmer_name': p.farmer.full_name,
        'amount': float(p.amount),
        'method': p.method,
        'reference': p.reference,
        'date_paid': str(p.date_paid),
    }

def seed_to_dict(s):
    return {
        'id': s.id,
        'seed_id': s.seed_id,
        'farmer_id': s.farmer.farmer_id,
        'farmer_name': s.farmer.full_name,
        'variety': s.variety,
        'quantity_kg': float(s.quantity_kg),
        'supplier_quality': s.supplier_quality,
        'distribution_date': str(s.distribution_date),
    }

def soil_to_dict(l):
    return {
        'id': l.id,
        'log_id': l.log_id,
        'farmer_id': l.farmer.farmer_id,
        'farmer_name': l.farmer.full_name,
        'ph_level': float(l.ph_level) if l.ph_level else None,
        'moisture_level': l.moisture_level,
        'water_status': l.water_status,
        'fertilizer_rec': l.fertilizer_rec,
        'log_date': str(l.log_date),
    }


# ─────────────────────────────────────────────────────────────
# HTML PAGE VIEWS  (serve the SPA-style pages)
# ─────────────────────────────────────────────────────────────

def index(request):
    user = get_session_user(request)
    if user:
        if user.role == 'admin':
            return redirect('/pages/admin-dashboard/')
        return redirect('/pages/farmer-dashboard/')
    return render(request, 'fpms_app/index.html')

@require_login
def page_view(request, page):
    user = get_session_user(request)
    context = {
        'user': user,
        'farmer_profile': getattr(user, 'farmer_profile', None) if user.role == 'farmer' else None,
    }
    templates = {
        'admin-dashboard':    'fpms_app/admin_dashboard.html',
        'farmers':            'fpms_app/farmers.html',
        'credits':            'fpms_app/credits.html',
        'stock':              'fpms_app/stock.html',
        'machinery':          'fpms_app/machinery.html',
        'payments':           'fpms_app/payments.html',
        'agronomic':          'fpms_app/agronomic.html',
        'reports':            'fpms_app/reports.html',
        'farmer-dashboard':   'fpms_app/farmer_dashboard.html',
        'farmer-credits':     'fpms_app/farmer_credits.html',
        'farmer-deliveries':  'fpms_app/farmer_deliveries.html',
        'farmer-booking':     'fpms_app/farmer_booking.html',
        'farmer-agronomic':   'fpms_app/farmer_agronomic.html',
    }
    # Role guard
    admin_only = {'admin-dashboard','farmers','credits','stock','machinery','payments','agronomic','reports'}
    farmer_only = {'farmer-dashboard','farmer-credits','farmer-deliveries','farmer-booking','farmer-agronomic'}
    if page in admin_only and user.role != 'admin':
        return redirect('/pages/farmer-dashboard/')
    if page in farmer_only and user.role != 'farmer':
        return redirect('/pages/admin-dashboard/')
    tpl = templates.get(page)
    if not tpl:
        return redirect('/')
    return render(request, tpl, context)


# ─────────────────────────────────────────────────────────────
# AUTH API
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['POST'])
def api_login(request):
    data = json.loads(request.body)
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role     = data.get('role', '').strip()
    try:
        user = User.objects.get(username=username, role=role)
    except User.DoesNotExist:
        return error('Invalid credentials or wrong role.')
    if not user.check_password(password):
        return error('Invalid credentials or wrong role.')
    request.session['user_id'] = user.id
    farmer_id = None
    if hasattr(user, 'farmer_profile') and user.farmer_profile:
        farmer_id = user.farmer_profile.farmer_id
    return ok({'role': user.role, 'name': user.full_name,
                'farmer_id': farmer_id, 'redirect': f'/pages/{"admin-dashboard" if user.role=="admin" else "farmer-dashboard"}/'})

@require_http_methods(['POST', 'GET'])
def api_logout(request):
    request.session.flush()
    return ok(msg='Logged out')

def api_me(request):
    user = get_session_user(request)
    if not user:
        return error('Not authenticated', 401)
    farmer_id = None
    if hasattr(user, 'farmer_profile') and user.farmer_profile:
        farmer_id = user.farmer_profile.farmer_id
    return ok({'id': user.id, 'username': user.username,
                'role': user.role, 'name': user.full_name,
                'farmer_id': farmer_id})


# ─────────────────────────────────────────────────────────────
# FARMERS API
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_login
def api_farmers(request):
    if request.method == 'GET':
        q = request.GET.get('q', '')
        qs = Farmer.objects.all()
        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(id_number__icontains=q) | Q(phone__icontains=q))
        return ok([farmer_to_dict(f) for f in qs])

    if request.method == 'POST':
        user = get_session_user(request)
        if user.role != 'admin':
            return error('Admin only', 403)
        data = json.loads(request.body)
        required = ['full_name', 'id_number', 'phone']
        for field in required:
            if not data.get(field):
                return error(f'{field} is required')
        if Farmer.objects.filter(id_number=data['id_number']).exists():
            return error('A farmer with this ID number already exists.')
        with transaction.atomic():
            fid = next_id('FRM', Farmer, 'farmer_id')
            farmer = Farmer.objects.create(
                farmer_id=fid,
                full_name=data['full_name'],
                id_number=data['id_number'],
                phone=data['phone'],
                location=data.get('location', ''),
                farm_size=data.get('farm_size', 0),
                plot_number=data.get('plot_number', ''),
            )
            # Create login user if password provided
            if data.get('password'):
                uname = 'farmer' + str(farmer.id)
                fu = User.objects.create(
                    username=uname,
                    password=make_password(data['password']),
                    role='farmer',
                    full_name=data['full_name'],
                )
                farmer.user = fu
                farmer.save()
        return ok(farmer_to_dict(farmer), 'Farmer registered successfully')

@csrf_exempt
@require_login
def api_farmer_detail(request, pk):
    try:
        f = Farmer.objects.get(pk=pk)
    except Farmer.DoesNotExist:
        return error('Farmer not found', 404)

    if request.method == 'GET':
        data = farmer_to_dict(f)
        data['credits'] = [credit_to_dict(c) for c in f.credits.all()]
        data['deliveries'] = [delivery_to_dict(d) for d in f.deliveries.all()]
        data['bookings'] = [booking_to_dict(b) for b in f.bookings.all()]
        data['total_delivered'] = float(f.total_delivered)
        data['outstanding_credit'] = float(f.outstanding_credit)
        return ok(data)

    if request.method == 'PATCH':
        user = get_session_user(request)
        if user.role != 'admin':
            return error('Admin only', 403)
        data = json.loads(request.body)
        for field in ['full_name', 'phone', 'location', 'farm_size', 'plot_number', 'status']:
            if field in data:
                setattr(f, field, data[field])
        f.save()
        return ok(farmer_to_dict(f), 'Farmer updated')


# ─────────────────────────────────────────────────────────────
# CREDITS API
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_login
def api_credits(request):
    user = get_session_user(request)

    if request.method == 'GET':
        q = request.GET.get('q', '')
        farmer_id = request.GET.get('farmer_id', '')
        qs = Credit.objects.select_related('farmer').all()
        if q:
            qs = qs.filter(farmer__full_name__icontains=q)
        if farmer_id:
            qs = qs.filter(farmer__farmer_id=farmer_id)
        if user.role == 'farmer':
            fp = getattr(user, 'farmer_profile', None)
            if fp:
                qs = qs.filter(farmer=fp)
            else:
                return ok([])
        totals = {
            'total_issued':  float(qs.aggregate(t=Sum('amount'))['t'] or 0),
            'outstanding':   float(qs.aggregate(t=Sum('outstanding'))['t'] or 0),
        }
        totals['repaid'] = totals['total_issued'] - totals['outstanding']
        return ok({'credits': [credit_to_dict(c) for c in qs], 'totals': totals})

    if request.method == 'POST':
        if user.role != 'admin':
            return error('Admin only', 403)
        data = json.loads(request.body)
        try:
            farmer = Farmer.objects.get(farmer_id=data['farmer_id'])
        except Farmer.DoesNotExist:
            return error('Farmer not found')
        cid = next_id('CRD', Credit, 'credit_id')
        amount = float(data['amount'])
        c = Credit.objects.create(
            credit_id=cid,
            farmer=farmer,
            credit_type=data.get('credit_type', 'Other'),
            amount=amount,
            outstanding=amount,
            description=data.get('description', ''),
        )
        return ok(credit_to_dict(c), 'Credit issued successfully')


# ─────────────────────────────────────────────────────────────
# DELIVERIES / STOCK API
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_login
def api_deliveries(request):
    user = get_session_user(request)

    if request.method == 'GET':
        q = request.GET.get('q', '')
        farmer_id = request.GET.get('farmer_id', '')
        qs = Delivery.objects.select_related('farmer').all()
        if q:
            qs = qs.filter(Q(farmer__full_name__icontains=q) | Q(variety__icontains=q))
        if farmer_id:
            qs = qs.filter(farmer__farmer_id=farmer_id)
        if user.role == 'farmer':
            fp = getattr(user, 'farmer_profile', None)
            if fp:
                qs = qs.filter(farmer=fp)
            else:
                return ok([])
        totals = {
            'total_stock':  float(qs.aggregate(t=Sum('weight'))['t'] or 0),
            'pending':      float(qs.exclude(milling_status='Completed').aggregate(t=Sum('weight'))['t'] or 0),
            'completed':    float(qs.filter(milling_status='Completed').aggregate(t=Sum('weight'))['t'] or 0),
        }
        return ok({'deliveries': [delivery_to_dict(d) for d in qs], 'totals': totals})

    if request.method == 'POST':
        if user.role != 'admin':
            return error('Admin only', 403)
        data = json.loads(request.body)
        try:
            farmer = Farmer.objects.get(farmer_id=data['farmer_id'])
        except Farmer.DoesNotExist:
            return error('Farmer not found')
        did = next_id('DEL', Delivery, 'delivery_id')
        d = Delivery.objects.create(
            delivery_id=did,
            farmer=farmer,
            delivery_date=data.get('delivery_date', date.today()),
            weight=float(data['weight']),
            variety=data.get('variety', 'Basmati'),
            milling_status=data.get('milling_status', 'Pending'),
        )
        return ok(delivery_to_dict(d), 'Delivery recorded')

@csrf_exempt
@require_login
def api_delivery_detail(request, pk):
    try:
        d = Delivery.objects.get(pk=pk)
    except Delivery.DoesNotExist:
        return error('Delivery not found', 404)
    if request.method == 'PATCH':
        user = get_session_user(request)
        if user.role != 'admin':
            return error('Admin only', 403)
        data = json.loads(request.body)
        if 'milling_status' in data:
            d.milling_status = data['milling_status']
            d.save()
        return ok(delivery_to_dict(d), 'Updated')


# ─────────────────────────────────────────────────────────────
# MACHINERY BOOKINGS API
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_login
def api_bookings(request):
    user = get_session_user(request)

    if request.method == 'GET':
        status_filter = request.GET.get('status', '')
        farmer_id = request.GET.get('farmer_id', '')
        qs = MachineryBooking.objects.select_related('farmer').all()
        if status_filter and status_filter != 'all':
            qs = qs.filter(status=status_filter)
        if farmer_id:
            qs = qs.filter(farmer__farmer_id=farmer_id)
        if user.role == 'farmer':
            fp = getattr(user, 'farmer_profile', None)
            if fp:
                qs = qs.filter(farmer=fp)
        counts = {
            'pending':  MachineryBooking.objects.filter(status='Pending').count(),
            'approved': MachineryBooking.objects.filter(status='Approved').count(),
            'rejected': MachineryBooking.objects.filter(status='Rejected').count(),
        }
        return ok({'bookings': [booking_to_dict(b) for b in qs], 'counts': counts})

    if request.method == 'POST':
        data = json.loads(request.body)
        if user.role == 'farmer':
            fp = getattr(user, 'farmer_profile', None)
            if not fp:
                return error('No farmer profile linked to your account')
            farmer = fp
        else:
            try:
                farmer = Farmer.objects.get(farmer_id=data['farmer_id'])
            except Farmer.DoesNotExist:
                return error('Farmer not found')
        bid = next_id('BKG', MachineryBooking, 'booking_id')
        b = MachineryBooking.objects.create(
            booking_id=bid,
            farmer=farmer,
            machinery_type=data['machinery_type'],
            requested_date=data['requested_date'],
            plot_number=data.get('plot_number', ''),
            notes=data.get('notes', ''),
        )
        return ok(booking_to_dict(b), 'Booking request submitted')

@csrf_exempt
@require_login
@require_admin
def api_booking_action(request, pk):
    try:
        b = MachineryBooking.objects.get(pk=pk)
    except MachineryBooking.DoesNotExist:
        return error('Booking not found', 404)
    data = json.loads(request.body)
    action = data.get('action')
    if action == 'approve':
        b.status = 'Approved'
    elif action == 'reject':
        b.status = 'Rejected'
    else:
        return error('Invalid action')
    b.save()
    return ok(booking_to_dict(b), f'Booking {b.status.lower()}')


# ─────────────────────────────────────────────────────────────
# PAYMENTS API
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_login
def api_payments(request):
    user = get_session_user(request)

    if request.method == 'GET':
        farmer_id = request.GET.get('farmer_id', '')
        qs = Payment.objects.select_related('farmer').all()
        if farmer_id:
            qs = qs.filter(farmer__farmer_id=farmer_id)
        if user.role == 'farmer':
            fp = getattr(user, 'farmer_profile', None)
            if fp:
                qs = qs.filter(farmer=fp)
        # Build summary per farmer for admin view
        if user.role == 'admin' and not farmer_id:
            summary = []
            for f in Farmer.objects.all():
                total_del = float(f.deliveries.aggregate(t=Sum('weight'))['t'] or 0)
                gross = total_del * PRICE_PER_KG
                credit_ded = float(f.credits.aggregate(t=Sum('outstanding'))['t'] or 0)
                already_paid = float(f.payments.aggregate(t=Sum('amount'))['t'] or 0)
                net = max(0, gross - credit_ded - already_paid)
                status = 'Paid' if net == 0 and already_paid > 0 else ('Partial' if already_paid > 0 else 'Pending')
                summary.append({
                    'farmer_id': f.farmer_id,
                    'farmer_name': f.full_name,
                    'total_delivered': total_del,
                    'gross': gross,
                    'credit_deduction': credit_ded,
                    'already_paid': already_paid,
                    'net_payable': net,
                    'status': status,
                })
            total_paid = float(Payment.objects.aggregate(t=Sum('amount'))['t'] or 0)
            all_gross = sum(s['gross'] for s in summary)
            return ok({
                'summary': summary,
                'history': [payment_to_dict(p) for p in qs],
                'total_paid': total_paid,
                'total_pending': max(0, all_gross - total_paid),
            })
        return ok({'history': [payment_to_dict(p) for p in qs]})

    if request.method == 'POST':
        if user.role != 'admin':
            return error('Admin only', 403)
        data = json.loads(request.body)
        try:
            farmer = Farmer.objects.get(farmer_id=data['farmer_id'])
        except Farmer.DoesNotExist:
            return error('Farmer not found')
        amount = float(data['amount'])
        with transaction.atomic():
            pid = next_id('PAY', Payment, 'payment_id')
            p = Payment.objects.create(
                payment_id=pid,
                farmer=farmer,
                amount=amount,
                method=data.get('method', 'Cash'),
                reference=data.get('reference', ''),
            )
            # Deduct from outstanding credits
            remaining = amount
            for c in farmer.credits.filter(outstanding__gt=0).order_by('date_issued'):
                if remaining <= 0:
                    break
                deduct = min(float(c.outstanding), remaining)
                c.outstanding = float(c.outstanding) - deduct
                c.status = 'Repaid' if c.outstanding == 0 else 'Partial'
                c.save()
                remaining -= deduct
        return ok(payment_to_dict(p), 'Payment processed')


# ─────────────────────────────────────────────────────────────
# AGRONOMIC API
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_login
def api_seeds(request):
    user = get_session_user(request)

    if request.method == 'GET':
        qs = SeedDistribution.objects.select_related('farmer').all()
        if user.role == 'farmer':
            fp = getattr(user, 'farmer_profile', None)
            if fp:
                qs = qs.filter(farmer=fp)
        return ok([seed_to_dict(s) for s in qs])

    if request.method == 'POST':
        if user.role != 'admin':
            return error('Admin only', 403)
        data = json.loads(request.body)
        try:
            farmer = Farmer.objects.get(farmer_id=data['farmer_id'])
        except Farmer.DoesNotExist:
            return error('Farmer not found')
        sid = next_id('SED', SeedDistribution, 'seed_id')
        s = SeedDistribution.objects.create(
            seed_id=sid,
            farmer=farmer,
            variety=data['variety'],
            quantity_kg=float(data['quantity_kg']),
            supplier_quality=data.get('supplier_quality', 'Certified'),
        )
        return ok(seed_to_dict(s), 'Seed distribution recorded')

@csrf_exempt
@require_login
def api_soil_logs(request):
    user = get_session_user(request)

    if request.method == 'GET':
        qs = SoilHealthLog.objects.select_related('farmer').all()
        if user.role == 'farmer':
            fp = getattr(user, 'farmer_profile', None)
            if fp:
                qs = qs.filter(farmer=fp)
        return ok([soil_to_dict(l) for l in qs])

    if request.method == 'POST':
        if user.role != 'admin':
            return error('Admin only', 403)
        data = json.loads(request.body)
        try:
            farmer = Farmer.objects.get(farmer_id=data['farmer_id'])
        except Farmer.DoesNotExist:
            return error('Farmer not found')
        lid = next_id('SHL', SoilHealthLog, 'log_id')
        l = SoilHealthLog.objects.create(
            log_id=lid,
            farmer=farmer,
            ph_level=data.get('ph_level') or None,
            moisture_level=data.get('moisture_level', 'Adequate'),
            water_status=data.get('water_status', 'Optimal'),
            fertilizer_rec=data.get('fertilizer_rec', ''),
        )
        return ok(soil_to_dict(l), 'Soil log recorded')


# ─────────────────────────────────────────────────────────────
# REPORTS API
# ─────────────────────────────────────────────────────────────

@require_login
def api_reports(request):
    report_type = request.GET.get('type', 'farmers')

    if report_type == 'farmers':
        data = [farmer_to_dict(f) for f in Farmer.objects.all()]
    elif report_type == 'credits':
        qs = Credit.objects.select_related('farmer').all()
        data = {
            'credits': [credit_to_dict(c) for c in qs],
            'total_issued': float(qs.aggregate(t=Sum('amount'))['t'] or 0),
            'outstanding':  float(qs.aggregate(t=Sum('outstanding'))['t'] or 0),
        }
    elif report_type == 'stock':
        qs = Delivery.objects.select_related('farmer').all()
        data = {
            'deliveries': [delivery_to_dict(d) for d in qs],
            'total_stock': float(qs.aggregate(t=Sum('weight'))['t'] or 0),
        }
    elif report_type == 'payments':
        qs = Payment.objects.select_related('farmer').all()
        data = {
            'payments': [payment_to_dict(p) for p in qs],
            'total_paid': float(qs.aggregate(t=Sum('amount'))['t'] or 0),
        }
    elif report_type == 'machinery':
        qs = MachineryBooking.objects.select_related('farmer').all()
        data = {'bookings': [booking_to_dict(b) for b in qs], 'total': qs.count()}
    elif report_type == 'agronomic':
        qs = SeedDistribution.objects.select_related('farmer').all()
        data = {
            'seeds': [seed_to_dict(s) for s in qs],
            'total_qty': float(qs.aggregate(t=Sum('quantity_kg'))['t'] or 0),
        }
    else:
        return error('Unknown report type')
    return ok(data)


# ─────────────────────────────────────────────────────────────
# DASHBOARD STATS
# ─────────────────────────────────────────────────────────────

@require_login
def api_dashboard_stats(request):
    user = get_session_user(request)
    if user.role == 'admin':
        total_farmers = Farmer.objects.count()
        total_credit  = float(Credit.objects.aggregate(t=Sum('amount'))['t'] or 0)
        total_stock   = float(Delivery.objects.aggregate(t=Sum('weight'))['t'] or 0)
        total_paid    = float(Payment.objects.aggregate(t=Sum('amount'))['t'] or 0)
        pending_bookings = MachineryBooking.objects.filter(status='Pending').count()
        recent_deliveries = [delivery_to_dict(d) for d in Delivery.objects.select_related('farmer').order_by('-delivery_date')[:5]]
        pending_bk_list   = [booking_to_dict(b) for b in MachineryBooking.objects.select_related('farmer').filter(status='Pending')[:5]]
        return ok({
            'total_farmers': total_farmers,
            'total_credit': total_credit,
            'total_stock': total_stock,
            'total_paid': total_paid,
            'pending_bookings': pending_bookings,
            'recent_deliveries': recent_deliveries,
            'pending_bookings_list': pending_bk_list,
        })
    else:
        fp = getattr(user, 'farmer_profile', None)
        if not fp:
            return ok({'error': 'No farmer profile'})
        total_delivered = float(fp.deliveries.aggregate(t=Sum('weight'))['t'] or 0)
        outstanding     = float(fp.outstanding_credit)
        gross           = total_delivered * PRICE_PER_KG
        already_paid    = float(fp.payments.aggregate(t=Sum('amount'))['t'] or 0)
        net_payable     = max(0, gross - outstanding - already_paid)
        deliveries = fp.deliveries.order_by('-delivery_date')
        last_milling = deliveries.first().milling_status if deliveries.exists() else '-'
        return ok({
            'total_delivered': total_delivered,
            'outstanding_credit': outstanding,
            'net_payable': net_payable,
            'last_milling_status': last_milling,
            'recent_deliveries': [delivery_to_dict(d) for d in deliveries[:5]],
            'credits': [credit_to_dict(c) for c in fp.credits.all()],
            'bookings': [booking_to_dict(b) for b in fp.bookings.order_by('-submitted_on')[:5]],
        })
