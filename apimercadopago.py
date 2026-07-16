import mercadopago
import uuid
from flask import request, jsonify

# =====================================================================
# FUNÇÃO 1: EXCLUSIVA PARA GERAR PIX
# =====================================================================
def gerar_link_pagamento():
    dados_recebidos = request.get_json() or {}
    email = dados_recebidos.get("email", "participante@email.com")
    nome = dados_recebidos.get("nome", "Participante")

    token = "TEST-8677986015174769-071410-62092e2af1b3457c19aa12ee873e701c-722783171"
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
# FUNÇÃO 2: EXCLUSIVA PARA CARTÃO (Sem parâmetros de Webhook)
# =====================================================================
def gerar_cartao_pagamento():
    dados_recebidos = request.get_json() or {}
    email = dados_recebidos.get("email", "participante@email.com")

    token = "TEST-8677986015174769-071410-62092e2af1b3457c19aa12ee873e701c-722783171"
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
        # URLs de retorno ajustadas para carregar o e-mail do atleta na barra de endereço
        "back_urls": {
            "success": "https://netlify.app" + email,
            "failure": "https://netlify.app",
            "pending": "https://netlify.app" + email
        },
        "auto_return": "approved"
        # Notificação de URL removida completamente aqui
    }
    
    try:
        result = sdk.preference().create(preference_data, request_options)
        response = result.get("response")
        
        if response and "init_point" in response:
            return jsonify({
                "link_cartao": response.get("init_point") 
            }), 200
        return jsonify({"erro": "Erro ao criar link do cartão"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
