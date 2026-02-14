#!/usr/bin/env python3
"""
CLI tool for logging Bookmap level responses.

Usage:
  python3 log_level.py NQ 25000 bounce --before 24995 --after 25042 --time 17:30 --confluence poc,prev_day_low --notes "Strong bid"
"""

import json
import argparse
from datetime import datetime
from pathlib import Path

VALID_SYMBOLS = ["NQ", "ES", "NVDA", "AAPL", "TSLA", "AMD"]
VALID_RESPONSES = ["bounce", "rejection", "breakout", "false"]
VALID_LEVEL_TYPES = [
    "prev_day_high", "prev_day_low",
    "weekly_high", "weekly_low",
    "monthly_high", "monthly_low",
    "poc", "vah", "val",
    "round_major", "round_minor", "quarter"
]

def load_stats(path: Path) -> dict:
    if not path.exists():
        return {"version": "1.0", "metadata": {}, "logs": []}
    return json.loads(path.read_text())

def save_stats(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2) + "\n")

def main():
    parser = argparse.ArgumentParser(description="Log Bookmap level response")
    parser.add_argument("symbol", choices=VALID_SYMBOLS, help="Trading symbol")
    parser.add_argument("level", type=float, help="Price level")
    parser.add_argument("response", choices=VALID_RESPONSES, help="Market response")
    parser.add_argument("--before", type=float, help="Price before touch")
    parser.add_argument("--after", type=float, help="Price after move")
    parser.add_argument("--time", help="Time (HH:MM)")
    parser.add_argument("--level-type", choices=VALID_LEVEL_TYPES, help="Level type")
    parser.add_argument("--confluence", help="Comma-separated confluence factors")
    parser.add_argument("--notes", help="Additional notes")
    
    args = parser.parse_args()
    
    # Build log entry
    timestamp = datetime.now().isoformat()
    if args.time:
        # Override timestamp with specific time (today's date)
        today = datetime.now().date()
        timestamp = f"{today}T{args.time}:00"
    
    entry = {
        "timestamp": timestamp,
        "symbol": args.symbol,
        "level": args.level,
        "response": args.response,
    }
    
    if args.level_type:
        entry["level_type"] = args.level_type
    
    if args.before and args.after:
        entry["price_before"] = args.before
        entry["price_after"] = args.after
        entry["move_size"] = abs(args.after - args.before)
    
    if args.confluence:
        entry["confluence"] = [c.strip() for c in args.confluence.split(",")]
    
    if args.notes:
        entry["notes"] = args.notes
    
    # Determine time_context (half-hour mark?)
    if args.time:
        minute = int(args.time.split(":")[1])
        if 25 <= minute <= 35 or 55 <= minute <= 5:
            entry["time_context"] = "half_hour"
    
    # Load, append, save
    stats_path = Path(__file__).parent / "level-stats.json"
    data = load_stats(stats_path)
    data["logs"].append(entry)
    save_stats(stats_path, data)
    
    print(f"✓ Logged {args.symbol} {args.level} {args.response}")
    print(f"  Total entries: {len(data['logs'])}")

if __name__ == "__main__":
    main()
