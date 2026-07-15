import mercadopago
import uuid

def gerar_link_pagamento(nome):  # Mantemos o nome da função para não quebrar seu servidor
    token = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
    sdk = mercadopago.SDK(token)

    request_options = mercadopago.config.RequestOptions()
    request_options.idempotency_key = str(uuid.uuid4())

    payment_data = {
        "transaction_amount": 50.00,
        "description": "Inscrição São Jorge Para Todos",
        "payment_method_id": "pix",  # Força o método Pix
        "payer": {
            "email": "participante@email.com",  # Obrigatório para gerar Pix
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
            
            # Retorna os dados necessários para o seu site desenhar o Pix na tela
            return {
                "id": response.get("id"),
                "copia_e_cola": transaction_data.get("qr_code"),
                "qr_code_base64": transaction_data.get("qr_code_base64")
            }
        print(f"Erro MP: {response}")
        return None
    except Exception as e:
        print(f"Erro crítico no Pix: {e}")
        return None
