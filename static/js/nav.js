document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // Theme toggler
    const themeSwitch = document.getElementById('theme-toggle');
    if (themeSwitch) {
        // Set initial theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        themeSwitch.innerHTML = savedTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';

        themeSwitch.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeSwitch.innerHTML = newTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        });
    }

    // Mini weather widget fetcher
    const weatherTextHi = document.getElementById('mini-weather-hi');
    const weatherTextEn = document.getElementById('mini-weather-en');
    const weatherIcon = document.getElementById('mini-weather-icon');

    if (weatherTextHi && weatherTextEn) {
        const fetchMiniWeather = async () => {
            try {
                const curLang = localStorage.getItem('kisanLanguage') || 'hi';
                const url = `/api/weather?city=Indore&lang=${curLang}`;
                console.log(`[nav.js] Fetching mini weather from: ${url}`);
                const response = await fetch(url);
                const data = await response.json();
                console.log(`[nav.js] Mini weather response:`, data);
                if (data && data.success) {
                    const temp = Math.round(data.temp);
                    const desc = data.desc_hi || data.desc;
                    weatherTextHi.textContent = `${temp}°C, ${desc}`;
                    weatherTextEn.textContent = `Indore: ${temp}°C, ${data.desc}`;
                    
                    // Simple icon mappings
                    let iconClass = 'fa-cloud-sun';
                    const main = (data.main_desc || '').toLowerCase();
                    if (main.includes('rain')) iconClass = 'fa-cloud-showers-heavy';
                    else if (main.includes('clear')) iconClass = 'fa-sun';
                    else if (main.includes('snow')) iconClass = 'fa-snowflake';
                    else if (main.includes('thunder')) iconClass = 'fa-bolt';
                    
                    if (weatherIcon) {
                        weatherIcon.className = `fas ${iconClass}`;
                    }
                }
            } catch (err) {
                console.error("Mini weather fetch failed", err);
            }
        };
        fetchMiniWeather();
        // Update weather every 10 mins
        setInterval(fetchMiniWeather, 10 * 60 * 1000);
    }
});
