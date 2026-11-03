#!/bin/sh
# Ролі з мінімальними правами (паролі — з .env, тому скрипт, а не SQL):
#   exporter — лише читання статистики для postgres-exporter;
#   shop_app — лише робота з даними магазину (генератор навантаження).
# Таймаути exporter не дають запитам моніторингу накопичуватися, коли таблицю заблоковано.
set -e
psql -v ON_ERROR_STOP=1 -v exporter_pw="$EXPORTER_PASSWORD" -v app_pw="$APP_DB_PASSWORD" \
     --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
CREATE USER exporter WITH PASSWORD :'exporter_pw';
GRANT pg_monitor TO exporter;
ALTER ROLE exporter SET lock_timeout = '1s';
ALTER ROLE exporter SET statement_timeout = '4s';

CREATE USER shop_app WITH PASSWORD :'app_pw';
GRANT SELECT, INSERT, UPDATE, DELETE ON customers, products, orders TO shop_app;
GRANT USAGE ON SEQUENCE customers_id_seq, orders_id_seq TO shop_app;
SQL
