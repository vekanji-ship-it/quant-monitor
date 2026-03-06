import requests
import pandas as pd
import yfinance as yf

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
        
        if exclude_etf:
            df = df[~df["證券代號"].astype(str).str.startswith('00')]
        
        top_list = df.sort_values(by=diff_col, ascending=False).head(25)
    except: return pd.DataFrame()

    results = []
    min_cap_value = min_cap * 100000000 
    
    for _, row in top_list.iterrows():
        code = str(row["證券代號"]).strip()
        try:
            stock = yf.Ticker(f"{code}.TW")
            
            # 均線過濾邏輯
            if above_5ma:
                hist = stock.history(period="5d")
                if len(hist) < 5: continue
                current_price = float(hist['Close'].iloc[-1])
                ma_5 = float(hist['Close'].mean())
                if current_price <= ma_5: continue
            
            # 💡 雙重保險抓取市值，避免為 0
            m_cap = 0
            try: m_cap = stock.fast_info.get('market_cap')
            except: pass
            
            if not m_cap:
                try: m_cap = stock.info.get('marketCap', 0)
                except: pass
            
            if m_cap >= min_cap_value:
                results.append({
                    "代號": code,
                    "名稱": str(row["證券名稱"]).strip(),
                    "三大法人買超(張)": int(row[diff_col] / 1000),
                    # 💡 精確到小數點第一位 (億)
                    "市值(億)": round(m_cap / 100000000, 1) 
                })
                if len(results) >= 8: break 
        except: continue
        
    return pd.DataFrame(results)