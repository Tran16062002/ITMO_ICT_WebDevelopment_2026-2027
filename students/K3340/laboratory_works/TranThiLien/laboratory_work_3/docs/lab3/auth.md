# Авторизация (Djoser)

| Метод | URL | Назначение |
| --- | --- | --- |
| POST | `/auth/users/` | регистрация пользователя (библиотекаря) |
| POST | `/auth/token/login/` | получение токена |
| POST | `/auth/token/logout/` | удаление токена (выход) |
| GET | `/auth/users/me/` | информация о текущем пользователе |

## Регистрация

```http
POST /auth/users/
Content-Type: application/json

{"username": "librarian", "password": "Lib_pass_2026"}
```

Ответ `201`:

```json
{"email": "", "username": "librarian", "id": 2}
```

## Получение токена

```http
POST /auth/token/login/
Content-Type: application/json

{"username": "librarian", "password": "Lib_pass_2026"}
```

Ответ `200`:

```json
{"auth_token": "db9b48ef7f87900bb3e61793f0f4d05621b09cd2"}
```

Дальше токен передаётся в каждом запросе:

```http
Authorization: Token db9b48ef7f87900bb3e61793f0f4d05621b09cd2
```

## Текущий пользователь

```http
GET /auth/users/me/
Authorization: Token <токен>
```

```json
{"email": "", "id": 2, "username": "librarian"}
```

## Выход

```http
POST /auth/token/logout/
Authorization: Token <токен>
```

Ответ `204`, токен больше не действует.
