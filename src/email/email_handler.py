import smtplib
from src.config import settings
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

email_templates = Environment(loader=FileSystemLoader("./src/email/templates"))

class EmailHandler():

    async def send_email(self, to: str, subject: str, html_content: str) -> None:
        msg = MIMEText(html_content, "html")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, [to], msg.as_string())


email_handler = EmailHandler()
