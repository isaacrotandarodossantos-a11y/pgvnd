import mercadopago

def gerar_link_pagamento(nome):
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
        "payer": {
            "name": nome
        },
        # TRAVA PARA EXIBIR APENAS PIX
        "payment_methods": {
            "excluded_payment_types": [
                {"id": "credit_card"},   
                {"id": "debit_card"},    
                {"id": "ticket"}         
            ],
            "installments": 1            
        },
        "back_urls": {
            # Manda direto para o seu agradecimento no Netlify
            "success": "https://netlify.app",
            "failure": "https://onrender.com",
            "pending": "https://onrender.com"
        },
        "auto_return": "approved",       # Redireciona o cliente sozinho
        "binary_mode": True,             # Pix direto aprovado/recusado
        "statement_descriptor": "INSCRICAO SJ"
    }
    
    try:
        result = sdk.preference().create(preference_data)
        payment = result.get("response")
        if payment and "init_point" in payment:
            return payment["init_point"]
        return None
    except Exception as e:
        print(f"Erro crítico na preferência: {e}")
        return None
