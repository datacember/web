CREATE DATABASE IF NOT EXISTS datacember;
drop database datacember;
create database datacember;
use datacember;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    github VARCHAR(255) NOT NULL,
    signup VARCHAR(255) NOT NULL,
    points INT DEFAULT 0
);

CREATE TABLE adventcontent (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_text TEXT,
    content_table TEXT,
    content_image TEXT
);

CREATE TABLE adventresponses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    response TEXT,
    date VARCHAR(255)
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    display INT,
    error TEXT
);

CREATE TABLE challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    html TEXT NOT NULL,
    `release` VARCHAR(255) NOT NULL,
    deadline VARCHAR(255) NOT NULL
);

CREATE TABLE adventreadmore (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT
);

INSERT INTO challenges (name, html, release, deadline)
VALUES 
    ('Stars', 'stars', '2024-12-1', '2024-12-5'),
    ('Froth Flotation', 'mining', '2024-12-6', '2024-12-12'),
    ('SQLippery When Icy!', 'cold', '2024-12-12', '2024-12-16'),
    ('Silicon Says', 'chess', '2024-12-17', '2024-12-23'),
    ('Word on the Street', 'news', '2024-12-26', '2024-12-31');

CREATE TABLE tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token TEXT NOT NULL,
    user TEXT NOT NULL,
    year INT,
    month INT,
    day INT,
    hour INT,
    minute INT
);

CREATE TABLE queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token INT,
    user TEXT,
    user_query TEXT,
    time DOUBLE,
    runtime TEXT,
    row_length INT
);
