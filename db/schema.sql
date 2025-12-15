CREATE DATABASE IF NOT EXISTS mydb;
USE mydb;


CREATE TABLE IF NOT EXISTS api_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- In production, store hashed passwords!
    auth_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO api_user (username, email, password) VALUES ('user', 'doron@example.com', 'doron')
ON DUPLICATE KEY UPDATE password='admin';
