// ===============================
//  SERENO — Frontend Controller
// ===============================

const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    setupTheme();       
    setupBattery();     
    setupMicSimulation();
    setupLightSimulation();
    setupVisualMasking();
    loadScripts();
    setupChat();
    setupTranslator();
    setupBrownNoise();
    carregarDashboard();
    setupEnergyBudget();
    setupPanicButton();
    setupSensoryProfile();
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
// 0. Bateria Social (Com Persistência Temporária)
// ===============================
function setupBattery() {
    const slider = document.getElementById("socialBattery");
    const icon = document.getElementById("batteryIcon");
    const pct = document.getElementById("batteryPct");
    const advice = document.getElementById("batteryAdvice");

    if (!slider) return;

    // --- CONFIGURAÇÃO DO TEMPO DE EXPIRAÇÃO ---
    // Define por quanto tempo (em horas) o valor deve ser lembrado
    const HORAS_EXPIRACAO = 4; 
    const TEMPO_LIMITE_MS = HORAS_EXPIRACAO * 60 * 60 * 1000; 

    const bateriaSalva = localStorage.getItem("sereno_bateria_valor");
    const timestampSalvo = localStorage.getItem("sereno_bateria_timestamp");

    if (bateriaSalva && timestampSalvo) {
        const agora = Date.now();
        // Se o tempo decorrido for menor que o limite, recupera o valor salvo
        if (agora - parseInt(timestampSalvo) < TEMPO_LIMITE_MS) {
            slider.value = bateriaSalva;
        } else {
            // Se o tempo expirou, remove os registros antigos e volta para 80%
            slider.value = 80;
            localStorage.removeItem("sereno_bateria_valor");
            localStorage.removeItem("sereno_bateria_timestamp");
        }
    }

    // Dispara enquanto o usuário arrasta a barra ou quando atualizado via IA
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

        // --- SALVA O ESTADO ATUAL E O MOMENTO DA MUDANÇA ---
        localStorage.setItem("sereno_bateria_valor", val);
        localStorage.setItem("sereno_bateria_timestamp", Date.now());
    });

    // Atualiza imediatamente os componentes visuais (ícones/cores) ao carregar a página
    slider.dispatchEvent(new Event('input'));

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
            
            // 2. ATUALIZA O GRÁFICO EM TEMPO REAL!
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

        // LÊ A PREFERÊNCIA DO USUÁRIO SALVA NO NAVEGADOR
        const perfilSaved = JSON.parse(localStorage.getItem("sereno_sensory_profile") || "{}");
        const estiloEscolhido = perfilSaved.estiloIA || "direct";

        // LÊ O NÍVEL ATUAL DA BATERIA SOCIAL, para a IA adaptar o tom da resposta
        const sliderBateria = document.getElementById("socialBattery");
        const bateriaAtual = sliderBateria ? parseInt(sliderBateria.value) : null;

        try {
            const res = await fetch(`${API_URL}/api/ia`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    texto: text, 
                    imagem: imgToSend,
                    estilo: estiloEscolhido,
                    bateria_atual: bateriaAtual
                })
            });
            const data = await res.json();
            loadingDiv.innerText = data.resposta;
        } catch (e) {
            loadingDiv.innerText = "Não consegui me conectar agora. Tente de novo em instantes.";
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
                alert("Não consegui me conectar agora. Tente de novo em instantes.");
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
// 4. Mascaramento Sonoro (Avançado)
// ===============================
function setupBrownNoise() {
    const noiseBtn = document.getElementById("noiseBtn");
    const noiseType = document.getElementById("noiseType");
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
                let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
                
                const selectedType = noiseType ? noiseType.value : 'brown'; 

                for (let i = 0; i < bufferSize; i++) {
                    const white = Math.random() * 2 - 1;
                    
                    if (selectedType === 'brown') {
                        lastOut = (lastOut + (0.02 * white)) / 1.02;
                        data[i] = lastOut * 3.5; 
                        
                    } else if (selectedType === 'white') {
                        data[i] = white * 0.05; 
                        
                    } else if (selectedType === 'pink') {
                        b0 = 0.99886 * b0 + white * 0.0555179;
                        b1 = 0.99332 * b1 + white * 0.0750759;
                        b2 = 0.96900 * b2 + white * 0.1538520;
                        b3 = 0.86650 * b3 + white * 0.3104856;
                        b4 = 0.55000 * b4 + white * 0.5329522;
                        b5 = -0.7616 * b5 - white * 0.0168980;
                        data[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.04;
                        b6 = white * 0.115926;
                        
                    } else if (selectedType === 'ocean') {
                        lastOut = (lastOut + (0.02 * white)) / 1.02;
                        let osciladorLFO = (Math.sin(i / audioContext.sampleRate * 1.0) + 1) / 2;
                        let volumeOnda = 0.2 + (osciladorLFO * 0.8); 
                        data[i] = (lastOut * 3.5) * volumeOnda; 
                        
                    } else if (selectedType === 'rain') {
                        // Chuva: Usa as frequências do Ruído Rosa + gotas aleatórias
                        b0 = 0.99886 * b0 + white * 0.0555179;
                        b1 = 0.99332 * b1 + white * 0.0750759;
                        b2 = 0.96900 * b2 + white * 0.1538520;
                        let rosa = (b0 + b1 + b2 + white * 0.5) * 0.04;
                        // Simula gotas pingando (picos aleatórios bem raros)
                        let gota = (Math.random() > 0.9995) ? (Math.random() * 0.4) : 0; 
                        data[i] = (rosa * 1.8) + gota;

                    } else if (selectedType === 'wind') {
                        // Vento: Ruído marrom mais abafado com rajadas irregulares
                        lastOut = (lastOut + (0.01 * white)) / 1.01; 
                        // Duas ondas LFO diferentes misturadas quebram o padrão repetitivo
                        let lfo1 = (Math.sin(i / audioContext.sampleRate * 0.4) + 1) / 2;
                        let lfo2 = (Math.sin(i / audioContext.sampleRate * 0.15) + 1) / 2;
                        let volumeVento = 0.1 + (lfo1 * 0.4) + (lfo2 * 0.5); 
                        data[i] = (lastOut * 4.0) * volumeVento; 
                    }
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

        if (noiseType) {
            noiseType.addEventListener("change", () => {
                if (isPlaying) {
                    noiseBtn.click(); 
                }
            });
        }
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

// ===============================
// 7. Orçamento de Energia
// ===============================
function setupEnergyBudget() {
    const btn = document.getElementById("analyzePlanBtn");
    const input = document.getElementById("planInput");
    const resultBox = document.getElementById("planResult");
    const slider = document.getElementById("socialBattery");

    if (btn) {
        btn.addEventListener("click", async () => {
            const texto = input.value.trim();
            if (!texto) return;

            // Muda o botão para estado de carregamento
            btn.innerText = "⏳ Calculando custos...";
            btn.disabled = true;
            resultBox.classList.remove("hidden");
            resultBox.innerHTML = "<em>Analisando a carga cognitiva e sensorial do seu dia...</em>";
            resultBox.style.borderLeftColor = "#ff9800"; // Laranja (processando)

            try {
                // Pega o valor atual da barra de bateria
                const bateriaAtual = parseInt(slider.value);

                const res = await fetch(`${API_URL}/api/energia/prever`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ 
                        bateria_atual: bateriaAtual, 
                        atividades: texto 
                    })
                });

                const data = await res.json();
                
                // Formata o texto da IA substituindo quebras de linha por <br> para o HTML
                const analiseFormatada = data.analise.replace(/\n/g, '<br>');
                resultBox.innerHTML = analiseFormatada;

                // Muda a cor da borda dependendo se a palavra "sobrecarga" ou "crítico" aparecer na resposta
                if (data.analise.toLowerCase().includes("sobrecarga") || data.analise.toLowerCase().includes("crítico")) {
                    resultBox.style.borderLeftColor = "#f44336"; // Vermelho (Perigo)
                } else {
                    resultBox.style.borderLeftColor = "#4caf50"; // Verde (Seguro)
                }

            } catch (e) {
                console.error(e);
                resultBox.innerHTML = "Dificuldade ao conectar com o motor preditivo.";
            } finally {
                btn.innerText = "Calcular Orçamento Diário";
                btn.disabled = false;
            }
        });
    }
}

// ===============================
// 8. Perfil Sensorial & Botão de Emergência Customizado
// ===============================

function setupSensoryProfile() {
    const overlay = document.getElementById("sensoryOverlay");
    const form = document.getElementById("sensoryForm");
    
    // 💡 TRUQUE DE DESENVOLVIMENTO:
    // Descomente a linha abaixo se quiser que o questionário apareça SEMPRE ao dar F5 para testar o layout
    localStorage.removeItem("sereno_sensory_profile");

    const profileSaved = localStorage.getItem("sereno_sensory_profile");

    // Se NÃO tem perfil salvo, exibe o questionário
    if (!profileSaved) {
        if (overlay) overlay.classList.remove("hidden");
    } else {
        // Se já tem, aplica as preferências direto
        aplicarPreferenciasSensoriais(JSON.parse(profileSaved));
    }

    // Listener do envio do formulário
    if (form) {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            
            const perfil = {
                visual: document.getElementById("sensoryVisual").value,
                somEmergencia: document.getElementById("sensoryNoise").value,
                estiloIA: document.getElementById("sensoryAI").value,
                animacaoVisual: document.getElementById("sensoryVisualAnimation").value
            };

            localStorage.setItem("sereno_sensory_profile", JSON.stringify(perfil));
            aplicarPreferenciasSensoriais(perfil);
            if (overlay) overlay.classList.add("hidden");
        });
    }

    // AÇÃO DO NOVO BOTÃO: Reabrir o questionário para edição
    const reopenBtn = document.getElementById("reopenSensoryBtn");
    if (reopenBtn && overlay) {
        reopenBtn.addEventListener("click", () => {
            // Se já existiam preferências, preenche o form com o que estava salvo
            if (profileSaved) {
                const dados = JSON.parse(profileSaved);
                if(document.getElementById("sensoryVisual")) document.getElementById("sensoryVisual").value = dados.visual;
                if(document.getElementById("sensoryNoise")) document.getElementById("sensoryNoise").value = dados.somEmergencia;
                if(document.getElementById("sensoryAI")) document.getElementById("sensoryAI").value = dados.estiloIA;
                if(document.getElementById("sensoryVisualAnimation") && dados.animacaoVisual) document.getElementById("sensoryVisualAnimation").value = dados.animacaoVisual;
            }
            overlay.classList.remove("hidden"); // Traz a tela de volta!
        });
    }

    // AÇÃO DO BOTÃO DE LIMPAR: Apaga tudo do localStorage de forma limpa pelo app
    const clearBtn = document.getElementById("clearDataBtn");
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            if (confirm("Tem certeza que deseja redefinir o Sereno? Isso apagará suas preferências sensoriais e temas.")) {
                localStorage.clear();
                window.location.reload(); // Recarrega a página zerada
            }
        });
    }
}

