// ===============================
//  SERENO — Frontend Controller
// ===============================

const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    setupTheme();       
    setupBattery();     
    setupMicSimulation();
    loadScripts();
    setupChat();
    setupTranslator();
    setupBrownNoise();
    carregarDashboard();
});

// ===============================
// -1. Modo Escuro
// ===============================
function setupTheme() {
    const themeBtn = document.getElementById("themeBtn");
    const savedTheme = localStorage.getItem("sereno_theme");
    
    if (savedTheme === "dark") {
        document.body.classList.add("dark-mode");
        themeBtn.innerText = "☀️";
    }

    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            if (document.body.classList.contains("dark-mode")) {
                localStorage.setItem("sereno_theme", "dark");
                themeBtn.innerText = "☀️";
            } else {
                localStorage.setItem("sereno_theme", "light");
                themeBtn.innerText = "🌙";
            }
        });
    }
}

// ===============================
// 0. Bateria Social
// ===============================
// ===============================
// 0. Bateria Social
// ===============================
function setupBattery() {
    const slider = document.getElementById("socialBattery");
    const icon = document.getElementById("batteryIcon");
    const pct = document.getElementById("batteryPct");
    const advice = document.getElementById("batteryAdvice");

    if (!slider) return;

    // Dispara enquanto o usuário arrasta a barra
    slider.addEventListener("input", () => {
        const val = parseInt(slider.value);
        pct.innerText = val + "%";
        
        // Lógica de ícones original
        if (val > 80) icon.innerText = "⚡";      
        else if (val > 40) icon.innerText = "🔋"; 
        else if (val > 20) icon.innerText = "🪫"; 
        else icon.innerText = "💀";               

        // NOVA LÓGICA DE CORES DA INTERFACE (3 Caminhos)
        if (val > 50) {
            pct.style.color = "#4caf50"; // Verde (Normal)
        } else if (val <= 50 && val >= 20) {
            pct.style.color = "#ff9800"; // Laranja/Amarelo (Alerta)
        } else if (val < 20) {
            pct.style.color = "#f44336"; // Vermelho (Crítico)
        }
    });

    // Dispara quando o usuário solta a barra
    slider.addEventListener("change", async () => {
        const val = parseInt(slider.value);
        advice.innerText = "Consultando o Sereno Engine...";
        advice.style.color = "var(--text-muted)";

        try {
            // 1. Salva no backend local (histórico)
            await fetch(`${API_URL}/api/battery`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ level: val })
            });
            
            // 2. ATUALIZA O GRÁFICO EM TEMPO REAL! <-- ADICIONE ESTA LINHA
            carregarDashboard();

            // 3. Chama a função que fala com o Webhook do Make
            buscarConselhoIA(val);

            // 4. Mantém a lógica de baixa estimulação
            if (val <= 20 && !document.body.classList.contains('low-stimulus')) {
               const confirmLow = confirm("Sua bateria social está crítica. Deseja ativar o modo Baixa Estimulação?");
               if(confirmLow) document.body.classList.add('low-stimulus');
            }

        } catch (e) {
            advice.innerText = "Erro ao conectar. Tente relaxar um pouco.";
            console.error(e);
        }
    });
}

// ===============================
// 0.5 Avaliador de Energia IA (NOVO)
// ===============================
async function analisarEnergiaViaIA(texto) {
    if(!texto) return;
    
    const advice = document.getElementById("batteryAdvice");
    if(advice) advice.innerText = "✨ IA calculando sua energia...";

    try {
        const res = await fetch(`${API_URL}/api/bateria/calcular`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ texto: texto })
        });
        const data = await res.json();
        
        // Mantém a compatibilidade com a variável atual
        const novoNivel = data.nivel !== undefined ? data.nivel : data.nivel_estimado;

        const slider = document.getElementById("socialBattery");
        if(slider) {
            slider.value = novoNivel;
            slider.dispatchEvent(new Event('input')); // Atualiza as cores e a porcentagem
            slider.dispatchEvent(new Event('change')); // Dispara o Webhook do Make que você já configurou!

            // NOVA LÓGICA: Alerta Preditivo (MMQ)
            if (data.previsao && data.previsao.alerta) {
                // O setTimeout dá tempo do Make responder, para não apagar nosso alerta matemático
                setTimeout(() => {
                    advice.style.color = "#f44336"; // Fica vermelho
                    // Junta o conselho do Make com o alerta preditivo
                    advice.innerHTML = `<strong>${data.previsao.mensagem}</strong><br>${advice.innerHTML}`;
                    
                    const icon = document.getElementById("batteryIcon");
                    if(icon) {
                        icon.innerText = "⚠️";
                        icon.classList.add("shake-animation"); // Inicia a animação de perigo
                    }
                }, 1500); 
            }
        }
    } catch (e) {
        console.error("Erro na leitura inteligente da bateria.", e);
    }
}

