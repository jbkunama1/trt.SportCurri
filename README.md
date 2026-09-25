# 🏅 Sport-Manager (trt.SportCurri)

Webapp für das **Schulcurriculum Sport (Realschule BW, Bildungsplan 2016)** – Jahresplanung ausfüllen, dokumentieren, ans Folgejahr übergeben.

## ✨ Features

| Bereich | Funktion |
|---------|----------|
| 📋 Jahresplanung | Checklisten pro Klassenstufe (5, 6, 7/8, 9, 10) mit offiziellen Stundenzahlen aus den Beispielcurricula |
| ✅ Status | ⬜ offen / ✅ erledigt / 🔶 teilweise / ➖ entfällt – einfach antippen |
| 📝 Notizen | Pro UV, mit Autosave |
| 📊 Bewertungsbogen | Instrumente + Ergebnisse dokumentieren |
| 🪞 Jahresreflexion | 4 Fragen als Übergabe ans Folgejahr |
| 🗓️ Schuljahre | Anlegen, aktivieren, **kopieren** (Status wird übernommen!) |
| 📥 Dokumente | Download-Bereich: neue Dateien in `static/docs/` erscheinen automatisch |
| ⬇️ Export | CSV, JSON, Druck/PDF, komplettes DB-Backup (Admin) |
| 👥 Benutzer | Rollen Admin/Lehrkraft, Deaktivieren, Passwort-Reset |
| 🎨 Themes | 5 Designs (Sporty 🌊, Sunset 🌅, Wald 🌲, Neon 💜, Dark 🌙) – pro User gespeichert |
| 📱 Mobile-first | Touch-optimierte Karten, PWA-Manifest |
| 📜 Audit-Log | Admin sieht die letzten Änderungen |
| ❤️ Health | `/health` Endpoint für Monitoring (z. B. Uptime Kuma) |

## 🚀 Start lokal

```bash
pip install -r requirements.txt
python scripts/generate_docs.py   # erzeugt die PDF-Materialien in static/docs/
python app.py
# → http://localhost:8080
```

**Erstlogin:** `admin` / `sport2026` → danach unter ⚙️ ändern!

## 🐳 Docker / Portainer

```bash
docker compose up -d --build
```

Die Datenbank liegt im Volume `sport_data` als `sport_manager.db` – überlebt Neustarts & Updates.
**Wichtig:** `SECRET_KEY` in der Compose-Datei ändern!

## 🗂️ Struktur

```
app.py                    # Flask-App (Backend + Routen + API)
templates/                # base, login, dashboard, klasse, admin, settings, downloads
static/themes.css         # alle 5 Designs (CSS-Variablen)
static/docs.css           # Styling Download-Seite
static/app.js             # Theme-Switch
static/klasse.js          # Autosave-Logik
static/manifest.json      # PWA
static/docs/              # Dokumente (PDFs per scripts/generate_docs.py erzeugen)
scripts/generate_docs.py  # Erzeugt Präsentation + Jahrestabellen als PDF
Dockerfile, docker-compose.yml, requirements.txt
```

## 📚 Quellen der Curriculum-Daten

- bildungsplaene-bw.de (Bildungsplan 2016, Sek I, Fach Sport)
- schule-bw.de → Beispielcurricula Kl. 5/6 & Kl. 10 (Landesinstitut für Schulentwicklung)
- lehrerfortbildung-bw.de → Jahresplanung, Themenverteilungsplan

## ⚖️ Lizenz

Frei nutzbar für schulische Zwecke. Curriculum-Inhalte basieren auf dem öffentlichen Bildungsplan 2016 BW.
