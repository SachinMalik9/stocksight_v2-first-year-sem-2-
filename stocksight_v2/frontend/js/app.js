const API_BASE = "http://127.0.0.1:5000";
let currentSym = 'TSLA';
let priceChart;
let currentTimeframe = '1d';

// ── 1. CLOCK LOGIC ──
function updateClock() {
    const now = new Date();
    const clockEl = document.getElementById('clock');
    if(clockEl) clockEl.textContent = now.toLocaleTimeString('en-US', {hour12: false});
}
setInterval(updateClock, 1000);
updateClock();
// --- TERMINAL SEARCH FUNCTIONALITY ---
const searchBtn = document.getElementById('stock-search-btn');
const searchInput = document.getElementById('stock-search-input');
const titleDisplay = document.getElementById('main-stock-title');

function executeSearch() {
    const newTicker = searchInput.value.trim().toUpperCase();
    
    if (newTicker !== "") {
        // 1. Set the global symbol to your search query
        currentSym = newTicker; 
        
        // 2. Update the UI Title
        if (titleDisplay) titleDisplay.textContent = currentSym;
        
        // 3. Trigger all data fetches for the new stock
        fetchPriceData(); // Fetches chart data
        fetchSummary();   // Fetches sentiment (If you have this function)
        
        // 4. Clear input
        searchInput.value = "";
        console.log(`Searching for: ${currentSym}`);
    }
}

// Click listener
searchBtn.addEventListener('click', executeSearch);

// Enter key listener
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') executeSearch();
});

// ── 2. PILL SWITCHING (SYMBOL SELECTION) ──
document.querySelectorAll('.pill').forEach(p => {
    p.addEventListener('click', async () => {
        document.querySelectorAll('.pill').forEach(x => x.classList.remove('active'));
        p.classList.add('active');
        currentSym = p.textContent.trim();
        
        // Safely update labels if they exist
        const mainTitle = document.getElementById('main-title');
        const sideName = document.getElementById('side-name');
        if(mainTitle) mainTitle.textContent = `${currentSym} — Market Intelligence`;
        if(sideName) sideName.textContent = currentSym;
        
        // Fetch new data immediately
        fetchPolrityData();
        fetchPriceData();
        fetchTweetData();
    });
});
// ── TIMEFRAME SWITCHING ──
document.querySelectorAll('.tf-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all buttons and add to the clicked one
        document.querySelectorAll('.tf-btn').forEach(x => x.classList.remove('active'));
        btn.classList.add('active');
        
        // Update the global timeframe variable
        currentTimeframe = btn.getAttribute('data-tf');
        
        // Trigger a fresh data fetch
        fetchPriceData(); 
    });
});

// ── 3. CRASH-PROOF NAVIGATION SWITCHER ──
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        const navText = this.textContent.trim();
        
        // Ignore clicks on the settings button
        if (navText.includes("Elasticsearch")) return;

        // Highlight the clicked button
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        this.classList.add('active');

        // Grab views
        const dashView = document.getElementById('view-dashboard');
        const historyView = document.getElementById('view-history');
        const sentimentView = document.getElementById('view-sentiment');

        // Hide all views securely
        if (dashView) dashView.style.display = "none";
        if (historyView) historyView.style.display = "none";
        if (sentimentView) sentimentView.style.display = "none";

        // Show selected view securely
        if (navText.includes("Dashboard") && dashView) {
            dashView.style.display = "block";
        } else if (navText.includes("Price History") && historyView) {
            historyView.style.display = "block";
        } else if (navText.includes("Sentiment Feed") && sentimentView) {
            sentimentView.style.display = "block";
        }
    });
});

// ── 4. CRASH-PROOF DATA FETCHING ──

