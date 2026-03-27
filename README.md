# FPMS – Farm Produce Management System
## Mwea Rice Farmers Cooperative Society
### Django + MySQL + HTML/CSS/JavaScript

---

## 📋 Project Overview

A full-stack web application for managing all operations of the Mwea Rice Farmers Cooperative Society including farmer registration, credit management, produce delivery tracking, milling status, machinery bookings, payments, and agronomic support.

**Tech Stack:**
- **Backend:** Python Django 4.2
- **Database:** MySQL 8.0+
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Authentication:** Django session-based auth

---

## 🗂️ Project Structure

```
fpms_django/
├── manage.py
├── requirements.txt
├── fpms_db_schema.sql          ← SQL schema (reference only)
├── fpms_project/
│   ├── settings.py             ← Django settings (configure DB here)
│   ├── urls.py
│   └── wsgi.py
└── fpms_app/
    ├── models.py               ← All 8 database models
    ├── views.py                ← All API endpoints + page views
    ├── urls.py                 ← All URL routes
    ├── admin.py                ← Django admin panel registration
    ├── apps.py
    ├── management/
    │   └── commands/
    │       └── seed_data.py    ← Demo data seeder command
    ├── templates/fpms_app/
    │   ├── base.html           ← Base template (all pages extend this)
    │   ├── index.html          ← Login page
    │   ├── admin_dashboard.html
    │   ├── farmers.html
    │   ├── credits.html
    │   ├── stock.html
    │   ├── machinery.html
    │   ├── payments.html
    │   ├── agronomic.html
    │   ├── reports.html
    │   ├── farmer_dashboard.html
    │   ├── farmer_credits.html
    │   ├── farmer_deliveries.html
    │   ├── farmer_booking.html
    │   └── farmer_agronomic.html
    └── static/fpms_app/
        ├── css/main.css
        └── js/
            ├── utils.js            ← Shared helpers (loaded on every page)
            ├── dashboard.js
            ├── farmers.js
            ├── credits.js
            ├── stock.js
            ├── machinery.js
            ├── payments.js
            ├── agronomic.js
            ├── reports.js
            ├── farmer_dashboard.js
            ├── farmer_credits.js
            ├── farmer_deliveries.js
            ├── farmer_booking.js
            └── farmer_agronomic.js
```

---

## ⚙️ Setup Instructions

### Step 1 – Prerequisites

Make sure you have installed:
- Python 3.10 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

### Step 2 – Create the MySQL Database

Open MySQL and run:
```sql
CREATE DATABASE fpms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 3 – Configure Database Credentials

Open `fpms_project/settings.py` and update the `DATABASES` section:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fpms_db',
        'USER': 'root',          # Your MySQL username
        'PASSWORD': 'yourpass',  # Your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Step 4 – Install Python Dependencies

```bash
pip install -r requirements.txt
```

> If `mysqlclient` fails to install on Windows, use:
> ```bash
> pip install mysqlclient --only-binary=:all:
> ```
> Or alternatively install `PyMySQL`:
> ```bash
> pip install PyMySQL
> ```
> Then add at the top of `fpms_project/__init__.py`:
> ```python
> import pymysql
> pymysql.install_as_MySQLdb()
> ```

### Step 5 – Run Migrations (Create Tables)

```bash
python manage.py makemigrations fpms_app
python manage.py migrate
```

This creates all tables in your MySQL database automatically.

### Step 6 – Seed Demo Data

```bash
python manage.py seed_data
```

This creates:
- 1 admin user
- 5 farmers with login accounts
- Credits, deliveries, bookings, payments, seed & soil records

### Step 7 – Start the Server

```bash
python manage.py runserver
```

Open your browser and go to: **http://127.0.0.1:8000**

---

## 🔐 Login Credentials

| Role          | Username  | Password  |
|---------------|-----------|-----------|
| Administrator | admin     | admin123  |
| Farmer 1      | farmer1   | farm123   |
| Farmer 2      | farmer2   | farm123   |
| Farmer 3      | farmer3   | farm123   |
| Farmer 4      | farmer4   | farm123   |
| Farmer 5      | farmer5   | farm123   |

---

## 🌐 API Endpoints

| Method | Endpoint                        | Description                    |
|--------|---------------------------------|--------------------------------|
| POST   | `/api/auth/login/`              | Login                          |
| POST   | `/api/auth/logout/`             | Logout                         |
| GET    | `/api/auth/me/`                 | Current user info              |
| GET    | `/api/dashboard/stats/`         | Dashboard statistics           |
| GET    | `/api/farmers/`                 | List / search farmers          |
| POST   | `/api/farmers/`                 | Register new farmer            |
| GET    | `/api/farmers/<id>/`            | Farmer detail + history        |
| PATCH  | `/api/farmers/<id>/`            | Update farmer                  |
| GET    | `/api/credits/`                 | List credits                   |
| POST   | `/api/credits/`                 | Issue credit                   |
| GET    | `/api/deliveries/`              | List deliveries                |
| POST   | `/api/deliveries/`              | Record delivery                |
| PATCH  | `/api/deliveries/<id>/`         | Update milling status          |
| GET    | `/api/bookings/`                | List bookings                  |
| POST   | `/api/bookings/`                | Submit booking request         |
| POST   | `/api/bookings/<id>/action/`    | Approve / reject booking       |
| GET    | `/api/payments/`                | Payment summary + history      |
| POST   | `/api/payments/`                | Process payment                |
| GET    | `/api/seeds/`                   | Seed distributions             |
| POST   | `/api/seeds/`                   | Record seed distribution       |
| GET    | `/api/soil-logs/`               | Soil health logs               |
| POST   | `/api/soil-logs/`               | Add soil log                   |
| GET    | `/api/reports/?type=<type>`     | Generate report data           |

---

## 🖥️ System Modules

### Administrator
- **Dashboard** — Live stats, recent deliveries, pending bookings
- **Farmer Management** — Register, search, view farmer history
- **Credit Management** — Issue credit, track balances, auto-deduction on payment
- **Stock & Deliveries** — Record paddy deliveries, update milling status
- **Machinery Bookings** — Approve/reject farmer booking requests
- **Payments** — Process farmer payouts with automatic credit deduction
- **Agronomic Support** — Seed distribution, soil health logs, yield tracking
- **Reports** — Generate & print 6 report types

### Farmer Portal
- **Dashboard** — Personal overview of credits, deliveries, milling, payout
- **My Credits** — View all issued credits and outstanding balances
- **My Deliveries** — View delivery history with estimated payouts
- **Book Machinery** — Submit and track machinery booking requests
- **Agronomic Info** — View seed records, soil logs, farming tips

---

## 🛠️ Django Admin Panel

Access the Django admin at: **http://127.0.0.1:8000/admin/**

Create a Django superuser first:
```bash
python manage.py createsuperuser
```

---

## 💰 Pricing Configuration

Default paddy price is **KES 40 per kg**.

To change: edit `PRICE_PER_KG = 40` in `fpms_app/views.py`

---

## 🔒 Production Deployment Notes

Before deploying to production:
1. Set `DEBUG = False` in `settings.py`
2. Set a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` with your domain
4. Run `python manage.py collectstatic`
5. Use a proper WSGI server (gunicorn) and reverse proxy (nginx)
6. Use environment variables for database credentials

---

## 👨‍💻 Developer

**Philip Githongo Manyara** — Reg: 24/04771
KCA University, School of Technology
Supervisor: Charles Malungu | Date: March 2026
