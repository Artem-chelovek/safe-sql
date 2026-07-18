#!/usr/bin/env python3
import os
import re
import sys

from dotenv import load_dotenv

try:
    import psycopg2
    import psycopg2.errors
except ImportError:
    print(
        "Ошибка: не установлен пакет psycopg2-binary. "
        "Выполните: pip install -r requirements.txt"
    )
    sys.exit(1)

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None


FORBIDDEN_KEYWORDS = (
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "EXECUTE", "CALL", "COPY",
    "MERGE", "REPLACE", "VACUUM", "COMMENT", "LOCK",
)

SELECT_PATTERN = re.compile(r"^\s*SELECT\b", re.IGNORECASE)
LIMIT_PATTERN = re.compile(r"\bLIMIT\b", re.IGNORECASE)


def strip_query(raw_query):
    query = raw_query.strip()
    query = query.rstrip(";").strip()
    return query

def validate_select_only(query):
    if not query:
        raise ValueError("Ошибка: пустой запрос")
    if ";" in query:
        raise ValueError("Ошибка: разрешён только один запрос за раз")
    if not SELECT_PATTERN.match(query):
        raise ValueError("Ошибка: разрешены только SELECT-запросы")
    upper_query = query.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_query):
            raise ValueError("Ошибка: разрешены только SELECT-запросы")
            


def ensure_limit(query):
    if LIMIT_PATTERN.search(query):
        return query
    return f"{query} LIMIT 5"


def get_connection_params():
    load_dotenv()
    params = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }
    missing = [key for key in ("dbname", "user") if not params[key]]
    if missing:
        raise RuntimeError(
            "Ошибка: не заданы обязательные переменные окружения "
            f"({', '.join(missing)}). Скопируйте .env.example в .env "
            "и укажите параметры подключения."
        )
    return params


def run_query(conn, query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
    return columns, rows


def print_results(columns, rows):
    if not rows:
        print("Запрос выполнен успешно. Строк не найдено.")
        return
    if tabulate is not None:
        print(tabulate(rows, headers=columns, tablefmt="psql"))
    else:
        print(" | ".join(columns))
        print("-" * (len(columns) * 12))
        for row in rows:
            print(" | ".join(str(value) for value in row))
    print(f"\nВсего строк: {len(rows)}")


def read_query():
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    return input("Введите SQL-запрос: ")

raw_query = read_query()
query = strip_query(raw_query)
try:
    validate_select_only(query)
except ValueError as exc:
    print(exc)
safe_query = ensure_limit(query)

try:
    params = get_connection_params()
except RuntimeError as exc:
    print(exc)

conn = None
try:
    conn = psycopg2.connect(**params)
except psycopg2.OperationalError as exc:
    print(f"Ошибка подключения к базе данных: {str(exc).strip()}")


try:
    columns, rows = run_query(conn, safe_query)
    print_results(columns, rows)
except psycopg2.errors.SyntaxError as exc:
    print(f"Ошибка синтаксиса SQL: {str(exc).strip()}")
except psycopg2.Error as exc:
    print(f"Ошибка выполнения запроса: {str(exc).strip()}")
except Exception as exc:
    print(f"Непредвиденная ошибка: {exc}")
finally:
    conn.close()

