# Python Lernreferenz – Quality Dashboard

Kurzreferenz für den geschriebenen Code. Ziel: Befehle verstehen, nicht nur abtippen.

---

## 1. Imports

```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
```

| Befehl | Bedeutung |
|---|---|
| `import X` | Lädt eine externe Bibliothek in den aktuellen Namespace |
| `import X as Y` | Lädt X, gibt ihm den kürzeren Alias Y – Konvention: `pd`, `plt`, `st` sind Standard-Aliase |

**Bibliotheken im Überblick:**
- `streamlit` – baut Web-UIs aus reinem Python, kein HTML/CSS nötig
- `pandas` – Datenanalyse: liest, filtert, transformiert tabellarische Daten (wie Excel, aber per Code)
- `matplotlib.pyplot` – Diagramme zeichnen (low-level, volle Kontrolle)

---

## 2. Streamlit – UI-Elemente

```python
st.set_page_config(page_title="Quality Dashboard", layout="wide")
st.title("📊 Quality Dashboard")
st.subheader("Rohdaten")
st.info("Keine Datei hochgeladen – Beispieldaten werden verwendet.")
st.dataframe(df)
st.pyplot(fig)
```

| Befehl | Was es macht |
|---|---|
| `set_page_config(...)` | Setzt Browser-Tab-Titel und Layout – muss als **erste** st-Zeile stehen |
| `st.title()` | Große Überschrift (H1) |
| `st.subheader()` | Kleinere Überschrift (H3) |
| `st.info()` | Blaue Infobox – für Hinweise an den Nutzer |
| `st.dataframe(df)` | Rendert einen pandas DataFrame als interaktive Tabelle |
| `st.pyplot(fig)` | Rendert ein matplotlib-Figure-Objekt als Bild |

```python
uploaded_file = st.file_uploader("CSV-Datei hochladen", type="csv")
```
Erzeugt einen Upload-Button. Gibt ein File-Objekt zurück oder `None` wenn nichts hochgeladen wurde.

```python
col1, col2, col3 = st.columns(3)
col1.metric("Fehler gesamt", int(df_sorted["Anzahl"].sum()))
```
`st.columns(3)` teilt die Seite in 3 gleich breite Spalten auf.
`metric()` zeigt eine KPI-Kachel mit Titel und Wert.

---

## 3. pandas – Daten einlesen und transformieren

```python
df = pd.read_csv("sample_data.csv")
```
Liest eine CSV-Datei als **DataFrame** – das zentrale Datenformat in pandas (wie eine Tabelle mit benannten Spalten).

```python
df_sorted = df.sort_values("Anzahl", ascending=False).reset_index(drop=True)
```

| Teil | Bedeutung |
|---|---|
| `.sort_values("Anzahl", ascending=False)` | Sortiert nach Spalte "Anzahl", absteigend |
| `.reset_index(drop=True)` | Setzt den Zeilenindex auf 0, 1, 2, … zurück. `drop=True` verhindert, dass der alte Index als neue Spalte auftaucht |

```python
df_sorted["Kumuliert_%"] = (df_sorted["Anzahl"].cumsum() / df_sorted["Anzahl"].sum() * 100)
```

| Teil | Bedeutung |
|---|---|
| `df["Spalte"] = ...` | Erstellt eine neue Spalte oder überschreibt eine bestehende |
| `.cumsum()` | Kumulierte Summe: jede Zeile enthält die Summe aller vorherigen Werte |
| `.sum()` | Gesamtsumme der Spalte (einzelner Skalar) |
| `* 100` | Umrechnung in Prozent |

```python
df_sorted.iloc[0]["Fehlerart"]
```
`iloc[0]` greift auf die **erste Zeile** per Positionsindex zu (unabhängig vom Spalteninhalt). `["Fehlerart"]` holt dann den Wert der Spalte.

---

## 4. matplotlib – Diagramme

```python
fig, ax1 = plt.subplots(figsize=(10, 5))
```
Erstellt eine Figure (`fig` = das gesamte Bild) und eine Axes (`ax1` = das eigentliche Diagramm darin).
`figsize=(10, 5)` = Breite 10 Zoll, Höhe 5 Zoll.

```python
ax1.bar(df_sorted["Fehlerart"], df_sorted["Anzahl"], color="steelblue")
ax1.set_xlabel("Fehlerart")
ax1.set_ylabel("Anzahl", color="steelblue")
ax1.tick_params(axis="x", rotation=30)
```

| Befehl | Bedeutung |
|---|---|
| `ax.bar(x, y)` | Balkendiagramm: x = Kategorien, y = Werte |
| `set_xlabel / set_ylabel` | Achsenbeschriftungen |
| `tick_params(axis="x", rotation=30)` | Dreht die x-Achsenbeschriftung um 30°, verhindert Überlappung |

```python
ax2 = ax1.twinx()
```
Erstellt eine **zweite Y-Achse** rechts, die dieselbe X-Achse teilt. Klassisches Muster für Pareto (Balken links = Anzahl, Linie rechts = Prozent).

```python
ax2.plot(df_sorted["Fehlerart"], df_sorted["Kumuliert_%"], color="red", marker="o", linewidth=2)
ax2.axhline(80, color="gray", linestyle="--", linewidth=1)
ax2.set_ylim(0, 110)
```

| Befehl | Bedeutung |
|---|---|
| `ax.plot(x, y)` | Liniendiagramm |
| `marker="o"` | Datenpunkte als Kreise markieren |
| `axhline(80, ...)` | Horizontale Linie bei y=80 – die 80%-Grenze der Pareto-Regel |
| `set_ylim(0, 110)` | Y-Achse auf 0–110 begrenzen (110 damit die 100%-Linie nicht am Rand klebt) |

```python
plt.tight_layout()
```
Passt Abstände automatisch an, damit Achsenbeschriftungen sich nicht überschneiden. Fast immer sinnvoll vor `st.pyplot()`.

---

## 5. Kontrollfluss & Dateilogik

```python
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("sample_data.csv")
```
`st.file_uploader` gibt `None` zurück wenn nichts hochgeladen wurde – `None` ist in Python falsy, ein File-Objekt truthy. `pd.read_csv()` akzeptiert sowohl Dateipfade (Strings) als auch File-Objekte direkt.

---

## Nächste Schritte (SPC-Karte)

Neue Konzepte die dabei dazukommen:
- `numpy` für Standardabweichung (`np.std`) und Mittelwert (`np.mean`)
- `pd.date_range` für Zeitachsen
- `ax.axhline` kennst du schon – wird für UCL/LCL/CL wiederverwendet
- Grundlegendes Verständnis von Normalverteilung und 3-Sigma-Regel
