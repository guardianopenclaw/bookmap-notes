# Bookmap Level Statistics System

System for å logge og analysere respons på Cloud Notes-nivåer.

## Formål

Validere hvilke nivåtyper (prev day, weekly, POC, runde tall, osv.) som gir best bounce/reversal-rate. Data brukes til å prioritere nivåer i trafikklys-systemet.

## Nivåtyper

- **prev_day_high / prev_day_low** - Forrige handelsdag high/low (RØD)
- **weekly_high / weekly_low** - Ukens high/low (RØD)
- **monthly_high / monthly_low** - Månedens high/low (RØD)
- **poc** - Point of Control fra volume profile (RØD)
- **vah / val** - Value Area High/Low (ORANGE)
- **round_major** - Store runde tall (x000, x500) (ORANGE)
- **round_minor** - Små runde tall (x100-x900) (GUL)
- **quarter** - Kvart-nivåer (.25, .50, .75) rundt major (GUL)

## Respons-typer

- **bounce** - Pris reverserer fra nivået (success)
- **rejection** - Pris avvises ved nivået (success)
- **breakout** - Pris bryter gjennom uten respons (failure)
- **false** - Falsk signal / whipsaw (failure)

## Bruk

### 1. Logg en respons

```bash
python3 log_level.py NQ 25000 bounce \
  --before 24995 \
  --after 25042 \
  --time 17:30 \
  --level-type round_major \
  --confluence poc,prev_day_low \
  --notes "Strong bid absorption, half-hour mark"
```

**Minimum (kun symbol, level, respons):**
```bash
python3 log_level.py NQ 25000 bounce
```

### 2. Generer statistikk-rapport

```bash
python3 analyze_stats.py
```

Output: `stats-report.md` med:
- Success rate per nivåtype
- Average move size
- Time-of-day correlation
- Confluence effect

### 3. Se rådata

```bash
cat level-stats.json
```

## Eksempel workflow

**Mandag 17. februar, 17:30:**
- NQ nærmer seg 25000 (Round major)
- Ser bid absorption i DOM
- Pris bouncer fra 24995 til 25042
- Logger:
  ```bash
  python3 log_level.py NQ 25000 bounce \
    --before 24995 --after 25042 --time 17:30 \
    --level-type round_major --confluence half_hour
  ```

**Etter 2-4 uker:**
```bash
python3 analyze_stats.py
```

Rapporten viser f.eks:
- prev_day_high: 72% success
- poc: 61% success
- round_major: 54% success
- quarter: 38% success

→ Justér trafikklys-prioritering basert på reelle data.

## Confluence tracking

Når flere nivåer overlapper (f.eks. POC på rundt tall), logg alle faktorer:

```bash
python3 log_level.py NQ 25000 bounce \
  --level-type round_major \
  --confluence poc,prev_day_low,half_hour
```

Analysen vil vise om confluence øker success rate.

## Automatisering (fremtidig)

Når IBKR-connector er klar:
- Auto-detect når pris nærmer seg Cloud Notes-nivå
- Auto-log respons basert på price action
- Real-time statistikk

## Datafiler

- **level-stats.json** - Rådata (alle loggoppføringer)
- **stats-report.md** - Generert rapport med analyse
- **log_level.py** - CLI logging tool
- **analyze_stats.py** - Analyse-script

## Tips

- Logg hver dag etter trading
- Noter confluence-faktorer (flere nivåer = høyere sannsynlighet?)
- Noter time-of-day (halvtime-marks gir ofte bedre respons)
- Bruk --notes for kvalitative observasjoner fra Bookmap
