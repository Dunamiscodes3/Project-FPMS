"""
Management command to seed the FPMS database with initial demo data.
Run: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import date, timedelta
from fpms_app.models import (User, Farmer, Credit, Delivery,
                              MachineryBooking, Payment,
                              SeedDistribution, SoilHealthLog)


class Command(BaseCommand):
    help = 'Seed the FPMS database with demo data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding FPMS database...')

        # Clear existing data (safe for dev)
        SoilHealthLog.objects.all().delete()
        SeedDistribution.objects.all().delete()
        Payment.objects.all().delete()
        MachineryBooking.objects.all().delete()
        Delivery.objects.all().delete()
        Credit.objects.all().delete()
        Farmer.objects.all().delete()
        User.objects.all().delete()

        # ── Admin User ───────────────────────────────────────
        admin = User.objects.create(
            username='admin',
            password=make_password('admin123'),
            role='admin',
            full_name='System Administrator',
        )
        self.stdout.write('  ✅ Admin user created  (admin / admin123)')

        # ── Farmers ──────────────────────────────────────────
        farmers_data = [
            ('FRM0001', 'John Mwangi',   '12345678', '0712345678', 'Wanguru',  3.5, 'W-045'),
            ('FRM0002', 'Mary Njeri',    '23456789', '0723456789', 'Thiba',    2.0, 'T-012'),
            ('FRM0003', 'Peter Kamau',   '34567890', '0734567890', 'Kirwara',  4.0, 'K-088'),
            ('FRM0004', 'Grace Wahu',    '45678901', '0745678901', 'Mutithi',  1.5, 'M-033'),
            ('FRM0005', 'Samuel Gitau',  '56789012', '0756789012', 'Wanguru',  3.0, 'W-091'),
        ]

        farmers = []
        for i, (fid, name, id_num, phone, loc, size, plot) in enumerate(farmers_data, 1):
            uname = f'farmer{i}'
            fu = User.objects.create(
                username=uname,
                password=make_password('farm123'),
                role='farmer',
                full_name=name,
            )
            f = Farmer.objects.create(
                farmer_id=fid,
                user=fu,
                full_name=name,
                id_number=id_num,
                phone=phone,
                location=loc,
                farm_size=size,
                plot_number=plot,
            )
            farmers.append(f)
            self.stdout.write(f'  ✅ Farmer: {name}  ({uname} / farm123)')

        f1, f2, f3, f4, f5 = farmers

        # ── Credits ──────────────────────────────────────────
        Credit.objects.create(credit_id='CRD0001', farmer=f1, credit_type='Fertilizer',
            amount=8000, outstanding=8000, description='Urea 100kg', status='Outstanding')
        Credit.objects.create(credit_id='CRD0002', farmer=f1, credit_type='Seed',
            amount=3500, outstanding=0, description='Basmati seeds 25kg', status='Repaid')
        Credit.objects.create(credit_id='CRD0003', farmer=f2, credit_type='Machinery',
            amount=5000, outstanding=2500, description='Tractor hire – ploughing', status='Partial')
        Credit.objects.create(credit_id='CRD0004', farmer=f3, credit_type='Fertilizer',
            amount=10000, outstanding=10000, description='NPK 200kg', status='Outstanding')
        Credit.objects.create(credit_id='CRD0005', farmer=f5, credit_type='Land Preparation',
            amount=6000, outstanding=6000, description='Land prep + harrowing', status='Outstanding')
        self.stdout.write('  ✅ Credits seeded')

        # ── Deliveries ───────────────────────────────────────
        today = date.today()
        Delivery.objects.create(delivery_id='DEL0001', farmer=f1,
            delivery_date=today - timedelta(days=20), weight=800,  variety='Basmati',   milling_status='Completed')
        Delivery.objects.create(delivery_id='DEL0002', farmer=f2,
            delivery_date=today - timedelta(days=15), weight=500,  variety='IR2793',    milling_status='Processing')
        Delivery.objects.create(delivery_id='DEL0003', farmer=f3,
            delivery_date=today - timedelta(days=10), weight=1200, variety='Basmati',   milling_status='Pending')
        Delivery.objects.create(delivery_id='DEL0004', farmer=f4,
            delivery_date=today - timedelta(days=8),  weight=350,  variety='Nerica',    milling_status='Completed')
        Delivery.objects.create(delivery_id='DEL0005', farmer=f5,
            delivery_date=today - timedelta(days=5),  weight=620,  variety='BW196',     milling_status='Processing')
        self.stdout.write('  ✅ Deliveries seeded')

        # ── Machinery Bookings ───────────────────────────────
        MachineryBooking.objects.create(booking_id='BKG0001', farmer=f1,
            machinery_type='Harvester', requested_date=today + timedelta(days=7),
            plot_number='W-045', status='Approved', notes='Morning slot preferred')
        MachineryBooking.objects.create(booking_id='BKG0002', farmer=f2,
            machinery_type='Tractor', requested_date=today + timedelta(days=5),
            plot_number='T-012', status='Pending', notes='Ploughing needed')
        MachineryBooking.objects.create(booking_id='BKG0003', farmer=f3,
            machinery_type='Tractor', requested_date=today + timedelta(days=9),
            plot_number='K-088', status='Pending', notes='')
        MachineryBooking.objects.create(booking_id='BKG0004', farmer=f5,
            machinery_type='Thresher', requested_date=today + timedelta(days=12),
            plot_number='W-091', status='Approved', notes='')
        self.stdout.write('  ✅ Machinery bookings seeded')

        # ── Payments ─────────────────────────────────────────
        Payment.objects.create(payment_id='PAY0001', farmer=f1,
            amount=32000, method='M-Pesa', reference='MP202503150001')
        Payment.objects.create(payment_id='PAY0002', farmer=f4,
            amount=14000, method='Bank Transfer', reference='BT202503160002')
        self.stdout.write('  ✅ Payments seeded')

        # ── Seed Distributions ───────────────────────────────
        SeedDistribution.objects.create(seed_id='SED0001', farmer=f1,
            variety='Basmati',  quantity_kg=25, supplier_quality='Certified')
        SeedDistribution.objects.create(seed_id='SED0002', farmer=f2,
            variety='IR2793',   quantity_kg=15, supplier_quality='Certified')
        SeedDistribution.objects.create(seed_id='SED0003', farmer=f3,
            variety='Basmati',  quantity_kg=35, supplier_quality='Good')
        SeedDistribution.objects.create(seed_id='SED0004', farmer=f5,
            variety='BW196',    quantity_kg=20, supplier_quality='Certified')
        self.stdout.write('  ✅ Seed distributions seeded')

        # ── Soil Health Logs ─────────────────────────────────
        SoilHealthLog.objects.create(log_id='SHL0001', farmer=f1,
            ph_level=6.5, moisture_level='Adequate', water_status='Optimal',
            fertilizer_rec='Apply NPK 20-10-10 at 50kg/acre')
        SoilHealthLog.objects.create(log_id='SHL0002', farmer=f2,
            ph_level=5.8, moisture_level='Low', water_status='Needs Attention',
            fertilizer_rec='Apply lime 200kg/acre + Urea 30kg/acre')
        SoilHealthLog.objects.create(log_id='SHL0003', farmer=f3,
            ph_level=6.8, moisture_level='Adequate', water_status='Optimal',
            fertilizer_rec='Apply CAN 40kg/acre at tillering stage')
        SoilHealthLog.objects.create(log_id='SHL0004', farmer=f5,
            ph_level=7.1, moisture_level='High', water_status='Needs Attention',
            fertilizer_rec='Reduce irrigation frequency; apply DAP 25kg/acre')
        self.stdout.write('  ✅ Soil health logs seeded')

        self.stdout.write(self.style.SUCCESS(
            '\n🎉 Database seeded successfully!\n'
            '   Admin login:   admin / admin123\n'
            '   Farmer login:  farmer1 / farm123  (up to farmer5)\n'
        ))
