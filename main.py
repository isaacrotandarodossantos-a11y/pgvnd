import os
import requests
import mercadopago
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
# Importa as duas funções separadas do seu arquivo apimercadopago.py
from apimercadopago import gerar_link_pagamento, gerar_cartao_pagamento

app = Flask(__name__, template_folder='.')
CORS(app)

TOKEN_MP = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
sdk = mercadopago.SDK(TOKEN_MP)

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw0PtbqTkA0Q7KIP1lnPX5BtMVmRW0q0m64ser2hJaxVBgaqI_zgirBr8OFBlb4nq58/exec"

@app.route("/")
def homepage():
    return render_template("index.html")

# =====================================================================
# ROTA 1: EXCLUSIVA PARA GERAR O PIX
# =====================================================================
@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    dados = request.get_json() or {}

    try:
        # Salva os dados na planilha do Google Sheets primeiro
        requests.post(GOOGLE_SHEET_URL, json=dados, timeout=10)
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")

    # Executa a função exclusiva de PIX (gerar_link_pagamento)
    dados_pix = gerar_link_pagamento()
    
    # Como a função apimercadopago já retorna um jsonify(), devolvemos direto
    return dados_pix

# =====================================================================
# ROTA 2: EXCLUSIVA PARA GERAR O LINK DE CARTÃO (Nova rota!)
# =====================================================================
@app.route("/gerar-cartao-pagamento", methods=["POST"])
def api_gerar_cartao():
    dados = request.get_json() or {}

    try:
        # Salva os dados na planilha do Google Sheets também para quem escolhe cartão
        requests.post(GOOGLE_SHEET_URL, json=dados, timeout=10)
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")

    # Executa a função exclusiva de Cartão (gerar_cartao_pagamento)
    dados_cartao = gerar_cartao_pagamento()
    
    # Devolve o link do Mercado Pago direto para o front-end
    return dados_cartao

# ROTA DE VERIFICAÇÃO DO PIX (Mantida idêntica para o Javascript consultar de 3 em 3s)
@app.route("/verificar-pagamento/<int:payment_id>", methods=["GET"])
def verificar_pagamento(payment_id):
    try:
        payment_info = sdk.payment().get(payment_id)
        if payment_info and "response" in payment_info:
            status = payment_info["response"].get("status")
            return jsonify({"status": status})
        return jsonify({"status": "error", "message": "Pagamento nao localizado"}), 400
    except Exception as e:
        print(f"Erro ao consultar status do Pix: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/compracerta")
def compra_certa():
    payment_id = request.args.get("payment_id")
    status_final = "pendente"

    if payment_id:
        try:
            payment_info = sdk.payment().get(payment_id)
            if payment_info and "response" in payment_info:
                status_real = payment_info["response"].get("status")
                if status_real == "approved":
                    status_final = "confirmado"
                else:
                    status_final = status_real
        except Exception as e:
            print(f"Erro ao consultar API: {e}")
    
    return render_template("compracerta.html", status=status_final)

@app.route("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
