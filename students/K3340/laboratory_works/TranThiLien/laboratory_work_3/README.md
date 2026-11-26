# Laboratory Work 3 — Чан Тхи Лиен, K3340

| Thư mục | Bài | CSDL |
| --- | --- | --- |
| `practice_3_1/django_project_tran/` | Thực hành 3.1: truy vấn Django ORM (project chủ xe của bài 2.1–2.3) | SQLite |
| `warriors_project/` | Thực hành 3.2: Django REST Framework | SQLite |
| `library_project/` | ЛР3 chính, variant 2 «Библиотека» | PostgreSQL |
| `docs/`, `mkdocs.yml` | Báo cáo MkDocs (tiếng Nga) cho cả 3 phần | — |

## 0. Môi trường (một lần)

```powershell
cd laboratory_work_3
python -m venv venv
venv\Scripts\activate            # PowerShell lỗi thì chạy trước: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
pip install -r requirements.txt
```

## 1. Thực hành 3.1

```powershell
cd practice_3_1\django_project_tran
python manage.py migrate
python manage.py seed_practice2
python manage.py practice31_task1      # tạo dữ liệu (chỉ chạy 1 lần)
python manage.py practice31_task2      # lọc
python manage.py practice31_task3      # tổng hợp
cd ..\..
```

Kết quả chạy so với `docs/practice3_1.md`. Làm lại từ đầu thì xoá `db.sqlite3` rồi chạy lại.

## 2. Thực hành 3.2

```powershell
cd warriors_project
python manage.py migrate
python manage.py runserver
```

Mở http://127.0.0.1:8000/war/skills/ và các URL trong `docs/practice3_2.md`. Thứ tự nhập dữ liệu (dùng form ở cuối trang DRF):

1. POST `/war/profession/create/` → `{"profession": {"title": "Backend", "description": "..."}}`
2. POST `/war/skill/create/` → `{"skill": {"title": "Python"}}`
3. POST `/war/warriors/create/` → `{"name": "Дмитрий", "race": "d", "level": 66, "profession": 1}`
4. POST `/war/skill_of_warrior/create/` → `{"warrior": 1, "skill": 1, "level": 20}`
5. GET `/war/warriors/professions/`, `/war/warriors/skills/`, `/war/warriors/1/`

Dừng server bằng `Ctrl+C`, rồi `cd ..`.

## 3. ЛР3: variant 2 «Библиотека»

Tạo database trong pgAdmin: `CREATE DATABASE library_db;`

```powershell
cd library_project
copy .env.example .env               # sửa DB_USER / DB_PASSWORD trong .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_library
python manage.py runserver
```

- Đăng ký: POST http://127.0.0.1:8000/auth/users/ `{"username": "librarian", "password": "Lib_pass_2026"}`
- Lấy token: POST http://127.0.0.1:8000/auth/token/login/ (cùng body)
- Gọi API kèm header `Authorization: Token <token>`, ví dụ GET http://127.0.0.1:8000/api/analytics/education/
- Trên trình duyệt: đăng nhập ở http://127.0.0.1:8000/api-auth/login/ rồi mở các URL `/api/...`

Muốn thử nhanh khi chưa có PostgreSQL: thêm dòng `USE_SQLITE=1` vào `.env`.

## 4. Báo cáo MkDocs

Chạy từ thư mục `laboratory_work_3`:

```powershell
mkdocs serve -a 127.0.0.1:8001       # xem ở http://127.0.0.1:8001
```

## 5. Đẩy lên git (nhánh lab3)

```powershell
git checkout -b lab3                 # nếu nhánh đã có: git checkout lab3
git add .
git status                           # không được có venv/, db.sqlite3, .env, site/
git commit -m "ЛР3: вариант 2 «Библиотека», практики 3.1 и 3.2"
git push -u origin lab3
```
