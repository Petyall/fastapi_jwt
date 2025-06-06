from fastapi import APIRouter, Query, Depends
from src.auth.services import UserRequests
from datetime import datetime, timedelta
from src.config import settings
from pydantic import EmailStr
from uuid import uuid4, UUID
from src.email.email_handler import email_templates, email_handler
from src.models import User
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/email", tags=["Модуль работы с email"])


@router.get("/confirm")
async def confirm_email(email: EmailStr = Query(...), token: UUID = Query(...)):
    user = await UserRequests.find_one_or_none(email=email, confirmation_token=str(token))
    if not user:
        return {"error": "Пользователь не найден"}
    if user.email_confirmed:
        return {"error": "Пользователь уже подтвержден"}
    created_at = user.confirmation_token_created_at
    if not created_at or datetime.now() - created_at > timedelta(hours=settings.EMAIL_CONFIRM_TOKEN_EXPIRE):
        return {"error": "Срок действия ссылки истёк"}
    success = await UserRequests.update(
        id=user.id,
        email_confirmed=True,
        email_confirmed_at=datetime.now(),
        confirmation_token=None,
        confirmation_token_created_at=None
    )
    if success:
        return {"message": "Email успешно подтверждён"}
    return {"error": "Неверный или просроченный токен"}


@router.post("/resend")
async def resend_confirmation(current_user: User = Depends(get_current_user)):
    user = await UserRequests.find_one_or_none(email=current_user.email)

    if not user:
        return {"error": "Пользователь не найден"}
    if user.email_confirmed:
        return {"error": "Почта уже подтверждена"}
    created_at = user.confirmation_token_created_at
    if datetime.now() - created_at < timedelta(hours=settings.EMAIL_CONFIRM_TOKEN_EXPIRE):
        return {"error": "Ссылка с подтверждением уже была отправлена на вашу почту!"}

    new_token = str(uuid4())
    created_at = datetime.now()

    await UserRequests.update(
        id=user.id,
        confirmation_token=new_token,
        confirmation_token_created_at=created_at
    )

    try:
        template = email_templates.get_template("confirm_email.html")
        link = f"{settings.FRONTEND_URL}/email/confirm?email={user.email}&token={new_token}"
        html_content = template.render(confirmation_link=link)

        await email_handler.send_email(
            to=user.email,
            subject="Подтверждение регистрации",
            html_content=html_content,
        )
    except Exception as e:
        return {"error": f"Ошибка отправки письма: {str(e)}"}

    return {"message": "Письмо с подтверждением отправлено повторно (действует в течение 72 часов)"}