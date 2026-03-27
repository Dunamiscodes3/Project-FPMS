"""
FPMS Django Models
All database tables for the Farm Produce Management System
Maps to MySQL via Django ORM
"""

from django.db import models
from django.contrib.auth.hashers import make_password


# ─────────────────────────────────────────────────────────────
# USER / AUTH
# ─────────────────────────────────────────────────────────────
class User(models.Model):
    ROLE_CHOICES = [('admin', 'Administrator'), ('farmer', 'Farmer')]

    username   = models.CharField(max_length=100, unique=True)
    password   = models.CharField(max_length=255)          # stored hashed
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES)
    full_name  = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.username} ({self.role})"

    def set_password(self, raw):
        self.password = make_password(raw)

    def check_password(self, raw):
        from django.contrib.auth.hashers import check_password
        return check_password(raw, self.password)


# ─────────────────────────────────────────────────────────────
# FARMERS
# ─────────────────────────────────────────────────────────────
class Farmer(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive')]

    farmer_id   = models.CharField(max_length=20, unique=True)
    user        = models.OneToOneField(User, null=True, blank=True,
                                       on_delete=models.SET_NULL,
                                       related_name='farmer_profile')
    full_name   = models.CharField(max_length=200)
    id_number   = models.CharField(max_length=20, unique=True)
    phone       = models.CharField(max_length=20)
    location    = models.CharField(max_length=100, blank=True)
    farm_size   = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    plot_number = models.CharField(max_length=50, blank=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    join_date   = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'farmers'

    def __str__(self):
        return f"{self.farmer_id} – {self.full_name}"

    @property
    def total_delivered(self):
        return sum(d.weight for d in self.deliveries.all())

    @property
    def outstanding_credit(self):
        return sum(c.outstanding for c in self.credits.all())


# ─────────────────────────────────────────────────────────────
# CREDITS
# ─────────────────────────────────────────────────────────────
class Credit(models.Model):
    STATUS_CHOICES = [
        ('Outstanding', 'Outstanding'),
        ('Partial', 'Partial'),
        ('Repaid', 'Repaid'),
    ]
    TYPE_CHOICES = [
        ('Seed', 'Seed'),
        ('Fertilizer', 'Fertilizer'),
        ('Machinery', 'Machinery'),
        ('Land Preparation', 'Land Preparation'),
        ('Other', 'Other'),
    ]

    credit_id   = models.CharField(max_length=20, unique=True)
    farmer      = models.ForeignKey(Farmer, on_delete=models.CASCADE,
                                    related_name='credits')
    credit_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    outstanding = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES,
                                   default='Outstanding')
    date_issued = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'credits'

    def __str__(self):
        return f"{self.credit_id} – {self.farmer.full_name} – {self.credit_type}"


# ─────────────────────────────────────────────────────────────
# PRODUCE DELIVERIES
# ─────────────────────────────────────────────────────────────
class Delivery(models.Model):
    MILLING_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
    ]
    VARIETY_CHOICES = [
        ('Basmati', 'Basmati'),
        ('IR2793', 'IR2793'),
        ('Nerica', 'Nerica'),
        ('BW196', 'BW196'),
    ]

    delivery_id    = models.CharField(max_length=20, unique=True)
    farmer         = models.ForeignKey(Farmer, on_delete=models.CASCADE,
                                       related_name='deliveries')
    delivery_date  = models.DateField()
    weight         = models.DecimalField(max_digits=10, decimal_places=2)
    variety        = models.CharField(max_length=20, choices=VARIETY_CHOICES,
                                      default='Basmati')
    milling_status = models.CharField(max_length=15, choices=MILLING_CHOICES,
                                      default='Pending')
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deliveries'
        ordering = ['-delivery_date']

    def __str__(self):
        return f"{self.delivery_id} – {self.farmer.full_name} – {self.weight}kg"


