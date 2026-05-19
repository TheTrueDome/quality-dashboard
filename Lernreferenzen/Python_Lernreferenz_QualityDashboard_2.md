# Python Lernreferenz – Quality Dashboard
*Zuletzt aktualisiert: SPC-Karte (Tab 2)*

---

## 1. Imports & Bibliotheken

```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
```

| Bibliothek | Zweck |
|---|---|
| `streamlit` | Web-UI aus reinem Python |
| `pandas` | Tabellarische Daten lesen, filtern, transformieren |
| `matplotlib.pyplot` | Diagramme zeichnen (low-level, volle Kontrolle) |
| `numpy` | Numerische Berechnungen: Mittelwert, Standardabweichung, Arrays |

---

## 2. Streamlit – UI-Elemente

### Grundelemente
```python
st.set_page_config(page_title="...", layout="wide")  # muss erste st-Zeile sein
st.title("...")          # H1-Überschrift
st.subheader("...")      # H3-Überschrift
st.info("...")           # blaue Infobox
st.warning("...")        # gelbe Warnbox
st.success("...")        # grüne Erfolgsbox
st.dataframe(df)         # interaktive Tabelle
st.pyplot(fig)           # matplotlib-Diagramm rendern
```

### Tabs
```python
tab1, tab2 = st.tabs(["Name Tab 1", "Name Tab 2"])

with tab1:
    # alles hier gehört zu Tab 1
    # JEDE Zeile muss 4 Leerzeichen eingerückt sein
    st.subheader("...")

with tab2:
    # alles hier gehört zu Tab 2
    st.subheader("...")
```
**Wichtig:** Python erkennt Blöcke ausschließlich über Einrückung.
Sobald eine Zeile weniger eingerückt ist als die erste Zeile im Block,
ist der Block für Python beendet – egal ob das beabsichtigt war oder nicht.

### Eingaben
```python
uploaded_file = st.file_uploader("Label", type="csv", key="eindeutiger_key")
# key ist Pflicht wenn mehrere Uploader auf einer Seite sind

col1, col2, col3 = st.columns(3)    # Seite in 3 Spalten aufteilen
col1.metric("Titel", wert)          # KPI-Kachel mit Titel und Wert
```

---

## 3. pandas – Daten einlesen und transformieren

```python
df = pd.read_csv("datei.csv")       # Datei von Disk
df = pd.read_csv(uploaded_file)     # File-Objekt von st.file_uploader
```

### Spalten und Berechnungen
```python
df["Spalte"]                            # Spalte als Series auslesen
df["Neu"] = df["A"] + df["B"]          # neue Spalte erstellen
df["Kumuliert"] = df["Wert"].cumsum()  # kumulierte Summe
df["Wert"].sum()                        # Gesamtsumme (Skalar)
```

### Filtern und Sortieren
```python
df.sort_values("Spalte", ascending=False)   # absteigend sortieren
df.reset_index(drop=True)                    # Index auf 0,1,2,... zurücksetzen
df[df["Wert"] > 100]                         # Zeilen filtern nach Bedingung
```

### Boolean Series
```python
df["Ausreißer"] = (df["Wert"] > ucl) | (df["Wert"] < lcl)
```
Erstellt eine Spalte mit True/False pro Zeile.
`|` = ODER, `&` = UND.

```python
df["Ausreißer"].any()   # True wenn mindestens ein Wert True ist
df["Ausreißer"].sum()   # zählt alle True-Werte (True=1, False=0)
```

### Zeilen auswählen
```python
df.iloc[0]            # erste Zeile per Positionsindex
df.iloc[0]["Spalte"]  # Wert einer Spalte in der ersten Zeile
```

---

## 4. numpy – Numerische Berechnungen

```python
np.mean(df["Wert"])          # arithmetischer Mittelwert
np.std(df["Wert"], ddof=1)   # Standardabweichung
```

### ddof – Freiheitsgrade

| Wert | Formel | Wann verwenden |
|---|---|---|
| `ddof=0` | Division durch n | Vollständige Grundgesamtheit |
| `ddof=1` | Division durch n-1 | Stichprobe (Normalfall in QM/SPC) |

In der SPC-Karte arbeitest du fast immer mit Stichproben → `ddof=1` ist korrekt.

