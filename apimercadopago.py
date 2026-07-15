import mercadopago

def gerar_link_pagamento(nome, email, cpf):
    # Insira o seu token aqui (sem o os.getenv se estiver direto no código)
    token = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
    sdk = mercadopago.SDK(token)

    preference_data = {
        "items": [
            {
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 0.01
            }
        ],
        "external_reference": cpf, # Agora o CPF chega aqui corretamente
        "back_urls": {
            "success": "https://bucolic-fox-ea9bba.netlify.app/",
            "failure": "https://pgvnd.onrender.com/compraerrada",
            "pending": "https://pgvnd.onrender.com/compraerrada"
        },
        "auto_return": "approved"
    }
    
    result = sdk.preference().create(preference_data)
    payment = result.get("response")
    
    return payment.get("init_point") if payment else None
