import os
import requests
import mercadopago
from flask import Flask, render_template, jsonify, request, render_template_string
from flask_cors import CORS

app = Flask(__name__, template_folder='.')
CORS(app)

# Inicialização do SDK do Mercado Pago
TOKEN = "APP_USR-8677986015174769-071410-f913279c1c5f01176f80d34cac8c035b-722783171"
sdk = mercadopago.SDK(TOKEN)

GOOGLE_SHEET_URL = "https://google.com"

# Tela visual do Pix gerada pelo seu próprio Render (Sem Webhook)
TELA_PIX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Pague com o Pix</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background: #f4f4f9; color: #333; }
        .box { background: white; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 90%; width: 350px; }
        textarea { width: 100%; height: 60px; margin: 15px 0; padding: 5px; box-sizing: border-box; resize: none; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #009ee3; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; }
        button:hover { background: #007bb6; }
        .loader { border: 4px solid #f3f3f3; border-top: 4px solid #28a745; border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite; display: inline-block; vertical-align: middle; margin-right: 8px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="box">
        <h2>Inscrição São Jorge</h2>
        <p>Escaneie ou copie o Pix abaixo para pagar:</p>
        <img src="data:image/jpeg;base64,{{ qrcode_base64 }}" width="220" style="margin: 10px 0;"><br>
        <textarea id="pixCode" readonly>{{ qrcode_copia_e_cola }}</textarea><br>
        <button onclick="copiarPix()">Copiar Código Pix</button>
        
        <p style="color: #28a745; font-weight: bold; margin-top: 20px;">
            <span class="loader"></span>Aguardando pagamento...
        </p>
        <p style="font-size:12px; color:#777; margin-top: -10px;">Esta tela mudará sozinha assim que você pagar no app do seu banco.</p>
    </div>

    <script>
        // O navegador fica perguntando diretamente para a API do seu Render se o Pix foi pago
        const intervalo = setInterval(async () => {
            try {
                const response = await fetch('/verificar-pagamento-direto?payment_id={{ payment_id }}');
                const dados = await response.json();
                
                if (dados.status === 'approved') {
                    clearInterval(intervalo);
                    // Redireciona na hora para a página de sucesso
                    window.location.href = "/compracerta?payment_id={{ payment_id }}";
                }
            } catch (erro) {
                console.error("Erro ao checar status:", erro);
            }
        }, 3000); // Executa a cada 3 segundos

        function copiarPix() {
            var copyText = document.getElementById("pixCode");
            copyText.select();
            copyText.setSelectionRange(0, 99999);
            navigator.clipboard.writeText(copyText.value);
            alert("Código Pix copiado!");
        }
    </script>
</body>
</html>
"""

@app.route("/")
def homepage():
    return render_template("index.html")

# ROTA DA NETLIFY: Gera o Pix diretamente e joga para a tela customizada
@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    dados = request.get_json() or {}
    nome = dados.get("nome", "Participante")
    # A API de pagamento direto do Pix exige um formato de e-mail do pagador
    email = dados.get("email", "comprador@email.com") 

    try:
        requests.post(GOOGLE_SHEET_URL, json=dados, timeout=10)
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")

    # Criando a cobrança Pix via Checkout Transparente (Direct API)
    payment_data = {
        "transaction_amount": 0.01, # Mantido R$ 10.00 para evitar travas de antifraude
        "description": "Inscrição São Jorge Para Todos",
        "payment_method_id": "pix",
        "payer": {
            "email": email,
            "first_name": nome
        }
    }

    try:
        result = sdk.payment().create(payment_data)
        payment = result.get("response")
        
        if payment and "point_of_interaction" in payment:
            pix_info = payment["point_of_interaction"]["transaction_data"]
            
            # Retorna o link da nossa própria página interna do Render que exibe o Pix
            link_proprio = f"https://onrender.com{payment['id']}&qr={pix_info['qr_code_base64']}&code={requests.utils.quote(pix_info['qr_code'])}"
            return jsonify({"link": link_proprio})
            
    except Exception as e:
        print(f"Erro ao gerar Pix: {e}")
        
    return jsonify({"error": "Erro ao gerar pagamento"}), 500

# Rota que renderiza a tela visual do QR Code
@app.route("/mostrar-pix")
def mostrar_pix():
    payment_id = request.args.get("id")
    qr = request.args.get("qr")
    code = request.args.get("code")
    return render_template_string(TELA_PIX_HTML, payment_id=payment_id, qrcode_base64=qr, qrcode_copia_e_cola=code)

# ROTA DE CHECAGEM: O Javascript da página fica batendo aqui de 3 em 3 segundos
@app.route("/verificar-pagamento-direto")
def verificar_pagamento_direto():
    payment_id = request.args.get("payment_id")
    if payment_id:
        try:
            # Pergunta em tempo real ao Mercado Pago o status atual desse ID
            payment_info = sdk.payment().get(payment_id)
            payment_data = payment_info.get("response")
            if payment_data:
                return jsonify({"status": payment_data.get("status")})
        except Exception as e:
            print(f"Erro ao consultar API: {e}")
            
    return jsonify({"status": "pending"})

@app.route("/compracerta")
def compra_certa():
    payment_id = request.args.get("payment_id")
    status_final = "pendente"

    if payment_id:
        try:
            payment_info = sdk.payment().get(payment_id)
            if payment_info.get("response"):
                status_real = payment_info["response"].get("status")
                if status_real == "approved":
                    status_final = "confirmado"
        except Exception as e:
            print(f"Erro ao consultar API: {e}")
    
    return render_template("compracerta.html", status=status_final)

@app.route("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
