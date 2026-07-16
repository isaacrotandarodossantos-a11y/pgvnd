import os
import requests
import mercadopago
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apimercadopago import gerar_link_pagamento, gerar_cartao_pagamento

app = Flask(__name__, template_folder='.')
CORS(app)

TOKEN_MP = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
sdk = mercadopago.SDK(TOKEN_MP)

# CREDENCIAIS PROTEGIDAS: Ninguém na internet consegue ver essas duas linhas!
CHAVE_SEGREDO = "9921"
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw0PtbqTkA0Q7KIP1lnPX5BtMVmRW0q0m64ser2hJaxVBgaqI_zgirBr8OFBlb4nq58/exec"

@app.route("/")
def homepage():
    return render_template("index.html")

# ROTA 1: EXCLUSIVA PARA GERAR O PIX + CRIAR CADASTRO PENDENTE
@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    dados = request.get_json() or {}
    
    # Injeta a segurança direto no servidor antes de mandar pro Google
    dados["acao"] = "salvar_cadastro"
    dados["token_seguranca"] = CHAVE_SEGREDO
    
    try:
        requests.post(GOOGLE_SHEET_URL, json=dados, timeout=10)
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")
        
    return gerar_link_pagamento()

# ROTA 2: EXCLUSIVA PARA GERAR O CARTÃO + CRIAR CADASTRO PENDENTE
@app.route("/gerar-cartao-pagamento", methods=["POST"])
def api_gerar_cartao():
    dados = request.get_json() or {}
    
    # Injeta a segurança direto no servidor antes de mandar pro Google
    dados["acao"] = "salvar_cadastro"
    dados["token_seguranca"] = CHAVE_SEGREDO
    
    try:
        requests.post(GOOGLE_SHEET_URL, json=dados, timeout=10)
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")
        
    return gerar_cartao_pagamento()

# ROTA 3: CONSULTA PAGAMENTO PIX + ATUALIZA PLANILHA PARA PAGO
@app.route("/verificar-pagamento/<int:payment_id>", methods=["GET"])
def verificar_pagamento(payment_id):
    # Captura o e-mail passado via parâmetro na URL para saber quem atualizar
    email_pagador = request.args.get("email")
    
    try:
        payment_info = sdk.payment().get(payment_id)
        if payment_info and "response" in payment_info:
            status = payment_info["response"].get("status")
            
            # Se o Pix foi pago, o próprio Render avisa o Google de forma blindada
            if status == "approved" and email_pagador:
                dados_atualizacao = {
                    "acao": "confirmar_pagamento",
                    "token_seguranca": CHAVE_SEGREDO,
                    "email": email_pagador,
                    "payment_id": str(payment_id)
                }
                try:
                    requests.post(GOOGLE_SHEET_URL, json=dados_atualizacao, timeout=10)
                except Exception as sheet_err:
                    print(f"Erro ao atualizar status na planilha: {sheet_err}")
                    
            return jsonify({"status": status})
        return jsonify({"status": "error"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ROTA 4: ATUALIZA PLANILHA PARA QUEM MANDOU RETORNO DO CARTÃO
@app.route("/confirmar-cartao", methods=["POST"])
def confirmar_cartao():
    dados = request.get_json() or {}
    email_pagador = dados.get("email")
    id_pagamento = dados.get("payment_id")
    
    if email_pagador:
        dados_atualizacao = {
            "acao": "confirmar_pagamento",
            "token_seguranca": CHAVE_SEGREDO,
            "email": email_pagador,
            "payment_id": id_pagamento or "cartao_credito"
        }
        try:
            requests.post(GOOGLE_SHEET_URL, json=dados_atualizacao, timeout=10)
            return jsonify({"status": "sucesso"}), 200
        except Exception as e:
            return jsonify({"status": "erro", "mensagem": str(e)}), 500
    return jsonify({"status": "dados_invalidos"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
