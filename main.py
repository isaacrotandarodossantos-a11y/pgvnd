import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from apimercadopago import gerar_link_pagamento

# O template_folder='.' diz ao Flask para procurar os .html na mesma pasta do main.py
app = Flask(__name__, template_folder='.')
CORS(app) 

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
    return render_template("compracerta.html")

@app.route("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
