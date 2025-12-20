// ===============================
//  SERENO — Frontend Controller
// ===============================

// Backend unificado (FastAPI)
const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    setupMicSimulation();
    loadScripts(); // Carrega scripts (online ou offline)
    setupChat();
});

// ===============================
// 1. Scripts Sociais (Com Fallback Offline)
// ===============================
async function loadScripts() {
    const container = document.getElementById("scriptsList");

    // Função auxiliar para desenhar o script na tela (evita repetição)
    const renderScript = (msg) => {
        const item = document.createElement("div");
        item.className = "script-item";
        item.innerHTML = `
            <div class="text">"${msg}"</div>
            <div style="display:flex;gap:8px">
                <button class="btn ghost" onclick="navigator.clipboard.writeText('${msg}')">Copiar</button>
                <button class="btn" onclick="falarTexto('${msg}')">Falar</button>
            </div>
        `;
        container.appendChild(item);
    };

    try {
        // Tenta buscar do servidor
        const res = await fetch(`${API_URL}/scripts`);
        if(!res.ok) throw new Error("Offline");
        
        const scripts = await res.json();
        
        // Se o servidor retornar lista vazia, usa fallback também
        if (scripts.length === 0) throw new Error("Lista vazia");

        container.innerHTML = "";
        scripts.forEach(s => renderScript(s.message));

    } catch (e) {
        console.warn("Backend offline ou sem dados. Carregando scripts de emergência.");
        container.innerHTML = "";
        
        // --- ADIÇÃO: Scripts Rápidos (Offline) ---
        const scriptsLocais = [
            "Preciso de um minuto para processar isso.",
            "O ambiente está muito barulhento para mim.",
            "Poderia repetir mais devagar, por favor?",
            "Prefiro continuar essa conversa por texto.",
            "Não estou me sentindo bem, preciso sair."
        ];
        scriptsLocais.forEach(msg => renderScript(msg));
    }
}

// Função Global de Fala
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
            loadingDiv.innerText = "Erro de conexão (Backend Offline). Tente novamente mais tarde.";
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
                    // Tenta enviar log silencioso, se falhar não faz nada
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