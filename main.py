import os
import requests
import mercadopago
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apimercadopago import gerar_link_pagamento

app = Flask(__name__, template_folder='.')
CORS(app)

# Definição do Token (Lembre-se de trocar no painel do Mercado Pago depois por segurança!)
TOKEN_MP = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
sdk = mercadopago.SDK(TOKEN_MP)

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw0PtbqTkA0Q7KIP1lnPX5BtMVmRW0q0m64ser2hJaxVBgaqI_zgirBr8OFBlb4nq58/exec"

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    dados = request.get_json() or {}
    nome = dados.get("nome", "Participante")

    try:
        # Envia os dados para salvar na sua planilha do Google Sheets
        requests.post(GOOGLE_SHEET_URL, json=dados, timeout=10)
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")

    # Gera o link travado apenas para PIX e direcionando para o Netlify
    link = gerar_link_pagamento(nome=nome)
    
    if link:
        return jsonify({"link": link})
    return jsonify({"error": "Erro ao gerar link de pagamento"}), 500

@app.route("/compracerta")
def compra_certa():
    payment_id = request.args.get("payment_id")
    status_final = "pendente"

    if payment_id:
        try:
            payment_info = sdk.payment().get(payment_id)
            if payment_info and "response" in payment_info:
                status_real = payment_info["response"].get("status")
                if status_real == "approved":
                    status_final = "confirmado"
                else:
                    status_final = status_real
        except Exception as e:
            print(f"Erro ao consultar API: {e}")
    
    return render_template("compracerta.html", status=status_final)

@app.route("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
