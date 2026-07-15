import mercadopago
import os

def gerar_link_pagamento(nome, email, cpf):
    # CORREÇÃO: Remova o os.getenv se você quiser passar o token diretamente
    token = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
    
    # Se você REALMENTE quiser usar variáveis de ambiente (mais seguro), 
    # o código correto seria: os.getenv("NOME_DA_SUA_VARIAVEL")
    
    sdk = mercadopago.SDK(token)

    url_sucesso = "https://bucolic-fox-ea9bba.netlify.app/"

    preference_data = {
        "items": [
            {
                "title": "Inscrição São Jorge Para Todos",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 0.01 # Corrigido: 0.01 em vez de 00.01
            }
        ],
        "external_reference": cpf,
        "back_urls": {
            "success": url_sucesso,
            "failure": "https://pgvnd.onrender.com/compraerrada",
            "pending": "https://pgvnd.onrender.com/compraerrada"
        },
        "auto_return": "approved"
    }
    
    result = sdk.preference().create(preference_data)
    payment = result.get("response")
    
    return payment.get("init_point") if payment else None
