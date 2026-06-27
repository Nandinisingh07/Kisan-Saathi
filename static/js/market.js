document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('market-filter-form');
    const tableBody = document.getElementById('mandi-table-body');
    const tableSearch = document.getElementById('table-search');
    const btnExport = document.getElementById('btn-export-csv');
    const recomContainer = document.getElementById('recommended-crops-list');
    const popularContainer = document.getElementById('popular-crops-list');

    let rawMandiData = []; // Store fetched records locally
    let priceChart = null; // Store chart instance for destroy/recreate

    // Handle Form Submit / Filter Trigger
    filterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        fetchMarketAdvisory();
    });

    // Fetch Market Data from Backend API
    async function fetchMarketAdvisory() {
        const state = document.getElementById('filter-state').value;
        const district = document.getElementById('filter-district').value;
        const land = document.getElementById('filter-land').value;

        Toast.info("मंडी भाव और फसल विश्लेषण लोड हो रहा है...", "Loading mandi rates and crop suggestions...");
        
        try {
            const url = `/api/market?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}&land_type=${encodeURIComponent(land)}`;
            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                rawMandiData = data.records || [];
                
                // 1. Render Recommendations
                renderRecommendations(data.recommended_crops, data.avg_prices);

                // 2. Render Popular
                renderPopularCrops(data.popular_crops, data.avg_prices);

                // 3. Render Table
                renderMandiTable(rawMandiData);

                // 4. Render Chart
                renderComparativeChart(data.popular_crops, data.recommended_crops, data.avg_prices);

                Toast.success("बाजार डेटा सफलतापूर्वक लोड किया गया", "Mandi prices and analysis updated");
            } else {
                Toast.error("डेटा प्राप्त करने में असमर्थ", "Failed to load: " + data.error);
                tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#e63946;">त्रुटि: ${data.error}</td></tr>`;
            }
        } catch (err) {
            console.error("Advisory load error", err);
            Toast.error("नेटवर्क त्रुटि: मंडी डेटा प्राप्त नहीं हुआ", "Network Error: Could not fetch mandi rates");
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#e63946;">नेटवर्क विफलता / Network Failure</td></tr>`;
        }
    }

    // Render crop recommendation lists
    function renderRecommendations(crops, avgPrices) {
        recomContainer.innerHTML = '';
        if (!crops || crops.length === 0) {
            recomContainer.innerHTML = `<span style="color:var(--text-muted);">कोई अनुकूल फसल नहीं मिली</span>`;
            return;
        }

        crops.forEach(crop => {
            const price = avgPrices[crop] || 'N/A';
            const priceFormatted = price !== 'N/A' ? `₹${Math.round(price)}/क्विं` : 'दर अनुपलब्ध';
            
            const div = document.createElement('div');
            div.style.padding = '0.75rem';
            div.style.background = 'var(--bg)';
            div.style.borderRadius = '8px';
            div.style.display = 'flex';
            div.style.justifyContent = 'space-between';
            div.style.alignItems = 'center';
            div.style.borderLeft = '4px solid var(--accent)';

            div.innerHTML = `
                <div class="bilingual-text">
                    <span class="hi-text" style="font-size:0.9rem;">${crop}</span>
                    <span class="en-text" style="font-size:0.75rem;">Soil-Compatible</span>
                </div>
                <span class="recom-badge">${priceFormatted}</span>
            `;
            recomContainer.appendChild(div);
        });
    }

    function renderPopularCrops(crops, avgPrices) {
        popularContainer.innerHTML = '';
        if (!crops || crops.length === 0) {
            popularContainer.innerHTML = `<span style="color:var(--text-muted);">कोई डेटा उपलब्ध नहीं</span>`;
            return;
        }

        crops.forEach(crop => {
            const price = avgPrices[crop] || 'N/A';
            const priceFormatted = price !== 'N/A' ? `₹${Math.round(price)}/क्विं` : 'दर अनुपलब्ध';

            const div = document.createElement('div');
            div.style.padding = '0.75rem';
            div.style.background = 'var(--bg)';
            div.style.borderRadius = '8px';
            div.style.display = 'flex';
            div.style.justifyContent = 'space-between';
            div.style.alignItems = 'center';
            div.style.borderLeft = '4px solid var(--secondary)';

            div.innerHTML = `
                <div class="bilingual-text">
                    <span class="hi-text" style="font-size:0.9rem;">${crop}</span>
                    <span class="en-text" style="font-size:0.75rem;">Trending in Mandi</span>
                </div>
                <span class="recom-badge" style="background:rgba(82, 183, 136, 0.15); color:var(--primary); border-color:rgba(82,183,136,0.3);">${priceFormatted}</span>
            `;
            popularContainer.appendChild(div);
        });
    }

    // Render Table Rows
    function renderMandiTable(records) {
        tableBody.innerHTML = '';
        if (records.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">मंडी में इस जिले के लिए कोई आवक दर्ज नहीं है। / No entries found.</td></tr>`;
            return;
        }

        records.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${r.commodity}</strong><br><span style="font-size:0.75rem; color:var(--text-muted);">${r.commodity}</span></td>
                <td>${r.market}</td>
                <td>${r.variety || 'Standard'}</td>
                <td>₹${r.min_price}</td>
                <td>₹${r.max_price}</td>
                <td><strong style="color:var(--primary-dark);">₹${r.modal_price}</strong></td>
                <td>${r.arrival_date}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // Filter Table dynamically
    tableSearch.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = rawMandiData.filter(r => 
            (r.commodity || '').toLowerCase().includes(query) ||
            (r.market || '').toLowerCase().includes(query) ||
            (r.variety || '').toLowerCase().includes(query)
        );
        renderMandiTable(filtered);
    });

    // Render Chart analysis
    function renderComparativeChart(popular, recommended, avgPrices) {
        const ctx = document.getElementById('crop-price-chart').getContext('2d');
        
        // Merge lists and remove duplicates
        const crops = [...new Set([...popular, ...recommended])].slice(0, 7);
        const dataValues = crops.map(c => Math.round(avgPrices[c] || 0));

        if (priceChart) {
            priceChart.destroy();
        }

        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const labelColor = isDark ? '#f4f9f4' : '#2d3142';
        const gridColor = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.05)';

        priceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: crops,
                datasets: [{
                    label: 'औसत भाव (₹ प्रति क्विंटल) / Avg Price',
                    data: dataValues,
                    backgroundColor: [
                        'rgba(45, 106, 79, 0.75)',
                        'rgba(82, 183, 136, 0.75)',
                        'rgba(212, 175, 55, 0.75)',
                        'rgba(64, 145, 108, 0.75)',
                        'rgba(27, 67, 50, 0.75)',
                        'rgba(116, 198, 157, 0.75)',
                        'rgba(181, 141, 16, 0.75)'
                    ],
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: labelColor, font: { family: 'DM Sans' } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: labelColor, font: { family: 'DM Sans' } }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: labelColor, font: { family: 'DM Sans' } },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // CSV compile & export
    btnExport.addEventListener('click', () => {
        if (rawMandiData.length === 0) {
            Toast.error("कोई डेटा डाउनलोड के लिए उपलब्ध नहीं है", "No data available to export");
            return;
        }

        let csvContent = "state,district,market,commodity,variety,grade,min_price,max_price,modal_price,arrival_date\n";
        rawMandiData.forEach(r => {
            const row = [
                `"${r.state}"`,
                `"${r.district}"`,
                `"${r.market}"`,
                `"${r.commodity}"`,
                `"${r.variety || ''}"`,
                `"${r.grade || ''}"`,
                r.min_price,
                r.max_price,
                r.modal_price,
                `"${r.arrival_date}"`
            ].join(",");
            csvContent += row + "\n";
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `mandi_prices_${document.getElementById('filter-district').value.toLowerCase()}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        Toast.success("CSV फ़ाइल डाउनलोड प्रारंभ हुई", "CSV download started successfully");
    });

    // Handle theme toggle chart update
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            // Give time for theme attribute to set on documentElement
            setTimeout(() => {
                if (priceChart && rawMandiData.length > 0) {
                    const state = document.getElementById('filter-state').value;
                    const district = document.getElementById('filter-district').value;
                    const land = document.getElementById('filter-land').value;
                    fetchMarketAdvisory();
                }
            }, 100);
        });
    }

    // Auto-init fetch on page load
    fetchMarketAdvisory();
});
