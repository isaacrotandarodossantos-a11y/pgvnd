import mercadopago
import os

def gerar_link_pagamento(nome, email, cpf):
    token = os.getenv("APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171")
    sdk = mercadopago.SDK(token)

    url_sucesso = "https://bucolic-fox-ea9bba.netlify.app/"

    preference_data = {
        "items": [
            {
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 60.00
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
