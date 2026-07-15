import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apimercadopago import gerar_link_pagamento

app = Flask(__name__, template_folder='.')
CORS(app) 

# --- ROTAS DO FLASK ---

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    dados = request.get_json() or {}
    
    # Extraindo os valores do JSON enviado pelo formulário
    nome = dados.get("nome", "Participante")
    email = dados.get("email")
    cpf = dados.get("cpf") # Adicionado: capturando o CPF aqui

    # Validação simples
    if not cpf:
        return jsonify({"error": "CPF é obrigatório"}), 400

    # Chamada corrigida: passando o CPF agora
    link = gerar_link_pagamento(nome=nome, email=email, cpf=cpf)
    
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
