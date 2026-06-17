-- Add email, username, and password columns to the users table
ALTER TABLE users 
    ADD COLUMN email VARCHAR(255) CONSTRAINT uq_users_email UNIQUE,
    ADD COLUMN username VARCHAR(50) CONSTRAINT uq_users_username UNIQUE,
    ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT 'TEMPORARY_HASHED_HOLDER';

-- Clear the default constraint after setup so future inserts require a password
ALTER TABLE users ALTER COLUMN password DROP DEFAULT;