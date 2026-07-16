import os
import mercadopago
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apimercadopago import gerar_link_pagamento, gerar_cartao_pagamento

app = Flask(__name__, template_folder='.')
CORS(app)

TOKEN_MP = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
sdk = mercadopago.SDK(TOKEN_MP)

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    return gerar_link_pagamento()

@app.route("/gerar-cartao-pagamento", methods=["POST"])
def api_gerar_cartao():
    return gerar_cartao_pagamento()

@app.route("/verificar-pagamento/<int:payment_id>", methods=["GET"])
def verificar_pagamento(payment_id):
    try:
        payment_info = sdk.payment().get(payment_id)
        if payment_info and "response" in payment_info:
            status = payment_info["response"].get("status")
            return jsonify({"status": status})
        return jsonify({"status": "error"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
