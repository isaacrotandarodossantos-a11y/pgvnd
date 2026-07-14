import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apimercadopago import gerar_link_pagamento
from utils_email import enviar_email_confirmacao # Importa a função que criamos

app = Flask(__name__, template_folder='.')
CORS(app) 

# --- ROTAS DO FLASK ---

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    dados = request.get_json() or {}
    nome = dados.get("nome", "Participante")
    email = dados.get("email")

    link = gerar_link_pagamento(nome=nome, email=email)
    
    if link:
        return jsonify({"link": link})
    return jsonify({"error": "Erro ao gerar link"}), 500

@app.route("/compracerta")
def compra_certa():
    # Captura os dados da URL
    nome = request.args.get('nome', 'Participante')
    email = request.args.get('email')

    # Dispara o envio do link de confirmação automaticamente
    if email:
        try:
            enviar_email_confirmacao(email, nome)
        except Exception as e:
            print(f"Erro ao enviar e-mail automático: {e}")

    return render_template("compracerta.html")

@app.route("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
