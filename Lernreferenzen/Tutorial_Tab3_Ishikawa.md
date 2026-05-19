# Tutorial – Tab 3: Ishikawa-Diagramm

## Was ist ein Ishikawa-Diagramm?

Ein Ishikawa-Diagramm (auch Fischgräten- oder Ursache-Wirkungs-Diagramm) visualisiert
systematisch mögliche Ursachen für ein Problem. Die Struktur sieht aus wie ein Fischskelett:

- Der Pfeil rechts = das Problem (Wirkung, "Fischkopf")
- Der Hauptpfeil (Rückgrat) zeigt von links nach rechts zum Problem
- 6 schräge Äste = Kategorien (die "6M")
- Kleine Zweige an den Ästen = konkrete Einzelursachen

**Die 6M-Kategorien** (Standard im QM):

| Kategorie | Bedeutung |
|---|---|
| Mensch | Qualifikation, Fehler, Motivation |
| Maschine | Verschleiß, Kalibrierung, Ausfälle |
| Material | Rohstoffqualität, Lieferantenfehler |
| Methode | Prozessanweisungen, Standards |
| Messung | Messgenauigkeit, Kalibrierung |
| Mitwelt | Temperatur, Lärm, Umgebung |

---

## Neue matplotlib-Konzepte in diesem Tab

### ax.axis('off')
```python
ax.axis('off')
```
Blendet Achsenlinien, Achsenbeschriftungen und den Rahmen komplett aus.
Nötig für jedes Diagramm das kein klassisches x/y-Koordinatensystem ist –
also Netzdiagramme, Schemata, Flowcharts, Ishikawa.

### ax.set_xlim / ax.set_ylim
```python
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
```
Legt die sichtbare Fläche fest. Da wir `axis('off')` verwenden,
definieren wir damit ein manuelles Koordinatensystem für unsere Zeichnung.
Alle `ax.plot` und `ax.text` Aufrufe verwenden danach diese Koordinaten.

### ax.plot für einzelne Linien
```python
ax.plot([x1, x2], [y1, y2], color="steelblue", linewidth=2)
```
Bisher haben wir `ax.plot(df["x"], df["y"])` verwendet – eine ganze Spalte.
Für das Ishikawa übergeben wir direkt zwei Punkte als Listen: Start [x1,y1] und Ende [x2,y2].

### ax.annotate mit arrowprops
```python
ax.annotate(
    '',                          # kein Text, nur Pfeil
    xy=(9.5, 3),                 # Pfeilspitze (Ziel)
    xytext=(0.5, 3),             # Pfeilstart
    arrowprops=dict(
        arrowstyle='->',
        color='black',
        lw=2.5
    )
)
```
`ax.plot` kann keine Pfeilspitzen zeichnen – dafür gibt es `ax.annotate`.
`arrowstyle='->'` ist der klassische Pfeil. Weitere Stile: `'-|>'`, `'fancy'`.

### ax.text mit bbox
```python
ax.text(
    x, y,                        # Position
    "Text",
    ha='center',                 # horizontale Ausrichtung: left, center, right
    va='center',                 # vertikale Ausrichtung: top, center, bottom
    fontsize=10,
    fontweight='bold',
    color='white',
    bbox=dict(
        boxstyle='round,pad=0.4',
        facecolor='steelblue',
        alpha=0.9
    )
)
```
`bbox` fügt dem Text eine Hintergrundbox hinzu.
`boxstyle='round'` = abgerundete Ecken, `pad=0.4` = Innenabstand.

### st.text_input und st.text_area
```python
problem = st.text_input("Problem / Wirkung", value="Hohe Ausschussrate")
ursachen = st.text_area("Ursachen (eine pro Zeile)", value="Linie 1\nLinie 2")
liste = [u.strip() for u in ursachen.split("\n") if u.strip()]
```
`text_input` = einzeiliges Eingabefeld.
`text_area` = mehrzeiliges Eingabefeld.
`value=` setzt den Standardwert der angezeigt wird wenn das Feld leer ist.
`.split("\n")` teilt den mehrzeiligen Text bei Zeilenumbrüchen in eine Liste.
`u.strip()` entfernt Leerzeichen am Rand jedes Eintrags.
`if u.strip()` filtert leere Zeilen heraus.

