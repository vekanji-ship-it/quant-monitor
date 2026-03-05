import yfinance as yf
import pandas as pd

def get_macro_environment():
    tickers = {
        "Nasdaq": "^IXIC",
        "SOX": "^SOX",
        "USD_TWD": "TWD=X"
    }
    
    macro_data = {}
    
    for name, ticker in tickers.items():
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        
        if len(hist) >= 2:
            # 加入 float() 強制轉換型態 👇
            current_price = float(hist['Close'].iloc[-1])
            prev_price = float(hist['Close'].iloc[-2])
            
            change_pct = ((current_price - prev_price) / prev_price) * 100
            
            macro_data[name] = {
                "price": round(current_price, 2),
                "change_pct": round(change_pct, 2)
            }
            
    return macro_data

if __name__ == "__main__":
    print(get_macro_environment())