# Laboratory Work 3. Django REST Framework

## Вариант 2 — Библиотека

---

## Сведения о студенте

| Поле | Значение |
|------|----------|
| **ФИО** | Чан Тхи Лиен |
| **Группа** | K3340 |
| **Номер лабораторной** | 3 |
| **Вариант** | 2 — Библиотека |

---

## Цель работы

Овладеть практическими навыками реализации REST API средствами Django REST Framework:

- построение запросов Django ORM (фильтрация, `related_name`, агрегация, аннотация);
- сериализация данных и вложенные сериализаторы;
- представления на основе `APIView` и generic-классов;
- регистрация и авторизация по токенам средствами Djoser;
- документирование endpoint-ов средствами MkDocs.

---

## Задачи

1. Выполнить практическую работу 3.1 — запросы Django ORM на модели автовладельцев.
2. Выполнить практическую работу 3.2 — REST API для воинов на Django REST Framework.
3. Реализовать модель базы данных варианта 2 средствами Django ORM (PostgreSQL).
4. Реализовать логику API средствами DRF: CRUD, вложенные объекты, операции библиотекаря, аналитические запросы, отчёт.
5. Подключить регистрацию, авторизацию по токенам и вывод текущего пользователя (Djoser).
6. Описать endpoint-ы средствами MkDocs.

---

## Стек технологий

| Технология | Назначение |
|------------|------------|
| Python 3, Django | веб-фреймворк, ORM |
| Django REST Framework | сериализаторы, представления, REST API |
| Djoser | регистрация, токены, `/auth/users/me/` |
| PostgreSQL | СУБД основной работы (практики — SQLite) |
| MkDocs + Material | документация |

---

## Структура репозитория

```text
laboratory_work_3/
├── practice_3_1/
│   └── django_project_tran/     ← практика 3.1: запросы ORM (модель из практик 2.1–2.3)
├── warriors_project/            ← практика 3.2: DRF, воины
│   ├── warriors_project/        ← настройки
│   └── warriors_app/            ← models, serializers, views, urls
├── library_project/             ← основная работа, вариант 2 «Библиотека»
│   ├── library_project/         ← настройки (PostgreSQL, DRF, Djoser)
│   └── library_app/             ← models, serializers, services, views, urls
├── docs/                        ← документация MkDocs
├── mkdocs.yml
├── requirements.txt
└── README.md
```

## Содержание

- [Практическая работа 3.1](practice3_1.md) — запросы Django ORM
- [Практическая работа 3.2](practice3_2.md) — Django REST Framework
- Вариант 2 «Библиотека»:
    - [Описание](lab3/overview.md)
    - [Установка и запуск](lab3/setup.md)
    - [Модель данных](lab3/models.md)
    - [Авторизация (Djoser)](lab3/auth.md)
    - [CRUD](lab3/crud.md)
    - [Вложенные объекты](lab3/nested.md)
    - [Операции библиотекаря](lab3/operations.md)
    - [Аналитические запросы](lab3/analytics.md)
    - [Отчёт за месяц](lab3/report.md)
- [Вывод](conclusion.md)
