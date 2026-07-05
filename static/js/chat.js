document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input-text');
    const btnSend = document.getElementById('btn-chat-send');
    const btnVoice = document.getElementById('btn-voice-rec');
    const micIcon = document.getElementById('mic-icon');
    const messagesBox = document.getElementById('chat-messages-box');
    const suggestions = document.getElementById('chat-suggestions');

    let recognition = null;
    let isRecording = false;
    let chatLanguageOverride = null;

    // Set up override behavior for local lang pills
    const langPills = document.querySelectorAll('.lang-pill');
    langPills.forEach(pill => {
        pill.addEventListener('click', () => {
            const selectedLang = pill.getAttribute('data-lang');
            if (chatLanguageOverride === selectedLang) {
                chatLanguageOverride = null;
                pill.classList.remove('active');
            } else {
                langPills.forEach(p => p.classList.remove('active'));
                chatLanguageOverride = selectedLang;
                pill.classList.add('active');
            }
        });
    });

    // Listen for global languageChanged custom event
    document.addEventListener('languageChanged', (e) => {
        chatLanguageOverride = null;
        langPills.forEach(p => p.classList.remove('active'));
        if (recognition) {
            const langMap = {
                'hi': 'hi-IN', 'en': 'en-IN', 'mr': 'mr-IN', 'gu': 'gu-IN', 'bn': 'bn-IN',
                'pa': 'pa-IN', 'ta': 'ta-IN', 'te': 'te-IN', 'kn': 'kn-IN', 'ml': 'ml-IN',
                'or': 'or-IN', 'ur': 'ur-IN', 'as': 'as-IN'
            };
            recognition.lang = langMap[e.detail] || 'hi-IN';
        }
    });

    // Web Speech Recognition setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'hi-IN'; // Default to listen for Hindi / bilingual

        recognition.onstart = () => {
            isRecording = true;
            micIcon.className = 'fas fa-stop text-danger';
            btnVoice.style.background = 'rgba(230, 57, 70, 0.15)';
            Toast.info("बोलना शुरू करें... / Listening...", "Speak into your microphone...");
        };

        recognition.onend = () => {
            isRecording = false;
            micIcon.className = 'fas fa-microphone';
            btnVoice.style.background = '';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            sendChatMessage(transcript);
        };

        recognition.onerror = (evt) => {
            console.error("Speech recognition error", evt);
            Toast.error("आवाज इनपुट विफल हुआ", "Speech input failed or timed out");
        };
    } else {
        btnVoice.title = "Web Speech is not supported in this browser";
        btnVoice.style.opacity = '0.5';
    }

    // Toggle speech recognition
    btnVoice.addEventListener('click', () => {
        if (!recognition) {
            Toast.error("आपका ब्राउज़र वॉइस इनपुट का समर्थन नहीं करता है।", "Speech recognition not supported in this browser.");
            return;
        }
        if (isRecording) {
            recognition.stop();
        } else {
            const curLang = chatLanguageOverride || localStorage.getItem('kisanLanguage') || 'hi';
            const langMap = {
                'hi': 'hi-IN', 'en': 'en-IN', 'mr': 'mr-IN', 'gu': 'gu-IN', 'bn': 'bn-IN',
                'pa': 'pa-IN', 'ta': 'ta-IN', 'te': 'te-IN', 'kn': 'kn-IN', 'ml': 'ml-IN',
                'or': 'or-IN', 'ur': 'ur-IN', 'as': 'as-IN'
            };
            recognition.lang = langMap[curLang] || 'hi-IN';
            recognition.start();
        }
    });

    // Send Message Handler
    btnSend.addEventListener('click', () => {
        const query = chatInput.value.trim();
        if (query) {
            sendChatMessage(query);
        }
    });

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const query = chatInput.value.trim();
            if (query) {
                sendChatMessage(query);
            }
        }
    });

    // Suggestion chip binding
    suggestions.addEventListener('click', (e) => {
        const chip = e.target.closest('.suggestion-chip');
        if (chip) {
            const query = chip.getAttribute('data-query');
            sendChatMessage(query);
        }
    });

    // Send chat to Flask API
    async function sendChatMessage(queryText) {
        // Clear input
        chatInput.value = '';

        // Render User Message
        appendMessage(queryText, '', 'user');

        // Render loading state
        const loadingBubble = document.createElement('div');
        loadingBubble.className = 'msg-bubble msg-ai loading-dots';
        loadingBubble.innerHTML = '<span>उत्तर तैयार हो रहा है... / Thinking...</span>';
        messagesBox.appendChild(loadingBubble);
        scrollChat();

        const curLang = chatLanguageOverride || localStorage.getItem('kisanLanguage') || 'hi';
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: queryText,
                    lang: curLang
                })
            });
            const data = await response.json();
            
            // Remove loading bubble
            loadingBubble.remove();

            if (data.success) {
                // Render AI Message
                appendMessage(data.reply_hi, data.reply_en, 'ai', data.audio_url);
                
                // Play audio response automatically if available
                if (data.audio_url) {
                    playVoiceMessage(data.audio_url);
                }
            } else {
                appendMessage(`क्षमा करें, मुझे समझने में समस्या हुई। त्रुटि: ${data.error}`, `Sorry, I encountered an error: ${data.error}`, 'ai');
            }
        } catch (err) {
            console.error("Chat error", err);
            loadingBubble.remove();
            appendMessage("सर्वर से संपर्क करने में असमर्थ। कृपया बाद में प्रयास करें।", "Cannot connect to server. Try again later.", 'ai');
        }
    }

    // Append bubble helper
    function appendMessage(hiText, enText, sender, audioUrl = '') {
        const bubble = document.createElement('div');
        bubble.className = `msg-bubble msg-${sender}`;

        if (sender === 'user') {
            bubble.innerHTML = `<div class="hi-text">${hiText}</div>`;
        } else {
            let audioBtn = '';
            if (audioUrl) {
                audioBtn = `
                    <div class="msg-audio-play" onclick="playVoiceMessage('${audioUrl}')">
                        <i class="fas fa-volume-up"></i>
                        <span>सुनें / Listen Audio</span>
                    </div>
                `;
            }
            bubble.innerHTML = `
                <div class="bilingual-text">
                    <span class="hi-text">${hiText}</span>
                    <span class="en-text" style="color:var(--text-muted); font-size:0.8rem;">${enText}</span>
                </div>
                ${audioBtn}
            `;
        }

        messagesBox.appendChild(bubble);
        scrollChat();
    }

    function scrollChat() {
        messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    // Voice response player
    window.playVoiceMessage = function(url) {
        if (!url) return;
        Toast.info("ऑडियो प्ले हो रहा है...", "Playing synthesized voice...");
        const audio = new Audio(url);
        audio.play().catch(e => {
            console.error("Audio playback error", e);
            Toast.error("ऑडियो प्ले करने में त्रुटि", "Could not play voice file");
        });
    };
});
