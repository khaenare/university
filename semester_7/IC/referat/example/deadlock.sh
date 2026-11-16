#!/bin/sh
# Створює взаємне блокування (deadlock): дві транзакції блокують ті самі
# рядки в протилежному порядку. PostgreSQL перериває одну з них через ~1 с.
set -e
cd "$(dirname "$0")"
psql() { docker compose exec -T postgres psql -U demo -d demo -v ON_ERROR_STOP=0 "$@"; }

psql -q -c "CREATE TABLE IF NOT EXISTS accounts (id int PRIMARY KEY, balance int);
            INSERT INTO accounts VALUES (1, 100), (2, 100) ON CONFLICT DO NOTHING;"

# Транзакція A: рядок 1, потім рядок 2
psql -c "BEGIN; UPDATE accounts SET balance = balance - 10 WHERE id = 1;
         SELECT pg_sleep(2); UPDATE accounts SET balance = balance + 10 WHERE id = 2; COMMIT;" &
# Транзакція B: рядок 2, потім рядок 1
psql -c "BEGIN; UPDATE accounts SET balance = balance - 10 WHERE id = 2;
         SELECT pg_sleep(2); UPDATE accounts SET balance = balance + 10 WHERE id = 1; COMMIT;" &
wait
