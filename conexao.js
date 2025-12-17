// ===============================
//  SERENO — Integração Frontend <-> Backend
// ===============================

const API_FASTAPI = "http://localhost:8000"; // Backend Principal
const API_FLASK = "http://localhost:5000";   // Backend IA

// ===============================
// 1. Carregar Scripts Sociais (do FastAPI)
// ===============================
async function loadScripts() {
    try {// ===============================
//  SERENO — Frontend Controller
// ===============================

// Agora usamos APENAS UM backend
const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    setupMicSimulation();
    loadScripts();
    setupChat();
});

// ===============================
// 1. Scripts Sociais (Do Banco de Dados)
// ===============================
async function loadScripts() {
    const container = document.getElementById("scriptsList");
    try {
        const res = await fetch(`${API_URL}/scripts`);
        const scripts = await res.json();
        
        container.innerHTML = "";
        scripts.forEach(s => {
            const item = document.createElement("div");
            item.className = "script-item";
            item.innerHTML = `
                <div class="text">"${s.message}"</div>
                <div style="display:flex;gap:8px">
                    <button class="btn ghost" onclick="falarTexto('${s.message}')">Falar</button>
                </div>
            `;
            container.appendChild(item);
        });
    } catch (e) {
        container.innerHTML = "<small>Erro ao carregar scripts do servidor.</small>";
    }
}

window.falarTexto = function(texto) {
    const utterance = new SpeechSynthesisUtterance(texto);
    utterance.lang = "pt-BR";
    window.speechSynthesis.speak(utterance);
};

// ===============================
// 2. Chat Multimodal (Texto + Imagem)
// ===============================
function setupChat() {
    const chatHistory = document.getElementById("chatHistory");
    const userTextInput = document.getElementById("userTextInput");
    const sendBtn = document.getElementById("sendBtn");
    const attachBtn = document.getElementById("attachBtn");
    const mediaInput = document.getElementById("mediaInput");
    const filePreview = document.getElementById("filePreview");
    const fileNameLabel = document.getElementById("fileName");
    const clearFileBtn = document.getElementById("clearFile");

    let selectedFileBase64 = null;

    // Abrir arquivo
    if(attachBtn) attachBtn.addEventListener("click", () => mediaInput.click());

    // Converter imagem para Base64
    if(mediaInput) mediaInput.addEventListener("change", () => {
        const file = mediaInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64String = reader.result;
                selectedFileBase64 = base64String.split(",")[1];
                filePreview.classList.remove("hidden");
                fileNameLabel.innerText = file.name;
            };
            reader.readAsDataURL(file);
        }
    });

    if(clearFileBtn) clearFileBtn.addEventListener("click", () => {
        mediaInput.value = "";
        selectedFileBase64 = null;
        filePreview.classList.add("hidden");
    });

    // Enviar para FastAPI
    async function sendMessage() {
        const text = userTextInput.value.trim();
        if (!text && !selectedFileBase64) return;

        // UI Feedback
        let userHtml = text;
        if(selectedFileBase64) userHtml += " <br><small>📎 [Imagem]</small>";
        appendMessage(userHtml, true);

        // Limpeza UI
        userTextInput.value = "";
        filePreview.classList.add("hidden");
        const imgToSend = selectedFileBase64;
        selectedFileBase64 = null;

        const loadingDiv = appendMessage("Processando...", false);

        try {
            const res = await fetch(`${API_URL}/api/ia`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ texto: text, imagem: imgToSend })
            });
            const data = await res.json();
            
            // Atualiza resposta
            loadingDiv.innerText = data.resposta;
        } catch (e) {
            loadingDiv.innerText = "Erro de conexão com o servidor (Porta 8000).";
        }
    }

    function appendMessage(html, isUser) {
        const div = document.createElement("div");
        div.className = `message ${isUser ? "user-msg" : "ai-msg"}`;
        div.innerHTML = html;
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return div;
    }

    if(sendBtn) sendBtn.addEventListener("click", sendMessage);
    if(userTextInput) userTextInput.addEventListener("keypress", (e) => {
        if(e.key === "Enter") sendMessage();
    });
}

// ===============================
// 3. Simulação de Sensores
// ===============================
function setupMicSimulation() {
    const micSwitch = document.getElementById('micSwitch');
    const levelPct = document.getElementById('levelPct');
    const soundBar = document.getElementById('soundLevel');
    const logCount = document.getElementById('logCount');
    let logs = 0;
    let simLevel = 8;

    if(micSwitch) {
        micSwitch.parentElement.addEventListener('click', () => {
            micSwitch.classList.toggle('on');
        });

        setInterval(() => {
            if (micSwitch.classList.contains('on')) {
                simLevel = Math.min(100, Math.max(0, simLevel + (Math.random() * 20 - 10)));
                if(levelPct) levelPct.textContent = Math.round(simLevel) + '%';
                if(soundBar) soundBar.style.width = simLevel + '%';

                if (simLevel > 85) {
                    logs++;
                    if(logCount) logCount.textContent = logs;
                    // Envia log silencioso para o servidor
                    fetch(`${API_URL}/events`, {
                        method: "POST", 
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({type: "som_alto", value: simLevel})
                    }).catch(()=>{});
                }
            }
        }, 800);
    }

    const lowStimBtn = document.getElementById('lowStimBtn');
    if(lowStimBtn) {
        lowStimBtn.addEventListener('click', () => {
            document.body.classList.toggle('low-stimulus');
        });
    }
}
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