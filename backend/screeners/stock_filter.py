import requests
import pandas as pd
import yfinance as yf

def get_midcap_institutional_buys():
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
        df = df[~df["證券代號"].astype(str).str.startswith('00')]
        
        # 💡 修改 A：擴大掃描範圍至前 30 名
        top_list = df.sort_values(by=diff_col, ascending=False).head(30)
    except: return pd.DataFrame()

    results = []
    for _, row in top_list.iterrows():
        code = str(row["證券代號"]).strip()
        try:
            stock = yf.Ticker(f"{code}.TW")
            m_cap = stock.fast_info.get('market_cap', 0)
            
            # 💡 修改 A：放寬市值下限到 50 億 (5000000000)
            if 5000000000 <= m_cap <= 100000000000:
                results.append({
                    "代號": code,
                    "名稱": str(row["證券名稱"]).strip(),
                    "三大法人買超(張)": int(row[diff_col] / 1000),
                    "市值(億)": round(m_cap / 100000000, 2)
                })
                if len(results) >= 8: break # 抓滿 8 檔就夠 AI 寫報告了
        except: continue
    return pd.DataFrame(results)