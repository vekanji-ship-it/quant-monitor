import os
import sys
import requests
import xml.etree.ElementTree as ET
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from data_fetchers.macro_env import get_macro_environment
from screeners.stock_filter import get_midcap_institutional_buys

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/macro")
async def read_macro():
    return get_macro_environment()

@app.get("/api/stocks")
async def read_stocks():
    df = get_midcap_institutional_buys()
    return df.to_dict(orient="records")

@app.get("/api/ai-report")
async def get_ai_report(stocks: str = Query(default="")):
    if not stocks: return {"report": "今日籌碼混沌，無符合強勢買超條件之中型股，建議保留現金觀望。"}
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key: return {"report": f"今日焦點標的：{stocks} (等待 AI 鑰匙啟用)"}
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": f"你是一位頂尖量化交易員。根據今日法人重金買超標的：{stocks}。寫約 50 字極簡早報，語氣專業俐落，帶有動能投資風格，直接寫出見解，不要列點。"}]}]}
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        return {"report": response.json()["candidates"][0]["content"]["parts"][0]["text"]}
    except: return {"report": f"AI 運算中。焦點標的：{stocks}"}

# 💡 修改 B：新增輕量級每日財經頭條 API
@app.get("/api/news")
async def read_news():
    try:
        url = "https://news.google.com/rss/search?q=股市+財經+when:1d&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        res = requests.get(url, timeout=5)
        root = ET.fromstring(res.content)
        news_list = [{"title": item.find('title').text, "link": item.find('link').text} for item in root.findall('.//item')[:5]]
        return news_list
    except: return []