**Warum Standardabweichung in der SPC?**
UCL = Mittelwert + 3 × Std. bedeutet: alles was mehr als 3 Standardabweichungen
vom Durchschnitt entfernt liegt, gilt statistisch als unwahrscheinlich (< 0,3 %)
und wird als Signal gewertet.

---

## 5. matplotlib – Alle bisherigen Konzepte

### Diagramm erstellen
```python
fig, ax = plt.subplots(figsize=(12, 5))
# fig = das gesamte Bild
# ax  = das Diagramm darin (Axes)
plt.tight_layout()   # Abstände automatisch anpassen
```

### Linien und Balken
```python
ax.plot(x, y, color="steelblue", marker="o", linewidth=1.5, label="...")
ax.bar(x, y, color="steelblue")
ax.axhline(wert, color="green", linestyle="--", linewidth=1.5, label="...")
```

### scatter – Einzelpunkte hervorheben (neu)
```python
ax.scatter(x, y, color="red", zorder=5, s=80, label="Ausreißer")
```

| Parameter | Bedeutung |
|---|---|
| `s` | Punktgröße in Pixeln² |
| `zorder` | Zeichenreihenfolge – höher = weiter vorne |

**scatter vs. plot:**
`plot` verbindet Punkte mit einer Linie (für Verläufe).
`scatter` zeichnet nur Punkte ohne Linie (für hervorgehobene Einzelwerte).

### zorder – Zeichenreihenfolge (neu)
```python
ax.fill_between(..., zorder=1)   # Hintergrund
ax.plot(...,        zorder=2)    # Linie darüber
ax.scatter(...,     zorder=5)    # Punkte ganz vorne
```
Ohne zorder kann ein Element ein anderes ungewollt überdecken.

### fill_between – Fläche füllen (neu)
```python
ax.fill_between(x, y_unten, y_oben, alpha=0.05, color="green")
```

| Parameter | Bedeutung |
|---|---|
| `y_unten` | untere Grenze (z. B. LCL) |
| `y_oben` | obere Grenze (z. B. UCL) |
| `alpha` | Transparenz: 0.0 = unsichtbar, 1.0 = voll deckend |

### Zweite Y-Achse
```python
ax2 = ax1.twinx()   # teilt dieselbe X-Achse, eigene Y-Achse rechts
```

### Achsenbeschriftung
```python
ax.set_xlabel("...")
ax.set_ylabel("...", color="steelblue")
ax.set_ylim(0, 110)
ax.tick_params(axis="x", rotation=30)
ax.legend(loc="upper right")
```

---

## 6. f-Strings mit Formatierung

```python
f"Mittelwert: {mean:.2f}"    # 2 Nachkommastellen → "10.23"
f"UCL: {ucl:.3f}"            # 3 Nachkommastellen → "11.234"
f"{int(n)} Ausreißer"        # int() schneidet Nachkommastellen ab
```
Schema: `{variable:.Nf}` – N = Anzahl Nachkommastellen, f = float.

---

## 7. Projektstruktur bisher

```
~/quality-dashboard/
├── app.py              # Hauptanwendung (Tab 1: Pareto, Tab 2: SPC)
├── sample_data.csv     # Testdaten Pareto  (Spalten: Fehlerart, Anzahl)
└── spc_data.csv        # Testdaten SPC     (Spalten: Messung, Wert)
```

### App starten
```bash
conda activate qualitydash
dashboard               # Alias: cd ~/quality-dashboard && streamlit run app.py
```

---

## 8. Vorschau – Ishikawa (Tab 3)

Neue Konzepte die dabei dazukommen:

| Konzept | Bedeutung |
|---|---|
| `ax.axis('off')` | Achsen und Rahmen ausblenden |
| `ax.annotate` mit `arrowprops` | Pfeil mit Spitze zeichnen |
| `ax.plot([x1,x2], [y1,y2])` | Einzelne Linie zwischen zwei Punkten |
| `ax.text` mit `bbox` | Text mit Hintergrundbox |
| `ax.set_xlim / set_ylim` | Feste Zeichenfläche definieren |
| `st.text_input` | Einzeiliges Texteingabefeld |
| `st.text_area` | Mehrzeiliges Texteingabefeld |
