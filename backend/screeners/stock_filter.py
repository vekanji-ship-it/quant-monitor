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
            print("❌ 證交所目前無資料 (可能尚未收盤或今日非交易日)。")
            return pd.DataFrame()
            
        print("✅ 成功取得主網籌碼資料，開始解析...")
        
        fields = data['fields']
        raw_data = data['data']
        
        df = pd.DataFrame(raw_data, columns=fields)
        
        code_col = "證券代號"
        name_col = "證券名稱"
        diff_col = "三大法人買賣超股數"
        
        if diff_col not in df.columns:
            print("❌ 找不到買賣超欄位，請確認證交所欄位名稱是否變更。")
            return pd.DataFrame()
            
        df[diff_col] = df[diff_col].astype(str).str.replace(',', '', regex=False)
        df[diff_col] = pd.to_numeric(df[diff_col], errors='coerce')
        
        # 💡 修正 1：為了符合 Vercel 10 秒限制，將初選名單縮減為前 15 名
        top_15 = df.sort_values(by=diff_col, ascending=False).head(15)
        
    except Exception as e:
        print(f"❌ 網路連線或解析錯誤: {e}")
        return pd.DataFrame()

    results = []
    print("2. 籌碼初選完成！開始逐一過濾市值 (100億 ~ 1000億)，這會需要呼叫美股 API，請稍候...")
    
    for index, row in top_15.iterrows(): # 💡 對應上面的變數名稱更改
        stock_code = str(row[code_col]).strip()
        stock_name = str(row[name_col]).strip()
        net_buy_shares = row[diff_col]
        
        if len(stock_code) != 4 or stock_code.startswith('00'):
            continue
            
        yf_ticker = f"{stock_code}.TW"
        
        try:
            stock = yf.Ticker(yf_ticker)
            market_cap = stock.info.get('marketCap', 0)
            
            if market_cap is None:
                continue
                
            if 10000000000 <= market_cap <= 100000000000:
                results.append({
                    "代號": stock_code,
                    "名稱": stock_name,
                    "三大法人買超(張)": int(net_buy_shares / 1000),
                    "市值(億)": round(market_cap / 100000000, 2)
                })
                print(f"  🎯 捕捉到符合標的: {stock_code} {stock_name}")
                
                # 抓滿 10 檔就收工
                if len(results) >= 10:
                    break
                    
        except Exception as e:
            continue
            
        # 💡 修正 2：縮短延遲時間為 0.1 秒，加快執行速度
        time.sleep(0.1)
        
    print("\n--- 📊 篩選完成！本日中型股動能清單 ---")
    return pd.DataFrame(results)

if __name__ == "__main__":
    final_list = get_midcap_institutional_buys()
    if not final_list.empty:
        print(final_list.to_string(index=False)) 
        #// 強制觸發 Vercel 更新 2026