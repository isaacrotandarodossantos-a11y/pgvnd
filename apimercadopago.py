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
                "unit_price": 0.01  # Valor ajustado para evitar bloqueio de teste
            }
        ],
        "payer": {
            "name": nome,
            "email": email,
            "identification": {
                "type": "CPF",
                "number": cpf  # O CPF é obrigatório para destravar o botão de pagamento
            }
        },
        "external_reference": cpf, 
        "back_urls": {
            "success": "https://bucolic-fox-ea9bba.netlify.app/",
            "failure": "https://pgvnd.onrender.com/compraerrada",
            "pending": "https://pgvnd.onrender.com/compraerrada"
        },
        "auto_return": "approved",
        "binary_mode": True
    }
    
    try:
        result = sdk.preference().create(preference_data)
        payment = result.get("response")
        
        if payment and "init_point" in payment:
            return payment["init_point"]
        else:
            print(f"Erro na resposta do Mercado Pago: {result}")
            return None
            
    except Exception as e:
        print(f"Erro ao gerar preferência: {e}")
        return None