function aplicarPreferenciasSensoriais(perfil) {
    if (!perfil) return;

    // 1. SINCRONIZA O SOM: Altera o select da interface principal para a escolha do usuário
    const noiseSelect = document.getElementById("noiseType");
    if (noiseSelect && perfil.somEmergencia) {
        noiseSelect.value = perfil.somEmergencia;
        
        // Dispara um evento de mudança caso seu script de áudio precise detectar a troca
        noiseSelect.dispatchEvent(new Event('change'));
    }

    // 2. SINCRONIZA O VISUAL: Aplica o modo de baixa estimulação e conforto visual
    if (perfil.visual === "high") {
        document.body.classList.add("low-stimulus");
        
        // Ativa o Dark Mode junto para dar o conforto imediato contra a luz forte
        document.body.classList.add("dark-mode");
        
        // Sincroniza o ícone do botão de tema lá do topo
        const themeBtn = document.getElementById("themeBtn");
        if (themeBtn) themeBtn.innerText = "☀️";
    } else {
        document.body.classList.remove("low-stimulus");
    }

    // 3. SINCRONIZA A ANIMAÇÃO VISUAL: Altera o select da interface principal para a escolha do usuário
    const visualSelect = document.getElementById("visualType");
    if (visualSelect && perfil.animacaoVisual) {
        visualSelect.value = perfil.animacaoVisual;
    }
}

