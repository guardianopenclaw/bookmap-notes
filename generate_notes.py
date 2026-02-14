#!/usr/bin/env python3
"""
Genererer Bookmap Cloud Notes CSV med prisnivåer.
Nivåer: Prev Day High/Low, Weekly High/Low, VAH/VAL/POC, Runde tall.
"""

import sys
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path

# Symbol-mapping: dxFeed -> yfinance
# Bookmap Cloud Notes krever eksplisitt format (ikke automap for futures)
SYMBOLS = {
    "NVDA@DXFEED":              ("NVDA",  "stock"),
    "AAPL@DXFEED":              ("AAPL",  "stock"),
    "TSLA@DXFEED":              ("TSLA",  "stock"),
    "AMD@DXFEED":               ("AMD",   "stock"),
    "/ESH26:XCME@DXFEED":       ("ES=F",  "es"),
    "/NQH26:XCME@DXFEED":       ("NQ=F",  "nq"),
}

# Trafikklys-farger (høyest til lavest prioritet)
RED    = "#FF0000"  # Kritiske nivåer
ORANGE = "#FF8C00"  # Viktige nivåer
YELLOW = "#FFD700"  # Sekundære nivåer
WHITE  = "#ffffff"  # Tekst
BLACK  = "#000000"  # Tekst (for gul bakgrunn)


def get_round_levels(price: float, sym_type: str) -> list[tuple[float, str, str]]:
    """
    Generer runde prisnivåer med trafikklys-prioritering.
    Returnerer: [(price, label, color), ...]
    
    Logikk:
    - Store runde (x000, x500) → ORANGE
    - Små runde (x100-x900, ikke x000/x500) → YELLOW
    - Kvart-nivåer (.25, .50, .75) rundt x000/x500 → YELLOW
    """
    if sym_type == "nq":
        step, spread = 50, 250
        major_mod = 500  # 25000, 25500, osv
    elif sym_type == "es":
        step, spread = 25, 150
        major_mod = 500  # 7000, 7500, osv
    else:
        step, spread = 5, 25
        major_mod = 50   # 200, 250, osv

    base = round(price / step) * step
    levels = []
    
    val = base - spread
    while val <= base + spread:
        val_rounded = round(val, 2)
        
        # Sjekk om dette er et stort rundt tall (x000 eller x500)
        is_major = (val_rounded % major_mod == 0)
        
        if is_major:
            # Hovedtall → ORANGE
            levels.append((val_rounded, f"Round {val_rounded:.0f}", ORANGE))
            
            # Legg til kvart-nivåer (.25, .50, .75) rundt major levels
            for quarter in [0.25, 0.50, 0.75]:
                quarter_level = round(val_rounded + quarter, 2)
                levels.append((quarter_level, f"Quarter {quarter_level:.2f}", YELLOW))
        else:
            # Små runde tall → YELLOW
            levels.append((val_rounded, f"Round {val_rounded:.0f}", YELLOW))
        
        val += step
    
    return levels


def compute_volume_profile(df) -> tuple[float, float, float]:
    """Beregn POC, VAH, VAL fra intraday-data (30-min bars)."""
    if df.empty or len(df) < 2:
        return None, None, None

    prices = ((df["High"] + df["Low"] + df["Close"]) / 3).values
    volumes = df["Volume"].values

    # Lag histogram med 50 bins
    price_min, price_max = prices.min(), prices.max()
    if price_max == price_min:
        return prices[0], prices[0], prices[0]

    bins = np.linspace(price_min, price_max, 51)
    hist = np.zeros(50)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    for p, v in zip(prices, volumes):
        idx = np.searchsorted(bins, p, side="right") - 1
        idx = max(0, min(idx, 49))
        hist[idx] += v

    # POC = bin med høyest volum
    poc_idx = np.argmax(hist)
    poc = round(float(bin_centers[poc_idx]), 2)

    # VAH/VAL: 70% av total volum sentrert rundt POC
    total_vol = hist.sum()
    target = total_vol * 0.70
    accumulated = hist[poc_idx]
    lo, hi = poc_idx, poc_idx

    while accumulated < target and (lo > 0 or hi < 49):
        expand_lo = hist[lo - 1] if lo > 0 else -1
        expand_hi = hist[hi + 1] if hi < 49 else -1
        if expand_lo >= expand_hi and lo > 0:
            lo -= 1
            accumulated += hist[lo]
        elif hi < 49:
            hi += 1
            accumulated += hist[hi]
        else:
            break

    vah = round(float(bin_centers[hi]), 2)
    val_ = round(float(bin_centers[lo]), 2)
    return poc, vah, val_


def make_note(symbol: str, price: float, note: str, fg: str, bg: str) -> str:
    return f"{symbol},{price:.2f},{note},{fg},{bg},left,3,FALSE"


def main():
    output_dir = Path(__file__).parent
    lines = [
        "Symbol,Price Level,Note,Foreground Color,Background Color,Text Alignment,Diameter,Draw Note Price Horizontal Line",
    ]

    for bm_sym, (yf_sym, sym_type) in SYMBOLS.items():
        print(f"Henter data for {yf_sym} (Bookmap: {bm_sym})...")
        ticker = yf.Ticker(yf_sym)

        # Daglig data for prev day og weekly
        try:
            daily = ticker.history(period="10d", interval="1d")
        except Exception as e:
            print(f"  FEIL daglig data: {e}")
            continue

        if daily.empty or len(daily) < 2:
            print(f"  Ikke nok daglig data for {yf_sym}")
            continue

        # Current price = siste close
        current = daily["Close"].iloc[-1]

        # Prev day = nest siste rad
        prev = daily.iloc[-2]
        prev_high = round(float(prev["High"]), 2)
        prev_low = round(float(prev["Low"]), 2)

        # KRITISKE NIVÅER (RØD)
        lines.append(make_note(bm_sym, prev_high, "Prev Day High", WHITE, RED))
        lines.append(make_note(bm_sym, prev_low, "Prev Day Low", WHITE, RED))

        # Weekly high/low (siste 5 handelsdager)
        week_data = daily.tail(5)
        wk_high = round(float(week_data["High"].max()), 2)
        wk_low = round(float(week_data["Low"].min()), 2)

        lines.append(make_note(bm_sym, wk_high, "Weekly High", WHITE, RED))
        lines.append(make_note(bm_sym, wk_low, "Weekly Low", WHITE, RED))

        # Volume Profile (30-min bars, 5 dager)
        try:
            intraday = ticker.history(period="5d", interval="30m")
            poc, vah, val_ = compute_volume_profile(intraday)
            if poc is not None:
                lines.append(make_note(bm_sym, poc, "POC", BLACK, RED))      # POC er kritisk
                lines.append(make_note(bm_sym, vah, "VAH", BLACK, ORANGE))   # VAH/VAL viktige
                lines.append(make_note(bm_sym, val_, "VAL", BLACK, ORANGE))
            else:
                print(f"  Kunne ikke beregne volume profile for {yf_sym}")
        except Exception as e:
            print(f"  FEIL intraday data: {e}")

        # Runde tall (med trafikklys-prioritering)
        for level, label, color in get_round_levels(float(current), sym_type):
            lines.append(make_note(bm_sym, level, label, WHITE, color))

    csv_path = output_dir / "notes.csv"
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nFerdig! Wrote {len(lines)-2} notes to {csv_path}")


if __name__ == "__main__":
    main()
