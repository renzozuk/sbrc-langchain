import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from langchain.tools import tool


@tool
def send_email(origin_address: str, origin_password: str, destiny_address: str, subject: str, content: str,
               smtp_server: str = "smtp.gmail.com", smtp_port: int = 587) -> None:
    """Envia e-mail."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = origin_address
    msg['To'] = destiny_address

    html_content = MIMEText(content, 'html', 'utf-8')
    msg.attach(html_content)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(origin_address, origin_password)
            server.send_message(msg)
        print("Email enviado com sucesso!")
    except Exception as e:
        print(f"Erro: {e}")
        raise
