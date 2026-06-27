document.addEventListener('DOMContentLoaded', () => {
    const logsContainer = document.getElementById('logs-container');
    const btnSimulate = document.getElementById('btn-simulate-call');
    const kpiTotalCalls = document.getElementById('kpi-total-calls');
    const kpiActiveCalls = document.getElementById('kpi-active-calls');

    let totalCalls = 1420;

    // Load logs on startup
    async function loadLogs() {
        try {
            const response = await fetch('/api/ivr/stats');
            const data = await response.json();
            if (data.success) {
                renderLogs(data.logs);
                kpiActiveCalls.textContent = data.active_calls;
            }
        } catch (err) {
            console.error("Failed to load IVR stats", err);
            logsContainer.innerHTML = '<p style="text-align: center; padding: 2rem; color: #e63946;">त्रुटि: डेटा लोड नहीं हुआ</p>';
        }
    }

    function renderLogs(logs) {
        logsContainer.innerHTML = '';
        if (logs.length === 0) {
            logsContainer.innerHTML = '<p style="text-align: center; padding: 2rem; color: var(--text-muted);">कोई कॉल लॉग नहीं है</p>';
            return;
        }

        logs.forEach(log => {
            const div = document.createElement('div');
            div.className = 'call-log-row';
            div.innerHTML = `
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="background:rgba(45, 106, 79, 0.1); color:var(--primary); width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center;">
                        <i class="fas fa-phone"></i>
                    </div>
                    <div class="bilingual-text">
                        <span class="hi-text" style="font-size:0.95rem;">${log.caller}</span>
                        <span class="en-text" style="font-size:0.75rem;">पथ / Menu Path: ${log.path}</span>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:1.5rem;">
                    <div class="bilingual-text" style="text-align: right;">
                        <span class="hi-text" style="font-size:0.85rem;">समय / Duration: ${log.duration}</span>
                        <span class="en-text" style="font-size:0.75rem;">${log.time}</span>
                    </div>
                    <button class="btn btn-outline" style="padding: 0.35rem 0.6rem; border-radius:50%;" onclick="playVoiceMessage('${log.audio_url || ''}')" title="कॉल बातचीत सुनें / Listen call">
                        <i class="fas fa-volume-up"></i>
                    </button>
                </div>
            `;
            logsContainer.appendChild(div);
        });
    }

    // Call Simulator
    btnSimulate.addEventListener('click', async () => {
        Toast.info("हेल्पलाइन कॉल सिमुलेशन शुरू हो रहा है...", "Simulating incoming IVR helpline call...");
        btnSimulate.disabled = true;

        try {
            const response = await fetch('/api/ivr/simulate', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                totalCalls += 1;
                kpiTotalCalls.textContent = totalCalls.toLocaleString();
                
                // Reload logs
                await loadLogs();

                // Highlight the top row
                const firstRow = logsContainer.firstElementChild;
                if (firstRow) {
                    firstRow.style.background = 'rgba(82, 183, 136, 0.15)';
                    firstRow.style.borderLeftColor = 'var(--accent)';
                    setTimeout(() => {
                        firstRow.style.background = '';
                        firstRow.style.borderLeftColor = '';
                    }, 4000);
                }

                Toast.success("कॉल सफलतापूर्वक सिमुलेट की गई", "Helpline call simulated");
                
                // Play audio of simulated welcome greeting
                if (data.audio_url) {
                    playVoiceMessage(data.audio_url);
                }
            }
        } catch (err) {
            console.error("Simulation failed", err);
            Toast.error("कॉल सिमुलेशन विफल", "Helpline call simulation failed");
        } finally {
            btnSimulate.disabled = false;
        }
    });

    // Auto load logs on startup
    loadLogs();
});
