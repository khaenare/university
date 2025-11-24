-- logic.sql
-- Логіка БД для інтернет-платформи фрилансерів:
-- збережені процедури, функції, тригери та представлення

-- ===========================================
-- ФУНКЦІЇ
-- ===========================================

-- Функція для обчислення загальної суми контракту
CREATE OR REPLACE FUNCTION fn_get_contract_total(p_contract_id INT)
RETURNS NUMERIC(12, 2) AS $$
DECLARE
    v_total NUMERIC(12, 2);
BEGIN
    SELECT COALESCE(SUM(amount), 0)
    INTO v_total
    FROM milestones
    WHERE contract_id = p_contract_id
      AND status <> 'cancelled';

    RETURN v_total;
END;
$$ LANGUAGE plpgsql;

-- Функція для обчислення середнього рейтингу фрилансера
CREATE OR REPLACE FUNCTION fn_get_freelancer_rating(p_freelancer_id INT)
RETURNS NUMERIC(4, 2) AS $$
DECLARE
    v_rating NUMERIC(4, 2);
BEGIN
    SELECT ROUND(AVG(rating)::NUMERIC, 2)
    INTO v_rating
    FROM reviews
    WHERE reviewee_id = p_freelancer_id;

    RETURN COALESCE(v_rating, 0);
END;
$$ LANGUAGE plpgsql;

-- Функція-тригер для логування зміни статусу контракту
CREATE OR REPLACE FUNCTION log_contract_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF (OLD.status IS DISTINCT FROM NEW.status) THEN
        INSERT INTO contract_status_history (contract_id, status_from, status_to, changed_at, changed_by)
        VALUES (OLD.contract_id, OLD.status, NEW.status, NOW(), NEW.updated_by);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ===========================================
-- ЗБЕРЕЖЕНІ ПРОЦЕДУРИ
-- ===========================================

