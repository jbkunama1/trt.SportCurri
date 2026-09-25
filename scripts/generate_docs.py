#!/usr/bin/env python3
"""Erzeugt die Materialien (Präsentation + Jahrestabellen) als PDF in static/docs/.
Benötigt: pip install reportlab
Aufruf:   python scripts/generate_docs.py
"""
import os
from functools import partial
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "docs")
os.makedirs(DOCS, exist_ok=True)
styles = getSampleStyleSheet()

title_style = ParagraphStyle("T", parent=styles["Heading1"], fontSize=26, textColor=colors.HexColor("#ffffff"), spaceAfter=10, alignment=TA_CENTER, fontName="Helvetica-Bold")
subtitle_style = ParagraphStyle("S", parent=styles["Heading2"], fontSize=16, textColor=colors.HexColor("#e8f0ff"), spaceAfter=14, alignment=TA_CENTER, fontName="Helvetica")
bullet_style = ParagraphStyle("Bl", parent=styles["Normal"], fontSize=11.5, textColor=colors.HexColor("#ffffff"), spaceAfter=4, leading=15, leftIndent=12, fontName="Helvetica")
footer_style = ParagraphStyle("F", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#aaaaaa"), alignment=TA_CENTER, fontName="Helvetica")

def colored_page(canvas, doc, color):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor(color))
    canvas.rect(0, 0, landscape(A4)[0], landscape(A4)[1], fill=1, stroke=0)
    canvas.restoreState()

