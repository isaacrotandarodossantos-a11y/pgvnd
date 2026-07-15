import mercadopago

def gerar_link_pagamento(nome, email, cpf):
    token = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
    sdk = mercadopago.SDK(token)

    preference_data = {
        "items": [
            {
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 60.00 # Certifique-se de usar o preço correto
            }
        ],
        # Identifica quem está pagando
        "payer": {
            "name": nome,
            "email": email
        },
        "external_reference": cpf, 
        "back_urls": {
            "success": "https://bucolic-fox-ea9bba.netlify.app/",
            "failure": "https://pgvnd.onrender.com/compraerrada",
            "pending": "https://pgvnd.onrender.com/compraerrada"
        },
        "auto_return": "approved"
        # Não adicionamos 'excluded_payment_types', logo, Pix, Crédito e Débito serão aceitos automaticamente.
    }
    
    try:
        result = sdk.preference().create(preference_data)
        payment = result.get("response")
        return payment.get("init_point")
    except Exception as e:
        print(f"Erro ao gerar preferência: {e}")
        return None
