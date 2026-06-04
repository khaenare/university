INSERT INTO users(username, password_hash, role) VALUES
('admin', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'admin'),
('reader', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'reader')
ON CONFLICT (username) DO NOTHING;

INSERT INTO publications(title, publisher, period_months, price) VALUES
('Наука і життя', 'Українська преса', 1, 120.00),
('Бізнес тиждень', 'Media Group', 1, 95.50),
('Літературний журнал', 'Культура', 1, 80.00);
