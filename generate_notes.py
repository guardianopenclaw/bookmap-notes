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
# Bookmap symbol (uten @DXFEED suffix) -> (yfinance ticker, type)
SYMBOLS = {
    "NVDA":              ("NVDA",  "stock"),
    "AAPL":              ("AAPL",  "stock"),
    "TSLA":              ("TSLA",  "stock"),
    "AMD":               ("AMD",   "stock"),
    "ESH26":             ("ES=F",  "es"),    # /ESH26 i Bookmap vises som ESH26 uten slash
    "NQH26":             ("NQ=F",  "nq"),    # /NQH26 i Bookmap vises som NQH26 uten slash
}

# Farger
BLUE   = "#0066FF"
YELLOW = "#FFD700"
GREY   = "#808080"
GREEN  = "#00AA00"
WHITE  = "#ffffff"
BLACK  = "#000000"


def get_round_levels(price: float, sym_type: str) -> list[float]:
    """Generer runde/psykologiske prisnivåer rundt current price."""
    if sym_type == "nq":
        step, spread = 50, 250
    elif sym_type == "es":
        step, spread = 25, 150
    else:
        step, spread = 5, 25

    base = round(price / step) * step
    levels = []
    val = base - spread
    while val <= base + spread:
        levels.append(round(val, 2))
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
        "#automap DXFEED,,,,,,,",
        "Symbol,Price Level,Note,Foreground Color,Background Color,Text Alignment,Diameter,Draw Note Price Horizontal Line",
    ]

    for bm_sym, (yf_sym, sym_type) in SYMBOLS.items():
        # bm_sym er allerede riktig format for Bookmap (NVDA, ESH26, NQH26)
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

        lines.append(make_note(bm_sym, prev_high, "Prev Day High", WHITE, BLUE))
        lines.append(make_note(bm_sym, prev_low, "Prev Day Low", WHITE, BLUE))

        # Weekly high/low (siste 5 handelsdager)
        week_data = daily.tail(5)
        wk_high = round(float(week_data["High"].max()), 2)
        wk_low = round(float(week_data["Low"].min()), 2)

        lines.append(make_note(bm_sym, wk_high, "Weekly High", WHITE, GREEN))
        lines.append(make_note(bm_sym, wk_low, "Weekly Low", WHITE, GREEN))

        # Volume Profile (30-min bars, 5 dager)
        try:
            intraday = ticker.history(period="5d", interval="30m")
            poc, vah, val_ = compute_volume_profile(intraday)
            if poc is not None:
                lines.append(make_note(bm_sym, poc, "POC", BLACK, YELLOW))
                lines.append(make_note(bm_sym, vah, "VAH", BLACK, YELLOW))
                lines.append(make_note(bm_sym, val_, "VAL", BLACK, YELLOW))
            else:
                print(f"  Kunne ikke beregne volume profile for {yf_sym}")
        except Exception as e:
            print(f"  FEIL intraday data: {e}")

        # Runde tall
        for level in get_round_levels(float(current), sym_type):
            lines.append(make_note(bm_sym, level, f"Round {level:.0f}", WHITE, GREY))

    csv_path = output_dir / "notes.csv"
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nFerdig! Wrote {len(lines)-2} notes to {csv_path}")


if __name__ == "__main__":
    main()
