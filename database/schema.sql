CREATE DATABASE IF NOT EXISTS research_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE research_portal;
CREATE TABLE IF NOT EXISTS opportunities (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    research_area VARCHAR(120) NOT NULL,
    faculty_name VARCHAR(120) NOT NULL,
    department VARCHAR(120) NOT NULL,
    required_skills TEXT NOT NULL,
    available_positions INT UNSIGNED NOT NULL,
    application_deadline DATE NOT NULL,
    status ENUM('Open', 'Closed') NOT NULL DEFAULT 'Open',
    CONSTRAINT positions_positive CHECK (available_positions > 0)
) ENGINE=InnoDB;
