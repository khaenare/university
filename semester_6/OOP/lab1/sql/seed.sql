INSERT INTO users(username, password_hash, role) VALUES
('admin', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'admin'),
('reader', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'reader'),
('olena', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'reader'),
('maksym', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'reader'),
('iryna', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'reader')
ON CONFLICT (username) DO NOTHING;

INSERT INTO publications(title, publisher, period_months, price) VALUES
('Наука і життя', 'Українська преса', 1, 120.00),
('Бізнес тиждень', 'Media Group', 1, 95.50),
('Літературний журнал', 'Культура', 1, 80.00),
('Технології майбутнього', 'Digital Press', 1, 149.00),
('Медичний огляд', 'Health Media', 1, 135.00),
('Спорт Арена', 'Champion House', 1, 89.00),
('Дитячий світ', 'Веселка', 1, 64.50),
('Освіта XXI', 'Academic Publishing', 1, 102.00),
('Фінансовий аналітик', 'Capital Review', 1, 175.00),
('Подорожі Україною', 'Travel UA', 1, 118.00),
('Архітектура і дизайн', 'Urban Studio', 1, 156.00),
('КіноКадр', 'Cinema Press', 1, 92.00),
('Еко Планета', 'Green Line', 1, 110.00),
('Історичний вісник', 'Heritage Books', 1, 99.00),
('Кулінарна майстерня', 'Taste Media', 1, 74.00),
('Авто Світ', 'Motor Press', 1, 130.00),
('Психологія сьогодні', 'Mindset', 1, 125.00),
('Аграрний огляд', 'AgroPro', 1, 115.00),
('Мистецтво простору', 'Gallery Lab', 1, 142.00),
('Кібербезпека PRO', 'Secure Digital', 1, 189.00);

INSERT INTO subscriptions(user_id, publication_id, months, total_amount, status)
SELECT u.id, p.id, 6, p.price * 6, 'created'
FROM users u, publications p
WHERE u.username = 'reader' AND p.title = 'Наука і життя';

INSERT INTO subscriptions(user_id, publication_id, months, total_amount, status)
SELECT u.id, p.id, 12, p.price * 12, 'active'
FROM users u, publications p
WHERE u.username = 'reader' AND p.title = 'Технології майбутнього';

INSERT INTO subscriptions(user_id, publication_id, months, total_amount, status)
SELECT u.id, p.id, 3, p.price * 3, 'active'
FROM users u, publications p
WHERE u.username = 'olena' AND p.title = 'Кулінарна майстерня';

INSERT INTO subscriptions(user_id, publication_id, months, total_amount, status)
SELECT u.id, p.id, 9, p.price * 9, 'created'
FROM users u, publications p
WHERE u.username = 'maksym' AND p.title = 'Фінансовий аналітик';

INSERT INTO subscriptions(user_id, publication_id, months, total_amount, status)
SELECT u.id, p.id, 4, p.price * 4, 'cancelled'
FROM users u, publications p
WHERE u.username = 'iryna' AND p.title = 'Подорожі Україною';

INSERT INTO payments(subscription_id, amount, status)
SELECT s.id, s.total_amount, 'registered'
FROM subscriptions s
JOIN users u ON u.id = s.user_id
JOIN publications p ON p.id = s.publication_id
WHERE u.username = 'reader' AND p.title = 'Наука і життя';

INSERT INTO payments(subscription_id, amount, status)
SELECT s.id, s.total_amount, 'paid'
FROM subscriptions s
JOIN users u ON u.id = s.user_id
JOIN publications p ON p.id = s.publication_id
WHERE u.username = 'reader' AND p.title = 'Технології майбутнього';

INSERT INTO payments(subscription_id, amount, status)
SELECT s.id, s.total_amount, 'cancelled'
FROM subscriptions s
JOIN users u ON u.id = s.user_id
JOIN publications p ON p.id = s.publication_id
WHERE u.username = 'iryna' AND p.title = 'Подорожі Україною';
