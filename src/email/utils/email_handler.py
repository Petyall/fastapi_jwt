import socket

from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
from aiosmtplib import SMTP, SMTPAuthenticationError, SMTPConnectError, SMTPException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings
from src.logs.logger import logger


class EmailHandler:
    """
    Класс для обработки отправки email-сообщений и рендеринга шаблонов.

    Использует aiosmtplib для асинхронной отправки email и Jinja2 для рендеринга HTML-шаблонов.
    """

    def __init__(
        self,
        smtp_host: str = settings.SMTP_HOST,
        smtp_port: int = settings.SMTP_PORT,
        smtp_username: str = settings.SMTP_USERNAME,
        smtp_password: str = settings.SMTP_PASSWORD,
        email_from: str = settings.EMAIL_FROM,
        template_path: str = settings.EMAIL_TEMPLATES,
    ) -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.email_from = email_from
        self.env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape(["html", "xml"])
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((SMTPException, socket.gaierror, TimeoutError, ConnectionRefusedError)),
        reraise=True
    )
    async def send_email(self, to: str, subject: str, html_content: str) -> None:
        """
        Асинхронно отправляет email-сообщение с использованием SMTP.
        Использует механизм повторов (tenacity) для обработки сетевых ошибок с экспоненциальной задержкой.

        Args:
            to: Адрес получателя.
            subject: Тема письма.
            html_content: HTML-содержимое письма.

        Raises:
            SMTPAuthenticationError: Ошибка авторизации на SMTP-сервере.
            SMTPConnectError: Ошибка подключения к SMTP-серверу.
            SMTPException: Общая ошибка SMTP-протокола.
            socket.gaierror: Ошибка разрешения имени хоста.
            ConnectionRefusedError: Сервер отклонил подключение.
            TimeoutError: Превышено время ожидания подключения.
            Exception: Необработанная ошибка при отправке.
        """
        msg = MIMEText(html_content, "html")
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = to

        try:
            smtp = SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                timeout=10,
                start_tls=True
            )
            await smtp.connect()
            await smtp.login(self.smtp_username, self.smtp_password)
            await smtp.send_message(msg)
            await smtp.quit()
        except SMTPAuthenticationError as e:
            logger.error(f"[SMTP] Ошибка авторизации при отправке на {to}: {type(e).__name__}: {e}")
            raise
        except SMTPConnectError as e:
            logger.error(f"[SMTP] Не удалось подключиться к серверу при отправке на {to}: {type(e).__name__}: {e}")
            raise
        except SMTPException as e:
            logger.error(f"[SMTP] Общая SMTP ошибка при отправке на {to}: {type(e).__name__}: {e}")
            raise
        except (socket.gaierror, ConnectionRefusedError, TimeoutError) as e:
            logger.error(f"[SMTP] Сетевая ошибка при отправке на {to}: {type(e).__name__}: {e}")
            raise
        except Exception as e:
            logger.exception(f"[SMTP] Неизвестная ошибка при отправке на {to}: {type(e).__name__}: {e}")
            raise

    def render_template(self, template_name: str, context: dict) -> str:
        """
        Рендерит HTML-шаблон с использованием Jinja2.

        Args:
            template_name: Имя файла шаблона (относительно директории EMAIL_TEMPLATES).
            context: Словарь с данными для подстановки в шаблон.

        Returns:
            Отрендеренный HTML-контент шаблона.
        """
        template = self.env.get_template(template_name)
        return template.render(**context)


email_handler = EmailHandler()
