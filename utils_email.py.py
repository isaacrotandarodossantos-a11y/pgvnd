import os
import smtplib
from email.message import EmailMessage

def enviar_email_confirmacao(cliente_email, nome_cliente):
    # Link do que você quer entregar (PDF, Drive ou Grupo de WhatsApp)
    LINK_DO_PRODUTO = "wa.me/5582991382121"
    
    msg = EmailMessage()
    msg['Subject'] = "Inscrição Confirmada - São Jorge Para Todos"
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = cliente_email
    
    # Texto do e-mail
    corpo_email = f"""
    Olá, {nome_cliente}!

    Sua inscrição para o evento "São Jorge Para Todos" foi confirmada com sucesso!

    Você pode acessar os detalhes e seu material através do link abaixo:
    {LINK_DO_PRODUTO}

    Nos vemos no evento!
    Equipe São Jorge Para Todos.
    """
    
    msg.set_content(corpo_email)

    # Conexão e envio
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            server.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")