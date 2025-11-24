-- data.sql
-- Початкові тестові дані для інтернет-платформи фрилансерів

-- =============================================
-- 1. ОЧИСТКА (TRUNCATE ВСІХ ДАНИХ)
-- =============================================

TRUNCATE TABLE
    contract_status_history,
    payments,
    invoices,
    milestones,
    contracts,
    proposals,
    project_required_skills,
    projects,
    messages,
    reviews,
    freelancer_skills,
    freelancer_profiles,
    client_profiles,
    project_categories,
    skills,
    user_roles,
    roles,
    users
RESTART IDENTITY CASCADE;

-- =============================================
-- 2. КОРИСТУВАЧІ ТА РОЛІ
-- =============================================

-- Користувачі:
-- 1 - клієнт
-- 2 - фрилансер
-- 3 - адміністратор
-- 4 - ще один клієнт
-- 5 - ще один фрилансер

INSERT INTO users (email, password_hash, full_name, user_type, is_deleted, created_at)
VALUES
    ('client1@example.com',     'hash_client1',     'Client One',        'client',     FALSE, NOW()),
    ('freelancer1@example.com', 'hash_freelancer1', 'Freelancer One',    'freelancer', FALSE, NOW()),
    ('admin@example.com',       'hash_admin',       'Admin User',        'admin',      FALSE, NOW()),
    ('client2@example.com',     'hash_client2',     'Client Two',        'client',     FALSE, NOW()),
    ('freelancer2@example.com', 'hash_freelancer2', 'Freelancer Two',    'freelancer', FALSE, NOW());

-- Ролі
INSERT INTO roles (role_name)
VALUES
    ('client'),
    ('freelancer'),
    ('admin')
ON CONFLICT (role_id) DO NOTHING;

-- Призначення ролей
-- user_id 1 -> client
-- user_id 2 -> freelancer
-- user_id 3 -> admin
-- user_id 4 -> client
-- user_id 5 -> freelancer
INSERT INTO user_roles (user_id, role_id)
VALUES
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 1),
    (5, 2)
ON CONFLICT (user_id, role_id) DO NOTHING;

-- =============================================
-- 3. ПРОФІЛІ КЛІЄНТІВ ТА ФРИЛАНСЕРІВ
-- =============================================

-- Профілі клієнтів
INSERT INTO client_profiles (user_id, company_name, website, description, is_deleted, created_at)
VALUES
    (1, 'Client One LLC', 'https://client1.example.com', 'Small business client', FALSE, NOW()),
    (4, 'Client Two Inc', 'https://client2.example.com', 'Corporate client',      FALSE, NOW());

-- Профілі фрилансерів
INSERT INTO freelancer_profiles (user_id, title, hourly_rate, overview, location, is_deleted, created_at)
VALUES
    (2, 'Full-stack Developer', 45.00, 'Python, React, APIs, microservices.', 'Remote', FALSE, NOW()),
    (5, 'Data Scientist',       60.00, 'ML, data analysis, dashboards.',      'Remote', FALSE, NOW());

-- =============================================
-- 4. НАВИЧКИ ТА НАВИЧКИ ФРИЛАНСЕРІВ
-- =============================================

INSERT INTO skills (name)
VALUES
    ('Python'),
    ('Django'),
    ('FastAPI'),
    ('React'),
    ('PostgreSQL'),
    ('Machine Learning'),
    ('Data Analysis')
ON CONFLICT (skill_id) DO NOTHING;

-- Прив’язка навичок до профілів фрилансерів
-- Профіль 1 (user 2) - веб-розробка
INSERT INTO freelancer_skills (freelancer_profile_id, skill_id)
VALUES
    (1, 1),  -- Python
    (1, 2),  -- Django
    (1, 4),  -- React
    (1, 5);  -- PostgreSQL

-- Профіль 2 (user 5) - data science
INSERT INTO freelancer_skills (freelancer_profile_id, skill_id)
VALUES
    (2, 1),  -- Python
    (2, 6),  -- ML
    (2, 7);  -- Data Analysis

-- =============================================
-- 5. КАТЕГОРІЇ ПРОЕКТІВ
-- =============================================

INSERT INTO project_categories (name)
VALUES
    ('Web Development'),
    ('Mobile Development'),
    ('Data Science'),
    ('DevOps')
ON CONFLICT (category_id) DO NOTHING;

-- На цей момент маємо:
-- users: 5 шт (з них 2 клієнти, 2 фрилансери, 1 адмін)
-- roles, user_roles: базові ролі
-- client_profiles, freelancer_profiles: по 2 профілі
-- skills + freelancer_skills: наповнені скіли
-- project_categories: кілька категорій

-- Далі всі бізнес-сутності (projects, proposals, contracts,
-- milestones, invoices, payments, reviews, contract_status_history)
-- будуть створюватися через наші збережені процедури з коду Python
-- (sp_create_project, sp_create_proposal, sp_accept_proposal,
--  sp_create_milestone, sp_pay_milestone), що якраз і демонструє
-- роботу бізнес-логіки БД.
