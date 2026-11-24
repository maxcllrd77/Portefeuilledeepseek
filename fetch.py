import yfinance as yf, json, datetime

T = {
    "SAF": "SAF.PA", "SPX": "SXR8.DE", "WLD": "IWDA.AS", "EM": "IS3N.DE",
    "SXXP": "EXSA.DE", "GOLD": "GOLD.PA", "SPCX": None, "AFR": "AFK",
    "URA": "URNU.L", "BTC": "BTC-EUR", "RNDR": "RENDER-USD", "ETH": "ETH-EUR",
    "XRP": "XRP-EUR", "SOL": "SOL-EUR", "HBAR": "HBAR-USD", "BABA": "BABA",
    "ATEL": "ALATA.PA", "FLNC": "FLNC", "LVMH": "MC.PA", "AI": "AI.PA",
    "AAPL": "AAPL", "APO": "APO",
}
USD = {"RENDER-USD", "HBAR-USD", "BABA", "AAPL", "FLNC", "APO", "URA", "AFK"}

def close(t):
    if t is None: raise ValueError("pas de ticker")
    return yf.download(t, period="400d", progress=False,
                       auto_adjust=True)["Close"].squeeze().dropna()

fx = close("EURUSD=X")
hist, px, status = {}, {}, {}
for k, t in T.items():
    try:
        c = close(t)
        if t in USD:
            c = c / fx.reindex(c.index).ffill().bfill()
        px[k] = round(float(c.iloc[-1]), 4)
        status[k] = {"src": "yahoo", "t": t, "date": str(c.index[-1].date())}
        for d, v in (c.pct_change().dropna() * 100).items():
            hist.setdefault(str(d.date()), {})[k] = round(float(v), 2)
    except Exception as e:
        status[k] = {"src": "missing", "t": t, "err": str(e)[:80]}
        print("MANQUANT", k, t, e)

json.dump({"updated": datetime.date.today().isoformat(),
           "px": px, "hist": hist, "status": status},
          open("data/prices.json", "w"), indent=1)
print(f"OK {len(px)}/{len(T)}, manquants: {[k for k in T if k not in px]}")