-- Процедура створення нового проекту
CREATE OR REPLACE PROCEDURE sp_create_project(
    IN p_client_id   INT,
    IN p_category_id INT,
    IN p_title       VARCHAR,
    IN p_description TEXT,
    IN p_budget_min  NUMERIC(12, 2),
    IN p_budget_max  NUMERIC(12, 2),
    IN p_created_by  INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO projects (
        client_id,
        category_id,
        title,
        description,
        budget_min,
        budget_max,
        status,
        is_deleted,
        created_at,
        created_by
    )
    VALUES (
        p_client_id,
        p_category_id,
        p_title,
        p_description,
        p_budget_min,
        p_budget_max,
        'open',
        FALSE,
        NOW(),
        p_created_by
    );
END;
$$;

-- Процедура м’якого видалення проекту (soft delete)
CREATE OR REPLACE PROCEDURE sp_soft_delete_project(
    IN p_project_id INT,
    IN p_user_id    INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE projects
    SET is_deleted = TRUE,
        status = CASE WHEN status = 'open' THEN 'cancelled' ELSE status END,
        updated_at = NOW(),
        updated_by = p_user_id
    WHERE project_id = p_project_id
      AND is_deleted = FALSE;
END;
$$;

-- Процедура відновлення проекту після soft delete
CREATE OR REPLACE PROCEDURE sp_restore_project(
    IN p_project_id INT,
    IN p_user_id    INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE projects
    SET is_deleted = FALSE,
        updated_at = NOW(),
        updated_by = p_user_id
    WHERE project_id = p_project_id
      AND is_deleted = TRUE;
END;
$$;

-- Процедура створення нового отклику (proposal) від фрилансера
CREATE OR REPLACE PROCEDURE sp_create_proposal(
    IN p_project_id    INT,
    IN p_freelancer_id INT,
    IN p_cover_letter  TEXT,
    IN p_bid_amount    NUMERIC(12, 2),
    IN p_created_by    INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Перевіряємо, що проект активний і не видалений
    IF NOT EXISTS (
        SELECT 1 FROM projects
        WHERE project_id = p_project_id
          AND is_deleted = FALSE
          AND status = 'open'
    ) THEN
        RAISE EXCEPTION 'Проект не існує, видалений або не відкритий для откликів';
    END IF;

    INSERT INTO proposals (
        project_id,
        freelancer_id,
        cover_letter,
        bid_amount,
        status,
        is_deleted,
        created_at,
        created_by
    )
    VALUES (
        p_project_id,
        p_freelancer_id,
        p_cover_letter,
        p_bid_amount,
        'pending',
        FALSE,
        NOW(),
        p_created_by
    );
END;
$$;

-- Процедура прийняття отклику:
-- 1) статус proposal -> accepted
-- 2) інші pending по цьому проекту -> rejected
-- 3) створення контракту між клієнтом і фрилансером
CREATE OR REPLACE PROCEDURE sp_accept_proposal(
    IN p_proposal_id INT,
    IN p_user_id     INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_project_id    INT;
    v_client_id     INT;
    v_freelancer_id INT;
    v_bid_amount    NUMERIC(12, 2);
BEGIN
    -- Отримуємо дані по отклику та проекту
    SELECT p.project_id,
           pr.client_id,
           p.freelancer_id,
           p.bid_amount
    INTO v_project_id, v_client_id, v_freelancer_id, v_bid_amount
    FROM proposals p
    JOIN projects pr ON p.project_id = pr.project_id
    WHERE p.proposal_id = p_proposal_id
      AND p.is_deleted = FALSE;

    IF v_project_id IS NULL THEN
        RAISE EXCEPTION 'Отклик не знайдено або він видалений';
    END IF;

    -- Приймаємо потрібний отклик
    UPDATE proposals
    SET status = 'accepted',
        updated_at = NOW(),
        updated_by = p_user_id
    WHERE proposal_id = p_proposal_id;

    -- Всі інші "pending" по цьому проекту відхиляємо
    UPDATE proposals
    SET status = 'rejected',
        updated_at = NOW(),
        updated_by = p_user_id
    WHERE project_id = v_project_id
      AND proposal_id <> p_proposal_id
      AND status = 'pending';

    -- Оновлюємо статус проекту
    UPDATE projects
    SET status = 'in_progress',
        updated_at = NOW(),
        updated_by = p_user_id
    WHERE project_id = v_project_id;

    -- Створюємо контракт на основі суми з отклику (як fixed_price)
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
        v_project_id,
        v_client_id,
        v_freelancer_id,
        CURRENT_DATE,
        'active',
        NULL,
        v_bid_amount,
        FALSE,
        NOW(),
        p_user_id
    );
END;
$$;

-- Процедура створення milestone для контракту
CREATE OR REPLACE PROCEDURE sp_create_milestone(
    IN p_contract_id INT,
    IN p_title       VARCHAR,
    IN p_description TEXT,
    IN p_due_date    DATE,
    IN p_amount      NUMERIC(12, 2),
    IN p_created_by  INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO milestones (
        contract_id,
        title,
        description,
        due_date,
        amount,
        status,
        created_at,
        created_by
    )
    VALUES (
        p_contract_id,
        p_title,
        p_description,
        p_due_date,
        p_amount,
        'pending',
        NOW(),
        p_created_by
    );
END;
$$;

-- Процедура оплати milestone:
-- 1) створюється інвойс (якщо треба, тут можна було б перевіряти існуючий)
-- 2) додається платіж
-- 3) оновлюється статус milestone
-- 4) якщо всі milestones оплачені -> контракт completed
CREATE OR REPLACE PROCEDURE sp_pay_milestone(
    IN p_milestone_id  INT,
    IN p_payer_id      INT,
    IN p_payment_method VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contract_id  INT;
    v_amount       NUMERIC(12, 2);
    v_receiver_id  INT;
    v_invoice_id   INT;
    v_all_paid     BOOLEAN;
BEGIN
    -- Отримуємо дані про milestone та контракт
    SELECT m.contract_id,
           m.amount,
           c.freelancer_id
    INTO v_contract_id, v_amount, v_receiver_id
    FROM milestones m
    JOIN contracts c ON m.contract_id = c.contract_id
    WHERE m.milestone_id = p_milestone_id;

    IF v_contract_id IS NULL THEN
        RAISE EXCEPTION 'Milestone не знайдено';
    END IF;

    -- Створюємо інвойс
    INSERT INTO invoices (
        contract_id,
        milestone_id,
        amount,
        issue_date,
        due_date,
        status,
        created_at,
        created_by
    )
    VALUES (
        v_contract_id,
        p_milestone_id,
        v_amount,
        CURRENT_DATE,
        CURRENT_DATE,
        'paid',
        NOW(),
        p_payer_id
    )
    RETURNING invoice_id INTO v_invoice_id;

    -- Створюємо платіж
    INSERT INTO payments (
        invoice_id,
        payer_id,
        receiver_id,
        amount,
        payment_method,
        payment_date,
        created_at
    )
    VALUES (
        v_invoice_id,
        p_payer_id,
        v_receiver_id,
        v_amount,
        p_payment_method,
        NOW(),
        NOW()
    );

    -- Оновлюємо статус milestone
    UPDATE milestones
    SET status = 'paid',
        updated_at = NOW(),
        updated_by = p_payer_id
    WHERE milestone_id = p_milestone_id;

    -- Перевіряємо, чи всі milestones по контракту оплачені або скасовані
    SELECT NOT EXISTS (
        SELECT 1
        FROM milestones
        WHERE contract_id = v_contract_id
          AND status NOT IN ('paid', 'cancelled')
    )
    INTO v_all_paid;

    IF v_all_paid THEN
        UPDATE contracts
        SET status = 'completed',
            end_date = CURRENT_DATE,
            updated_at = NOW(),
            updated_by = p_payer_id
        WHERE contract_id = v_contract_id;
    END IF;
END;
$$;

-- ===========================================
-- ТРИГЕРИ
-- ===========================================

-- Тригер логування історії статусів контракту
CREATE TRIGGER trg_log_contract_status
AFTER UPDATE ON contracts
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION log_contract_status_change();

-- ===========================================
-- ПРЕДСТАВЛЕННЯ (VIEW)
-- ===========================================

-- Представлення активних (відкритих) проектів
CREATE OR REPLACE VIEW v_open_projects AS
SELECT
    p.project_id,
    p.title,
    p.description,
    p.budget_min,
    p.budget_max,
    p.status,
    pc.name       AS category_name,
    u.user_id     AS client_id,
    u.full_name   AS client_name,
    u.email       AS client_email,
    p.created_at
FROM projects p
JOIN users u ON p.client_id = u.user_id
LEFT JOIN project_categories pc ON p.category_id = pc.category_id
WHERE p.is_deleted = FALSE
  AND p.status = 'open';

-- Представлення активних контрактів фрилансерів
CREATE OR REPLACE VIEW v_freelancer_active_contracts AS
SELECT
    c.contract_id,
    c.project_id,
    c.client_id,
    c.freelancer_id,
    c.status,
    c.start_date,
    c.end_date,
    fn_get_contract_total(c.contract_id) AS total_amount
FROM contracts c
WHERE c.is_deleted = FALSE
  AND c.status = 'active';

-- Деталізоване представлення контракту з проектом та рейтингом фрилансера
CREATE OR REPLACE VIEW v_contract_details AS
SELECT
    c.contract_id,
    c.project_id,
    c.client_id,
    c.freelancer_id,
    c.status,
    c.start_date,
    c.end_date,
    fn_get_contract_total(c.contract_id)    AS total_amount,
    p.title                                 AS project_title,
    p.description                           AS project_description,
    u_client.full_name                      AS client_name,
    u_freelancer.full_name                  AS freelancer_name,
    fn_get_freelancer_rating(c.freelancer_id) AS freelancer_rating
FROM contracts c
JOIN projects p          ON c.project_id = p.project_id
JOIN users u_client      ON c.client_id = u_client.user_id
JOIN users u_freelancer  ON c.freelancer_id = u_freelancer.user_id;
