import yfinance as yf
import pandas as pd

def get_macro_environment():
    tickers = {
        "Nasdaq": "^IXIC",
        "SOX": "^SOX",
        "USD_TWD": "TWD=X",
        "TWII": "^TWII"  # 台股加權指數
    }
    
    macro_data = {}
    
    for name, ticker in tickers.items():
        try:
            stock = yf.Ticker(ticker)
            
            if name != "TWII":
                # 一般指數抓 5 天確保能避開週末與國定假日
                hist = stock.history(period="5d")
                if len(hist) >= 2:
                    current = float(hist['Close'].iloc[-1])
                    prev = float(hist['Close'].iloc[-2])
                    macro_data[name] = {
                        "price": round(current, 2),
                        "change_pct": round(((current - prev) / prev) * 100, 2)
                    }
                else:
                    macro_data[name] = {"price": 0, "change_pct": 0}
            else:
                # 台股大盤抓 1 個月 (1mo) 的歷史資料用來畫圖
                hist = stock.history(period="1mo")
                if len(hist) >= 2:
                    current = float(hist['Close'].iloc[-1])
                    prev = float(hist['Close'].iloc[-2])
                    
                    # 將 Close 價格序列轉為 list，準備給前端畫圖
                    history_prices = [float(p) for p in hist['Close'].tolist()]
                    
                    macro_data[name] = {
                        "price": round(current, 2),
                        "change_pct": round(((current - prev) / prev) * 100, 2),
                        "history": [round(p, 2) for p in history_prices]
                    }
                else:
                    macro_data[name] = {"price": 0, "change_pct": 0, "history": []}
                
        except Exception as e:
            print(f"無法取得 {name} 數據: {e}")
            macro_data[name] = {"price": 0, "change_pct": 0, "history": []}
            
    return macro_data

if __name__ == "__main__":
    print(get_macro_environment())