---

## Schritt 1 – Hilfsfunktion zum Zeichnen vorbereiten

Füge diese Funktion **vor** den Tab-Definitionen in `app.py` ein,
direkt nach den Import-Zeilen:

```python
def draw_ishikawa(ax, problem, kategorien_oben, kategorien_unten):
    """
    Zeichnet ein Ishikawa-Diagramm auf eine matplotlib Axes.

    problem           : String – das Problem rechts am Pfeil
    kategorien_oben   : Liste von 3 Dicts {'name': str, 'ursachen': [str, ...]}
    kategorien_unten  : Liste von 3 Dicts {'name': str, 'ursachen': [str, ...]}
    """
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    # ── Rückgrat (Hauptpfeil) ────────────────────────────────────────────────
    ax.annotate('', xy=(9.3, 3.5), xytext=(0.5, 3.5),
                arrowprops=dict(arrowstyle='->', color='#1A1A1A', lw=2.5))

    # ── Problembox (Fischkopf) ───────────────────────────────────────────────
    ax.text(9.4, 3.5, problem,
            ha='left', va='center', fontsize=9, fontweight='bold', color='white',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#C0392B', alpha=0.9))

    # ── Ankerpunkte auf dem Rückgrat ────────────────────────────────────────
    ankerpunkte = [2.5, 5.0, 7.5]

    # ── Obere Äste (Kategorien oben) ────────────────────────────────────────
    for anker_x, kat in zip(ankerpunkte, kategorien_oben):
        spitze_x = anker_x - 1.2
        spitze_y = 6.0

        # Hauptast
        ax.plot([spitze_x, anker_x], [spitze_y, 3.5],
                color='#2E5FA3', linewidth=2)

        # Kategoriename
        ax.text(spitze_x, spitze_y + 0.3, kat['name'],
                ha='center', va='bottom', fontsize=9,
                fontweight='bold', color='#2E5FA3')

        # Einzelursachen als kleine Zweige
        ursachen = kat.get('ursachen', [])[:4]
        for k, ursache in enumerate(ursachen):
            # Position entlang des Hauptastes (gleichmäßig verteilt)
            t = (k + 1) / (len(ursachen) + 1)
            zx = spitze_x + t * (anker_x - spitze_x)
            zy = spitze_y + t * (3.5 - spitze_y)
            # kleiner horizontaler Zweig
            ax.plot([zx - 0.8, zx], [zy + 0.5, zy],
                    color='#888888', linewidth=1.2)
            ax.text(zx - 0.85, zy + 0.55, ursache,
                    ha='right', va='bottom', fontsize=7.5, color='#333333')

    # ── Untere Äste (Kategorien unten) ──────────────────────────────────────
    for anker_x, kat in zip(ankerpunkte, kategorien_unten):
        spitze_x = anker_x - 1.2
        spitze_y = 1.0

        # Hauptast
        ax.plot([spitze_x, anker_x], [spitze_y, 3.5],
                color='#2E5FA3', linewidth=2)

        # Kategoriename
        ax.text(spitze_x, spitze_y - 0.3, kat['name'],
                ha='center', va='top', fontsize=9,
                fontweight='bold', color='#2E5FA3')

        # Einzelursachen
        ursachen = kat.get('ursachen', [])[:4]
        for k, ursache in enumerate(ursachen):
            t = (k + 1) / (len(ursachen) + 1)
            zx = spitze_x + t * (anker_x - spitze_x)
            zy = spitze_y + t * (3.5 - spitze_y)
            ax.plot([zx - 0.8, zx], [zy - 0.5, zy],
                    color='#888888', linewidth=1.2)
            ax.text(zx - 0.85, zy - 0.55, ursache,
                    ha='right', va='top', fontsize=7.5, color='#333333')
```

