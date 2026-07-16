import mercadopago
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/gerar-link-pagamento', methods=['POST'])
def rota_pagamento():
    dados_recebidos = request.get_json()
    
    nome = dados_recebidos.get("nome", "Participante")
    email = dados_recebidos.get("email", "participante@email.com")
    metodo = dados_recebidos.get("metodo_pagamento")

    token = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
    sdk = mercadopago.SDK(token)

    request_options = mercadopago.config.RequestOptions()
    request_options.idempotency_key = str(uuid.uuid4())

    # FLUXO 1: SE O USUÁRIO ESCOLHER PIX
    if metodo == "pix":
        payment_data = {
            "transaction_amount": 50.00,
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
            
            if result.get("status") == 201 and response:
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

    # FLUXO 2: SE O USUÁRIO ESCOLHER CARTÃO
    elif metodo == "cartao":
        preference_data = {
            "items": [{
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "unit_price": 50.00,
                "currency_id": "BRL"
            }],
            "payer": {
                "name": nome,
                "email": email
            },
            "payment_methods": {
                "excluded_payment_types": [{"id": "ticket"}, {"id": "bank_transfer"}],
                "installments": 12
            },
            "statement_descriptor": "INSCRICAO SJ",
            "back_urls": {
                "success": "https://netlify.app",
                "failure": "https://netlify.app",
                "pending": "https://netlify.app"
            },
            "auto_return": "approved"
        }
        try:
            result = sdk.preference().create(preference_data, request_options)
            response = result.get("response")
            
            if result.get("status") in [200, 201] and response:
                return jsonify({
                    "id": "cartao_checkout", 
                    "link_cartao": response.get("init_point") 
                }), 200
            return jsonify({"erro": "Erro ao criar preferência de cartão"}), 400
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    return jsonify({"erro": "Método inválido"}), 400
