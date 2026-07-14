import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from apimercadopago import gerar_link_pagamento

app = Flask(__name__)
CORS(app) # Permite a comunicação do HTML com o Python

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    link = gerar_link_pagamento()
    if link:
        return jsonify({"link": link})
    return jsonify({"error": "Erro ao gerar link"}), 500

@app.route("/compracerta")
def compra_certa():
    return "Compra aprovada com sucesso!"

@app.route("/compraerrada")
def compra_errada():
    return "Erro no pagamento ou cancelado."

if __name__ == "__main__":
    # Ajuste para rodar corretamente no Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
