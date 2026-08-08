import os
import pandas as pd
import json
import yfinance as yf
from datetime import datetime
import pytz

KST = pytz.timezone("Asia/Seoul")
DATA_DIR    = "data"
REPORT_FILE = os.path.join(DATA_DIR, "us_flow_report.md")
REPORT_JSON_FILE = os.path.join(DATA_DIR, "us_flow_report.json")

def generate_us_flow_report():
    print("Generating US Flow Report...")
    etfs = {
        "SPY": "S&P 500",
        "QQQ": "Nasdaq 100",
        "IWM": "Russell 2000",
        "RSP": "S&P 500 Equal Weight",
        "SOXX": "Semiconductor"
    }
    
    results = []
    market_dates = []
    
    for ticker, name in etfs.items():
        try:
            df = yf.download(ticker, period="1mo", progress=False)
            if df.empty or len(df) < 20:
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            close = df['Close']
            volume = df['Volume']
            market_dates.append(pd.Timestamp(df.index[-1]).strftime("%Y-%m-%d"))
            
            recent_pct = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
            recent_vol = volume.iloc[-1]
            avg_vol_20 = volume.rolling(20).mean().iloc[-1]
            
            # 거래량 가중 프록시: (종가등락률 * 거래량) / 20일평균거래량
            flow_proxy = (recent_pct * recent_vol) / avg_vol_20
            
            results.append({
                "ticker": ticker,
                "name": name,
                "pct": float(recent_pct),
                "vol_ratio": float(recent_vol / avg_vol_20),
                "flow_proxy": float(flow_proxy)
            })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            
    # Sort by flow_proxy descending (strongest buy pressure first)
    results.sort(key=lambda x: x["flow_proxy"], reverse=True)
    
    now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append(f"## 🦅 미국 주요 ETF 수급 동향 프록시 리포트")
    lines.append(f"*업데이트 시간: {now_str} (KST)*\n")
    lines.append("> ⚠️ **주의**: 본 데이터는 실제 기관의 자금 유출입(Creation/Redemption) 데이터가 아닌, **일일 종가 등락률과 거래량을 결합한 가중 프록시 지표(근사치)**입니다. 무료 API의 한계로 인해 매수/매도 압력을 추정하는 용도로만 활용하십시오.\n")
    
    lines.append("| Ticker | Name | 등락률(%) | 거래량 비율(vs 20일) | 수급 프록시 스코어 | 상태 |")
    lines.append("|--------|------|-----------|--------------------|--------------------|------|")
    
    for r in results:
        status = "🟢 강한 매수" if r["flow_proxy"] > 1.0 else ("🟡 중립" if r["flow_proxy"] > -1.0 else "🔴 강한 매도")
            
        lines.append(f"| **{r['ticker']}** | {r['name']} | {r['pct']:.2f}% | {r['vol_ratio']:.2f}x | **{r['flow_proxy']:.2f}** | {status} |")
        
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    snapshot = {
        "generated_at_kst": now_str,
        "market_as_of": max(market_dates) if market_dates else None,
        "method": "daily_return_pct_x_volume_ratio_20d",
        "is_actual_fund_flow": False,
        "records": results,
    }
    with open(REPORT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
        
    print(f"Saved to {REPORT_FILE} and {REPORT_JSON_FILE}")

if __name__ == "__main__":
    generate_us_flow_report()
