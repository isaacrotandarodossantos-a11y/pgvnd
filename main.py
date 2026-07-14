import os
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apimercadopago import gerar_link_pagamento
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4

# Configura o Flask para buscar os HTMLs na raiz
app = Flask(__name__, template_folder='.')
CORS(app) 

# --- FUNÇÃO QUE CRIA O PDF E ENVIA O E-MAIL AUTOMATICAMENTE ---
def enviar_email_com_certificado(cliente_email, nome_cliente):
    nome_seguro = nome_cliente.replace(' ', '_')
    caminho_pdf = f"Certificado_{nome_seguro}.pdf"
    
    # 1. Criação do PDF
    c = canvas.Canvas(caminho_pdf, pagesize=landscape(A4))
    
    # Borda decorativa
    c.setStrokeColorRGB(0.2, 0.4, 0.6)
    c.rect(20, 20, 802, 555, stroke=1, fill=0)
    
    # Textos do certificado
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(421, 450, "CERTIFICADO DE INSCRIÇÃO")
    
    c.setFont("Helvetica", 20)
    c.drawCentredString(421, 350, "Certificamos que o(a) atleta")
    
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(421, 290, nome_cliente)
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(421, 220, "confirmou sua vaga com sucesso no evento:")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(421, 180, "SÃO JORGE PARA TODOS")
    
    c.save()

    # 2. Configuração e Envio do E-mail
    msg = EmailMessage()
    msg['Subject'] = f"Seu Certificado - São Jorge Para Todos"
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = cliente_email
    
    # Corpo do e-mail em HTML (mais bonito)
    msg.set_content(f"Olá, {nome_cliente}!\n\nSua inscrição para o evento São Jorge Para Todos foi confirmada com sucesso!\n\nSegue em anexo o seu certificado oficial de inscrição.\n\nNos vemos lá!")

    # Anexa o arquivo PDF gerado
    with open(caminho_pdf, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=f"Certificado_Inscricao.pdf")

    # Envia de fato usando as credenciais que você colocou no Render
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.send_message(msg)
    
    # Remove o arquivo temporário do servidor para não acumular lixo no Render
    if os.path.exists(caminho_pdf):
        os.remove(caminho_pdf)


# --- ROTAS DO FLASK ---

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    # Pega os dados enviados pelo seu index.html
    dados = request.get_json() or {}
    nome = dados.get("nome", "Participante")
    email = dados.get("email")

    # Geramos o link de pagamento passando os dados do cliente
    # (Assim o Mercado Pago consegue nos devolver esses dados na volta)
    link = gerar_link_pagamento(nome=nome, email=email)
    
    if link:
        return jsonify({"link": link})
    return jsonify({"error": "Erro ao gerar link"}), 500

@app.route("/compracerta")
def compra_certa():
    # Quando o Mercado Pago traz o cliente de volta, capturamos os dados da URL
    nome = request.args.get('nome', 'Participante')
    email = request.args.get('email')

    # Se tivermos o e-mail, envia o certificado de forma 100% automática
    if email:
        try:
            enviar_email_com_certificado(email, nome)
        except Exception as e:
            print(f"Erro ao enviar e-mail automático: {e}")

    return render_template("compracerta.html")

@app.route("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
