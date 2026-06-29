CREATE TABLE admins (
    admin_id VARCHAR(50) NOT NULL,
    admin_name VARCHAR(100) NOT NULL,
    admin_address TEXT,
    phone_number VARCHAR(15) NOT NULL,
    fee_balance NUMERIC(10, 2) DEFAULT 0.00 NOT NULL, -- Kept to mirror user fields exactly
    email VARCHAR(255) CONSTRAINT uq_admins_email UNIQUE,
    username VARCHAR(50) CONSTRAINT uq_admins_username UNIQUE,
    password VARCHAR(255) NOT NULL,
    
    -- Primary key constraint for admins
    CONSTRAINT pk_admins PRIMARY KEY (admin_id)
);

-- Indexing phone number for fast lookups if admins receive system alerts via SMS
CREATE INDEX idx_admins_phone ON admins(phone_number);

CREATE TABLE IF NOT EXISTS water_schedules (
    schedule_id VARCHAR(50) PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    delivery_time VARCHAR(255) NOT NULL
);