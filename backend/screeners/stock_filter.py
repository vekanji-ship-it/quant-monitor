import requests
import pandas as pd
import yfinance as yf
import time

def get_midcap_institutional_buys():
    url = "https://www.twse.com.tw/fund/T86?response=json&selectType=ALL"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data.get('stat') != 'OK': return pd.DataFrame()
        
        df = pd.DataFrame(data['data'], columns=data['fields'])
        diff_col = "三大法人買賣超股數"
        df[diff_col] = pd.to_numeric(df[diff_col].astype(str).str.replace(',', ''), errors='coerce')
        
        # 💡 為了速度，先取前 10 名進行精確過濾
        top_list = df.sort_values(by=diff_col, ascending=False).head(10)
    except:
        return pd.DataFrame()

    results = []
    for _, row in top_list.iterrows():
        code = str(row["證券代號"]).strip()
        if len(code) != 4 or code.startswith('00'): continue
        
        try:
            stock = yf.Ticker(f"{code}.TW")
            # 💡 關鍵：使用 fast_info 取得市值，速度提升 1000%
            m_cap = stock.fast_info.get('market_cap', 0)
            
            # 市值區間 $10^{10} \le M_{cap} \le 10^{11}$ (即 100 億 ~ 1000 億)
            if 10000000000 <= m_cap <= 100000000000:
                results.append({
                    "代號": code,
                    "名稱": str(row["證券名稱"]).strip(),
                    "三大法人買超(張)": int(row[diff_col] / 1000),
                    "市值(億)": round(m_cap / 100000000, 2)
                })
        except: continue
        
    return pd.DataFrame(results)