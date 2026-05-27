# Python Lernreferenz – Quality Dashboard
*Zuletzt aktualisiert: FMEA (Tab 4)*

---

## 1. Imports & Bibliotheken

```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import openpyxl
```

| Bibliothek | Zweck |
|---|---|
| `streamlit` | Web-UI aus reinem Python |
| `pandas` | Tabellarische Daten lesen, filtern, transformieren |
| `matplotlib.pyplot` | Diagramme zeichnen (low-level, volle Kontrolle) |
| `numpy` | Numerische Berechnungen: Mittelwert, Standardabweichung |
| `io` | Arbeitsspeicher-Puffer für Datei-Exporte (PNG, Excel) |
| `openpyxl` | Excel-Dateien lesen und schreiben |

**Regel:** Alle Imports gehören an den Dateianfang – nie mitten in einen Block.

---

## 2. Streamlit – UI-Elemente

### Grundelemente
```python
st.set_page_config(page_title="...", layout="wide")  # erste st-Zeile
st.title("...")          # H1
st.subheader("...")      # H3
st.markdown("**fett**")  # Markdown-Text
st.info("...")           # blaue Infobox
st.warning("...")        # gelbe Warnbox
st.success("...")        # grüne Erfolgsbox
st.error("...")          # rote Fehlerbox  ← neu in FMEA
st.dataframe(df)         # interaktive Tabelle (read-only)
st.pyplot(fig)           # matplotlib-Diagramm
```

### Tabs
```python
tab1, tab2, tab3, tab4 = st.tabs(["Name1", "Name2", "Name3", "Name4"])

with tab1:
    # Inhalt Tab 1 – 4 Leerzeichen Einrückung, konsequent
    st.subheader("...")
```
**Kernregel:** Alles was zu einem `with`-Block gehört, muss durchgehend
gleich eingerückt sein. Sobald die Einrückung bricht, ist der Block beendet.

### Eingaben
```python
uploaded_file = st.file_uploader("Label", type="csv", key="eindeutig")
problem = st.text_input("Label", value="Standardwert")
text    = st.text_area("Label", value="Zeile1\nZeile2", height=100)

col1, col2 = st.columns(2)
col1.metric("Titel", wert)
```

### data_editor – editierbare Tabelle (neu in FMEA)
```python
edited_df = st.data_editor(
    default_data,
    num_rows="dynamic",      # Zeilen hinzufügen / löschen möglich
    width='stretch',         # volle Breite (use_container_width ab 2026 deprecated)
    column_config={
        "S (Schwere)": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
    }
)
```

| Parameter | Bedeutung |
|---|---|
| `num_rows="dynamic"` | Nutzer kann Zeilen hinzufügen (+) und löschen |
| `width='stretch'` | Tabelle füllt die volle Containerbreite |
| `column_config` | Definiert Eingaberegeln pro Spalte (Typ, Min, Max, Schrittweite) |

Gibt einen neuen DataFrame zurück – der originale `default_data` bleibt unverändert.

### Download-Buttons
```python
# PNG-Export
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
buf.seek(0)
st.download_button(label="PNG speichern", data=buf,
                   file_name="datei.png", mime="image/png")

# Excel-Export
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="FMEA")
buffer.seek(0)
st.download_button(label="Excel exportieren", data=buffer,
                   file_name="datei.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
```

`io.BytesIO()` = Puffer im Arbeitsspeicher – matplotlib/pandas schreibt
die Datei da hinein, Streamlit liest sie aus und stellt sie als Download bereit.
Keine temporäre Datei auf der Festplatte nötig.

`buf.seek(0)` setzt den Lesecursor zurück an den Anfang des Puffers –
ohne das würde Streamlit eine leere Datei liefern.

---

## 3. pandas – Alle bisherigen Konzepte

### Einlesen
```python
df = pd.read_csv("datei.csv")        # von Disk
df = pd.read_csv(uploaded_file)      # von st.file_uploader
df = pd.DataFrame({                  # direkt aus Dictionary erstellen (neu FMEA)
    "Spalte1": [1, 2, 3],
    "Spalte2": ["a", "b", "c"],
})
```

### Spalten und Berechnungen
```python
df["Neu"]      = df["A"] * df["B"]           # neue Spalte
df["Kumuliert"]= df["Wert"].cumsum()          # kumulierte Summe
df["Wert"].sum()                               # Gesamtsumme
df["RPN"]      = df["S"] * df["O"] * df["D"] # RPN-Formel (FMEA)
```

### Filtern und Sortieren
```python
df.sort_values("Spalte", ascending=False)
df.reset_index(drop=True)
df[df["Wert"] > 100]                  # Zeilen nach Bedingung filtern
df.dropna(subset=["RPN"])             # Zeilen mit NaN in "RPN" entfernen (neu FMEA)
```

`dropna(subset=["RPN"])` ist wichtig wenn Nutzer leere Zeilen in
`st.data_editor` hinzufügen – leere Zellen erzeugen NaN, NaN * Zahl = NaN,
und `NaN.max()` würde einen Fehler werfen.

