import mercadopago
import os

def gerar_link_pagamento(nome, email, cpf):
    token = os.getenv("MP_TOKEN")
    sdk = mercadopago.SDK(token)

    url_sucesso = "https://bucolic-fox-ea9bba.netlify.app/"

    preference_data = {
        "items": [
            {
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 79.90
            }
        ],
        "external_reference": cpf, # <--- ESSENCIAL: Vincula o pagamento ao CPF
        "back_urls": {
            "success": url_sucesso,
            "failure": "https://pgvnd.onrender.com/compraerrada",
            "pending": "https://pgvnd.onrender.com/compraerrada"
        },
        "auto_return": "approved"
    }
    
    result = sdk.preference().create(preference_data)
    payment = result.get("response")
    
    return payment.get("init_point") if payment else None
