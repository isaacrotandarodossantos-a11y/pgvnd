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
                "unit_price": 0.01  # AUMENTADO PARA R$ 10.00 (Valores < R$ 1.00 costumam travar)
            }
        ],
        "payer": {
            "name": nome
        },
        "back_urls": {
            "success": "https://bucolic-fox-ea9bba.netlify.app/",
            "failure": "https://pgvnd.onrender.com/compraerrada",
            "pending": "https://pgvnd.onrender.com/compraerrada"
        },
        "auto_return": "approved", # Tenta redirecionar automaticamente
        "binary_mode": False,        # Força aprovação imediata (sem pendência)
        "statement_descriptor": "INSCRICAO SJ" # Nome que aparece no extrato
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
