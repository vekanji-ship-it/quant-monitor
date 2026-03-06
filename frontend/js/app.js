let twiiChartInstance = null;

// 抓取總經數據與大盤
async function updateMacroData() {
    try {
        const response = await fetch('/api/macro');
        const data = await response.json();

        document.querySelector('#nasdaq-val').innerText = data.Nasdaq.price.toLocaleString();
        updateChange('#nasdaq-change', data.Nasdaq.change_pct);
        document.querySelector('#sox-val').innerText = data.SOX.price.toLocaleString();
        updateChange('#sox-change', data.SOX.change_pct);
        document.querySelector('#twd-val').innerText = data.USD_TWD.price;
        updateChange('#twd-change', data.USD_TWD.change_pct, true); 

        if (data.TWII) {
            document.querySelector('#twii-val').innerText = data.TWII.price.toLocaleString();
            updateChange('#twii-change', data.TWII.change_pct);
            
            if (data.TWII.history && data.TWII.history.length > 0) {
                drawTWIIChart(data.TWII.history, data.TWII.change_pct);
            }
        }
    } catch (error) {
        console.error("無法取得總經數據:", error);
    }
}

function updateChange(selector, value, isCurrency = false) {
    const el = document.querySelector(selector);
    if(!el) return;
    const prefix = value > 0 ? "▲" : "▼";
    el.innerText = `${prefix} ${Math.abs(value)}%`;
    
    if (value > 0) {
        el.className = isCurrency ? 'card-change down' : 'card-change up';
    } else {
        el.className = isCurrency ? 'card-change up' : 'card-change down';
    }
}

function drawTWIIChart(historyData, changePct) {
    const ctx = document.getElementById('twiiChart').getContext('2d');
    
    if (twiiChartInstance) {
        twiiChartInstance.destroy();
    }
    
    const isUp = changePct >= 0;
    const mainColor = isUp ? 'rgba(52, 199, 89, 1)' : 'rgba(255, 59, 48, 1)'; 
    const gradientTop = isUp ? 'rgba(52, 199, 89, 0.4)' : 'rgba(255, 59, 48, 0.4)';
    const gradientBottom = isUp ? 'rgba(52, 199, 89, 0)' : 'rgba(255, 59, 48, 0)';

    const gradient = ctx.createLinearGradient(0, 0, 0, 180);
    gradient.addColorStop(0, gradientTop);
    gradient.addColorStop(1, gradientBottom);

    const labels = historyData.map((_, index) => index);

    twiiChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: historyData,
                borderColor: mainColor,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 4,
                fill: true,
                backgroundColor: gradient,
                tension: 0.3 
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: { 
                    mode: 'index',
                    intersect: false,
                    displayColors: false,
                    callbacks: {
                        title: () => null, 
                        label: function(context) {
                            return context.parsed.y.toLocaleString();
                        }
                    }
                } 
            },
            scales: {
                x: { display: false },
                y: { 
                    display: false, 
                    min: Math.min(...historyData) * 0.995, 
                    max: Math.max(...historyData) * 1.005 
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// 抓取選股清單並綁定點擊事件
async function updateStockList() {
    try {
        const excludeEtf = document.getElementById('filter-etf').checked;
        const above5ma = document.getElementById('filter-5ma').checked;
        const minCap = document.getElementById('filter-cap').value;

        const tbody = document.querySelector('#stock-list-body');
        const aiReport = document.querySelector('#ai-report-content');
        
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-secondary);">重新掃描市場籌碼中，請稍候...</td></tr>';
        aiReport.innerText = "等待名單出爐後進行 AI 解析...";

        const url = `/api/stocks?min_cap=${minCap}&exclude_etf=${excludeEtf}&above_5ma=${above5ma}`;
        const response = await fetch(url);
        const stocks = await response.json();
        
        tbody.innerHTML = ''; 
        
        if (stocks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-secondary);">當前條件下無符合之標的，請嘗試放寬參數。</td></tr>';
            fetchAIReport(""); 
            return;
        }

        stocks.forEach(stock => {
            const tr = document.createElement('tr');
            // 💡 賦予可點擊的 Class，並綁定開啟 Modal 的函數
            tr.className = 'clickable-row';
            tr.onclick = () => openStockModal(stock['代號'], stock['名稱'], stock['三大法人買超(張)']);
            
            tr.innerHTML = `
                <td style="color: var(--text-secondary);">${stock['代號']}</td>
                <td>${stock['名稱']}</td>
                <td class="highlight-buy">+${stock['三大法人買超(張)'].toLocaleString()}</td>
                <td>${stock['市值(億)']}</td>
            `;
            tbody.appendChild(tr);
        });

        const stockNames = stocks.map(s => s['名稱']).join('、');
        fetchAIReport(stockNames);

    } catch (error) {
        console.error("無法取得選股名單:", error);
        document.querySelector('#stock-list-body').innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--down-color);">資料載入失敗</td></tr>';
        document.querySelector('#ai-report-content').innerText = "連線中斷，無法產生分析報告。";
    }
}

