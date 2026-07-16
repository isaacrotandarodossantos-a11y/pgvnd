const URL_SERVIDOR = "https://pgvnd.onrender.com";
const URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbw0PtbqTkA0Q7KIP1lnPX5BtMVmRW0q0m64ser2hJaxVBgaqI_zgirBr8OFBlb4nq58/exec";

// Função global auxiliar para enviar dados ao Google Script via JSONP sem erro de CORS
function enviarParaGoogle(dados) {
    return new Promise((resolve) => {
        const callbackName = "googleCallback_" + Date.now();
        window[callbackName] = function(resposta) {
            delete window[callbackName];
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
                // [PASSO 1 NOVO] Salva os dados na planilha como "Pendente" imediatamente
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

                // 2. Gera o pagamento na API do Render
                const rota = dados.metodo_pagamento === "cartao" ? "/gerar-cartao-pagamento" : "/gerar-link-pagamento";
                const res = await fetch(URL_SERVIDOR + rota, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(dados)
                });
                
                const data = await res.json();

                if (dados.metodo_pagamento === "cartao" && data.link_cartao) {
                    window.location.href = data.link_cartao;
                } else if (data.qr_code_base64) {
                    document.querySelector('.checkout').style.display = 'none';
                    const areaPix = document.getElementById('area-pix');
                    areaPix.style.display = 'block';
                    
                    document.getElementById('imagem-qrcode').src = `data:image/png;base64,${data.qr_code_base64}`;
                    document.getElementById('texto-copia-cola').value = data.copia_e_cola;

                    // Criar botão de Confirmação Manual e WhatsApp
                    const areaBotoes = document.createElement("div");
                    areaBotoes.innerHTML = `
                        <button id="btnConfirmarManual" style="margin-top:20px; padding:15px; width:100%; background:#007bff; color:white; border:none; border-radius:5px;">
                            CONFIRMAR PAGAMENTO E CHAMAR NO WHATSAPP
                        </button>
                    `;
                    areaPix.appendChild(areaBotoes);

                    document.getElementById("btnConfirmarManual").addEventListener("click", async () => {
                        const btnManual = document.getElementById("btnConfirmarManual");
                        btnManual.innerText = "CONFIRMANDO...";
                        
                        // [PASSO 3 CORRIGIDO] Atualiza para "Pago" via JSONP para evitar CORS
                        await enviarParaGoogle({
                            token_seguranca: "9921",
                            acao: "confirmar_pagamento",
                            email: dados.email
                        });

                        // Abre o WhatsApp
                        const msg = `Olá! Acabei de realizar o pagamento PIX da minha inscrição. Nome: ${dados.nome}`;
                        window.open(`https://wa.me/5582999999999?text=${encodeURIComponent(msg)}`, '_blank');
                        
                        alert("Confirmação enviada! Você será redirecionado.");
                        window.location.href = "https://seu-site-final.netlify.app";
                    });

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