SLIDES = [
    {"bg": "#1a1a2e", "title": "🎯 Schulcurriculum Sport", "sub": "Realschule BW | Bildungsplan 2016 | Sekundarstufe I",
     "p": [("📘", "Aktualisiert nach offiziellen Beispielcurricula des Landesinstituts für Schulentwicklung"),
           ("🕒", "Struktur: 75 % Kerncurriculum + 25 % Schulcurriculum (Freiräume)"),
           ("🎓", "Fachkonferenz Sport – Entwurf zur Abstimmung")]},
    {"bg": "#16213e", "title": "🤔 Warum ein Schulcurriculum?", "sub": "Rahmenbedingungen & Zielsetzung",
     "p": [("📚", "<b>Stundentafel:</b> Kl. 5/6: 3 Wochenstunden | Kl. 7–10: 2 Wochenstunden"),
           ("🗓️", "<b>Bausteinprinzip:</b> Kl. 5/6 verpflichtend | Kl. 7–9 Unterrichtsvorhaben | Kl. 10 Themenverteilungsplan (mind. 3 UV à max. 20 Std.)"),
           ("🎯", "<b>Ziel:</b> Verbindliche Jahresplanung, Progression, faire Bewertung"),
           ("💡", "<b>Struktur:</b> 75 % Kerncurriculum (verpflichtend) + 25 % Schulcurriculum (frei gestaltbar)"),
           ("✅", "<b>Vorteil:</b> Keine Doppelungen, klare Progression, Übergabe ans Folgejahr")]},
    {"bg": "#0f3460", "title": "💪 Kompetenzmodell – 4 Bereiche", "sub": "Prozessbezogene Kompetenzen",
     "p": [("🏃‍♂️", "<b>Bewegungskompetenz:</b> konditionell, koordinativ, Fertigkeiten sichern, hohes Bewegungsniveau"),
           ("🧠", "<b>Reflexions- & Urteilskompetenz:</b> Sinnrichtungen des Sports erkennen, situations- und zielangemessen handeln"),
           ("👤", "<b>Personalkompetenz:</b> Selbstbild entwickeln, Ziele formulieren, Emotionen regulieren, Gesundheit fördern"),
           ("🤝", "<b>Sozialkompetenz:</b> unterstützen, wertschätzen, fair handeln, verbindliches Regelhandeln")]},
    {"bg": "#533483", "title": "⚖️ Regeln der Jahresplanung (offiziell)", "sub": "Verbindliche Vorgaben nach BP 2016",
     "p": [("1️⃣", "<b>Kl. 5/6:</b> Jeder Inhaltsbereich mind. 1× in der Klassenstufe enthalten (nicht jährlich!)"),
           ("2️⃣", "<b>Kl. 7–9:</b> UV auf Basis mind. eines Inhaltsbereichs – Doppelungen pro Stufe vermeiden"),
           ("3️⃣", "<b>Kl. 9–10:</b> Pflicht: 'Miteinander/gegeneinander kämpfen' ODER 'Fahren, Rollen, Gleiten' mind. 1×"),
           ("4️⃣", "<b>Kl. 10:</b> Mind. 3 UV, jedes UV max. 20 Std., je 2 sportpädagogische Perspektiven"),
           ("5️⃣", "<b>Schulcurriculum:</b> ca. 25 % Freiräume – schulspezifisch (Turniere, Schwimmen, Trendsport)")]},
    {"bg": "#e94560", "title": "📅 Klasse 5 (105 Std. = 78 KC + 27 SC)", "sub": "Nach offiziellem Beispielcurriculum",
     "p": [("🎮", "<b>Spielen – 18 Std.:</b> Spielfähigkeit entwickeln (Ballspiele, Grundtechniken, Fairplay)"),
           ("🏃", "<b>Laufen, Springen, Werfen – 12 Std.:</b> Kondition & Spiel grundlegend entwickeln"),
           ("🤸", "<b>Bewegen an Geräten – 15 Std.:</b> Bewegungssicherheit & Vielfalt erwerben"),
           ("💃", "<b>Tanzen, Gestalten, Darstellen – 12 Std.:</b> Rhythmisch bewegen (nur Kl. 5 oder 6!)"),
           ("💪", "<b>Fitness entwickeln – 12 Std.:</b> Grundlagen der Trainingsprinzipien"),
           ("🥋", "<b>Kämpfen (WP) – 9 Std.:</b> Ringen & Raufen vorwiegend am Boden"),
           ("🌟", "<b>Schulcurriculum – 27 Std.:</b> Schulturniere, Trendsport, Ergänzungen")]},
    {"bg": "#1a1a2e", "title": "📅 Klasse 6 (105 Std. = 92 KC + 13 SC)", "sub": "Nach offiziellem Beispielcurriculum",
     "p": [("🎮", "<b>Spielen – 24 Std.:</b> Spielfähigkeit vertiefen (Technik + Regeln + Fairplay)"),
           ("🏃", "<b>Laufen, Springen, Werfen – 18 Std.:</b> Anlauftechniken (Gerade, Kurve), Sprung, Wurf"),
           ("🤸", "<b>Bewegen an Geräten – 18 Std.:</b> Sicherheit & Vielfalt vertiefen"),
           ("🏊", "<b>Bewegen im Wasser – 16 Std.:</b> Grundlagen, Schwimmtechniken (nur Kl. 5 oder 6!)"),
           ("💪", "<b>Fitness entwickeln – 8 Std.:</b> Ebenen der Belastungssteuerung"),
           ("🥋", "<b>Kämpfen (WP) – 8 Std.:</b> Ringen & Raufen vorwiegend im Stand"),
           ("🌟", "<b>Schulcurriculum – 13 Std.:</b> schulspezifische Akzente")]},
    {"bg": "#16213e", "title": "📅 Klassen 7/8 (70 Std. = 54 KC + 16 SC)", "sub": "Unterrichtsvorhaben-basiert",
     "p": [("🏐", "<b>UV 1: Sportspiel vertieft – 18 Std.:</b> z. B. Badminton/Volleyball (kontinuitätsorientiert)"),
           ("💪", "<b>UV 2: Fitness entwickeln – 18 Std.:</b> Ausdauer, Kraft, Herzfrequenz, Trainingsprinzipien"),
           ("🕺", "<b>UV 3: Tanzen, Gestalten, Darstellen – 18 Std.:</b> Style, Rhythm & Move, Choreografie"),
           ("🌟", "<b>Schulcurriculum – 16 Std.:</b> Projekttag, Klettern, JtfO, schuleigene Turniere"),
           ("⚠️", "<b>Regel:</b> Derselbe Inhaltsbereich nicht zweimal pro Klassenstufe; SC darf max. 2 IB des KC nutzen")]},
    {"bg": "#0f3460", "title": "📅 Klasse 9 (70 Std. = 54 KC + 16 SC)", "sub": "Progressionsstufe 'Verändern & Optimieren'",
     "p": [("🏀", "<b>UV 1: Komplexes Sportspiel – 18 Std.:</b> Taktik, Positionsspiel, Schiedsrichterrolle"),
           ("🚴", "<b>UV 2: Fahren, Rollen, Gleiten (WP) – 16 Std.:</b> Fahrrad/Inlines, Tourenregeln, Umweltverträglichkeit"),
           ("🕹️", "<b>UV 3: Spielen alternativ – 12 Std.:</b> Fan-/Trendspiele mit Einsatzbezug"),
           ("🤸", "<b>UV 4: Gestalten/Fitness – 8 Std.:</b> Bewegungen neu zusammensetzen, ästhetische Bezüge"),
           ("🌟", "<b>Schulcurriculum – 16 Std.:</b> Kooperation Vereine, Schnupperangebote")]},
    {"bg": "#533483", "title": "📅 Klasse 10 (70 Std. = 54 KC + 16 SC)", "sub": "Nach offiziellem Beispielcurriculum (Themenverteilungsplan)",
     "p": [("🏸", "<b>UV 1: Badminton – 18 Std.:</b> Rückschlagspiel, Wettkampf, Turnierorganisation"),
           ("🧭", "<b>UV 2: Orientierungslauf – 18 Std.:</b> Karte, Kompass, Gelände, GPS-Sportarten"),
           ("🏋️", "<b>UV 3: Fitness – 18 Std.:</b> individuelles Fitnessprogramm + Punch & Kick"),
           ("🌟", "<b>Schulcurriculum – 16 Std.:</b> Abwechslung Angebote, Muckibude-Training, neue Angebote testen"),
           ("📏", "<b>Regel:</b> Je UV max. 20 Std. + 2 sportpädagogische Perspektiven (Erlebnis, Leistung, Gesundheit, Ausdruck, Risiko, Ästhetik, Kooperation)")]},
    {"bg": "#e94560", "title": "📊 Bewertung & Leistungsfeststellung", "sub": "Prozess- und produktorientiert",
     "p": [("✅", "<b>Dokumentieren:</b> Beobachtungsbögen (Technik, Taktik, Sozialverhalten)"),
           ("⏱️", "<b>Messen:</b> Fitness-Tests, Zeiten, Weiten, HF-Messung"),
           ("🎭", "<b>Präsentieren:</b> Choreografien, Turnierleitung, Schiedsrichterleistung"),
           ("🪑", "<b>Selbsteinschätzen:</b> Trainingsprotokolle, Reflexionshefte, Lernstandsaufnahme"),
           ("🎓", "<b>Leitperspektiven:</b> BNE & Gesundheit, Medienbildung (Videoanalyse), BO (Trainer-C/Übungsleiter)")]},
    {"bg": "#1a1a2e", "title": "🏫 Organisation & Teamarbeit", "sub": "Ein neuer Modus der Zusammenarbeit",
     "p": [("👥", "<b>UV-Teams:</b> Jedes UV wird von mind. 2 Kolleg:innen gemeinsam vorbereitet"),
           ("🔄", "<b>Bausteinlogik:</b> Wahlpflichtangebote flexibel nach Sporträumen & Expertise"),
           ("👫", "<b>Doppelstunden:</b> Anmelden! Warum? Koedukativ/kooperativ, Klassenwechsel, Stationsmodelle"),
           ("⚠️", "<b>Sicherheit:</b> Gerätecheck, Aufsicht, Erste Hilfe, Schwimmen mit Rettungsschwimmer:in"),
           ("📈", "<b>Differenzierung:</b> Niveaustufen G/M/E, Wahlaufgaben, Kooperation")]},
    {"bg": "#16213e", "title": "✅ Beschlussvorschlag & Nächste Schritte", "sub": "Von der Planung zur Umsetzung",
     "p": [("1️⃣", "<b>Beschließen:</b> Jahresplanung als Fachcurriculum Sport (Kl. 5–10)"),
           ("2️⃣", "<b>Zuordnen:</b> Räume, Geräte, Außenstellen (OL-Gelände) + Kollegiums-Expertise"),
           ("3️⃣", "<b>Terminieren:</b> Themenverteilungsplan ins Schuljahr eintragen (Belegungspläne!)"),
           ("4️⃣", "<b>Dokumentieren:</b> Jahrestabellen ausfüllen → Übergabe ans Folgejahr"),
           ("5️⃣", "<b>Auswerten:</b> Ende SJ: Was passt? Wechsel der Inhaltsbereiche im SC möglich"),
           ("🎉", "<b>Viel Erfolg!</b> – Quellen: schule-bw.de / lehrerfortbildung-bw.de")]},
]

