import mercadopago

def gerar_link_pagamento(nome, email, cpf):
    token = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
    sdk = mercadopago.SDK(token)

    # Limpeza extra do CPF para garantir apenas números
    cpf_limpo = str(cpf).replace(".", "").replace("-", "").strip()

    preference_data = {
        "items": [
            {
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 1.00
            }
        ],
        "payer": {
            "name": nome,
            "email": email,
            "identification": {
                "type": "CPF",
                "number": cpf_limpo
            }
        },
        "external_reference": cpf_limpo, 
        "back_urls": {
            "success": "https://bucolic-fox-ea9bba.netlify.app/",
            "failure": "https://pgvnd.onrender.com/compraerrada",
            "pending": "https://pgvnd.onrender.com/compraerrada"
        },
        "auto_return": "approved",
        "binary_mode": True  # Essencial para fluxo direto de aprovação
    }
    
    try:
        result = sdk.preference().create(preference_data)
        payment = result.get("response")
        
        # Log detalhado para depuração no Render
        if payment and "init_point" in payment:
            return payment["init_point"]
        else:
            # Captura erros de validação do Mercado Pago (ex: CPF inválido)
            print(f"Erro na criação da preferência: {result.get('message', 'Sem mensagem')}")
            print(f"Detalhes: {result}")
            return None
            
    except Exception as e:
        print(f"Erro crítico na comunicação com Mercado Pago: {e}")
        return None
