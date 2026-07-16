import mercadopago
import uuid
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS # Lembre-se de ativar o CORS no Flask

app = Flask(__name__)
CORS(app) # Permite que seu HTML acesse o Flask sem bloqueios

URL_GOOGLE_SCRIPT = "https://google.com"

def comunicar_google_sheets(acao, dados_atleta):
    """Envia os dados direto do Python para o Google Sheets via POST"""
    payload = {
        "token_seguranca": "9921",
        "acao": acao,
        **dados_atleta
    }
    try:
        # Requisições de servidor para servidor via POST não sofrem bloqueio de CORS
        requests.post(URL_GOOGLE_SCRIPT, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao integrar com Google Sheets: {e}")

# =====================================================================
# ROTA 1: GERAR PIX (E CRIAR COMO PENDENTE)
# =====================================================================
@app.route("/gerar-link-pagamento", methods=["POST"])
def gerar_link_pagamento():
    dados_recebidos = request.get_json() or {}
    email = dados_recebidos.get("email", "participante@email.com")
    nome = dados_recebidos.get("nome", "Participante")

    token = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
    sdk = mercadopago.SDK(token)
    request_options = mercadopago.config.RequestOptions()
    request_options.idempotency_key = str(uuid.uuid4())

    payment_data = {
        "transaction_amount": 0.01,
        "description": "Inscrição São Jorge Para Todos",
        "payment_method_id": "pix",
        "payer": {
            "email": email,
            "first_name": nome
        },
        "statement_descriptor": "INSCRICAO SJ"
    }
    
    try:
        result = sdk.payment().create(payment_data, request_options)
        response = result.get("response")
        
        if response and "id" in response:
            # 🚀 SALVA COMO PENDENTE ASSIM QUE O PIX FOR GERADO
            comunicar_google_sheets("criar_pendente", dados_recebidos)
            
            point_of_interaction = response.get("point_of_interaction", {})
            transaction_data = point_of_interaction.get("transaction_data", {})
            
            return jsonify({
                "id": response.get("id"),
                "qr_code_base64": transaction_data.get("qr_code_base64"),
                "copia_e_cola": transaction_data.get("qr_code")
            }), 200
        return jsonify({"erro": "Erro ao criar pagamento Pix"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# =====================================================================
# ROTA 2: GERAR CARTÃO (E CRIAR COMO PENDENTE)
# =====================================================================
@app.route("/gerar-cartao-pagamento", methods=["POST"])
def gerar_cartao_pagamento():
    dados_recebidos = request.get_json() or {}
    email = dados_recebidos.get("email", "participante@email.com")

    token = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
    sdk = mercadopago.SDK(token)
    request_options = mercadopago.config.RequestOptions()
    request_options.idempotency_key = str(uuid.uuid4())

    preference_data = {
        "items": [{
            "title": "Inscrição São Jorge Para Todos",
            "quantity": 1,
            "unit_price": 5.00,
            "currency_id": "BRL"
        }],
        "payer": {
            "email": email
        },
        "payment_methods": {
            "excluded_payment_types": [{"id": "ticket"}, {"id": "bank_transfer"}],
            "installments": 12
        },
        "statement_descriptor": "INSCRICAO SJ",
        "binary_mode": True, 
        "back_urls": {
            "success": "https://netlify.app", # Corrigido o hhttps://
            "failure": "https://netlify.app",
            "pending": "https://netlify.app"
        },
        "auto_return": "approved",
        "external_reference": email
    }
    
    try:
        result = sdk.preference().create(preference_data, request_options)
        response = result.get("response")
        
        if response and "init_point" in response:
            # 🚀 SALVA COMO PENDENTE ASSIM QUE O LINK DO CARTÃO FOR GERADO
            comunicar_google_sheets("criar_pendente", dados_recebidos)
            
            return jsonify({
                "link_cartao": response.get("init_point") 
            }), 200
        return jsonify({"erro": "Erro ao criar link do cartão"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# =====================================================================
# ROTA 3: CONFIRMAÇÃO MANUAL (Acionada pelo botão do front-end)
# =====================================================================
@app.route("/confirmar-pagamento-manual", methods=["POST"])
def confirmar_manual():
    dados_recebidos = request.get_json() or {}
    # Avisa o Google Sheets para mudar o status do email para "Pago"
    comunicar_google_sheets("confirmar_pagamento", {"email": dados_recebidos.get("email")})
    return jsonify({"status": "solicitado"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
