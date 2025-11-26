-- schema.sql
-- Схема БД для інтернет-платформи фрилансерів (PostgreSQL)

-- ================================
-- Розширення, які можуть знадобитися
-- ================================
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Загальна функція для автооновлення updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ======================
-- Користувачі та ролі
-- ======================

CREATE TABLE users (
    user_id         SERIAL PRIMARY KEY,
    email           VARCHAR(150) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(150) NOT NULL,
    user_type       VARCHAR(20)  NOT NULL CHECK (user_type IN ('freelancer', 'client', 'admin')),
    is_deleted      BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by      INT NULL,
    updated_at      TIMESTAMPTZ,
    updated_by      INT NULL,
    CONSTRAINT fk_users_created_by FOREIGN KEY (created_by) REFERENCES users(user_id),
    CONSTRAINT fk_users_updated_by FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

CREATE TABLE roles (
    role_id     SERIAL PRIMARY KEY,
    role_name   VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE user_roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

-- ==========================================
-- Профілі фрилансерів та клієнтів
-- ==========================================

CREATE TABLE freelancer_profiles (
    freelancer_profile_id SERIAL PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    title           VARCHAR(200),
    hourly_rate     NUMERIC(12, 2),
    overview        TEXT,
    location        VARCHAR(150),
    is_deleted      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      INT NULL,
    updated_at      TIMESTAMPTZ,
    updated_by      INT NULL,
    CONSTRAINT fk_freelancer_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_freelancer_created_by FOREIGN KEY (created_by) REFERENCES users(user_id),
    CONSTRAINT fk_freelancer_updated_by FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

CREATE TABLE client_profiles (
    client_profile_id SERIAL PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    company_name    VARCHAR(200),
    website         VARCHAR(200),
    description     TEXT,
    is_deleted      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      INT NULL,
    updated_at      TIMESTAMPTZ,
    updated_by      INT NULL,
    CONSTRAINT fk_client_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_client_created_by FOREIGN KEY (created_by) REFERENCES users(user_id),
    CONSTRAINT fk_client_updated_by FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

-- ==============================
-- Навички та категорії проектів
-- ==============================

CREATE TABLE skills (
    skill_id    SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE freelancer_skills (
    freelancer_profile_id INT NOT NULL,
    skill_id              INT NOT NULL,
    PRIMARY KEY (freelancer_profile_id, skill_id),
    CONSTRAINT fk_fs_profile FOREIGN KEY (freelancer_profile_id) REFERENCES freelancer_profiles(freelancer_profile_id),
    CONSTRAINT fk_fs_skill   FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
);

CREATE TABLE project_categories (
    category_id SERIAL PRIMARY KEY,
    name        VARCHAR(150) NOT NULL UNIQUE
);

-- ======================
-- Проекти та вимоги
-- ======================

CREATE TABLE projects (
    project_id      SERIAL PRIMARY KEY,
    client_id       INT NOT NULL,
    category_id     INT,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    budget_min      NUMERIC(12, 2),
    budget_max      NUMERIC(12, 2),
    status          VARCHAR(20) NOT NULL CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled')),
    is_deleted      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      INT NULL,
    updated_at      TIMESTAMPTZ,
    updated_by      INT NULL,
    CONSTRAINT fk_projects_client    FOREIGN KEY (client_id)   REFERENCES users(user_id),
    CONSTRAINT fk_projects_category  FOREIGN KEY (category_id) REFERENCES project_categories(category_id),
    CONSTRAINT fk_projects_created_by FOREIGN KEY (created_by) REFERENCES users(user_id),
    CONSTRAINT fk_projects_updated_by FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

CREATE TABLE project_required_skills (
    project_id  INT NOT NULL,
    skill_id    INT NOT NULL,
    PRIMARY KEY (project_id, skill_id),
    CONSTRAINT fk_prs_project FOREIGN KEY (project_id) REFERENCES projects(project_id),
    CONSTRAINT fk_prs_skill   FOREIGN KEY (skill_id)   REFERENCES skills(skill_id)
);

-- ======================================
-- Отклики фрилансерів на проекти
-- ======================================

CREATE TABLE proposals (
    proposal_id     SERIAL PRIMARY KEY,
    project_id      INT NOT NULL,
    freelancer_id   INT NOT NULL,
    cover_letter    TEXT,
    bid_amount      NUMERIC(12, 2),
    status          VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'accepted', 'rejected', 'withdrawn')),
    is_deleted      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      INT NULL,
    updated_at      TIMESTAMPTZ,
    updated_by      INT NULL,
    CONSTRAINT fk_proposals_project    FOREIGN KEY (project_id)    REFERENCES projects(project_id),
    CONSTRAINT fk_proposals_freelancer FOREIGN KEY (freelancer_id) REFERENCES users(user_id),
    CONSTRAINT fk_proposals_created_by FOREIGN KEY (created_by)    REFERENCES users(user_id),
    CONSTRAINT fk_proposals_updated_by FOREIGN KEY (updated_by)    REFERENCES users(user_id)
);

-- ==============================
-- Контракти та історія статусів
-- ==============================

CREATE TABLE contracts (
    contract_id     SERIAL PRIMARY KEY,
    project_id      INT NOT NULL,
    client_id       INT NOT NULL,
    freelancer_id   INT NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE,
    status          VARCHAR(20) NOT NULL CHECK (status IN ('active', 'completed', 'cancelled')),
    hourly_rate     NUMERIC(12, 2),
    fixed_price     NUMERIC(12, 2),
    is_deleted      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      INT NULL,
    updated_at      TIMESTAMPTZ,
    updated_by      INT NULL,
    CONSTRAINT fk_contracts_project    FOREIGN KEY (project_id)    REFERENCES projects(project_id),
    CONSTRAINT fk_contracts_client     FOREIGN KEY (client_id)     REFERENCES users(user_id),
    CONSTRAINT fk_contracts_freelancer FOREIGN KEY (freelancer_id) REFERENCES users(user_id),
    CONSTRAINT fk_contracts_created_by FOREIGN KEY (created_by)    REFERENCES users(user_id),
    CONSTRAINT fk_contracts_updated_by FOREIGN KEY (updated_by)    REFERENCES users(user_id)
);

CREATE TABLE contract_status_history (
    history_id  SERIAL PRIMARY KEY,
    contract_id INT NOT NULL,
    status_from VARCHAR(20),
    status_to   VARCHAR(20) NOT NULL,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by  INT,
    CONSTRAINT fk_csh_contract   FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    CONSTRAINT fk_csh_changed_by FOREIGN KEY (changed_by)  REFERENCES users(user_id)
);

-- ==============================
-- Milestones, інвойси, платежі
-- ==============================

CREATE TABLE milestones (
    milestone_id    SERIAL PRIMARY KEY,
    contract_id     INT NOT NULL,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    due_date        DATE,
    amount          NUMERIC(12, 2) NOT NULL,
    status          VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'in_review', 'approved', 'paid', 'cancelled')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      INT NULL,
    updated_at      TIMESTAMPTZ,
    updated_by      INT NULL,
    CONSTRAINT fk_milestones_contract   FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    CONSTRAINT fk_milestones_created_by FOREIGN KEY (created_by)  REFERENCES users(user_id),
    CONSTRAINT fk_milestones_updated_by FOREIGN KEY (updated_by)  REFERENCES users(user_id)
);

CREATE TABLE invoices (
    invoice_id      SERIAL PRIMARY KEY,
    contract_id     INT NOT NULL,
    milestone_id    INT,
    amount          NUMERIC(12, 2) NOT NULL,
    issue_date      DATE NOT NULL,
    due_date        DATE,
    status          VARCHAR(20) NOT NULL CHECK (status IN ('unpaid', 'paid', 'cancelled')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      INT NULL,
    updated_at      TIMESTAMPTZ,
    updated_by      INT NULL,
    CONSTRAINT fk_invoices_contract   FOREIGN KEY (contract_id)  REFERENCES contracts(contract_id),
    CONSTRAINT fk_invoices_milestone  FOREIGN KEY (milestone_id) REFERENCES milestones(milestone_id),
    CONSTRAINT fk_invoices_created_by FOREIGN KEY (created_by)   REFERENCES users(user_id),
    CONSTRAINT fk_invoices_updated_by FOREIGN KEY (updated_by)   REFERENCES users(user_id)
);

CREATE TABLE payments (
    payment_id      SERIAL PRIMARY KEY,
    invoice_id      INT NOT NULL,
    payer_id        INT NOT NULL,
    receiver_id     INT NOT NULL,
    amount          NUMERIC(12, 2) NOT NULL,
    payment_method  VARCHAR(50),
    payment_date    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_payments_invoice  FOREIGN KEY (invoice_id)  REFERENCES invoices(invoice_id),
    CONSTRAINT fk_payments_payer    FOREIGN KEY (payer_id)    REFERENCES users(user_id),
    CONSTRAINT fk_payments_receiver FOREIGN KEY (receiver_id) REFERENCES users(user_id)
);

-- ==============================
-- Відгуки та повідомлення
-- ==============================

CREATE TABLE reviews (
    review_id   SERIAL PRIMARY KEY,
    contract_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    reviewee_id INT NOT NULL,
    rating      INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_reviews_contract  FOREIGN KEY (contract_id)  REFERENCES contracts(contract_id),
    CONSTRAINT fk_reviews_reviewer  FOREIGN KEY (reviewer_id)  REFERENCES users(user_id),
    CONSTRAINT fk_reviews_reviewee  FOREIGN KEY (reviewee_id)  REFERENCES users(user_id)
);

CREATE TABLE messages (
    message_id  SERIAL PRIMARY KEY,
    contract_id INT,
    sender_id   INT NOT NULL,
    receiver_id INT NOT NULL,
    body        TEXT NOT NULL,
    sent_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_read     BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted  BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_messages_contract  FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    CONSTRAINT fk_messages_sender    FOREIGN KEY (sender_id)   REFERENCES users(user_id),
    CONSTRAINT fk_messages_receiver  FOREIGN KEY (receiver_id) REFERENCES users(user_id)
);

-- =======================================
-- Тригери для автооновлення updated_at
-- =======================================

CREATE TRIGGER trg_users_set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_freelancer_set_updated_at
BEFORE UPDATE ON freelancer_profiles
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_client_set_updated_at
BEFORE UPDATE ON client_profiles
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_projects_set_updated_at
BEFORE UPDATE ON projects
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_proposals_set_updated_at
BEFORE UPDATE ON proposals
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_contracts_set_updated_at
BEFORE UPDATE ON contracts
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_milestones_set_updated_at
BEFORE UPDATE ON milestones
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_invoices_set_updated_at
BEFORE UPDATE ON invoices
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- ===========================
-- Індекси (різні типи)
-- ===========================

-- B-tree індекси для типових фільтрів
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_projects_client_id ON projects(client_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_proposals_project_id ON proposals(project_id);
CREATE INDEX idx_contracts_client_id ON contracts(client_id);
CREATE INDEX idx_contracts_freelancer_id ON contracts(freelancer_id);

-- Частковий індекс лише для відкритих проектів
CREATE INDEX idx_projects_open
ON projects(project_id)
WHERE status = 'open' AND is_deleted = FALSE;

-- GIN-індекс для пошуку по назві та опису проекту
CREATE INDEX idx_projects_search
ON projects
USING GIN (
    to_tsvector('simple', COALESCE(title, '') || ' ' || COALESCE(description, ''))
);

-- Процедура для створення нового контракту
CREATE OR REPLACE PROCEDURE sp_create_contract(
    IN p_project_id INT,
    IN p_client_id INT,
    IN p_freelancer_id INT,
    IN p_start_date DATE,
    IN p_status VARCHAR(20),
    IN p_hourly_rate NUMERIC(12, 2),
    IN p_fixed_price NUMERIC(12, 2),
    IN p_created_by INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO contracts (
        project_id,
        client_id,
        freelancer_id,
        start_date,
        status,
        hourly_rate,
        fixed_price,
        is_deleted,
        created_at,
        created_by
    )
    VALUES (
        p_project_id,
        p_client_id,
        p_freelancer_id,
        p_start_date,
        p_status,
        p_hourly_rate,
        p_fixed_price,
        FALSE,
        NOW(),
        p_created_by
    );
END;
$$;

-- Процедура для створення нового повідомлення
CREATE OR REPLACE PROCEDURE sp_create_message(
    IN p_contract_id INT,
    IN p_sender_id INT,
    IN p_receiver_id INT,
    IN p_body TEXT,
    IN p_is_read BOOLEAN,
    IN p_is_deleted BOOLEAN,
    IN p_sent_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO messages (contract_id, sender_id, receiver_id, body, is_read, is_deleted, sent_at)
    VALUES (p_contract_id, p_sender_id, p_receiver_id, p_body, p_is_read, p_is_deleted, p_sent_at);
END;
$$;


-- ===========================================
-- Додаткові індекси для демонстрації різних типів
-- ===========================================

-- 1) Звичайний btree-індекс по статусу проекту
-- (якщо такого ще немає у schema.sql)
CREATE INDEX IF NOT EXISTS idx_projects_status
    ON projects (status);

-- 2) HASH-індекс по email користувача
-- Це вже інший тип індексу (hash), а не btree.
CREATE INDEX IF NOT EXISTS idx_users_email_hash
    ON users USING hash (email);