// ATUALIZAÇÃO: O botão de pânico agora obedece o questionário!
function setupPanicButton() {
    const panicBtn = document.getElementById("panicBtn");
    
    if (panicBtn) {
        panicBtn.addEventListener("click", () => {
            document.body.classList.add("low-stimulus");
            
            // Recupera o som preferido do questionário (se não achar, usa 'brown' como padrão)
            let somPreferido = "brown";
            const perfilSalvo = localStorage.getItem("sereno_sensory_profile");
            if (perfilSalvo) {
                somPreferido = JSON.parse(perfilSalvo).somEmergencia;
            }

            const noiseSelect = document.getElementById("noiseType");
            const noiseBtn = document.getElementById("noiseBtn");
            
            if (noiseSelect && noiseBtn) {
                noiseSelect.value = somPreferido; // Ativa o som configurado no questionário!
                if (noiseBtn.innerText.includes("Tocar")) {
                    noiseBtn.click();
                }
            }

            const focusCard = document.querySelector(".focus-card");
            if (focusCard) {
                focusCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }
}

// ===============================
// 9. Monitoramento de Luz e Brilho
// ===============================
function setupLightSimulation() {
    const lightBtn = document.getElementById("lightBtn");
    const video = document.getElementById("lightVideo");
    const display = document.getElementById("lightDisplay");
    const icon = document.getElementById("lightIcon");
    
    let streamActive = false;
    let localStream = null;
    let animationFrameId = null;
    
    // NOVO: Variável de cooldown para não sobrecarregar o servidor
    let ultimoAlertaLuz = 0; 

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d", { willReadFrequently: true });

    if (!lightBtn || !video) return;

    lightBtn.addEventListener("click", async () => {
        if (!streamActive) {
            try {
                localStream = await navigator.mediaDevices.getUserMedia({ 
                    video: { width: 300, height: 200, facingMode: "user" } 
                });
                
                video.srcObject = localStream;
                streamActive = true;
                lightBtn.innerText = "🛑 Parar Monitoramento Visual";
                lightBtn.classList.remove("ghost");
                lightBtn.classList.add("warn");

                video.onloadedmetadata = () => {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    processarBrilho();
                };

            } catch (err) {
                console.error("Erro ao acessar a câmera: ", err);
                display.innerText = "Acesso à câmera negado ou indisponível.";
            }
        } else {
            pararMonitoramento();
        }
    });

    function processarBrilho() {
        if (!streamActive) return;

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        try {
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            let somaBrilho = 0;
            let totalPixels = 0;

            for (let i = 0; i < data.length; i += 20) {
                const r = data[i];
                const g = data[i+1];
                const b = data[i+2];

                const brilhoPixel = (0.299 * r) + (0.587 * g) + (0.114 * b);
                somaBrilho += brilhoPixel;
                totalPixels++;
            }

            const brilhoMedio = Math.round((somaBrilho / totalPixels) / 255 * 100);
            
            display.innerText = `Brilho: ${brilhoMedio}%`;

            if (brilhoMedio > 75) { 
                display.innerText += " - Ambiente Muito Claro!";
                display.style.color = "var(--danger)";
                icon.innerText = "⚠️💥";
                
                const sliderBateria = document.getElementById("socialBattery");
                if (sliderBateria && parseInt(sliderBateria.value) < 50) {
                    if (!document.body.classList.contains("low-stimulus")) {
                        document.body.classList.add("low-stimulus");
                        console.log("Sereno Engine: Modo Baixa Estimulação ativado por excesso de luz.");
                    }
                }

                // ==========================================
                // NOVO: Integração com o Backend (com Cooldown de 3s)
                // ==========================================
                const agora = Date.now();
                if (agora - ultimoAlertaLuz > 3000) {
                    ultimoAlertaLuz = agora;
                    
                    // Envia o evento para o Python
                    fetch(`${API_URL}/events`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({type: "luz_alta", value: brilhoMedio})
                    }).catch(()=>{});

                    // Atualiza o contador visual na tela (o mesmo usado pelo microfone)
                    const logCount = document.getElementById('logCount');
                    if (logCount) {
                        logCount.textContent = parseInt(logCount.textContent || 0) + 1;
                    }
                }
                // ==========================================

            } else if (brilhoMedio < 20) {
                display.style.color = "var(--text-muted)";
                icon.innerText = "🌙";
            } else {
                display.style.color = "var(--text-main)";
                icon.innerText = "😎";
            }

        } catch (e) {
            console.error("Erro ao analisar os pixels: ", e);
        }

        animationFrameId = requestAnimationFrame(processarBrilho);
    }

    function pararMonitoramento() {
        streamActive = false;
        lightBtn.innerText = "Iniciar Monitoramento Visual";
        lightBtn.classList.remove("warn");
        lightBtn.classList.add("ghost");
        display.innerText = "Brilho: Oculto";
        display.style.color = "var(--text-muted)";
        icon.innerText = "☀️";

        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
        }
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
    }
}

// ===============================
// 10. Mascaramento Visual Regulatório
// ===============================
function setupVisualMasking() {
    const openBtn = document.getElementById("visualMaskBtn");
    const closeBtn = document.getElementById("closeVisualMaskBtn");
    const overlay = document.getElementById("visualMaskOverlay");
    
    // Novos elementos capturados
    const visualTypeSelect = document.getElementById("visualType");
    const shapeElement = document.getElementById("visualShape");

    if (!openBtn || !overlay || !closeBtn) return;

    // Abre o modo de calmaria
    openBtn.addEventListener("click", () => {
        
        // Lê qual animação o usuário escolheu no menu
        if (visualTypeSelect && shapeElement) {
            const chosenType = visualTypeSelect.value;
            // Limpa as classes anteriores e aplica a nova
            shapeElement.className = ""; 
            shapeElement.classList.add("shape-" + chosenType);
        }

        // Exibe a tela
        overlay.classList.remove("visual-mask-hidden");
    });

    // Fecha o modo de calmaria
    closeBtn.addEventListener("click", () => {
        overlay.classList.add("visual-mask-hidden");
    });
}

// ===============================
// 11. Diário de Gatilhos
// ===============================
async function setupTriggerDiary() {
    const listContainer = document.getElementById("triggerList");
    const btnAnalyze = document.getElementById("analyzeTriggersBtn");
    const resultBox = document.getElementById("triggerAnalysisResult");

    if (!listContainer || !btnAnalyze) return;

    // Função para carregar a lista do banco
    async function carregarLista() {
        try {
            const res = await fetch(`${API_URL}/api/triggers`);
            const eventos = await res.json();

            listContainer.innerHTML = ""; // Limpa o "Carregando..."

            if (eventos.length === 0) {
                listContainer.innerHTML = "<p style='text-align:center; color:var(--text-muted); font-size:13px;'>Nenhum gatilho registrado ainda.</p>";
                return;
            }

            eventos.forEach(evento => {
                // Formata a data/hora
                const hora = new Date(evento.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                
                // Escolhe o ícone e a cor com base no tipo
                let icone = "📌";
                let nomeFormatado = evento.tipo;
                let cor = "var(--text-main)";

                if (evento.tipo === "som_alto") {
                    icone = "🔊";
                    nomeFormatado = "Ruído Elevado";
                    cor = "#ff9800";
                } else if (evento.tipo === "luz_alta") {
                    icone = "☀️";
                    nomeFormatado = "Excesso de Luz";
                    cor = "#f44336";
                }

                // Cria o item da lista
                const item = document.createElement("div");
                item.style.cssText = `display: flex; justify-content: space-between; align-items: center; padding: 10px; background: var(--input-bg); border: 1px solid var(--border-color); border-radius: 8px;`;
                item.innerHTML = `
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size: 18px;">${icone}</span>
                        <div>
                            <strong style="color: ${cor}; font-size: 14px;">${nomeFormatado}</strong><br>
                            <span style="font-size: 12px; color: var(--text-muted);">Nível medido: ${evento.valor}</span>
                        </div>
                    </div>
                    <span style="font-size: 12px; color: var(--text-muted); font-weight: bold;">${hora}</span>
                `;
                listContainer.appendChild(item);
            });

        } catch (e) {
            listContainer.innerHTML = "<p style='color:var(--danger);'>Não consegui carregar o diário agora. Tente de novo em instantes.</p>";
        }
    }

    // Chama a função de carregar assim que a página abre
    carregarLista();

    // Ação do botão de análise da IA
    btnAnalyze.addEventListener("click", async () => {
        btnAnalyze.innerText = "⏳ A IA está lendo seu diário...";
        btnAnalyze.disabled = true;
        resultBox.classList.remove("hidden");
        resultBox.innerHTML = "<em>Procurando padrões nos horários e gatilhos...</em>";

        try {
            const res = await fetch(`${API_URL}/api/triggers/analyze`, { method: "POST" });
            const data = await res.json();
            
            // Troca as quebras de linha por <br> para o HTML
            resultBox.innerHTML = data.analise.replace(/\n/g, '<br>');
        } catch (e) {
            resultBox.innerHTML = "Não consegui analisar os padrões agora. Tente de novo em instantes.";
        } finally {
            btnAnalyze.innerText = "✨ Analisar Padrões com IA";
            btnAnalyze.disabled = false;
        }
    });
}