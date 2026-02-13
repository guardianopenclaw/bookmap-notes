# Bookmap Cloud Notes Generator

Genererer prisnivåer som CSV for import i Bookmap Cloud Notes.

## Oppsett

```bash
pip install yfinance numpy
```

## Bruk

```bash
python generate_notes.py
```

Scriptet henter markedsdata via yfinance og genererer `notes.csv` med følgende nivåer:

| Nivå | Farge | Beskrivelse |
|------|-------|-------------|
| Prev Day High/Low | 🔵 Blå (#0066FF) | Forrige dags høy/lav |
| Weekly High/Low | 🟢 Grønn (#00AA00) | Ukentlig høy/lav (5 dager) |
| POC / VAH / VAL | 🟡 Gul (#FFD700) | Volume Profile (30-min bars, 5 dager) |
| Runde tall | ⚪ Grå (#808080) | Psykologiske nivåer nær current price |

## Symboler

- NVDA, AAPL, TSLA, AMD (aksjer)
- /ESH26:XCME (ES futures) — runde tall hver 25 poeng
- /NQH26:XCME (NQ futures) — runde tall hver 50 poeng

## Import i Bookmap

1. Kjør `python generate_notes.py`
2. Åpne Bookmap → Cloud Notes → Import CSV
3. Velg `notes.csv`

CSV-formatet bruker `#automap DXFEED` for automatisk symbol-matching.
