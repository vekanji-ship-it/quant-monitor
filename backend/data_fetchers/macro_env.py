import yfinance as yf
import pandas as pd

def get_macro_environment():
    # 💡 這裡加入了台股加權指數 (^TWII)
    tickers = {
        "Nasdaq": "^IXIC",
        "SOX": "^SOX",
        "USD_TWD": "TWD=X",
        "TWII": "^TWII"  
    }
    
    macro_data = {}
    
    for name, ticker in tickers.items():
        try:
            stock = yf.Ticker(ticker)
            # 使用 5d 確保遇到週末或連續假日也能抓到前兩個交易日的資料
            hist = stock.history(period="5d")
            
            if len(hist) >= 2:
                # 加入 float() 強制轉換型態，避免 JSON 序列化錯誤
                current_price = float(hist['Close'].iloc[-1])
                prev_price = float(hist['Close'].iloc[-2])
                
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                macro_data[name] = {
                    "price": round(current_price, 2),
                    "change_pct": round(change_pct, 2)
                }
            else:
                macro_data[name] = {"price": 0, "change_pct": 0}
                
        except Exception as e:
            print(f"無法取得 {name} 數據: {e}")
            macro_data[name] = {"price": 0, "change_pct": 0}
            
    return macro_data

if __name__ == "__main__":
    print(get_macro_environment())