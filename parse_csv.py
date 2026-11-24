import csv, json, sys, datetime

KM = {
    "Safran": ("SAF", "Safran", "Actions"),
    "Core S&P 500 USD (Acc)": ("SPX", "Core S&P 500", "ETF & Or"),
    "Core MSCI World USD (Acc)": ("WLD", "Core MSCI World", "ETF & Or"),
    "MSCI Emerging Markets EUR (Acc)": ("EM", "MSCI Emerging Markets", "ETF & Or"),
    "Core Stoxx Europe 600 EUR (Acc)": ("SXXP", "Core Stoxx Europe 600", "ETF & Or"),
    "Physical Gold": ("GOLD", "Physical Gold", "ETF & Or"),
    "SpaceX": ("SPCX", "SpaceX", "Actions"),
    "MSCI Africa Top 50 Swap USD (Acc)": ("AFR", "MSCI Africa Top 50", "ETF & Or"),
    "Uranium USD (Acc)": ("URA", "Uranium", "ETF & Or"),
    "Bitcoin": ("BTC", "Bitcoin", "Crypto"),
    "Render": ("RNDR", "Render", "Crypto"),
    "Ethereum": ("ETH", "Ethereum", "Crypto"),
    "XRP": ("XRP", "XRP", "Crypto"),
    "Solana": ("SOL", "Solana", "Crypto"),
    "Hedera": ("HBAR", "Hedera", "Crypto"),
    "Alibaba Group": ("BABA", "Alibaba Group", "Actions"),
    "Avenir Telecom": ("ATEL", "Avenir Telecom", "Actions"),
    "Fluence Energy": ("FLNC", "Fluence Energy", "Actions"),
    "LVMH Moët Hennessy": ("LVMH", "LVMH Moët Hennessy", "Actions"),
    "Air Liquide": ("AI", "Air Liquide", "Actions"),
    "Apple": ("AAPL", "Apple", "Actions"),
    "Private Equity": ("APO", "Private Equity (Apollo)", "Actions"),
    "Bureau Veritas": ("BVI", "Bureau Veritas", "Actions"),
    "Sanofi": ("SAN", "Sanofi", "Actions"),
    "Adobe": ("ADBE", "Adobe", "Actions"),
    "Synopsys": ("SNPS", "Synopsys", "Actions"),
    "Visa": ("V", "Visa", "Actions"),
    "Kalray": ("ALKAL", "Kalray", "Actions"),
    "Alten": ("ATE", "Alten", "Actions"),
}

def fnum(s):
    if not s: return 0.0
    try:
        return float(str(s).replace(",", ".").strip() or 0)
    except ValueError:
        return 0.0

def parse(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    rows = [{k.lower().strip(): (v or "").strip() for k, v in r.items()} for r in rows]

    pos, versements, dividendes, frais = {}, {}, {}, {}
    tx, cash_in = [], []

    def ensure(name):
        if name not in pos:
            meta = KM.get(name, (name[:5].upper(), name, "Actions"))
            pos[name] = {"k": meta[0], "n": meta[1], "c": meta[2],
                         "sh": 0.0, "cost": 0.0, "div": 0.0}
        return pos[name]

    for r in rows:
        cat  = r.get("category", "").upper()
        typ  = r.get("type", "").upper()
        name = r.get("name", "")
        date = (r.get("date") or "")[:10]
        month = date[:7]
        amount = fnum(r.get("amount", ""))
        shares = fnum(r.get("shares", ""))
        fee  = abs(fnum(r.get("fee", "")))
        tax  = abs(fnum(r.get("tax", "")))

        if cat == "CASH" and typ in ("CUSTOMER_INPAYMENT", "TRANSFER_INBOUND",
                                     "TRANSFER_INSTANT_INBOUND") and amount > 0:
            cash_in.append({"date": date, "amount": amount})
        if cat == "CASH" and typ in ("TRANSFER_OUTBOUND", "TRANSFER_INSTANT_OUTBOUND") and amount < 0:
            cash_in.append({"date": date, "amount": amount})

        if fee > 0 or tax > 0:
            frais[month] = round(frais.get(month, 0) + fee + tax, 2)

        if cat == "TRADING" and typ in ("BUY", "SELL"):
            p = ensure(name)
            if typ == "BUY":
                p["sh"] += shares
                if amount < 0:
                    p["cost"] += -amount
                    cl = p["c"]
                    versements.setdefault(month, {}).setdefault(cl, 0.0)
                    versements[month][cl] = round(versements[month][cl] + (-amount), 2)
            else:
                if p["sh"] > 1e-9:
                    p["cost"] *= max(0.0, 1 + shares / p["sh"])
                p["sh"] += shares

        elif cat == "CASH" and typ == "PRIVATE_MARKET_BUY":
            p = ensure(name)
            if amount < 0:
                p["cost"] += -amount
                cl = p["c"]
                versements.setdefault(month, {}).setdefault(cl, 0.0)
                versements[month][cl] = round(versements[month][cl] + (-amount), 2)

        elif cat == "CASH" and typ == "IPO_SUBSCRIPTION":
            p = ensure(name)
            if amount < 0:
                p["cost"] += -amount
            elif amount > 0:
                p["cost"] = max(0.0, p["cost"] - amount)

        elif cat == "CORPORATE_ACTION" and typ == "BONUS_ISSUE":
            ensure(name)["sh"] += shares

        elif cat == "CASH" and typ == "DIVIDEND":
            if name in pos: pos[name]["div"] += amount
            dividendes[month] = round(dividendes.get(month, 0) + amount, 2)
        elif cat == "CASH" and typ == "INTEREST_PAYMENT":
            dividendes[month] = round(dividendes.get(month, 0) + amount, 2)

        if cat in ("TRADING", "CASH") and typ not in ("PEA_MARKETING", "BONUS", "TAX_OPTIMIZATION"):
            tx.append({"date": date, "cat": cat, "type": typ, "name": name,
                       "amount": amount, "shares": shares})

    A = []
    for name, p in pos.items():
        if p["sh"] < 1e-4: continue
        A.append([p["n"], p["k"], p["c"], round(p["cost"], 2), round(p["sh"], 6), None])

    M = {m: {c: v for c, v in d.items() if abs(v) > 0.005}
         for m, d in versements.items() if any(abs(v) > 0.005 for v in d.values())}
    D = {m: v for m, v in dividendes.items() if abs(v) > 0.005}
    F = {m: v for m, v in frais.items() if abs(v) > 0.005}

    return {
        "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "A": sorted(A, key=lambda x: -x[3]),
        "M": dict(sorted(M.items())),
        "D": dict(sorted(D.items())),
        "F": dict(sorted(F.items())),
        "TX": tx,
        "CASHIN": cash_in,
    }

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "Exportation_de_transactions.csv"
    out = parse(src)
    json.dump(out, open("data/portfolio.json", "w"), ensure_ascii=False, indent=1)
    print(f"OK {len(out['A'])} positions, {len(out['TX'])} tx, {len(out['CASHIN'])} flux cash")