---

## Schritt 2 – Tab 3 in app.py ergänzen

Ändere die Tab-Zeile oben in `app.py`:
```python
# ALT:
tab1, tab2 = st.tabs(["Pareto-Analyse", "SPC-Karte"])

# NEU:
tab1, tab2, tab3 = st.tabs(["Pareto-Analyse", "SPC-Karte", "Ishikawa-Diagramm"])
```

Füge dann am Ende der Datei den dritten Tab-Block hinzu:

```python
# === TAB 3: ISHIKAWA ===
with tab3:
    st.subheader("Ishikawa-Diagramm (Ursache-Wirkungs-Analyse)")

    # ── Problemdefinition ────────────────────────────────────────────────────
    problem = st.text_input("Problem / Wirkung (erscheint rechts am Pfeil)",
                             value="Hohe Ausschussrate")

    st.markdown("**Ursachen eingeben** – eine Ursache pro Zeile, max. 4 pro Kategorie:")

    # ── Eingabefelder für 6 Kategorien (2 Spalten à 3) ──────────────────────
    col_links, col_rechts = st.columns(2)

    with col_links:
        mensch_input    = st.text_area("👤 Mensch",    value="Fehlende Schulung\nMüdigkeit", height=100)
        maschine_input  = st.text_area("⚙️ Maschine",  value="Verschleiß\nFalsche Kalibrierung", height=100)
        material_input  = st.text_area("📦 Material",  value="Schlechte Rohstoffqualität\nFalsche Charge", height=100)

    with col_rechts:
        methode_input   = st.text_area("📋 Methode",   value="Unklare Anweisungen\nFehlende Standards", height=100)
        messung_input   = st.text_area("📏 Messung",   value="Nicht kalibrierte Geräte", height=100)
        mitwelt_input   = st.text_area("🌡️ Mitwelt",   value="Temperaturschwankungen\nVibration", height=100)

    # ── Texteingaben in Listen umwandeln ────────────────────────────────────
    def parse(text):
        return [u.strip() for u in text.split("\n") if u.strip()]

    # ── Diagramm zeichnen ───────────────────────────────────────────────────
    kategorien_oben = [
        {'name': 'Mensch',   'ursachen': parse(mensch_input)},
        {'name': 'Maschine', 'ursachen': parse(maschine_input)},
        {'name': 'Material', 'ursachen': parse(material_input)},
    ]
    kategorien_unten = [
        {'name': 'Methode',  'ursachen': parse(methode_input)},
        {'name': 'Messung',  'ursachen': parse(messung_input)},
        {'name': 'Mitwelt',  'ursachen': parse(mitwelt_input)},
    ]

    fig3, ax3 = plt.subplots(figsize=(14, 7))
    draw_ishikawa(ax3, problem, kategorien_oben, kategorien_unten)
    plt.tight_layout()
    st.pyplot(fig3)
```

---

## Schritt 3 – App neu starten und testen

```bash
dashboard
```

Du siehst jetzt drei Tabs. Im Ishikawa-Tab kannst du:
- Das Problem oben in das Textfeld eintippen
- Ursachen je Kategorie eingeben (eine pro Zeile)
- Das Diagramm aktualisiert sich automatisch beim Tippen

---

## Was passiert bei jedem Tastendruck?

Streamlit führt bei jeder Nutzerinteraktion das gesamte `app.py` von oben nach
unten neu aus. Das ist das Kernprinzip von Streamlit: kein manuelles
"Aktualisieren" – die App reagiert reaktiv auf jede Eingabe.

---

## Checkpoint nach diesem Tab

```
~/quality-dashboard/
├── app.py              # Tab 1: Pareto, Tab 2: SPC, Tab 3: Ishikawa
├── sample_data.csv
└── spc_data.csv
```

**Mögliche nächste Schritte:**
- GitHub Repository einrichten und den Code hochladen (für den Lebenslauf)
- Supplier Scorecard (Projekt 2) starten
- Diagramme exportierbar machen (Download-Button in Streamlit)
