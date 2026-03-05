import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 💡 絕對路徑修正：告訴 Vercel 去 backend 資料夾裡找東西
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 現在 Python 就能順利看到 data_fetchers 和 screeners 了
from data_fetchers.macro_env import get_macro_environment
from screeners.stock_filter import get_midcap_institutional_buys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/macro")
async def read_macro():
    return get_macro_environment()

@app.get("/api/stocks")
async def read_stocks():
    df = get_midcap_institutional_buys()
    return df.to_dict(orient="records")