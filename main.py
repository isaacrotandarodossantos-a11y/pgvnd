import os
import requests
import mercadopago
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apimercadopago import gerar_link_pagamento

app = Flask(__name__, template_folder='.')
CORS(app)

# SEGURANÇA: O token é lido da variável de ambiente, nunca fixo no código
# No Render, vá em 'Environment' e adicione: MP_ACCESS_TOKEN = seu_novo_token_aqui
ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
sdk = mercadopago.SDK(ACCESS_TOKEN)

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw0PtbqTkA0Q7KIP1lnPX5BtMVmRW0q0m64ser2hJaxVBgaqI_zgirBr8OFBlb4nq58/exec"

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    dados = request.get_json() or {}
    nome = dados.get("nome", "Participante")

    try:
        requests.post(GOOGLE_SHEET_URL, json=dados, timeout=10)
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")

    link = gerar_link_pagamento(nome=nome)
    
    if link:
        return jsonify({"link": link})
    return jsonify({"error": "Erro ao gerar link de pagamento"}), 500

@app.route("/compracerta")
def compra_certa():
    # Captura o ID do pagamento que o Mercado Pago envia na URL
    payment_id = request.args.get("payment_id")
    
    status_final = "pendente"

    if payment_id:
        try:
            # Consulta a API para garantir que o pagamento foi aprovado
            payment_info = sdk.payment().get(payment_id)
            if payment_info.get("response"):
                status_real = payment_info["response"].get("status")
                if status_real == "approved":
                    status_final = "confirmado"
        except Exception as e:
            print(f"Erro ao consultar API: {e}")
    
    # Passa o status para o seu HTML
    return render_template("compracerta.html", status=status_final)

@app.route("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
