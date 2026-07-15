import mercadopago
import os

def gerar_link_pagamento(nome, email):
    token = os.getenv("MP_TOKEN")
    sdk = mercadopago.SDK(token)

    # URL correta apontando para o seu servidor
    url_sucesso = f"https://bucolic-fox-ea9bba.netlify.app/"

    preference_data = {
        "items": [
            {
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 00.01
            }
        ],
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
