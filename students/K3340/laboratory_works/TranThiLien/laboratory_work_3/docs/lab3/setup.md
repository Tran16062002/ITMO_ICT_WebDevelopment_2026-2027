# Установка и запуск

## 1. Окружение

```bash
cd laboratory_work_3
python -m venv venv
# Windows (cmd): venv\Scripts\activate.bat   PowerShell: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd library_project
```

## 2. База данных PostgreSQL

Создайте базу данных (через pgAdmin или psql):

```sql
CREATE DATABASE library_db;
```

Скопируйте `library_project/.env.example` в `library_project/.env` и укажите имя пользователя и пароль PostgreSQL.

## 3. Миграции, суперпользователь, демо-данные

```bash
python manage.py makemigrations library_app
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_library          # демонстрационные данные
```

## 4. Запуск

```bash
python manage.py runserver
```

- API: <http://127.0.0.1:8000/api/>
- Админ-панель: <http://127.0.0.1:8000/admin/>
- Вход в браузерный интерфейс DRF: <http://127.0.0.1:8000/api-auth/login/>

## 5. Документация

Команды выполняются из папки `laboratory_work_3` (там лежит `mkdocs.yml`).
Порт 8000 занят Django, поэтому документацию запускаем на 8001:

```bash
mkdocs serve -a 127.0.0.1:8001     # просмотр: http://127.0.0.1:8001
mkdocs build                       # статический сайт в папке site/
```
