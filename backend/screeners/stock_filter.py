import requests
import pandas as pd
import yfinance as yf

# 💡 接收前端傳來的參數：最低市值、是否排除ETF、是否站上5MA
def get_midcap_institutional_buys(min_cap: int = 50, exclude_etf: bool = True, above_5ma: bool = False):
    url = "https://www.twse.com.tw/fund/T86?response=json&selectType=ALL"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data.get('stat') != 'OK': return pd.DataFrame()
        
        df = pd.DataFrame(data['data'], columns=data['fields'])
        diff_col = "三大法人買賣超股數"
        df[diff_col] = pd.to_numeric(df[diff_col].astype(str).str.replace(',', ''), errors='coerce')
        df = df[df["證券代號"].astype(str).str.len() == 4]
        
        # 💡 條件開關：是否排除 ETF (00開頭)
        if exclude_etf:
            df = df[~df["證券代號"].astype(str).str.startswith('00')]
        
        # 取前 25 名進行運算
        top_list = df.sort_values(by=diff_col, ascending=False).head(25)
    except: return pd.DataFrame()

    results = []
    # 將前端傳來的「億」轉換為實際數字
    min_cap_value = min_cap * 100000000 
    
    for _, row in top_list.iterrows():
        code = str(row["證券代號"]).strip()
        try:
            stock = yf.Ticker(f"{code}.TW")
            current_price = 0
            
            # 💡 條件開關：如果開啟了 5MA 限制，就計算歷史價格
            if above_5ma:
                hist = stock.history(period="5d")
                if len(hist) < 5: continue
                current_price = float(hist['Close'].iloc[-1])
                ma_5 = float(hist['Close'].mean())
                
                # 如果沒有站上 5MA，直接跳過這檔股票
                if current_price <= ma_5:
                    continue
            
            # 取得市值
            m_cap = stock.fast_info.get('market_cap', 0)
            
            # 💡 條件開關：判斷市值是否大於設定的下限
            if m_cap >= min_cap_value:
                results.append({
                    "代號": code,
                    "名稱": str(row["證券名稱"]).strip(),
                    "三大法人買超(張)": int(row[diff_col] / 1000),
                    "市值(億)": round(m_cap / 100000000, 2)
                })
                # 抓滿 8 檔就輸出，避免 Vercel 超時
                if len(results) >= 8: break 
        except: continue
        
    return pd.DataFrame(results)