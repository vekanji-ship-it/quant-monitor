from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_fetchers.macro_env import get_macro_environment
from screeners.stock_filter import get_midcap_institutional_buys # 💡 新增：匯入選股模組

app = FastAPI()

# 允許跨網域請求 (讓你的 HTML 檔案能讀取 API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/macro")
async def read_macro():
    data = get_macro_environment()
    return data

# 💡 新增：提供選股清單的 API 路由
@app.get("/api/stocks")
async def read_stocks():
    df = get_midcap_institutional_buys()
    return df.to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    # 啟動伺服器，監聽 8000 埠口
    uvicorn.run(app, host="127.0.0.1", port=8000)