def build_presentation(path):
    doc = SimpleDocTemplate(path, pagesize=landscape(A4), rightMargin=1.6*cm, leftMargin=1.6*cm, topMargin=1.6*cm, bottomMargin=1.6*cm)
    story = []
    for i, s in enumerate(SLIDES):
        story += [Paragraph(s["title"], title_style), Paragraph(s["sub"], subtitle_style), Spacer(1, 0.4*cm)]
        story += [Paragraph(f"{e}  {t}", bullet_style) for e, t in s["p"]]
        story += [Spacer(1, 0.6*cm), Paragraph(f"Folie {i+1}/{len(SLIDES)} • Schulcurriculum Sport Realschule BW (BP 2016) • Quellen: Landesinstitut für Schulentwicklung, schule-bw.de", footer_style)]
        if i < len(SLIDES) - 1:
            story.append(PageBreak())
    doc.build(story, onFirstPage=partial(colored_page, color=SLIDES[0]["bg"]),
              onLaterPages=lambda c, d: colored_page(c, d, SLIDES[(doc.page - 1) % len(SLIDES)]["bg"]))

t_title = ParagraphStyle("TT", parent=title_style, textColor=colors.HexColor("#1a1a2e"), fontSize=22)
t_sub = ParagraphStyle("TS", parent=subtitle_style, textColor=colors.HexColor("#0f3460"), fontSize=13)
t_h = ParagraphStyle("TH", parent=styles["Heading2"], textColor=colors.HexColor("#1a1a2e"), fontSize=14, spaceAfter=6)
t_b = ParagraphStyle("TB", parent=styles["Normal"], textColor=colors.HexColor("#333333"), fontSize=10, spaceAfter=4)

