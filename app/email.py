from smtplib import SMTP_SSL
from pydantic import EmailStr
from email.message import EmailMessage

from app.config import settings
from app.users.dependencies import get_uuid


async def create_email_confirmation_template(email_to: EmailStr):
    # Получение UUID пользователя
    uuid = await get_uuid(email_to)
    # Создание экземпляра письма
    email = EmailMessage()
    # Заголовок письма
    email["Subject"] = "Здравствуйте! Подтвердите, пожалуйста, Вашу регистрацию."
    # Адрес отправителя
    email["From"] = settings.SMTP_USER
    # Адрес получателя
    email["To"] = email_to
    # Ссылка для подтверждения
    confirm_link = f"{settings.APP_ORIGIN}auth/confirm-email?email={email_to}&uuid={uuid}"
    # Текст письма
    email.set_content(
        f"""
        <h1>Подтверждение почты</h1>
        Здравствуйте! Перейдите, пожалуйста, по ссылке, чтобы завершить Вашу регистрацию.
        {confirm_link}
        """,
        subtype="html",
    )
    return email

async def send_email_confirmation_email(email_to: EmailStr):
    # Переменная с адресом отправителя
    # email_to_mock = settings.SMTP_USER # ЗАМЕНИТЬ НА ПОЛЬЗОВАТЕЛЬСКИЙ EMAIL
    email_to_mock = email_to
    # Переменная вызывающая текст для отправки письма
    msg_content = await create_email_confirmation_template(email_to_mock)

    with SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        # Авторизация в почтовом сервере
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        # Отправка письма
        server.send_message(msg_content)
