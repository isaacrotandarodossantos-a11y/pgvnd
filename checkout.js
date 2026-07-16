const URL_SERVIDOR = "https://pgvnd.onrender.com";
const URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbw0PtbqTkA0Q7KIP1lnPX5BtMVmRW0q0m64ser2hJaxVBgaqI_zgirBr8OFBlb4nq58/exec";

// Função global auxiliar para enviar dados ao Google Script via JSONP sem erro de CORS
function enviarParaGoogle(dados) {
    return new Promise((resolve) => {
        const callbackName = "googleCallback_" + Date.now();
        window[callbackName] = function(resposta) {
            delete window[window[callbackName]];
            document.getElementById(callbackName)?.remove();
            resolve(resposta);
        };
        const script = document.createElement("script");
        script.id = callbackName;
        script.src = `${URL_GOOGLE_SCRIPT}?callback=${callbackName}&dados=${encodeURIComponent(JSON.stringify(dados))}`;
        document.body.appendChild(script);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("Script carregado!");
    const form = document.getElementById("checkoutForm");
    
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById("btnFinalizar");
            btn.disabled = true;
            btn.innerText = "PROCESSANDO...";

            const dados = Object.fromEntries(new FormData(form).entries());
            localStorage.setItem("email_atleta_reserva", dados.email);

            try {
                // [PASSO 1] Salva os dados na planilha como "Pendente" imediatamente
                await enviarParaGoogle({
                    token_seguranca: "9921",
                    acao: "criar_pendente",
                    nome: dados.nome,
                    cpf: dados.cpf,
                    email: dados.email,
                    contato: dados.contato,
                    tamanhoCamisa: dados.tamanhoCamisa,
                    emergencia: dados.emergencia
                });

                // [PASSO 2] Gera o pagamento na API do Render
                const rota = dados.metodo_pagamento === "cartao" ? "/gerar-cartao-pagamento" : "/gerar-link-pagamento";
                const res = await fetch(URL_SERVIDOR + rota, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(dados)
                });
                
                const data = await res.json();

                if (dados.metodo_pagamento === "cartao" && data.link_cartao) {
                    // Cartão vai direto para o checkout do Mercado Pago
                    window.location.href = data.link_cartao;
                } else if (data.qr_code_base64) {
                    // Esconde o formulário e exibe o QR Code do Pix na tela
                    document.querySelector('.checkout').style.display = 'none';
                    const areaPix = document.getElementById('area-pix');
                    areaPix.style.display = 'block';
                    
                    document.getElementById('imagem-qrcode').src = `data:image/png;base64,${data.qr_code_base64}`;
                    document.getElementById('texto-copia-cola').value = data.copia_e_cola;

                    // Adiciona uma mensagem visual para avisar o atleta que a tela mudará sozinha
                    const avisoVisual = document.createElement("div");
                    avisoVisual.innerHTML = `
                        <p style="margin-top:20px; text-align:center; font-weight:bold; color:#28a745; animation: blink 1.5s infinite;">
                            🔄 Aguardando pagamento... A página atualizará automaticamente!
                        </p>
                    `;
                    areaPix.appendChild(avisoVisual);

                    // 🚀 SISTEMA DE REDIRECIONAMENTO AUTOMÁTICO ULTRAVELOZ (SEM PRECISAR CLICAR)
                    const pagamentoId = data.id; // ID retornado pelo Mercado Pago
                    const emailAtleta = dados.email;

                    const checarStatusPix = setInterval(async () => {
                        try {
                            // Consulta a rota /verificar-pagamento que já está no seu main.py
                            const resposta = await fetch(`${URL_SERVIDOR}/verificar-pagamento/${pagamentoId}?email=${encodeURIComponent(emailAtleta)}`);
                            const resultado = await resposta.json();

                            console.log("Checando Pix... Status retornado:", resultado.status);

                            // Assim que o Mercado Pago retornar 'approved', joga para o Netlify na hora
                            if (resultado.status === "approved") {
                                clearInterval(checarStatusPix); // Interrompe o loop imediatamente
                                
                                // Abre o WhatsApp em segundo plano antes de sair da página
                                const msg = `Olá! Realizei o pagamento PIX e minha inscrição já foi confirmada. Nome: ${dados.nome}`;
                                window.open(`https://wa.me/5582999999999?text=${encodeURIComponent(msg)}`, '_blank');
                                
                                // Redireciona de forma instantânea para a página de agradecimento (com https:// correto)
                                window.location.href = "https://cheery-fox-9fdceb.netlify.app/"; 
                            }
                        } catch (erro) {
                            console.error("Erro ao verificar status do Pix:", erro);
                        }
                    }, 500); // 🚀 500ms = Executa duas vezes por segundo para garantir atraso ZERO

                } else {
                    throw new Error("Resposta inválida do servidor");
                }
            } catch (err) {
                alert("Erro ao processar: " + err.message);
                btn.disabled = false;
                btn.innerText = "FINALIZAR INSCRIÇÃO";
            }
        });
    }
});
