-- Create the database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS goroute_db;

-- Use the database
USE goroute_db;

-- Drop the bookings table if it exists to avoid column mismatch errors
DROP TABLE IF EXISTS bookings;

-- Create the bookings table
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    package_type VARCHAR(100) NOT NULL,
    travel_date DATE NOT NULL,
    guests INT NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'Cash',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
