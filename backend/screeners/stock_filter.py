import requests
import pandas as pd
import yfinance as yf
import time

def get_midcap_institutional_buys():
    print("1. 正在向台灣證交所 (主網) 獲取最新三大法人籌碼...")
    url = "https://www.twse.com.tw/fund/T86?response=json&selectType=ALL"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('stat') != 'OK':
            return pd.DataFrame()
            
        fields = data['fields']
        raw_data = data['data']
        df = pd.DataFrame(raw_data, columns=fields)
        
        diff_col = "三大法人買賣超股數"
        df[diff_col] = df[diff_col].astype(str).str.replace(',', '', regex=False)
        df[diff_col] = pd.to_numeric(df[diff_col], errors='coerce')
        
        # 💡 為了穩定度，先抓前 12 名確保 10 秒內跑完
        top_list = df.sort_values(by=diff_col, ascending=False).head(12)
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return pd.DataFrame()

    results = []
    for index, row in top_list.iterrows():
        stock_code = str(row["證券代號"]).strip()
        if len(stock_code) != 4 or stock_code.startswith('00'):
            continue
            
        try:
            stock = yf.Ticker(f"{stock_code}.TW")
            # 💡 關鍵加速：使用 fast_info 取得市值，這比 .info 快非常多
            market_cap = stock.fast_info.get('market_cap', 0)
            
            if market_cap and 10000000000 <= market_cap <= 100000000000:
                results.append({
                    "代號": stock_code,
                    "名稱": str(row["證券名稱"]).strip(),
                    "三大法人買超(張)": int(row[diff_col] / 1000),
                    "市值(億)": round(market_cap / 100000000, 2)
                })
                if len(results) >= 8: break
        except:
            continue
        
        # 💡 雲端執行時取消延遲以追求極速
        
    return pd.DataFrame(results)

if __name__ == "__main__":
    final_list = get_midcap_institutional_buys()
    if not final_list.empty:
        print(final_list.to_string(index=False))
# 💡 強制觸發 Vercel 更新 2026