# ─────────────────────────────────────────────────────────────
# MACHINERY BOOKINGS
# ─────────────────────────────────────────────────────────────
class MachineryBooking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    MACHINERY_CHOICES = [
        ('Tractor', 'Tractor'),
        ('Harvester', 'Harvester'),
        ('Transplanter', 'Transplanter'),
        ('Thresher', 'Thresher'),
        ('Ploughing Machine', 'Ploughing Machine'),
    ]

    booking_id     = models.CharField(max_length=20, unique=True)
    farmer         = models.ForeignKey(Farmer, on_delete=models.CASCADE,
                                       related_name='bookings')
    machinery_type = models.CharField(max_length=30, choices=MACHINERY_CHOICES)
    requested_date = models.DateField()
    plot_number    = models.CharField(max_length=50, blank=True)
    notes          = models.TextField(blank=True)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES,
                                      default='Pending')
    submitted_on   = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'machinery_bookings'
        ordering = ['-submitted_on']

    def __str__(self):
        return f"{self.booking_id} – {self.farmer.full_name} – {self.machinery_type}"


# ─────────────────────────────────────────────────────────────
# PAYMENTS
# ─────────────────────────────────────────────────────────────
class Payment(models.Model):
    METHOD_CHOICES = [
        ('M-Pesa', 'M-Pesa'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cash', 'Cash'),
    ]

    payment_id  = models.CharField(max_length=20, unique=True)
    farmer      = models.ForeignKey(Farmer, on_delete=models.CASCADE,
                                    related_name='payments')
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    method      = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference   = models.CharField(max_length=100, blank=True)
    date_paid   = models.DateField(auto_now_add=True)
    notes       = models.TextField(blank=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-date_paid']

    def __str__(self):
        return f"{self.payment_id} – {self.farmer.full_name} – KES {self.amount}"


# ─────────────────────────────────────────────────────────────
# SEED DISTRIBUTION
# ─────────────────────────────────────────────────────────────
class SeedDistribution(models.Model):
    QUALITY_CHOICES = [
        ('Certified', 'Certified'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
    ]
    VARIETY_CHOICES = [
        ('Basmati', 'Basmati'),
        ('IR2793', 'IR2793'),
        ('Nerica', 'Nerica'),
        ('BW196', 'BW196'),
    ]

    seed_id         = models.CharField(max_length=20, unique=True)
    farmer          = models.ForeignKey(Farmer, on_delete=models.CASCADE,
                                        related_name='seeds')
    variety         = models.CharField(max_length=20, choices=VARIETY_CHOICES)
    quantity_kg     = models.DecimalField(max_digits=8, decimal_places=2)
    supplier_quality= models.CharField(max_length=15, choices=QUALITY_CHOICES,
                                       default='Certified')
    distribution_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'seed_distributions'

    def __str__(self):
        return f"{self.seed_id} – {self.farmer.full_name} – {self.variety}"


# ─────────────────────────────────────────────────────────────
# SOIL HEALTH LOGS
# ─────────────────────────────────────────────────────────────
class SoilHealthLog(models.Model):
    MOISTURE_CHOICES = [
        ('Adequate', 'Adequate'),
        ('Low', 'Low'),
        ('High', 'High'),
    ]
    WATER_CHOICES = [
        ('Optimal', 'Optimal'),
        ('Needs Attention', 'Needs Attention'),
        ('Critical', 'Critical'),
    ]

    log_id          = models.CharField(max_length=20, unique=True)
    farmer          = models.ForeignKey(Farmer, on_delete=models.CASCADE,
                                        related_name='soil_logs')
    ph_level        = models.DecimalField(max_digits=4, decimal_places=2,
                                          null=True, blank=True)
    moisture_level  = models.CharField(max_length=15, choices=MOISTURE_CHOICES,
                                       default='Adequate')
    water_status    = models.CharField(max_length=20, choices=WATER_CHOICES,
                                       default='Optimal')
    fertilizer_rec  = models.TextField(blank=True)
    log_date        = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'soil_health_logs'
        ordering = ['-log_date']

    def __str__(self):
        return f"{self.log_id} – {self.farmer.full_name}"
