# Oppdrag: Bookmap Level Statistics Infrastructure

## Mål
Bygg komplett system for å logge og analysere respons på Bookmap Cloud Notes-nivåer.
Dette skal brukes for å validere hvilke nivåtyper som gir best bounce/reversal-rate.

## Nivåtyper (fra generate_notes.py)
- prev_day_high / prev_day_low
- weekly_high / weekly_low
- monthly_high / monthly_low
- poc (Point of Control)
- vah / val (Value Area High/Low)
- round_major (x000, x500)
- round_minor (andre x00)
- quarter (x.25, x.50, x.75 rundt major)

## Oppgaver

### 1. Logging-struktur (JSON)
Lag `bookmap-notes/level-stats.json`:
```json
{
  "version": "1.0",
  "logs": [
    {
      "timestamp": "2026-02-17T17:30:00",
      "symbol": "NQ",
      "level": 25000.0,
      "level_type": "round_major",
      "response": "bounce",
      "price_before": 24995.0,
      "price_after": 25042.0,
      "move_size": 47.0,
      "time_context": "half_hour",
      "confluence": ["round_major", "prev_day_low"],
      "notes": "Strong bid absorption visible"
    }
  ]
}
```

### 2. CLI logging tool
Script: `bookmap-notes/log_level.py`
Usage: `python3 log_level.py NQ 25000 bounce --before 24995 --after 25042 --time 17:30 --confluence poc`

Validering:
- Symbol må være en av: NQ, ES, NVDA, AAPL, TSLA, AMD
- Response må være: bounce, rejection, breakout, false
- Level må være numerisk

### 3. Analyse-script
Script: `bookmap-notes/analyze_stats.py`
Output: `bookmap-notes/stats-report.md`

Beregn:
- Success rate per level_type
- Average move size per type
- Time-of-day correlation (half-hour intervals)
- Confluence effect (2+ levels = better?)
- Win rate når flere faktorer overlapper

### 4. Visualisering (optional, hvis tid)
- Matplotlib chart: level_type vs bounce_rate
- Heatmap: time_of_day vs success_rate

## Levering
Commit alt til bookmap-notes/ repo:
- level-stats.json (tom struktur)
- log_level.py (CLI tool)
- analyze_stats.py (analyse)
- STATS_README.md (hvordan bruke systemet)

Git commit message: "Statistics infrastructure for level tracking"

## Constraints
- Python 3.9+ (Mac Mini har dette)
- Ingen eksterne dependencies utover stdlib (matplotlib optional)
- Kjør tester for å verifisere at logging fungerer
