-- ============================================================
-- FPMS MySQL Database Schema
-- Farm Produce Management System
-- Mwea Rice Farmers Cooperative Society
-- ============================================================
-- Run this ONLY if you prefer manual DB setup over Django migrations.
-- Normally just run: python manage.py migrate
-- ============================================================

CREATE DATABASE IF NOT EXISTS fpms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fpms_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    role        ENUM('admin','farmer') NOT NULL,
    full_name   VARCHAR(200) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Farmers table
CREATE TABLE IF NOT EXISTS farmers (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id    VARCHAR(20)  NOT NULL UNIQUE,
    user_id      INT NULL,
    full_name    VARCHAR(200) NOT NULL,
    id_number    VARCHAR(20)  NOT NULL UNIQUE,
    phone        VARCHAR(20)  NOT NULL,
    location     VARCHAR(100) DEFAULT '',
    farm_size    DECIMAL(6,2) DEFAULT 0.00,
    plot_number  VARCHAR(50)  DEFAULT '',
    status       ENUM('Active','Inactive') DEFAULT 'Active',
    join_date    DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Credits table
CREATE TABLE IF NOT EXISTS credits (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    credit_id   VARCHAR(20) NOT NULL UNIQUE,
    farmer_id   INT NOT NULL,
    credit_type ENUM('Seed','Fertilizer','Machinery','Land Preparation','Other') NOT NULL,
    amount      DECIMAL(12,2) NOT NULL,
    outstanding DECIMAL(12,2) NOT NULL,
    description TEXT DEFAULT '',
    status      ENUM('Outstanding','Partial','Repaid') DEFAULT 'Outstanding',
    date_issued DATE NOT NULL,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Deliveries table
CREATE TABLE IF NOT EXISTS deliveries (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    delivery_id    VARCHAR(20) NOT NULL UNIQUE,
    farmer_id      INT NOT NULL,
    delivery_date  DATE NOT NULL,
    weight         DECIMAL(10,2) NOT NULL,
    variety        ENUM('Basmati','IR2793','Nerica','BW196') DEFAULT 'Basmati',
    milling_status ENUM('Pending','Processing','Completed') DEFAULT 'Pending',
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Machinery bookings table
CREATE TABLE IF NOT EXISTS machinery_bookings (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    booking_id     VARCHAR(20) NOT NULL UNIQUE,
    farmer_id      INT NOT NULL,
    machinery_type ENUM('Tractor','Harvester','Transplanter','Thresher','Ploughing Machine') NOT NULL,
    requested_date DATE NOT NULL,
    plot_number    VARCHAR(50) DEFAULT '',
    notes          TEXT DEFAULT '',
    status         ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
    submitted_on   DATE NOT NULL,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    payment_id  VARCHAR(20) NOT NULL UNIQUE,
    farmer_id   INT NOT NULL,
    amount      DECIMAL(12,2) NOT NULL,
    method      ENUM('M-Pesa','Bank Transfer','Cash') NOT NULL,
    reference   VARCHAR(100) DEFAULT '',
    date_paid   DATE NOT NULL,
    notes       TEXT DEFAULT '',
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed distributions table
CREATE TABLE IF NOT EXISTS seed_distributions (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    seed_id           VARCHAR(20) NOT NULL UNIQUE,
    farmer_id         INT NOT NULL,
    variety           ENUM('Basmati','IR2793','Nerica','BW196') NOT NULL,
    quantity_kg       DECIMAL(8,2) NOT NULL,
    supplier_quality  ENUM('Certified','Good','Average','Poor') DEFAULT 'Certified',
    distribution_date DATE NOT NULL,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Soil health logs table
CREATE TABLE IF NOT EXISTS soil_health_logs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    log_id          VARCHAR(20) NOT NULL UNIQUE,
    farmer_id       INT NOT NULL,
    ph_level        DECIMAL(4,2) NULL,
    moisture_level  ENUM('Adequate','Low','High') DEFAULT 'Adequate',
    water_status    ENUM('Optimal','Needs Attention','Critical') DEFAULT 'Optimal',
    fertilizer_rec  TEXT DEFAULT '',
    log_date        DATE NOT NULL,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Django sessions (created automatically by migrate, listed here for reference)
-- django_session table is auto-created by Django

SELECT 'FPMS schema created successfully.' AS status;
