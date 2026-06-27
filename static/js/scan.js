document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video-stream');
    const canvas = document.getElementById('capture-canvas');
    const fileUploader = document.getElementById('file-uploader');
    const laser = document.getElementById('laser-line');
    const btnSnap = document.getElementById('btn-snap');
    const btnToggleCam = document.getElementById('btn-toggle-cam');
    const btnClearHistory = document.getElementById('btn-clear-history');
    const historyContainer = document.getElementById('history-container');
    const historyEmpty = document.getElementById('history-empty');

    const modeDiseaseBtn = document.getElementById('mode-disease');
    const modeQrcodeBtn = document.getElementById('mode-qrcode');
    const diseaseResultView = document.getElementById('result-disease-view');
    const qrcodeResultView = document.getElementById('result-qrcode-view');

    // State variables
    let currentMode = 'disease'; // 'disease' or 'qrcode'
    let stream = null;
    let cameraActive = false;

    // Mode selection handlers
    modeDiseaseBtn.addEventListener('click', () => {
        currentMode = 'disease';
        modeDiseaseBtn.classList.add('active');
        modeQrcodeBtn.classList.remove('active');
        diseaseResultView.style.display = 'block';
        qrcodeResultView.style.display = 'none';
        Toast.info("फसल रोग मोड सक्रिय किया गया", "Crop disease mode activated");
    });

    modeQrcodeBtn.addEventListener('click', () => {
        currentMode = 'qrcode';
        modeQrcodeBtn.classList.add('active');
        modeDiseaseBtn.classList.remove('active');
        qrcodeResultView.style.display = 'block';
        diseaseResultView.style.display = 'none';
        Toast.info("क्यूआर सत्यापन मोड सक्रिय किया गया", "Product QR verification mode activated");
    });

    // Camera Stream Management
    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: 640, height: 480 }
            });
            video.srcObject = stream;
            video.style.display = 'block';
            document.getElementById('no-camera-msg').style.display = 'none';
            cameraActive = true;
            laser.style.display = 'block';
        } catch (err) {
            console.error("Camera access failed", err);
            video.style.display = 'none';
            document.getElementById('no-camera-msg').style.display = 'block';
            cameraActive = false;
            laser.style.display = 'none';
        }
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
        }
        video.style.display = 'none';
        document.getElementById('no-camera-msg').style.display = 'block';
        cameraActive = false;
        laser.style.display = 'none';
    }

    btnToggleCam.addEventListener('click', () => {
        if (cameraActive) {
            stopCamera();
            btnToggleCam.innerHTML = '<i class="fas fa-video"></i> चालू करें / Start Cam';
        } else {
            startCamera();
            btnToggleCam.innerHTML = '<i class="fas fa-video-slash"></i> बंद करें / Stop Cam';
        }
    });

    // Capture Snap from Stream
    btnSnap.addEventListener('click', () => {
        if (!cameraActive) {
            Toast.error("कृपया पहले कैमरे को सक्षम करें या फ़ाइल अपलोड करें", "Please start camera or upload an image file");
            return;
        }

        // Add scan line sweep effect
        laser.style.animation = 'none';
        setTimeout(() => laser.style.animation = 'scanAnim 1s ease-in-out', 50);

        const ctx = canvas.getContext('2d');
        canvas.width = 300;
        canvas.height = 300;
        // Crop a square from the center of the video
        const minDim = Math.min(video.videoWidth, video.videoHeight);
        const sx = (video.videoWidth - minDim) / 2;
        const sy = (video.videoHeight - minDim) / 2;
        
        ctx.drawImage(video, sx, sy, minDim, minDim, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.85);

        sendImageToBackend(dataUrl);
    });

    // File Uploader handler
    fileUploader.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(evt) {
            const tempImg = new Image();
            tempImg.onload = function() {
                const ctx = canvas.getContext('2d');
                canvas.width = 300;
                canvas.height = 300;
                ctx.drawImage(tempImg, 0, 0, canvas.width, canvas.height);
                const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
                sendImageToBackend(dataUrl);
            };
            tempImg.src = evt.target.result;
        };
        reader.readAsDataURL(file);
    });

    // Send base64 image data to the Flask API
    async function sendImageToBackend(base64Image) {
        Toast.info("छवि का प्रसंस्करण हो रहा है...", "Analyzing image, please wait...");
        const curLang = localStorage.getItem('kisanLanguage') || 'hi';
        try {
            const response = await fetch('/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: base64Image,
                    mode: currentMode,
                    lang: curLang
                })
            });

            const data = await response.json();
            if (data.success) {
                if (currentMode === 'disease') {
                    displayDiseaseResult(data);
                    saveToHistory({
                        mode: 'disease',
                        image: base64Image,
                        crop_hi: data.crop_hi,
                        crop_en: data.crop,
                        disease_hi: data.disease_hi,
                        disease_en: data.disease,
                        pesticide: data.pesticide,
                        timestamp: new Date().toLocaleTimeString()
                    });
                    Toast.success("स्कैन पूर्ण: रोग की पहचान की गई", "Analysis Complete: Disease Identified");
                } else {
                    displayQRResult(data);
                    saveToHistory({
                        mode: 'qrcode',
                        image: base64Image,
                        qr_id: data.product_id,
                        verified: data.verified,
                        mfg: data.manufacturer,
                        name: data.name,
                        timestamp: new Date().toLocaleTimeString()
                    });
                    if (data.verified) {
                        Toast.success("सत्यापन सफल: उत्पाद असली है", "Verification Successful: Genuine Product");
                    } else {
                        Toast.error("चेतावनी: उत्पाद नकली या अपंजीकृत हो सकता है", "Warning: Counterfeit/Unregistered Product");
                    }
                }
            } else {
                Toast.error("स्कैन विफल: " + (data.message_hi || data.error), "Scan failed: " + data.error);
            }
        } catch (err) {
            console.error("Scan submission error", err);
            Toast.error("नेटवर्क त्रुटि: सर्वर से संपर्क नहीं हो सका", "Network Error: Could not reach server");
        }
    }

    // Display helpers
    function displayDiseaseResult(data) {
        document.getElementById('res-crop-hi').textContent = data.crop_hi || data.crop;
        document.getElementById('res-crop-en').textContent = data.crop || '';
        document.getElementById('res-disease-hi').textContent = data.disease_hi || data.disease;
        document.getElementById('res-disease-en').textContent = data.disease || '';
        document.getElementById('res-pesticide').textContent = data.pesticide || 'कोई सिफारिश नहीं / No recommendation';

        // Update dashboard cache
        localStorage.setItem('lastScanResult', JSON.stringify({
            disease: `${data.crop_hi || data.crop} (${data.disease_hi || data.disease})`,
            pesticide: data.pesticide,
            is_healthy: (data.disease || '').toLowerCase().includes('healthy')
        }));
    }

    function displayQRResult(data) {
        const badge = document.getElementById('qr-status-badge');
        document.getElementById('res-qr-id').textContent = data.product_id || 'अज्ञात / Unknown';
        document.getElementById('res-qr-mfg').textContent = data.manufacturer || 'अज्ञात / Unknown';
        
        if (data.verified) {
            badge.textContent = "असली उत्पाद / Genuine Product";
            badge.style.background = "rgba(82, 183, 136, 0.2)";
            badge.style.color = "var(--primary)";
        } else {
            badge.textContent = "नकली या अपंजीकृत / Counterfeit or Fake";
            badge.style.background = "rgba(230, 57, 70, 0.2)";
            badge.style.color = "#e63946";
        }
    }

    // Local Storage History Management
    function saveToHistory(item) {
        let history = JSON.parse(localStorage.getItem('kisanScanHistory')) || [];
        // Keep last 10 items
        history.unshift(item);
        if (history.length > 10) history.pop();
        localStorage.setItem('kisanScanHistory', JSON.stringify(history));
        renderHistory();
    }

    function renderHistory() {
        const history = JSON.parse(localStorage.getItem('kisanScanHistory')) || [];
        historyContainer.innerHTML = '';
        
        if (history.length === 0) {
            historyEmpty.style.display = 'block';
            return;
        }

        historyEmpty.style.display = 'none';
        history.forEach((item, index) => {
            const el = document.createElement('div');
            el.className = 'history-item';
            
            let titleHi = '';
            let subtitleHi = '';
            if (item.mode === 'disease') {
                titleHi = `${item.crop_hi} - ${item.disease_hi}`;
                subtitleHi = `कीटनाशक: ${item.pesticide}`;
            } else {
                titleHi = item.verified ? `असली: ${item.name || 'Agri Product'}` : `संदेहास्पद: नकली उत्पाद`;
                subtitleHi = `Mfg: ${item.mfg || 'N/A'}`;
            }

            el.innerHTML = `
                <img class="history-img" src="${item.image}" alt="scan thumb">
                <div class="bilingual-text" style="flex-grow:1;">
                    <span class="hi-text" style="font-size:0.85rem;">${titleHi}</span>
                    <span class="en-text" style="font-size:0.75rem;">${subtitleHi}</span>
                </div>
                <span style="font-size:0.7rem; color:var(--text-muted);">${item.timestamp}</span>
            `;

            el.addEventListener('click', () => {
                // Restore selection back to result views
                if (item.mode === 'disease') {
                    currentMode = 'disease';
                    modeDiseaseBtn.click();
                    displayDiseaseResult({
                        crop: item.crop_en,
                        crop_hi: item.crop_hi,
                        disease: item.disease_en,
                        disease_hi: item.disease_hi,
                        pesticide: item.pesticide
                    });
                } else {
                    currentMode = 'qrcode';
                    modeQrcodeBtn.click();
                    displayQRResult({
                        product_id: item.qr_id,
                        verified: item.verified,
                        manufacturer: item.mfg,
                        name: item.name
                    });
                }
                Toast.info("इतिहास परिणाम पुनर्प्राप्त किया गया", "History scan details restored");
            });

            historyContainer.appendChild(el);
        });
    }

    btnClearHistory.addEventListener('click', () => {
        localStorage.removeItem('kisanScanHistory');
        renderHistory();
        Toast.success("इतिहास साफ़ कर दिया गया", "Scan history successfully cleared");
    });

    // Auto-init camera and history list
    startCamera();
    renderHistory();
});
