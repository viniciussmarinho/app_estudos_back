import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from jinja2 import Template
from ..config import settings

class EmailService:
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name

    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: str = None
    ) -> bool:
        """Envia email"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Text part
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)

            # HTML part
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password,
            )
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    async def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        """Envia email de reset de senha"""
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
        
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Reset de Senha - StudyApp</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #3B82F6;">Olá, {{ user_name }}!</h2>
                <p>Você solicitou a redefinição da sua senha no StudyApp.</p>
                <p>Clique no botão abaixo para criar uma nova senha:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{{ reset_url }}" style="background-color: #3B82F6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Redefinir Senha
                    </a>
                </div>
                <p><strong>Atenção:</strong> Este link expira em 30 minutos.</p>
                <p>Se você não solicitou esta redefinição, ignore este email.</p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #666;">
                    StudyApp - Sistema de Organização de Estudos
                </p>
            </div>
        </body>
        </html>
        """)
        
        html_content = html_template.render(
            user_name=user_name,
            reset_url=reset_url
        )
        
        text_content = f"""
        Olá, {user_name}!
        
        Você solicitou a redefinição da sua senha no StudyApp.
        
        Acesse o link abaixo para criar uma nova senha:
        {reset_url}
        
        Atenção: Este link expira em 30 minutos.
        
        Se você não solicitou esta redefinição, ignore este email.
        
        StudyApp - Sistema de Organização de Estudos
        """
        
        return await self.send_email(
            to_email=to_email,
            subject="Reset de Senha - StudyApp",
            html_content=html_content,
            text_content=text_content
        )

    async def send_reminder_email(
        self, 
        to_email: str, 
        user_name: str, 
        event_title: str, 
        event_date: str, 
        event_type: str,
        days_until: int
    ) -> bool:
        """Envia email de lembrete de evento"""
        subject = f"Lembrete: {event_title}"
        
        if days_until == 0:
            time_text = "hoje"
        elif days_until == 1:
            time_text = "amanhã"
        else:
            time_text = f"em {days_until} dias"
        
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Lembrete - StudyApp</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #3B82F6;">Olá, {{ user_name }}!</h2>
                <p>Este é um lembrete sobre o seu compromisso:</p>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1f2937;">{{ event_title }}</h3>
                    <p style="margin: 5px 0;"><strong>Tipo:</strong> {{ event_type }}</p>
                    <p style="margin: 5px 0;"><strong>Data:</strong> {{ event_date }}</p>
                    <p style="margin: 5px 0;"><strong>Acontece:</strong> {{ time_text }}</p>
                </div>
                <p>Não se esqueça de se preparar!</p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #666;">
                    StudyApp - Sistema de Organização de Estudos
                </p>
            </div>
        </body>
        </html>
        """)
        
        html_content = html_template.render(
            user_name=user_name,
            event_title=event_title,
            event_type=event_type,
            event_date=event_date,
            time_text=time_text
        )
        
        text_content = f"""
        Olá, {user_name}!
        
        Este é um lembrete sobre o seu compromisso:
        
        {event_title}
        Tipo: {event_type}
        Data: {event_date}
        Acontece: {time_text}
        
        Não se esqueça de se preparar!
        
        StudyApp - Sistema de Organização de Estudos
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

email_service = EmailService()