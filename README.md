# FastAPI проект с JWT авторизацией с ролевой моделью и подтверждением регистрации по email

Этот проект представляет собой пример реализации авторизации на базе JSON Web Tokens (JWT) и подтверждения регистрации пользователя через электронную почту. Также были добавлены две роли - пользователь и администратор.

## Установка и запуск

Чтобы запустить приложение, выполните следующие шаги:

1. Клонируйте данный репозиторий:

```
$ git clone https://github.com/Petyall/fastapi-jwt-example.git
```

2. Перейдите в папку проекта:

```
$ cd fastapi-jwt-example
```

3. Установите зависимости:

```
$ pip install -r requirements.txt
```

4. Запустите приложение:

```
$ uvicorn main:app --reload
```

После этого вы можете перейти по адресу http://127.0.0.1:8000/ в браузере и начать работу с приложением.

## Описание API

API предоставляет следующие ресурсы:

### Регистрация пользователя

`POST /auth/register/`

Эндпоинт для создания нового пользователя.

Пример запроса:
```json
{
    "email": "test@example.com",
    "password": "password"
}
```

Пример ответа:
```json
{
    {"message":"Для подтверждения пользователя test@example.com было отправлено письмо с ссылкой для завершения регистрации"}
}
```

### Подтверждение регистрации

`GET /auth/confirm-email/`

Эндпоинт для подтверждения регистрации пользователя. Токен и почта пользователя передается в URL.

Пример запроса:
```
GET /auth/confirm-email?email=test@example.com&uuid=test-uuid-for-user
```

Пример ответа:
```json
{
    {"message":"Электронный адрес подтвержден."}
}
```

### Авторизация пользователя

`POST /auth/login/`

Эндпоинт для генерации JWT-токена.

Пример запроса:
```json
{
    "email": "test@example.com",
    "password": "password"
}
```

Пример ответа:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiaWF0IjoxNTE2MjM5MDIyfQ.lZxLw3QsZVv3tH5G0PKplbWJkX90F-10x6BbPKH_7Y",
    "token_type": "bearer"
}
```

### Защищенный ресурс

`GET /auth/all`

Защищенный эндпоинт к которому могут получить доступ только администраторы

Пример запроса:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjg3MDA1MjA4fQ.QEkRfGoHnUhwVI3xczP8OE8QkGkMX02pEU1W2z4zScM"
}
```

Пример ответа:
```json
{
  {
    "role_id": 2,
    "uuid": "e6acdcd1-e411-4441-9b73-2dbfc9e2b682",
    "confirmation_sent": "2023-06-19T10:15:06.802041",
    "id": 1,
    "email": "admin@example.com",
    "hashed_password": "$2b$12$l4m/Jlmda..UlIE5yIfTH.BQvoG5znyvdW/lXFvOcZQvfa.Tr2Eru",
    "is_confirmed": true,
    "confirmation_date": "2023-06-19T10:16:36.673315"
  },
  {
    "role_id": 1,
    "uuid": "9c33961e-c21c-4f29-bfe4-682a68f05016",
    "confirmation_sent": "2023-06-19T10:17:11.636720",
    "id": 2,
    "email": "test@example.com",
    "hashed_password": "$2b$12$26JiQ4fz1S8USV3.3Xtp5eWjLdDe.bA5WeKxXE8jIqLkqIkkzolUO",
    "is_confirmed": false,
    "confirmation_date": ""
  }
}
```

## Технологии

В проекте были использованы следующие технологии:

- [FastAPI](https://fastapi.tiangolo.com/) — современный веб-фреймворк для Python;
- [aiosqlite](https://github.com/omnilib/aiosqlite) — асинхронный SQLite-драйвер;