def header_note(t, sub):
    return [Paragraph(t, t_title), Paragraph(sub, t_sub), Spacer(1, 0.3*cm),
            Paragraph("<b>Legende:</b> □ = nicht gemacht | ✓ = erledigt | △ = teilweise | — = entfällt | <b>Quelle:</b> Beispielcurricula des Landesinstituts für Schulentwicklung (schule-bw.de)", t_b), Spacer(1, 0.3*cm)]

def big_table(rows):
    t = Table(rows, colWidths=[1.4*cm, 10*cm, 2.2*cm, 1.6*cm, 4.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8), ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6fb")]),
    ]))
    return t

def ref_table(label):
    t = Table([[f"<b>{q}</b>", ""] for q in ["Was lief gut?", "Was war zu schwer / zu leicht?", "Welche UV ändern wir nächstes Jahr?", "Tipps für die Kollegin / den Kollegen:"]],
              colWidths=[6*cm, 13.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef1f7")),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 28), ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return [Paragraph(f"<b>📝 Jahresreflexion – {label}</b>", t_h), Spacer(1, 0.2*cm), t]

KLASSEN = [
    ("📋 Jahrestabelle Sport – Klasse 5", "Schuljahr: _______________ | 3 Wochenstd. = 105 Std. (78 KC + 27 SC) | Realschule BW", [
        ["UV 1", "🎮 <b>Spielen</b> – Spielfähigkeit entwickeln (technische Möglichkeiten, Bewegungstricks, selbst Regeln festlegen/überwachen)", "18", "□", ""],
        ["UV 2", "🏃 <b>Laufen, Springen, Werfen</b> – Kondition & Spiel grundlegend entwickeln (Schnelligkeit, Beweglichkeit)", "12", "□", ""],
        ["UV 3", "🤸 <b>Bewegen an Geräten</b> – Bewegungssicherheit & -vielfalt erwerben", "15", "□", ""],
        ["UV 4", "💃 <b>Tanzen, Gestalten, Darstellen</b> – rhythmisch bewegen (einfache Schrittfolgen/Choreografien)", "12", "□", ""],
        ["UV 5", "💪 <b>Fitness entwickeln</b> – Grundlagen der Trainingsprinzipien", "12", "□", ""],
        ["WP 1", "🥋 <b>Kämpfen (WP)</b> – Ringen & Raufen vorwiegend am Boden", "9", "□", ""],
        ["SC", "🌟 <b>Schulcurriculum</b> – Schulturniere, Trendsport, Ergänzungen (z. B. Fahren, Rollen, Gleiten)", "27", "□", ""]]),
    ("📋 Jahrestabelle Sport – Klasse 6", "Schuljahr: _______________ | 3 Wochenstd. = 105 Std. (92 KC + 13 SC) | Realschule BW", [
        ["UV 1", "🎮 <b>Spielen</b> – Spielfähigkeit vertiefen (Technik sichern, Regeln anwenden, verbindlich handeln)", "24", "□", ""],
        ["UV 2", "🏃 <b>Laufen, Springen, Werfen</b> – Anlauftechniken (Gerade/Kurve), kinesthetische Differenzierung", "18", "□", ""],
        ["UV 3", "🤸 <b>Bewegen an Geräten</b> – Bewegungssicherheit & -vielfalt vertiefen", "18", "□", ""],
        ["UV 4", "🏊 <b>Bewegen im Wasser</b> – Grundlagen & Schwimmtechniken (nur in Kl. 5 ODER 6)", "16", "□", ""],
        ["UV 5", "💪 <b>Fitness entwickeln</b> – Ebenen der Belastungssteuerung", "8", "□", ""],
        ["WP 1", "🥋 <b>Kämpfen (WP)</b> – Ringen & Raufen vorwiegend im Stand", "8", "□", ""],
        ["SC", "🌟 <b>Schulcurriculum</b> – schulspezifische Akzente", "13", "□", ""]]),
    ("📋 Jahrestabelle Sport – Klasse 7/8", "Schuljahr: _______________ | 2 Wochenstd. = 70 Std. (54 KC + 16 SC) | Realschule BW", [
        ["UV 1", "🏐 <b>Spielen vertieft</b> – z. B. Badminton/Volleyball/Fußball (kontinuitätsorientiert)", "18", "□", ""],
        ["UV 2", "💪 <b>Fitness entwickeln</b> – Ausdauer, Kraft, Herzfrequenz, Trainingsprinzipien, Selbstlernen", "18", "□", ""],
        ["UV 3", "🕺 <b>Tanzen, Gestalten, Darstellen</b> – Style, Rhythm & Move (Choreografie, Videoanalyse, Präsentation)", "18", "□", ""],
        ["SC", "🌟 <b>Schulcurriculum</b> – Projekttag, Klettern, JtfO, Turniere (max. 2 IB des KC)", "16", "□", ""],
        ["⚠️", "<b>Regel:</b> IB 'Kämpfen' ODER 'Fahren/Rollen/Gleiten' muss mind. 1× in Kl. 9–10 kommen", "—", "□", ""]]),
    ("📋 Jahrestabelle Sport – Klasse 9", "Schuljahr: _______________ | 2 Wochenstd. = 70 Std. (54 KC + 16 SC) | Realschule BW", [
        ["UV 1", "🏀 <b>Komplexes Sportspiel</b> – Taktik, Positionsspiel, Spiel-/Wettkampfsysteme", "18", "□", ""],
        ["UV 2", "🚴 <b>Fahren, Rollen, Gleiten (WP)</b> – Fahrrad/Inlines, Tourenregeln, Umweltverträglichkeit, GPS", "16", "□", ""],
        ["UV 3", "🕹️ <b>Spielen alternativ</b> – Fan-/Trendspiele mit Einsatzbezug (Schulhofsport beleben)", "12", "□", ""],
        ["UV 4", "🤸 <b>Gestalten/Fitness</b> – Bewegungen neu zusammensetzen, ästhetische Bezüge", "8", "□", ""],
        ["SC", "🌟 <b>Schulcurriculum</b> – Kooperation Vereine, Schnupperangebote, Projekttag", "16", "□", ""]]),
    ("📋 Jahrestabelle Sport – Klasse 10", "Schuljahr: _______________ | 2 Wochenstd. = 70 Std. (54 KC + 16 SC) | Realschule BW", [
        ["UV 1", "🏸 <b>Badminton</b> – Rückschlagspiel, Wettkampf, Turnierorganisation", "18", "□", ""],
        ["UV 2", "🧭 <b>Orientierungslauf</b> – Karte, Kompass, Gelände, GPS-Sportarten, Erlebnispädagogik", "18", "□", ""],
        ["UV 3", "🏋️ <b>Fitness entwickeln</b> – individuelles Fitnessprogramm + Punch & Kick", "18", "□", ""],
        ["SC", "🌟 <b>Schulcurriculum</b> – Abwechslung Angebote, Muckibude-Training, neue Angebote testen", "16", "□", ""],
        ["📏", "<b>Regel:</b> Jedes UV: 2 sportpädagogische Perspektiven (Leistung, Gesundheit, Erlebnis, Risiko, Ausdruck, Kooperation, Ästhetik)", "—", "□", ""]]),
]

def build_checklisten(path):
    st = []
    hdr = ["<b>UV</b>", "<b>Inhaltsbereich / Unterrichtsvorhaben</b>", "<b>Std.</b>", "<b>Status</b>", "<b>Notizen</b>"]
    for i, (t, sub, rows) in enumerate(KLASSEN):
        st += header_note(t, sub)
        st.append(big_table([hdr] + rows))
        st += [Spacer(1, 0.4*cm)] + ref_table(t.split("–")[-1].strip())
        if i < len(KLASSEN) - 1:
            st.append(PageBreak())
    SimpleDocTemplate(path, pagesize=landscape(A4), rightMargin=1.2*cm, leftMargin=1.2*cm,
                      topMargin=1.2*cm, bottomMargin=1.2*cm).build(st)

if __name__ == "__main__":
    p1 = os.path.join(DOCS, "Praesentation_Schulcurriculum_Sport_v3.pdf")
    p2 = os.path.join(DOCS, "Jahrestabellen_Checklisten_LEER_v2.pdf")
    build_presentation(p1)
    build_checklisten(p2)
    print(f"✅ {p1}")
    print(f"✅ {p2}")
