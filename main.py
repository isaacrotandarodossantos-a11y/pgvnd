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
    app.run(debug=True)