async function fetchAIReport(stockNames) {
    try {
        const aiResponse = await fetch(`/api/ai-report?stocks=${encodeURIComponent(stockNames)}`);
        const aiData = await aiResponse.json();
        document.querySelector('#ai-report-content').innerText = aiData.report;
    } catch (error) {
        console.error("AI 報告產生失敗:", error);
        document.querySelector('#ai-report-content').innerText = "AI 模組連線失敗，請檢查設定。";
    }
}

async function updateNews() {
    try {
        const response = await fetch('/api/news');
        const newsList = await response.json();
        
        const ul = document.querySelector('#news-list');
        ul.innerHTML = ''; 
        
        if (newsList.length === 0) {
            ul.innerHTML = '<li style="color: var(--text-secondary);">目前無最新新聞</li>';
            return;
        }

        newsList.forEach(news => {
            const li = document.createElement('li');
            li.innerHTML = `<a href="${news.link}" target="_blank" class="news-link">${news.title}</a>`;
            ul.appendChild(li);
        });

    } catch (error) {
        console.error("無法取得新聞:", error);
        document.querySelector('#news-list').innerHTML = '<li style="color: var(--down-color);">新聞載入失敗，請稍後再試</li>';
    }
}

// 💡 新增：打開與關閉彈出視窗的邏輯
async function openStockModal(symbol, name, netBuy) {
    const modal = document.getElementById('stock-modal');
    modal.style.display = 'flex';
    document.getElementById('modal-title').innerText = `${symbol} ${name}`;
    
    // 預設載入文字
    document.getElementById('modal-fundamentals').innerHTML = '<div style="color:var(--text-secondary)">連線至證交所與資料庫...</div>';
    document.getElementById('modal-news').innerHTML = '<li style="color:var(--text-secondary)">搜尋最新新聞中...</li>';

    try {
        const response = await fetch(`/api/stock/${symbol}?name=${encodeURIComponent(name)}`);
        const data = await response.json();
        
        // 填入籌碼與基本面
        const fund = data.fundamentals;
        document.getElementById('modal-fundamentals').innerHTML = `
            <div class="info-box"><div class="info-label">本日法人買超</div><div class="info-value highlight-buy">+${netBuy.toLocaleString()} 張</div></div>
            <div class="info-box"><div class="info-label">本益比 (P/E)</div><div class="info-value">${fund.pe_ratio}</div></div>
            <div class="info-box"><div class="info-label">股價淨值比 (P/B)</div><div class="info-value">${fund.pb_ratio}</div></div>
            <div class="info-box"><div class="info-label">最新殖利率</div><div class="info-value">${fund.dividend_yield}</div></div>
            <div class="info-box"><div class="info-label">52週最高價</div><div class="info-value">${fund['52w_high']}</div></div>
            <div class="info-box"><div class="info-label">52週最低價</div><div class="info-value">${fund['52w_low']}</div></div>
        `;

        // 填入專屬新聞
        const newsUl = document.getElementById('modal-news');
        newsUl.innerHTML = '';
        if (data.news && data.news.length > 0) {
            data.news.forEach(n => {
                newsUl.innerHTML += `<li><a href="${n.link}" target="_blank" class="news-link">${n.title}</a></li>`;
            });
        } else {
            newsUl.innerHTML = '<li style="color:var(--text-secondary)">暫無相關新聞</li>';
        }
        
    } catch (error) {
        document.getElementById('modal-fundamentals').innerHTML = '<div style="color:var(--down-color)">資料獲取失敗</div>';
    }
}

function closeModal(event) {
    if (event.target.id === 'stock-modal' || event.target.className === 'close-btn') {
        document.getElementById('stock-modal').style.display = 'none';
    }
}

// 綁定「套用並掃描」按鈕事件
document.getElementById('btn-search').addEventListener('click', () => {
    updateStockList();
});

// 啟動所有函式
updateMacroData();
updateStockList();
updateNews();