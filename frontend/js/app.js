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

// 繪製台股大盤趨勢圖
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

// 💡 修改：抓取選股清單 (動態讀取參數並更新 URL)
async function updateStockList() {
    try {
        // 取得介面上的設定值
        const excludeEtf = document.getElementById('filter-etf').checked;
        const above5ma = document.getElementById('filter-5ma').checked;
        const minCap = document.getElementById('filter-cap').value;

        const tbody = document.querySelector('#stock-list-body');
        const aiReport = document.querySelector('#ai-report-content');
        
        // 切換為載入狀態
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-secondary);">重新掃描市場籌碼中，請稍候...</td></tr>';
        aiReport.innerText = "等待名單出爐後進行 AI 解析...";

        // 將參數組裝進網址
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

// 呼叫 AI 寫早報
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

// 抓取每日財經新聞
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

// 網頁載入時同時執行所有功能
updateMacroData();
updateStockList();
updateNews();

// 💡 新增：綁定「套用並掃描」按鈕事件
document.getElementById('btn-search').addEventListener('click', () => {
    updateStockList();
});