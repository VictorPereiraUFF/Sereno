// ===============================
//  SERENO — Integração Frontend <-> Backend
// ===============================

const API_FASTAPI = "http://localhost:8000"; // Backend Principal
const API_FLASK = "http://localhost:5000";   // Backend IA

// ===============================
// 1. Carregar Scripts Sociais (do FastAPI)
// ===============================
async function loadScripts() {
    try {
        // Tenta buscar do backend (porta 8000)
        const response = await fetch(`${API_FASTAPI}/scripts`);
        
        if (!response.ok) throw new Error("Falha ao buscar scripts");

        const scripts = await response.json();
        const container = document.getElementById("scriptsList");

        if (scripts.length > 0) {
            container.innerHTML = ""; // Limpa os exemplos hardcoded do HTML
            
            scripts.forEach(script => {
                const item = document.createElement("div");
                item.className = "script-item";
                item.innerHTML = `
                    <div class="text">"${script.message}"</div>
                    <div style="display:flex;gap:8px">
                        <button class="btn ghost" onclick="navigator.clipboard.writeText('${script.message}')">Copiar</button>
                        <button class="btn" onclick="falarTexto('${script.message}')">Falar</button>
                    </div>
                `;
                container.appendChild(item);
            });
        }
    } catch (error) {
        console.warn("Backend offline, usando scripts visuais padrão.", error);
    }
}

// ===============================
// 2. Integração com IA Social (do Flask)
// ===============================
const suggestBtn = document.getElementById("suggestBtn");

if (suggestBtn) {
    suggestBtn.addEventListener("click", async () => {
        const originalText = suggestBtn.innerText;
        suggestBtn.innerText = "Pensando...";
        
        try {
            // Envia uma situação genérica para a IA (pode ser customizado)
            const response = await fetch(`${API_FLASK}/api/social-helper`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ situation: "Estou em um lugar barulhento e me sentindo sobrecarregado." })
            });

            const data = await response.json();
            alert(`Sugestão da IA: \n\n${data.response}`);
            
        } catch (error) {
            alert("Não foi possível conectar à IA Auxiliar (Porta 5000).");
        } finally {
            suggestBtn.innerText = originalText;
        }
    });
}

// ===============================
// 3. Utilitários (TTS e Logs)
// ===============================

// Função para o navegador "falar" o texto (Acessibilidade)
window.falarTexto = function(texto) {
    const utterance = new SpeechSynthesisUtterance(texto);
    utterance.lang = "pt-BR";
    window.speechSynthesis.speak(utterance);
};

// Hook no log de eventos (conecta com a simulação do HTML)
// Observa mudanças no contador de logs para enviar ao backend
const logCountElement = document.getElementById("logCount");
if(logCountElement) {
    const observer = new MutationObserver(async () => {
        const count = parseInt(logCountElement.innerText);
        if (count > 0) {
            // Envia evento de 'pico_som' para o FastAPI
            try {
                await fetch(`${API_FASTAPI}/events`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        event_type: "pico_som",
                        value: 80.0, // Valor simulado
                        device_id: "browser_client",
                        timestamp: new Date().toISOString()
                    })
                });
                console.log("Evento registrado no servidor.");
            } catch (e) {
                console.warn("Erro ao salvar log no servidor.");
            }
        }
    });
    observer.observe(logCountElement, { childList: true });
}

// Inicializa
document.addEventListener("DOMContentLoaded", () => {
    loadScripts();
});