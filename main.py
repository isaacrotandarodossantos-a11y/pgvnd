import os
import requests  # Certifique-se de ter instalado: pip install requests
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apimercadopago import gerar_link_pagamento

app = Flask(__name__, template_folder='.')
CORS(app)

# URL do seu Script do Google (o Web App que você criou no Apps Script)
GOOGLE_SHEET_URL = "SUA_URL_DO_WEB_APP_APPS_SCRIPT_AQUI"

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    dados = request.get_json() or {}
    
    nome = dados.get("nome", "Participante")
    email = dados.get("email")
    cpf = str(dados.get("cpf", "")).replace(".", "").replace("-", "").strip()

    if not cpf:
        return jsonify({"error": "CPF é obrigatório"}), 400

    # 1. Salvar na Planilha ANTES de gerar o pagamento
    try:
        # Envia os dados para o Google Apps Script
        requests.post(GOOGLE_SHEET_URL, json=dados, timeout=10)
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")
        # Decida se quer bloquear o pagamento caso a planilha falhe
        # return jsonify({"error": "Erro ao salvar cadastro"}), 500

    # 2. Gera o link de pagamento
    link = gerar_link_pagamento(nome=nome, email=email, cpf=cpf)
    
    if link:
        # Retorna o link para o JavaScript do index.html fazer o redirecionamento
        return jsonify({"link": link})
    
    return jsonify({"error": "Erro ao gerar link de pagamento"}), 500

@app.route("/compracerta")
def compra_certa():
    return render_template("compracerta.html")

@app.route("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
