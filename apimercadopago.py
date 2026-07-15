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
        # Bloqueia outros meios e força a exibição direta do Pix
        "payment_methods": {
            "excluded_payment_types": [
                {"id": "credit_card"},   # Bloqueia Cartão de Crédito
                {"id": "debit_card"},    # Bloqueia Cartão de Débito
                {"id": "ticket"}         # Bloqueia Boleto Bancário
            ],
            "installments": 1            # Sem parcelamentos
        },
        "back_urls": {
            # Direciona o cliente para a sua página de agradecimento no Netlify
            "success": "https://netlify.app",
            "failure": "https://onrender.com",
            "pending": "https://onrender.com"
        },
        "auto_return": "approved",       # Redireciona o usuário sozinho sem precisar clicar
        "binary_mode": True,             # Pix é aprovado ou recusado na hora (sem pendências)
        "statement_descriptor": "INSCRICAO SJ"
    }
    
    try:
        result = sdk.preference().create(preference_data)
        payment = result.get("response")
        
        if payment and "init_point" in payment:
            return payment["init_point"]
        else:
            print(f"Erro na criação da preferência: {result}")
            return None
            
    except Exception as e:
        print(f"Erro crítico: {e}")
        return None
