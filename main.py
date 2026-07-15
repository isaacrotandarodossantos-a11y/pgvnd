import os
import requests
import mercadopago
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__, template_folder='.')
CORS(app)

# Inicialização do SDK do Mercado Pago
TOKEN = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
sdk = mercadopago.SDK(TOKEN)

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw0PtbqTkA0Q7KIP1lnPX5BtMVmRW0q0m64ser2hJaxVBgaqI_zgirBr8OFBlb4nq58/exec"

# FUNÇÃO QUE ESTAVA NO OUTRO ARQUIVO (Trazida para cá para corrigir o erro)
def gerar_link_pagamento_interno(nome):
    preference_data = {
        "items": [
            {
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 10.00  # Mantido R$ 10.00 para evitar que o Pix trave
            }
        ],
        "payer": {
            "name": nome
        },
        "back_urls": {
            "success": "https://netlify.app",  # Seu site Netlify
            "failure": "https://onrender.com",
            "pending": "https://onrender.com"
        },
        "auto_return": "approved",
        "statement_descriptor": "INSCRICAO SJ",
        # Adicionado para o Mercado Pago avisar seu servidor sobre o Pix
        "notification_url": "https://onrender.com"
    }
    try:
        result = sdk.preference().create(preference_data)
        payment = result.get("response")
        if payment and "init_point" in payment:
            return payment["init_point"]
        return None
    except Exception as e:
        print(f"Erro crítico na preferência: {e}")
        return None


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

    # Chama a função local interna
    link = gerar_link_pagamento_interno(nome=nome)
    
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
            if payment_info.get("response"):
                status_real = payment_info["response"].get("status")
                if status_real == "approved":
                    status_final = "confirmado"
        except Exception as e:
            print(f"Erro ao consultar API: {e}")
    
    return render_template("compracerta.html", status=status_final)


@app.route("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")


# NOVA ROTA: Escuta a aprovação silenciosa do Pix enviada pelo Mercado Pago
@app.route('/webhook-mercado-pago', methods=['POST'])
def webhook():
    payment_id = request.args.get('data.id') or request.args.get('id')
    topic = request.args.get('type') or request.args.get('topic')
    
    if request.is_json:
        data = request.get_json()
        if data and data.get("type") == "payment":
            payment_id = data.get("data", {}).get("id")
            topic = "payment"

    if topic == "payment" and payment_id:
        try:
            payment_info = sdk.payment().get(payment_id)
            payment_data = payment_info.get("response")
            
            if payment_data:
                status = payment_data.get("status")
                print(f"Webhook Pix recebido! ID: {payment_id} | Status: {status}")
                
                if status == "approved":
                    # ---------------------------------------------------------------
                    # RECOMENDADO: Aqui você pode rodar uma função para avisar a sua 
                    # planilha do Google Sheets que esse participante específico já pagou!
                    # ---------------------------------------------------------------
                    print(f"Sucesso: Pix {payment_id} foi confirmado.")
                    
        except Exception as e:
            print(f"Erro ao processar webhook: {e}")
            return jsonify({"status": "error_handled"}), 200

    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
