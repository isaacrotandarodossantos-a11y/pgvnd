import mercadopago

def gerar_pix_pagamento(nome, email):
    token = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
    sdk = mercadopago.SDK(token)

    payment_data = {
        "transaction_amount": 0.01, # Valor corrigido para R$ 10.00
        "description": "Inscrição São Jorge Para Todos",
        "payment_method_id": "pix",  # Força o método de pagamento a ser Pix
        "payer": {
            "email": email,          # OBRIGATÓRIO para Pix na API de Payments
            "first_name": nome
        },
        "notification_url": "https://suaapi.com" # URL para receber a confirmação
    }
    
    try:
        # Usando sdk.payment().create() em vez de preference
        result = sdk.payment().create(payment_data)
        payment = result.get("response")
        
        if payment and "point_of_interaction" in payment:
            pix_info = payment["point_of_interaction"]["transaction_data"]
            return {
                "qr_code_base64": pix_info["qr_code_base64"], # Imagem do QR Code
                "qr_code": pix_info["qr_code"],               # Chave Copia e Cola
                "payment_id": payment["id"]                    # ID para consultar o status depois
            }
        else:
            print(f"Erro na criação do Pix: {result}")
            return None
            
    except Exception as e:
        print(f"Erro crítico: {e}")
        return None
