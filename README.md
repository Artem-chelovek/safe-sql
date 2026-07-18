# Безопасный SQL Runner

Простой CLI-инструмент на Python для безопасного выполнения read-only
запросов к PostgreSQL. Разрешает выполнять только `SELECT`-запросы и
автоматически ограничивает выборку `LIMIT 5`, если лимит не указан явно.

## Возможности

- Подключение к PostgreSQL через параметры из `.env`
- Проверка, что запрос — это **только SELECT** (остальные запросы блокируются)
- Автоматическое добавление `LIMIT 5`, если лимит не задан
- Вывод результата в консоль в виде таблицы
- Обработка ошибок подключения, конфигурации и выполнения запроса

## Требования

- Python 3.10+
- Доступный сервер PostgreSQL

## (ОПЦИОНАЛЬНО) Установка PostgreSQL

Если PostgreSQL ещё не установлен локально, ниже — быстрая установка
для основных дистрибутивов. Если сервер уже есть (локально, в Docker
или на удалённом хосте) — этот шаг можно пропустить и перейти сразу
к «Установка скрипта».

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib

sudo systemctl enable --now postgresql
sudo systemctl status postgresql   # должно быть active (running)
```

### Arch Linux

```bash
sudo pacman -S --needed postgresql

# инициализация кластера БД (только при первой установке)
sudo -iu postgres initdb -D /var/lib/postgres/data

sudo systemctl enable --now postgresql
sudo systemctl status postgresql
```

### (ОПЦИОНАЛЬНО) Создание базы данных и пользователя

После установки PostgreSQL по умолчанию создаётся системный пользователь
`postgres` без пароля для входа по паролю. Задайте пароль и создайте базу,
которую будет использовать скрипт (значения ниже соответствуют
`.env.example`):

```bash
sudo -u postgres psql
```

Внутри `psql`:

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    age INT
);
INSERT INTO students (name, age) VALUES
    ('Иван', 20), ('Мария', 22), ('Пётр', 19),
    ('Анна', 21), ('Олег', 23), ('Света', 20);
\q
```




## Установка скрипта

```bash
git clone https://github.com/Artem-chelovek/safe-sql
cd safe-sql

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## Настройка подключения

Скопируйте пример конфигурации и укажите свои данные для подключения к БД:

```bash
cp .env.example .env
```

Содержимое `.env`:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=postgres
DB_PASSWORD=postgres
```

## Запуск

```bash
python main.py
```

Программа попросит ввести SQL-запрос:

```
Введите SQL-запрос:
```

### Пример 1 — обычный SELECT

```
Введите SQL-запрос: SELECT * FROM students
```

Так как `LIMIT` не указан, он будет добавлен автоматически (`LIMIT 5`),
и в консоль будет выведена таблица с результатом.

### Пример 2 — запрос с уже заданным LIMIT

```
Введите SQL-запрос: SELECT * FROM students LIMIT 20
```

Лимит не изменяется, если он уже указан в запросе.

### Пример 3 — запрещённый запрос

```
Введите SQL-запрос: DELETE FROM students
```

Вывод:

```
Ошибка: разрешены только SELECT-запросы
```

Аналогично блокируются `INSERT`, `UPDATE`, `DROP`, `ALTER`, `TRUNCATE`
и другие изменяющие операции, а также попытки выполнить несколько
запросов через `;`.

## Структура проекта

```
.
├── main.py            # основной скрипт
├── requirements.txt   # зависимости
├── .env.example        # пример конфигурации подключения
└── README.md
```
