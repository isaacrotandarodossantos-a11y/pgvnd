import mercadopago

def gerar_link_pagamento():
    # Token de produção (substitua pelo seu atual após gerar um novo)
    sdk = mercadopago.SDK("TEST-8677986015174769-071410-62092e2af1b3457c19aa12ee873e701c-722783171")

    preference_data = {
        "items": [
            {
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 1.00
            }
        ],
        "back_urls": {
            "success": "http://127.0.0.1:5000/compracerta",
            "failure": "http://127.0.0.1:5000/compraerrada",
            "pending": "http://127.0.0.1:5000/compraerrada"
        }
    }
    
    result = sdk.preference().create(preference_data)
    payment = result.get("response")
    
    return payment.get("init_point") if payment else None
