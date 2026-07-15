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

# Esta página carrega o Checkout Oficial do Mercado Pago DENTRO do seu servidor.
# Ela processa Cartão, Pix e Boleto e redireciona SOZINHA após o pagamento!
TELA_CHECKOUT_TRANSPARENTE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pagamento Seguro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Carrega a biblioteca oficial do Mercado Pago -->
    <script src="https://mercadopago.com"></script>
</head>
<body>
    <!-- Onde o checkout com Pix, Cartão e Boleto vai aparecer na tela -->
    <div id="paymentBrick_container"></div>

    <script>
        // Inicializa o Mercado Pago com sua Public Key obtida do token
        const mp = new MercadoPago('APP_USR-6725287e-d30d-4054-946f-d90c1e8ba84a');
        const bricksBuilder = mp.bricks();

        const renderPaymentBrick = async (bricksBuilder) => {
            const settings = {
                initialization: {
                    amount: 0.01, // Valor final de R$ 0,01 centavo
                    preferenceId: "{{ preference_id }}",
                    payer: {
                        firstName: "{{ nome }}",
                        email: "comprador@email.com"
                    },
                },
                customization: {
                    paymentMethods: {
                        theme: "default",
                        allPaymentMethods: "all", // Ativa Pix, Cartão, Boleto, etc.
                    },
                },
                callbacks: {
                    onReady: () => {
                        console.log("Checkout pronto!");
                    },
                    onSubmit: ({ selectedPaymentMethod, formData }) => {
                        // Quando o cliente clica em pagar, envia direto para o Mercado Pago
                        return new Promise((resolve, reject) => {
                            fetch("/processar-pagamento-direto", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify(formData),
                            })
                            .then((response) => response.json())
                            .then((result) => {
                                if (result.status === "approved" || result.status == "pending") {
                                    // REDIRECIONA NA HORA!
                                    window.location.href = "/compracerta?payment_id=" + result.id;
                                } else {
                                    window.location.href = "/compraerrada";
                                }
                                resolve();
                            })
                            .catch((error) => {
                                window.location.href = "/compraerrada";
                                reject();
                            });
                        });
                    },
                    onError: (error) => {
                        console.error(error);
                    },
                },
            };
            window.paymentBrickController = await bricksBuilder.create(
                "payment",
                "paymentBrick_container",
                settings
            );
        };
        renderPaymentBrick(bricksBuilder);
    </script>
</body>
</html>
"""

@app.route("/")
def homepage():
    return render_template("index.html")

# ROTA DA NETLIFY: Manda o cliente para a tela integrada do Render
@app.route("/gerar-link-pagamento", methods=["POST"])
def api_gerar_link():
    dados = request.get_json() or {}
    nome = dados.get("nome", "Participante")

    try:
        requests.post(GOOGLE_SHEET_URL, json=dados, timeout=10)
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")

    # Cria uma preferência leve apenas para registrar o item de R$ 0,01
    preference_data = {
        "items": [{"title": "Inscrição São Jorge", "quantity": 1, "currency_id": "BRL", "unit_price": 0.01}]
    }
    
    try:
        result = sdk.preference().create(preference_data)
        pref = result.get("response")
        if pref:
            # Retorna o link da página do Render que vai abrir o checkout direto na tela do usuário
            link_proprio = f"https://onrender.com{pref['id']}&nome={requests.utils.quote(nome)}"
            return jsonify({"link": link_proprio})
    except Exception as e:
        print(f"Erro: {e}")

    return jsonify({"error": "Erro ao gerar pagamento"}), 500


@app.route("/checkout-seguro")
def checkout_seguro():
    preference_id = request.args.get("id")
    nome = request.args.get("nome")
    return render_template_string(TELA_CHECKOUT_TRANSPARENTE, preference_id=preference_id, nome=nome)


# ROTA QUE FAZ A MÁGICA: Executa o pagamento e devolve a resposta instantânea
@app.route("/processar-pagamento-direto", methods=["POST"])
def processar_pagamento_direto():
    form_data = request.get_json()
    try:
        result = sdk.payment().create(form_data)
        payment = result.get("response")
        return jsonify({
            "status": payment.get("status"),
            "id": payment.get("id")
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


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
