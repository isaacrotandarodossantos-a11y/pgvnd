import mercadopago

def gerar_link_pagamento():
    # Token de produção (substitua pelo seu atual após gerar um novo)
    sdk = mercadopago.SDK("APP_USR-6514550609577640-071410-7564a86a2d54dc3b44f20e9dc2ddfeff-3535803663")

    preference_data = {
        "items": [
            {
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 60.00
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