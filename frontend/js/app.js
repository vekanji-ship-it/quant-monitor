// 抓取總經數據
async function updateMacroData() {
    try {
        // 💡 修正：改用相對路徑，讓 Vercel 知道去哪裡找 API
        const response = await fetch('/api/macro');
        const data = await response.json();

        // 更新 Nasdaq
        document.querySelector('#nasdaq-val').innerText = data.Nasdaq.price.toLocaleString();
        updateChange('#nasdaq-change', data.Nasdaq.change_pct);

        // 更新 SOX
        document.querySelector('#sox-val').innerText = data.SOX.price.toLocaleString();
        updateChange('#sox-change', data.SOX.change_pct);

        // 更新 匯率
        document.querySelector('#twd-val').innerText = data.USD_TWD.price;
        updateChange('#twd-change', data.USD_TWD.change_pct, true); // true 代表匯率邏輯（跌是升值）

    } catch (error) {
        console.error("無法取得總經數據:", error);
    }
}

function updateChange(selector, value, isCurrency = false) {
    const el = document.querySelector(selector);
    const prefix = value > 0 ? "▲" : "▼";
    el.innerText = `${prefix} ${Math.abs(value)}%`;
    
    // 根據漲跌調整顏色
    if (value > 0) {
        el.className = isCurrency ? 'card-change down' : 'card-change up';
    } else {
        el.className = isCurrency ? 'card-change up' : 'card-change down';
    }
}

// 抓取選股清單並更新表格
async function updateStockList() {
    try {
        // 💡 修正：改用相對路徑
        const response = await fetch('/api/stocks');
        const stocks = await response.json();
        
        const tbody = document.querySelector('#stock-list-body');
        tbody.innerHTML = ''; // 清空 Loading 訊息
        
        if (stocks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">今日無符合條件之標的</td></tr>';
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

    } catch (error) {
        console.error("無法取得選股名單:", error);
        document.querySelector('#stock-list-body').innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--down-color);">資料載入失敗，請確認後端伺服器狀態</td></tr>';
    }
}

// 網頁載入時同時執行這兩個功能 // 強制觸發 Vercel 更新 2026
updateMacroData();
updateStockList();