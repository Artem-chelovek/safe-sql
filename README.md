# Безопасный SQL Runner

## Требования

- ОС Linux с bash-терминалом
- Python 3.10+
- PostgreSQL (локально или доступ к удалённому серверу)

## Установка


### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Artem-chelovek/safe-sql
cd safe-sql
```
### 2. Установите Python и PostgreSQL

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip postgresql postgresql-contrib
```

Проверьте версию Python (нужна 3.10+):

```bash
python3 --version
```

### 3. Запустите PostgreSQL

Кластер БД создаётся автоматически при установке пакета, нужно только включить службу:

```bash
sudo systemctl enable --now postgresql
```

Проверьте, что служба запущена:

```bash
sudo systemctl status postgresql
```

### 4. Задайте пароль для пользователя БД и создайте базу данных

```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
sudo -u postgres createdb sql_runner_demo
```

Если получаете `password authentication failed`, откройте
`/etc/postgresql/*/main/pg_hba.conf`, проверьте строки `host ... 127.0.0.1/32 ...`
и перезапустите службу:

```bash
sudo systemctl restart postgresql
```

### 5. Создайте виртуальное окружение и установите зависимости

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Настройте подключение к базе данных

```bash
cp .env.example .env
```

Откройте `.env` и укажите параметры, соответствующие шагу 4:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sql_runner_demo
DB_USER=postgres
DB_PASSWORD=postgres
```

### 7. (Опционально) Создайте тестовую таблицу с данными

```bash
PGPASSWORD=postgres psql -h localhost -U postgres -d sql_runner_demo -c "
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    age INT
);
INSERT INTO students (name, age) VALUES
    ('Иван', 20), ('Мария', 22), ('Пётр', 19),
    ('Анна', 21), ('Олег', 23), ('Света', 20);
"
```

## Запуск

```bash
python main.py
```

Скрипт спросит:

```
Введите SQL-запрос:
```

### Примеры

**Обычный SELECT (LIMIT добавится автоматически):**

```
Введите SQL-запрос: SELECT * FROM students
```

Выполнится как `SELECT * FROM students LIMIT 5`, результат выводится таблицей в консоли.

**SELECT со своим LIMIT (не меняется):**

```
Введите SQL-запрос: SELECT * FROM students LIMIT 20
```

**Запрещённый запрос:**

```
Введите SQL-запрос: DELETE FROM students
```

Вывод:

```
Ошибка: разрешены только SELECT-запросы
```

Также блокируются `INSERT`, `UPDATE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`,
несколько запросов через `;` и другие изменяющие операции.

Запрос можно передать и сразу аргументом командной строки:

```bash
python main.py "SELECT * FROM students"
```

## Обработка ошибок

Скрипт не падает с трассировкой (traceback) и корректно обрабатывает:

- отсутствие/неверные данные подключения в `.env`;
- недоступность базы данных;
- синтаксические ошибки в SQL;
- запрещённые операторы;
- пустой запрос.

## Структура проекта

```
.
├── main.py            # основной скрипт
├── requirements.txt    # зависимости
├── .env.example         # шаблон переменных окружения
└── README.md
```

## Как это работает (кратко)

1. Запрос очищается от пробелов и завершающей `;`.
2. Проверяется, что это ровно один оператор и он начинается с `SELECT`
   (плюс дополнительная проверка на отсутствие ключевых слов вроде
   `DELETE`, `DROP`, `INSERT` и т.д.).
3. Если в запросе нет `LIMIT`, добавляется `LIMIT 5`.
4. Запрос выполняется через `psycopg2`, результат печатается таблицей
   (через `tabulate`).