async function fetchPolrityData() {
    try {
        const res = await fetch(`${API_BASE}/summary?symbol=${currentSym}`);
        const data = await res.json();
        const pol = data.polarity || 0;

        const sPol = document.getElementById("s-polarity");
        const mPol = document.getElementById("m-polarity");
        
        const formatted = (pol > 0 ? "+" : "") + pol.toFixed(2);
        const color = pol >= 0 ? "var(--pos)" : "var(--neg)";

        if(sPol) { sPol.innerText = formatted; sPol.style.color = color; }
        if(mPol) { mPol.innerText = formatted; mPol.style.color = color; }

        const apiStatus = document.getElementById("api-status");
        const apiDot = document.getElementById("api-dot");
        if(apiStatus) { apiStatus.innerText = "Connected"; apiStatus.style.color = "var(--green)"; }
        if(apiDot) { apiDot.style.background = "var(--green)"; }
    } catch (err) {
        // Suppress console errors to keep terminal clean and handle UI fallback safely
        const apiStatus = document.getElementById("api-status");
        const apiDot = document.getElementById("api-dot");
        if(apiStatus) { apiStatus.innerText = "Waiting..."; apiStatus.style.color = "var(--red)"; }
        if(apiDot) { apiDot.style.background = "var(--red)"; }
    }
}
async function fetchPriceData() {
    try {
        const res = await fetch(`${API_BASE}/price?symbol=${currentSym}&range=${currentTimeframe}`);
        const data = await res.json();
        
        // Keep it simple, let the backend do the hard work!
        const prices = Array.isArray(data.prices) ? data.prices : [];
        const labels = Array.isArray(data.labels) ? data.labels : [];
        
        // 1. Update Sidebar Price
        const sLast = document.getElementById('s-last');
        if (sLast) {
            sLast.textContent = prices.length ? '$' + (prices[prices.length - 1] || 0).toFixed(2) : 'Waiting...';
        }
        
        // ... (rest of your chart drawing code) ...

        // 2. Update the Chart
        const chartCanvas = document.getElementById('priceChart');
        if (chartCanvas) {
            if (priceChart) {
                priceChart.data.labels = labels;
                priceChart.data.datasets[0].data = prices;
                priceChart.update('none');
            } else {
                priceChart = new Chart(chartCanvas, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{ label: 'Price', data: prices, borderColor: '#00e5ff', backgroundColor: 'rgba(0,229,255,0.04)', fill: true, tension: 0.4, pointRadius: 0, borderWidth: 2 }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#5a6480', maxTicksLimit: 6 }, grid: { color: 'rgba(30,45,61,0.6)' } }, y: { position: 'left', ticks: { color: '#00e5ff', callback: v => '$' + v.toFixed(2) }, grid: { color: 'rgba(30,45,61,0.6)' } } } }
                });
            }
        }

        // 3. Update History Table (Now Timeframe-Aware)
        const historyTable = document.getElementById("history-table-body");
        const historyHeader = document.querySelector("#view-history thead tr");

        if (historyTable) {
            if (prices.length === 0) {
                historyTable.innerHTML = `<tr><td colspan="3" style="text-align:center; padding: 20px; color: var(--muted); font-style: italic;">No data available for this range...</td></tr>`;
            } else {
                // Change the Header Text based on the mode
                if (historyHeader) {
                    historyHeader.innerHTML = `
                        <th style="padding: 12px;">${currentTimeframe === '1d' ? 'TIMESTAMP' : 'DATE'}</th>
                        <th>SYMBOL</th>
                        <th>${currentTimeframe === '1d' ? 'LIVE PRICE' : 'CLOSE PRICE'}</th>
                    `;
                }

                let rowsHTML = "";
                // Loop backwards so the most recent data is at the top
                for (let i = prices.length - 1; i >= 0; i--) {
                    const timeLabel = labels[i] || '--:--';
                    const safePrice = typeof prices[i] === 'number' ? prices[i] : 0;
                    rowsHTML += `
                        <tr style="border-bottom: 1px solid var(--border);">
                            <td style="padding: 12px; color: var(--muted);">${timeLabel}</td>
                            <td style="padding: 12px; font-weight: 700; color: var(--accent2);">${currentSym}</td>
                            <td style="padding: 12px; font-family: 'DM Mono', monospace; color: var(--green);">$${safePrice.toFixed(2)}</td>
                        </tr>`;
                }
                historyTable.innerHTML = rowsHTML;
            }
        }
    } catch (err) {
        console.error("Fetch error:", err);
    }
}

async function fetchTweetData() {
    try {
        const res = await fetch(`${API_BASE}/tweets?symbol=${currentSym}`);
        const tweets = await res.json();
        
        // Safe check: If tweets isn't an array (due to empty DB error), make it an empty array
        const safeTweets = Array.isArray(tweets) ? tweets : [];
        const tbody = document.getElementById("tweet-body");

        if(tbody) {
            if (safeTweets.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" style="text-align:center; padding: 20px; color: var(--muted); font-style: italic;">
                            Listening for live sentiment data...
                        </td>
                    </tr>`;
            } else {
                tbody.innerHTML = safeTweets.map(t => `
                    <tr style="border-bottom: 1px solid var(--border);">
                        <td style="padding: 12px;"><div style="font-weight:700;color:var(--accent2)">${t.author || 'System'}</div></td>
                        <td style="padding: 12px;"><div>${t.message || ''}</div></td>
                        <td style="padding: 12px;"><span style="color:${t.sentiment === 'positive' ? 'var(--pos)' : t.sentiment === 'negative' ? 'var(--neg)' : 'var(--muted)'}">${t.sentiment || 'neutral'}</span></td>
                        <td style="padding: 12px;"><div style="font-family:'DM Mono',monospace;color:${(t.polarity || 0) > 0 ? 'var(--pos)' : (t.polarity || 0) < 0 ? 'var(--neg)' : 'var(--muted)'}">${((t.polarity || 0) > 0 ? "+" : "") + (t.polarity || 0).toFixed(2)}</div></td>
                    </tr>
                `).join("");
            }
        }
    } catch (err) { 
        // Silently catch fetch errors
    }
}

// ── 5. INITIALIZATION ──
setInterval(fetchPolrityData, 5000);
setInterval(fetchPriceData, 5000);
setInterval(fetchTweetData, 5000);

// Initial Call
fetchPolrityData(); 
fetchPriceData(); 
fetchTweetData()