import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import openpyxl

def draw_ishikawa(ax, problem,kategorien_oben, kategorien_unten):
    ax.set_xlim(0,10)
    ax.set_ylim(0,7)
    ax.axis('off')

    #Hauptpfeil (Rückgrat)
    ax.annotate('',xy=(0.3,3.5), xytext=(0.5,3.5),
                arrowprops=dict(arrowstyle='->', color='#1A1A1A', lw=2.5))
    
    #Problembox (Fischkopf)
    ax.text(0.4,3.5,problem,
            ha='left', va='center', fontsize=9, fontweight='bold', color='white',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#C0392B', alpha=0.9))

    #Ankerpunkte auf dem Rückgrat
    ankerpunkte=[2.5,5.0,7.5]

    #Obere Äste (Kategorien oben)
    for anker_x, kat in zip(ankerpunkte, kategorien_oben):
        spitze_x = anker_x - 1.2
        spitze_y = 6.0

        #Hauptast
        ax.plot([spitze_x, anker_x],[spitze_y,3.5],
                color='#2E5FA3', linewidth=2)
        
        #Kategorienname
        ax.text(spitze_x, spitze_y + 0.3, kat['name'],
                ha='center', va='bottom', fontsize=9,
                fontweight='bold', color='#2E5FA3')
        
        #Einzelursachen als kleine Zweige
        ursachen = kat.get('ursachen', [])[:4]
        for k, ursache in enumerate(ursachen):
            #Position entlang des Hauptastes (gleichmäßig verteilt)
            t = (k + 1) / (len(ursachen) +1)
            zx = spitze_x + t * (anker_x - spitze_x)
            zy = spitze_y + t *(3.5 - spitze_y)            
            # kleiner horizontaler Zweig
            ax.plot([zx - 0.8, zx], [zy + 0.5, zy],
                    color='#888888', linewidth=1.2)
            ax.text(zx - 0.85, zy + 0.55, ursache,
                    ha='right', va='bottom', fontsize=7.5, color='#333333')

    #Untere Äste (Kategorien unten)
    for anker_x, kat in zip(ankerpunkte, kategorien_unten):
        spitze_x = anker_x -1.2
        spitze_y = 1.0

        #Hauptast
        ax.plot([spitze_x, anker_x], [spitze_y, 3.5],
        color='#2E5FA3', linewidth=2)

        #Kategorienname
        ax.text(spitze_x, spitze_y - 0.3, kat['name'],
                ha='center', va='top', fontsize=9,
                fontweight='bold', color='#2E5FA3')
        
        #Einzelursachen
        ursachen = kat.get('ursachen', [])[:4]
        for k, ursache in enumerate(ursachen):
            t= (k+1) / (len(ursachen) + 1)
            zx = spitze_x + t * (anker_x - spitze_x)
            zy = spitze_y + t * (3.5 - spitze_y)
            ax.plot([zx - 0.8, zx],[zy - 0.5, zy],
                    color='#888888', linewidth=1.2)
            ax.text(zx-0.85, zy - 0.55, ursache,
                    ha='right', va='top', fontsize=7.5, color='#333333')

st.set_page_config(page_title="Quality Dashboard", layout="wide")  
st.title("Quality Dashboard")

# --- Tabs ---
tab1, tab2, tab3 , tab4 = st.tabs(["Pareto-Analyse", "SPC-Karte", "Ishikawa-Diagramm", "FMEA"])

# === TAB 1: PARETO ===
with tab1:
    st.subheader("Pareto-Analyse")

    uploaded_pareto = st.file_uploader("CSV hochladen (Spalten: Fehlerart, Anzahl)",
                                        type="csv", key="pareto")
    if uploaded_pareto:
        df = pd.read_csv(uploaded_pareto)
    else:
        st.info("Keine Datei hochgeladen - Beispieldaten werden verwendet")
        df = pd.read_csv("sample_data.csv")
    
    st.dataframe(df)

    df_sorted = df.sort_values("Anzahl", ascending=False).reset_index(drop=True)
    df_sorted["Kumuliert_%"] = (
        df_sorted["Anzahl"].cumsum() / df_sorted["Anzahl"].sum() *100
    )

    fig, ax1 = plt.subplots(figsize=(10,5))
    ax1.bar(df_sorted["Fehlerart"], df_sorted["Anzahl"], color="steelblue")
    ax1.set_xlabel("Fehlerart")
    ax1.set_ylabel("Anzahl", color="steelblue")
    ax1.tick_params(axis="x", rotation=30)

    ax2 = ax1.twinx()
    ax2.plot(df_sorted["Fehlerart"], df_sorted["Kumuliert_%"],
        color="red", marker="o", linewidth=2)
    ax2.axhline(80, color="gray", linestyle="--", linewidth=1)
    ax2.set_ylabel("Kumuliert %", color="red")
    ax2.set_ylim(0,110)

    plt.tight_layout()
    st.pyplot(fig)

    col1, col2, col3 = st.columns(3)
    col1.metric("Fehler gesamt", int(df_sorted["Anzahl"].sum()))
    col2.metric("Fehlerarten", len(df_sorted))
    col3.metric("Häufigster Fehler", df_sorted.iloc[0]["Fehlerart"])

# === TAB 2: SPC ===
with tab2:
    st.subheader("SPC-Karte (Einzelwert / X-Chart)")

    uploaded_spc = st.file_uploader("CSV hochladen (Spalten: Messung, Wert)",
                                    type="csv", key="spc")
    if uploaded_spc:
        df_spc = pd.read_csv(uploaded_spc)
    else:
        st.info("Keine Datei hochgeladen - Beispieldaten werden verwendet.")
        df_spc = pd.read_csv("spc_data.csv")
    
# --- Kennzahlen berechnen ---
    mean = np.mean(df_spc["Wert"])
    std  = np.std(df_spc["Wert"], ddof=1) # ddof=1 = Stichproben-Std.abw.
    ucl  = mean + 3 * std
    lcl  = mean - 3 * std

# --- Ausreißer markieren ---
    df_spc["Ausreißer"] = (df_spc["Wert"] > ucl) | (df_spc["Wert"] < lcl)

# --- Diagramm ---
    fig2, ax = plt.subplots(figsize=(12,5))

    ax.plot(df_spc["Messung"], df_spc["Wert"],
        color="steelblue", marker="o", linewidth=1.5, label="Messwert")

# --- Ausreißer rot hervorheben ---
    outliers = df_spc[df_spc["Ausreißer"]]
    ax.scatter(outliers["Messung"], outliers["Wert"],
            color="red", zorder=5, s=80, label="Ausreißer (außerhalb 3σ)")

# --- Kontrollgrenzen ---
    ax.axhline(mean, color="green", linewidth=1.5, linestyle="-", label=f"CL (σ {mean:.2f})")
    ax.axhline(ucl, color="orange", linewidth=1.5, linestyle="--", label=f"UCL ({ucl:.2f})")
    ax.axhline(lcl, color="orange", linewidth=1.5, linestyle="--", label=f"LCL ({lcl:.2f})")

    ax.fill_between(df_spc["Messung"], lcl, ucl, alpha=0.05, color="green")
    ax.set_xlabel("Messung Nr.")
    ax.set_ylabel("Messwert")
    ax.legend(loc="upper right")
    plt.tight_layout()
    st.pyplot(fig2)

# --- KPI-Zeile ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mittelwert (CL)", f"{mean:.3f}")
    col2.metric("UCL", f"{ucl:.3f}")
    col3.metric("LCL", f"{lcl:.3f}")
    col4.metric("Ausreißer", int(df_spc["Ausreißer"].sum()))

# --- Warnung, wenn Ausreißer vorhanden ---
    if df_spc["Ausreißer"].any():
        st.warning(f"⚠️ {int(df_spc['Ausreißer'].sum())} Messung(en) außerhalb der Kontrollgrenzen - Prozess prüfen")
    else:
        st.success("✅ Alle Messungen innerhalb der Kontrollgrenzen, Prozess stabil.")

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

    buf = io.BytesIO()
    fig3.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    st.download_button(
        label="Diagramm als PNG speichern",
        data=buf,
        file_name=f"Ishikawa_{problem}.png",
        mime="image/png")

# === TAB 4: FMEA ===

with tab4:
    st.subheader("FMEA – Fehlermöglichkeits- und Einflussanalyse")

    # ── Standardtabelle als Startpunkt ────────────────────────────────────────

    default_data = pd.DataFrame({
        "Fehlerart":     ["Maßabweichung", "Oberflächenfehler", "Falsche Beschriftung"],
        "Mögliche Ursache": ["Werkzeugverschleiß", "Verunreinigung", "Druckerfehler"],
        "Auswirkung":    ["Ausschuss", "Optischer Mangel", "Falsche Verwendung"],
        "S (Schwere)":   [8, 5, 7],
        "O (Auftreten)": [4, 6, 3],
        "D (Entdeckung)":[3, 4, 5],
    })

    st.markdown("**Tabelle direkt bearbeiten** – Werte in die Zellen tippen, RPN wird automatisch berechnet:")

    # ── Editierbare Tabelle ───────────────────────────────────────────────────
    edited_df = st.data_editor(
        default_data,
        num_rows="dynamic",       # Zeilen hinzufügen / löschen möglich
        width='stretch',
        column_config={
            "S (Schwere)":    st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
            "O (Auftreten)":  st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
            "D (Entdeckung)": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
        }
    )

    # ── RPN berechnen ─────────────────────────────────────────────────────────
    edited_df["RPN"] = (
        edited_df["S (Schwere)"] *
        edited_df["O (Auftreten)"] *
        edited_df["D (Entdeckung)"]
    )

    # ── Nach RPN absteigend sortieren ─────────────────────────────────────────
    result_df = edited_df.dropna(subset=["RPN"]).sort_values("RPN", ascending=False).reset_index(drop=True)
    
    # ── Farbkodierung ─────────────────────────────────────────────────────────
    def farbe_rpn(val):
        if val >= 200:
            return "background-color: #FFCCCC"   # rot – kritisch
        elif val >= 100:
            return "background-color: #FFF3CC"   # gelb – erhöht
        else:
            return "background-color: #CCFFCC"   # grün – unkritisch

    styled = result_df.style.map(farbe_rpn, subset=["RPN"])

    st.subheader("Ergebnis – sortiert nach RPN")
    st.dataframe(styled, width='stretch')

    # ── KPI-Zeile ─────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    col1.metric("Höchster RPN",  int(result_df["RPN"].max()))
    col2.metric("Ø RPN",         round(result_df["RPN"].mean(), 1))
    col3.metric("Kritische Punkte (RPN ≥ 200)",
                int((result_df["RPN"] >= 200).sum()))

    # ── Warnung ───────────────────────────────────────────────────────────────
    if (result_df["RPN"] >= 200).any():
        st.error("🔴 Mindestens ein Risiko ist kritisch (RPN ≥ 200) – sofortige Maßnahme erforderlich.")
    elif (result_df["RPN"] >= 100).any():
        st.warning("🟡 Erhöhte Risiken vorhanden (RPN ≥ 100) – Maßnahmen prüfen.")
    else:
        st.success("🟢 Alle Risiken im unkritischen Bereich.")

    # ── Excel-Export ──────────────────────────────────────────────────────────
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        result_df.to_excel(writer, index=False, sheet_name="FMEA")
    buffer.seek(0)

    st.download_button(
        label="📥 FMEA als Excel exportieren",
        data=buffer,
        file_name="FMEA_Auswertung.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )