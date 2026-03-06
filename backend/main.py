import os
import sys
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from data_fetchers.macro_env import get_macro_environment
from screeners.stock_filter import get_midcap_institutional_buys

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

@app.get("/api/macro")
async def read_macro():
    return get_macro_environment()

@app.get("/api/stocks")
async def read_stocks():
    df = get_midcap_institutional_buys()
    return df.to_dict(orient="records")

@app.get("/api/ai-report")
async def get_ai_report(stocks: str = Query(default="")):
    if not stocks:
        return {"report": "今日籌碼混沌，無百億中型股符合強勢買超條件，建議保留現金觀望。"}
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"report": f"【系統提示】請至 Vercel 後台設定 GEMINI_API_KEY。今日焦點標的：{stocks}"}
        
    try:
        # 💡 輕量化魔法：直接打 API 網址，不依賴肥大的官方套件
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": f"你是一位頂尖的量化交易員。請根據以下今日法人重金買超的中型股名單：{stocks}。寫一段約 50 字的極簡早報，語氣要專業、俐落，帶有華爾街的動能投資風格，直接寫出見解，不要列點。"}]
            }]
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        
        # 解析 Gemini 回傳的結果
        report_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return {"report": report_text}
        
    except Exception as e:
        return {"report": f"系統運算中...今日焦點標的：{stocks}"}