### Boolean Series
```python
df["Ausreißer"] = (df["Wert"] > ucl) | (df["Wert"] < lcl)
df["Ausreißer"].any()    # True wenn mind. ein True
df["Ausreißer"].sum()    # zählt alle True-Werte
```

### Styling – Zellen einfärben (neu in FMEA)
```python
def farbe_rpn(val):
    if val >= 200:
        return "background-color: #FFCCCC"   # rot
    elif val >= 100:
        return "background-color: #FFF3CC"   # gelb
    else:
        return "background-color: #CCFFCC"   # grün

styled = df.style.map(farbe_rpn, subset=["RPN"])
st.dataframe(styled, width='stretch')
```

`df.style.map(funktion, subset=["Spalte"])` wendet die Funktion auf jeden
einzelnen Zellwert in der angegebenen Spalte an und gibt einen CSS-String
zurück der die Hintergrundfarbe setzt.

**Wichtig:** Ab pandas 2.1 heißt die Methode `.map()` – vorher hieß sie
`.applymap()`. Bei Fehlermeldungen zu `applymap` immer auf `.map()` wechseln.

---

## 4. numpy – Numerische Berechnungen

```python
np.mean(df["Wert"])          # arithmetischer Mittelwert
np.std(df["Wert"], ddof=1)   # Standardabweichung (Stichprobe)
```

### ddof – Freiheitsgrade
| Wert | Formel | Wann |
|---|---|---|
| `ddof=0` | ÷ n | Vollständige Grundgesamtheit |
| `ddof=1` | ÷ n−1 | Stichprobe (Normalfall in QM/SPC) |

---

## 5. matplotlib – Alle Konzepte

### Grundstruktur
```python
fig, ax = plt.subplots(figsize=(12, 5))
plt.tight_layout()
st.pyplot(fig)
```

### Linien, Balken, Punkte
```python
ax.plot(x, y, color="steelblue", marker="o", linewidth=1.5, label="...")
ax.bar(x, y, color="steelblue")
ax.scatter(x, y, color="red", zorder=5, s=80, label="...")
ax.axhline(wert, color="green", linestyle="--", linewidth=1.5)
ax.fill_between(x, y_unten, y_oben, alpha=0.05, color="green")
```

### Ishikawa – Spezialkonzepte
```python
ax.axis('off')                          # Achsen ausblenden
ax.set_xlim(0, 10)                      # feste Zeichenfläche
ax.set_ylim(0, 7)
ax.annotate('', xy=ziel, xytext=start,  # Pfeil zeichnen
            arrowprops=dict(arrowstyle='->', color='black', lw=2.5))
ax.plot([x1, x2], [y1, y2], ...)        # einzelne Linie
ax.text(x, y, "Text", ha='center',      # Text mit Hintergrundbox
        bbox=dict(boxstyle='round,pad=0.5', facecolor='red'))
```

### Zweite Y-Achse (Pareto)
```python
ax2 = ax1.twinx()   # teilt X-Achse, eigene Y-Achse rechts
```

### zorder – Zeichenreihenfolge
Höherer Wert = weiter vorne. Verhindert dass Elemente sich gegenseitig überdecken.

---

## 6. f-Strings mit Formatierung

```python
f"{mean:.2f}"    # 2 Nachkommastellen
f"{ucl:.3f}"     # 3 Nachkommastellen
f"{int(n)} Stück" # in Integer umwandeln
```

---

## 7. Sicherheitsregeln

**Tokens und Passwörter gehören nie in den Code** – auch nicht als Kommentar.
Wenn ein Token versehentlich committed wurde:
1. Token sofort auf GitHub löschen (Settings → Developer settings → Tokens)
2. Neuen Token erstellen
3. Kommentar aus Code entfernen, committen, pushen

---

## 8. Projektstruktur

```
~/quality-dashboard/
├── app.py              # Tab 1: Pareto, Tab 2: SPC, Tab 3: Ishikawa, Tab 4: FMEA
├── sample_data.csv     # Testdaten Pareto  (Fehlerart, Anzahl)
├── spc_data.csv        # Testdaten SPC     (Messung, Wert)
├── start.sh            # Startet VS Code + Streamlit
└── git_push.sh         # Commit + Push mit Nachricht
```

### App starten
```bash
dashboard    # Alias für: conda activate + cd + streamlit run app.py
```

### Code committen und pushen
```bash
bash ~/quality-dashboard/git_push.sh
# oder per Desktop-Icon "Git Push"
```

---

## 9. Mögliche nächste Schritte

| Idee | Neue Konzepte |
|---|---|
| Supplier Scorecard (Projekt 2) | `fpdf2` für PDF-Erstellung, `openpyxl` Styling |
| Tab 5: KPI-Übersicht | `st.metric` mit Delta, mehrere DataFrames zusammenführen |
| Darkmode / Theming | `.streamlit/config.toml` Konfigurationsdatei |
| Passwortschutz | `streamlit-authenticator` Bibliothek |
