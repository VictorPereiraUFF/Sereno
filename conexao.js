// ===============================
//  SERENO — Frontend Controller
// ===============================

const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    setupMicSimulation();
    loadScripts();
    setupChat();
    setupTranslator(); // <--- Novo Tradutor
    setupBrownNoise(); // <--- Ruído Marrom (organizado em função)
});

// ===============================
// 1. Scripts Sociais (Híbrido)
// ===============================
async function loadScripts() {
    const container = document.getElementById("scriptsList");
    
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
        const res = await fetch(`${API_URL}/scripts`);
        if(!res.ok) throw new Error("Offline");
        
        const scripts = await res.json();
        if (scripts.length === 0) throw new Error("Lista vazia");

        container.innerHTML = "";
        scripts.forEach(s => renderScript(s.message));

    } catch (e) {
        console.warn("Backend offline. Carregando scripts de emergência.");
        container.innerHTML = "";
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

window.falarTexto = function(texto) {
    const utterance = new SpeechSynthesisUtterance(texto);
    utterance.lang = "pt-BR";
    window.speechSynthesis.speak(utterance);
};

// ===============================
// 2. Chat Multimodal
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

    if(attachBtn) attachBtn.addEventListener("click", () => mediaInput.click());

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

    async function sendMessage() {
        const text = userTextInput.value.trim();
        if (!text && !selectedFileBase64) return;

        let userHtml = text;
        if(selectedFileBase64) userHtml += " <br><small>📎 [Imagem]</small>";
        appendMessage(userHtml, true);

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
            loadingDiv.innerText = data.resposta;
        } catch (e) {
            loadingDiv.innerText = "Erro: Servidor offline.";
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
// 3. Tradutor de Intenção (Novo)
// ===============================
function setupTranslator() {
    const rawInput = document.getElementById("rawInput");
    const translateBtn = document.getElementById("translateBtn");
    const resultBox = document.getElementById("politeResult");
    const resultText = document.getElementById("translatedText");

    if(translateBtn) {
        translateBtn.addEventListener("click", async () => {
            const texto = rawInput.value.trim();
            if(!texto) return;

            translateBtn.innerText = "⏳ ...";
            translateBtn.disabled = true;

            try {
                const res = await fetch(`${API_URL}/api/suavizar`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ texto: texto })
                });
                const data = await res.json();
                
                resultText.innerText = data.revisado;
                resultBox.classList.remove("hidden");
            } catch (e) {
                alert("Erro ao conectar com a IA.");
            } finally {
                translateBtn.innerText = "✨ Suavizar";
                translateBtn.disabled = false;
            }
        });
    }

    if(rawInput) rawInput.addEventListener("keypress", (e) => {
        if(e.key === "Enter") translateBtn.click();
    });
}

window.copiarTraducao = function() {
    const texto = document.getElementById("translatedText").innerText;
    navigator.clipboard.writeText(texto);
    alert("Copiado!");
};

// ===============================
// 4. Ruído Marrom (Brown Noise)
// ===============================
function setupBrownNoise() {
    const noiseBtn = document.getElementById("noiseBtn");
    let audioContext = null;
    let noiseSource = null;
    let isPlaying = false;

    if (noiseBtn) {
        noiseBtn.addEventListener("click", () => {
            if (!isPlaying) {
                if (!audioContext) audioContext = new (window.AudioContext || window.webkitAudioContext)();
                
                const bufferSize = audioContext.sampleRate * 5; 
                const buffer = audioContext.createBuffer(1, bufferSize, audioContext.sampleRate);
                const data = buffer.getChannelData(0);

                let lastOut = 0;
                for (let i = 0; i < bufferSize; i++) {
                    const white = Math.random() * 2 - 1;
                    lastOut = (lastOut + (0.02 * white)) / 1.02;
                    data[i] = lastOut * 3.5; 
                }

                noiseSource = audioContext.createBufferSource();
                noiseSource.buffer = buffer;
                noiseSource.loop = true;
                
                const gainNode = audioContext.createGain();
                gainNode.gain.value = 0.5;
                
                noiseSource.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                noiseSource.start();
                isPlaying = true;
                noiseBtn.innerText = "⏹ Parar";
                noiseBtn.classList.add("warn");
            } else {
                if (noiseSource) noiseSource.stop();
                isPlaying = false;
                noiseBtn.innerText = "▶ Tocar";
                noiseBtn.classList.remove("warn");
            }
        });
    }
}

// ===============================
// 5. Simulação Sensores
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