// ===============================
// 1. Scripts Sociais
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
        container.innerHTML = "";
        const scriptsLocais = [
            "Preciso de um minuto para processar isso.",
            "O ambiente está muito barulhento para mim.",
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

        // CHAMA A IA PARA LER A BATERIA AQUI!
        analisarEnergiaViaIA(text);

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
// 3. Tradutor de Intenção
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

            // CHAMA A IA PARA LER A BATERIA AQUI!
            analisarEnergiaViaIA(texto);

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
            // Alterna a classe na tela
            const isActive = document.body.classList.toggle('low-stimulus');
            
            // Envia a ordem para o Arduino ligar ou desligar o dispositivo físico!
            const comando = isActive ? '1' : '0';
            
            fetch(`${API_URL}/api/motor`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({estado: comando})
            })
            .then(res => res.json())
            .then(data => console.log("Resposta do Arduino:", data))
            .catch(err => console.error("Erro ao tentar acionar hardware:", err));
        });
    }
}

async function buscarConselhoIA(nivelBateria) {
    const webhookURL = "https://hook.us2.make.com/tbv3xye5m0pyhip99903cqal8q85ihon"; // COLE A URL DO WEBHOOK AQUI

    // Opcional: Mostrar um "Carregando..." na interface
    const campoTexto = document.getElementById('batteryAdvice'); // Verifique se o ID está correto no seu HTML
    if (campoTexto) campoTexto.innerText = "Consultando o Sereno Engine...";

    try {
        const response = await fetch(webhookURL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nivel: nivelBateria })
        });

        const data = await response.json();
        
        if (campoTexto) {
            campoTexto.innerText = data.conselho;
        }
        return data.conselho;

    } catch (error) {
        console.error("Erro na automação:", error);
        if (campoTexto) campoTexto.innerText = "Tire um momento para relaxar.";
    }
}

// ===============================
// 6. Dashboard de Impacto
// ===============================
let meuGrafico = null; // Variável global para guardar o gráfico e atualizá-lo depois

async function carregarDashboard() {
    const canvas = document.getElementById('impactChart');
    if (!canvas) return; 

    try {
        const res = await fetch(`${API_URL}/api/battery/history`);
        const historico = await res.json();

        // TRUQUE VISUAL: Se o banco estiver vazio, cria um ponto de partida para o gráfico não ficar invisível!
        if (historico.length === 0) {
            historico.push({ level: parseInt(document.getElementById("socialBattery").value) || 80, timestamp: new Date().toISOString() });
        }

        historico.reverse();

        const niveis = historico.map(registro => registro.level);
        const rotulos = historico.map(registro => {
            const data = new Date(registro.timestamp); 
            return `${data.getHours()}h${data.getMinutes().toString().padStart(2, '0')}`;
        });

        const ctx = canvas.getContext('2d');
        
        // Destrói o desenho antigo antes de injetar os dados novos (previne erros na tela)
        if (meuGrafico) {
            meuGrafico.destroy();
        }

        meuGrafico = new Chart(ctx, {
            type: 'line',
            data: {
                labels: rotulos,
                datasets: [{
                    label: 'Energia Social (%)',
                    data: niveis,
                    borderColor: '#4caf50', 
                    backgroundColor: 'rgba(76, 175, 80, 0.2)', 
                    borderWidth: 3,
                    tension: 0.4, 
                    fill: true,
                    pointRadius: 5,
                    pointBackgroundColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { 
                        beginAtZero: true, 
                        max: 100 
                    }
                },
                plugins: {
                    legend: { display: false } 
                }
            }
        });
    } catch (e) {
        console.error("Erro ao carregar os dados do Dashboard:", e);
    }
}