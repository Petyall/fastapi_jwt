import smtplib
import socket

from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

from src.config import settings
from src.logs.logger import logger


email_templates = Environment(loader=FileSystemLoader(settings.EMAIL_TEMPLATES))

class EmailHandler:

    async def send_email(self, to: str, subject: str, html_content: str) -> None:
        msg = MIMEText(html_content, "html")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAIL_FROM, [to], msg.as_string())
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"[SMTP] Ошибка авторизации при отправке на {to}: {type(e).__name__}: {e}")
        except smtplib.SMTPConnectError as e:
            logger.error(f"[SMTP] Не удалось подключиться к серверу при отправке на {to}: {type(e).__name__}: {e}")
        except smtplib.SMTPException as e:
            logger.error(f"[SMTP] Общая SMTP ошибка при отправке на {to}: {type(e).__name__}: {e}")
        except (socket.gaierror, ConnectionRefusedError, TimeoutError) as e:
            logger.error(f"[SMTP] Сетевая ошибка при отправке на {to}: {type(e).__name__}: {e}")
        except Exception as e:
            logger.exception(f"[SMTP] Неизвестная ошибка при отправке на {to}: {type(e).__name__}: {e}")

email_handler = EmailHandler()
