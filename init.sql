CREATE TABLE IF NOT EXISTS doctors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    mobile VARCHAR(20),
    register_no VARCHAR(100) UNIQUE,
    bio TEXT,
    profile_image_url TEXT,
    onboarding_status VARCHAR(50) DEFAULT 'in_progress',
    current_step INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    icon_name VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS doctor_departments (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    department_id INTEGER REFERENCES departments(id),
    UNIQUE(doctor_id, department_id)
);

CREATE TABLE IF NOT EXISTS qualifications (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    qualification VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS specializations (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    specialization VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),
    pincode VARCHAR(20),
    flat_house TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8)
);

CREATE TABLE IF NOT EXISTS appointment_settings (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    consultation_charge INTEGER,
    follow_up_charge INTEGER,
    follow_up_period_days INTEGER,
    advance_booking_days INTEGER,
    avg_duration_minutes INTEGER
);

CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    day_of_week INTEGER,
    start_time TIME,
    end_time TIME,
    is_available BOOLEAN DEFAULT TRUE
);

INSERT INTO departments (name, icon_name) VALUES
    ('Cardiology', 'heart'),
    ('Casualty', 'ambulance'),
    ('Dentistry', 'tooth'),
    ('Gynaecology', 'female'),
    ('Orthopedic', 'bone'),
    ('Psychiatry', 'brain'),
    ('Radiology', 'xray'),
    ('Paediatrics', 'baby'),
    ('General Surgery', 'surgery'),
    ('Intensive Care', 'icu')
ON CONFLICT (name) DO NOTHING;