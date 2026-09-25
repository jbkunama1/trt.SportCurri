# Sport-Manager v2 – mit integrierter Dokumenten-Bibliothek (Downloads)
# Flask + SQLite, mobile-first, Themes, Benutzerverwaltung, Admin, Export
import os, json, csv, io, sqlite3, functools, datetime
from flask import (Flask, render_template, request, redirect, url_for,
                   session, jsonify, send_file, send_from_directory, abort, flash)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get('DATA_DIR', os.path.join(BASE_DIR, 'data'))
DOCS_DIR = os.path.join(BASE_DIR, 'static', 'docs')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, 'sport_manager.db')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'CHANGE_ME_IN_PRODUCTION_please')

STAGES = [
    {'key': '5',   'label': 'Klasse 5',   'emoji': '🎒', 'hours': 105, 'kc': 78, 'sc': 27},
    {'key': '6',   'label': 'Klasse 6',   'emoji': '🧢', 'hours': 105, 'kc': 92, 'sc': 13},
    {'key': '78',  'label': 'Klasse 7/8', 'emoji': '🏐', 'hours': 70,  'kc': 54, 'sc': 16},
    {'key': '9',   'label': 'Klasse 9',   'emoji': '🚴', 'hours': 70,  'kc': 54, 'sc': 16},
    {'key': '10',  'label': 'Klasse 10',  'emoji': '🏸', 'hours': 70,  'kc': 54, 'sc': 16},
]

STATUS = ['offen', 'erledigt', 'teilweise', 'entfaellt']
STATUS_ICON = {'offen': '⬜', 'erledigt': '✅', 'teilweise': '🔶', 'entfaellt': '➖'}

DOC_META = {
    'Praesentation_Schulcurriculum_Sport_v3.pdf': ('🎨', 'Präsentation Fachkonferenz', '12 Folien, bunt, mit allen Regeln des BP 2016'),
    'Jahrestabellen_Checklisten_LEER_v2.pdf': ('📋', 'Jahrestabellen & Checklisten', 'Leere Vorlagen (Kl. 5–10) zum Ausdrucken & Ankreuzen'),
    'Schulcurriculum_Sport_Uebersicht.md': ('📝', 'Kurzübersicht (Markdown)', 'Zum Einpflegen in GitHub/Doku'),
}
DOC_FALLBACK = {'pdf': ('📄', 'PDF-Dokument'), 'md': ('📝', 'Markdown-Dokument')}

CURRICULUM = {
    '5': [
        ('UV 1', '🎮 Spielen', 'Spielfähigkeit entwickeln: Ballspiele, technische Möglichkeiten, Bewegungstricks, Regeln selbst festlegen & überwachen, Fairplay', 18),
        ('UV 2', '🏃 Laufen, Springen, Werfen', 'Kondition & Spiel grundlegend entwickeln: Sprint, Sprung, Wurf, Schnelligkeit & Beweglichkeit über Spiele', 12),
        ('UV 3', '🤸 Bewegen an Geräten', 'Bewegungssicherheit & -vielfalt erwerben (Boden, Kasten, Reck; Sicherungsaufgaben)', 15),
        ('UV 4', '💃 Tanzen, Gestalten, Darstellen', 'Rhythmisch bewegen: einfache Schrittfolgen & Choreografien je nach Musik (nur Kl. 5 oder 6!)', 12),
        ('UV 5', '💪 Fitness entwickeln', 'Grundlagen der Trainingsprinzipien, einfache Selbstversuche', 12),
        ('WP 1', '🥋 Kämpfen (WP)', 'Ringen & Raufen vorwiegend am Boden', 9),
        ('SC',   '🌟 Schulcurriculum', 'Schulturniere, Trendsport, Ergänzungen (z. B. Fahren, Rollen, Gleiten)', 27),
    ],
    '6': [
        ('UV 1', '🎮 Spielen', 'Spielfähigkeit vertiefen: Technik sichern, Regeln anwenden, verbindliches Regelhandeln', 24),
        ('UV 2', '🏃 Laufen, Springen, Werfen', 'Anlauftechniken (Gerade/Kurve), kinesthetische Differenzierung, besondere Start-/Sprungformen', 18),
        ('UV 3', '🤸 Bewegen an Geräten', 'Bewegungssicherheit & -vielfalt vertiefen', 18),
        ('UV 4', '🏊 Bewegen im Wasser', 'Grundlagen & Schwimmtechniken (nur in Kl. 5 ODER 6), Selbst- & Fremdrettung', 16),
        ('UV 5', '💪 Fitness entwickeln', 'Ebenen der Belastungssteuerung', 8),
        ('WP 1', '🥋 Kämpfen (WP)', 'Ringen & Raufen vorwiegend im Stand', 8),
        ('SC',   '🌟 Schulcurriculum', 'Schulspezifische Akzente', 13),
    ],
    '78': [
        ('UV 1', '🏐 Spielen vertieft', 'z. B. Badminton / Volleyball / Fußball – kontinuitätsorientiert, Spielfähigkeit & Anwendungsrezepte', 18),
        ('UV 2', '💪 Fitness entwickeln', 'Ausdauer & Kraft, Herzfrequenz messen, Trainingsprinzipien, Selbstlernen (z. B. Mobile-Coach)', 18),
        ('UV 3', '🕺 Tanzen, Gestalten, Darstellen', 'Style, Rhythm & Move: Schrittfolgen, Choreografie, Videoanalyse, Präsentation', 18),
        ('SC',   '🌟 Schulcurriculum', 'Projekttag, Klettern, JtfO, schuleigene Turniere (max. 2 Inhaltsbereiche des KC)', 16),
    ],
    '9': [
        ('UV 1', '🏀 Komplexes Sportspiel', 'Taktik, Positionsspiel, Spiel-/Wettkampfsysteme, Schiedsrichterrolle', 18),
        ('UV 2', '🚴 Fahren, Rollen, Gleiten (WP)', 'Fahrrad/Inlines: StVZO-Regeln, Touren, Umweltverträglichkeit, GPS-Sportarten', 16),
        ('UV 3', '🕹️ Spielen alternativ', 'Fan-/Trendspiele mit Einsatzbezug – den Schulhofsport beleben', 12),
        ('UV 4', '🤸 Gestalten / Fitness', 'Bewegungen neu zusammensetzen (gerätegebunden/gymnastisch), ästhetische Bezüge', 8),
        ('SC',   '🌟 Schulcurriculum', 'Kooperation Vereine, Schnupperangebote, Projekttag', 16),
    ],
    '10': [
        ('UV 1', '🏸 Badminton', 'Rückschlagspiel: Technik, Wettkampf, Turnierorganisation (Perspektiven: Leistung + Kooperation)', 18),
        ('UV 2', '🧭 Orientierungslauf', 'Karte, Kompass, Gelände, GPS-Sportarten, Natur & Erlebnispädagogik', 18),
        ('UV 3', '🏋️ Fitness entwickeln', 'Individuelles Fitnessprogramm + Punch & Kick (Perspektive: Gesundheit)', 18),
        ('SC',   '🌟 Schulcurriculum', 'Abwechslung Angebote, Muckibude-Training, neue Angebote testen, regelm. Fitness mit Trainingsplan', 16),
    ],
}

EVALUATIONS = {
    '5':  [('Technik', 'Beobachtungsbogen Fußball/Handball/Basketball'), ('Leichtathletik', 'Zeiten (Sprint) & Weiten (Wurf/Sprung)'),
           ('Turnen', 'Geräte-Checkliste (Boden, Kasten, Reck)'), ('Sozialverhalten', 'Fairplay-Bogen (Schiedsrichter, Helfer)'),
           ('Fitness', 'Basis-Tests (Liegestütz, Sprint)')],
    '6':  [('Spielen', 'Technik- & Regelverständnis-Check'), ('Schwimmen', 'Schwimmabzeichen-Stand, Technik'),
           ('Turnen', 'Sicherungsaufgaben & Gerätekür'), ('Sozialverhalten', 'Verbindliches Regelhandeln'),
           ('Fitness', 'Belastungssteuerung (Puls messen)')],
    '78': [('Sportspiel', 'Technik-Check (Aufschlag, Annahme, Clear)'), ('Fitness', 'HF-Messung, Zirkel-Protokoll'),
           ('Tanzen', 'Choreografie-Präsentation (Kreativität, Synchronität)'), ('Reflexion', 'Trainingsprotokoll & Selbstbewertung'),
           ('Sozialverhalten', 'Fairplay & Teambewertung')],
    '9':  [('Sportspiel', 'Taktikverständnis, Schiedsrichterleistung'), ('Fahren/Rollen/Gleiten', 'Tourenplanung, Regelwissen'),
           ('Gestalten', 'Kür nach ästhetischen Kriterien'), ('Fitness', 'Trainingsplan-Umsetzung'),
           ('Reflexion', 'Ernährungs-/Trainingsprotokoll')],
    '10': [('Badminton', 'Spielauswertung, Turnierleitung'), ('Orientierungslauf', 'Kartenarbeit, Laufzeit, Postenarbeit'),
           ('Fitness', 'Individuelles Programm + Umsetzung'), ('Sozialverhalten', 'Organisation, Teamfähigkeit'),
           ('Reflexion', 'Selbsteinschätzung, Zielüberprüfung')],
}

REFLECTION_QUESTIONS = [
    ('gut',     'Was lief gut?'),
    ('schwer',  'Was war zu schwer / zu leicht?'),
    ('aendern', 'Welche UV ändern wir nächstes Jahr?'),
    ('tipps',   'Tipps für die Kollegin / den Kollegen:'),
]

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA foreign_keys=ON')
    return db

def init_db():
    db = get_db()
    db.executescript('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'teacher',
        theme TEXT NOT NULL DEFAULT 'sporty',
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS school_years(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT UNIQUE NOT NULL,
        active INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS checklist(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_year_id INTEGER NOT NULL REFERENCES school_years(id),
        stage TEXT NOT NULL,
        item_code TEXT NOT NULL,
        item_title TEXT NOT NULL,
        item_desc TEXT NOT NULL,
        hours INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'offen',
        note TEXT NOT NULL DEFAULT '',
        updated_by TEXT,
        updated_at TEXT,
        UNIQUE(school_year_id, stage, item_code)
    );
    CREATE TABLE IF NOT EXISTS evaluations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_year_id INTEGER NOT NULL REFERENCES school_years(id),
        stage TEXT NOT NULL,
        area TEXT NOT NULL,
        instrument TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0,
        result TEXT NOT NULL DEFAULT '',
        UNIQUE(school_year_id, stage, area)
    );
    CREATE TABLE IF NOT EXISTS reflections(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_year_id INTEGER NOT NULL REFERENCES school_years(id),
        stage TEXT NOT NULL,
        qkey TEXT NOT NULL,
        answer TEXT NOT NULL DEFAULT '',
        UNIQUE(school_year_id, stage, qkey)
    );
    CREATE TABLE IF NOT EXISTS audit_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, action TEXT, detail TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    ''')
    db.commit()
    if not db.execute("SELECT 1 FROM users WHERE role='admin'").fetchone():
        db.execute('INSERT INTO users(username, display_name, password_hash, role) VALUES(?,?,?,?)',
                   ('admin', 'Administrator', generate_password_hash('sport2026'), 'admin'))
        db.commit()
    db.close()

def seed_year(db, year_id):
    for stg in STAGES:
        for code, title, desc, hours in CURRICULUM[stg['key']]:
            db.execute('INSERT OR IGNORE INTO checklist(school_year_id,stage,item_code,item_title,item_desc,hours) VALUES(?,?,?,?,?,?)',
                       (year_id, stg['key'], code, title, desc, hours))
        for area, instrument in EVALUATIONS[stg['key']]:
            db.execute('INSERT OR IGNORE INTO evaluations(school_year_id,stage,area,instrument) VALUES(?,?,?,?)',
                       (year_id, stg['key'], area, instrument))
        for qkey, _ in REFLECTION_QUESTIONS:
            db.execute('INSERT OR IGNORE INTO reflections(school_year_id,stage,qkey) VALUES(?,?,?)',
                       (year_id, stg['key'], qkey))
    db.commit()

def log(db, action, detail=''):
    db.execute('INSERT INTO audit_log(username,action,detail) VALUES(?,?,?)',
               (session.get('user', {}).get('username', 'system'), action, detail))
    db.commit()

def login_required(f):
    @functools.wraps(f)
    def wrapper(*a, **kw):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*a, **kw)
    return wrapper

def admin_required(f):
    @functools.wraps(f)
    def wrapper(*a, **kw):
        if session.get('user', {}).get('role') != 'admin':
            abort(403)
        return f(*a, **kw)
    return wrapper

def current_year(db):
    y = db.execute('SELECT * FROM school_years WHERE active=1 LIMIT 1').fetchone()
    if not y:
        y = db.execute('SELECT * FROM school_years ORDER BY id DESC LIMIT 1').fetchone()
    return y

def list_docs():
    out = []
    if os.path.isdir(DOCS_DIR):
        for fn in sorted(os.listdir(DOCS_DIR)):
            ext = fn.rsplit('.', 1)[-1].lower() if '.' in fn else ''
            if fn in DOC_META:
                icon, title, desc = DOC_META[fn]
            else:
                icon, title = DOC_FALLBACK.get(ext, ('📎', ext.upper() + '-Datei'))
                desc = fn
            out.append({'file': fn, 'icon': icon, 'title': title, 'desc': desc,
                        'size_kb': round(os.path.getsize(os.path.join(DOCS_DIR, fn)) / 1024, 1)})
    return out

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'db': os.path.exists(DB_PATH), 'docs': len(list_docs())})

@app.route('/login', methods=['GET', 'POST'])
def login():
    err = None
    if request.method == 'POST':
        db = get_db()
        u = db.execute('SELECT * FROM users WHERE username=? AND active=1',
                       (request.form['username'].strip(),)).fetchone()
        db.close()
        if u and check_password_hash(u['password_hash'], request.form['password']):
            session['user'] = {'id': u['id'], 'username': u['username'],
                               'name': u['display_name'], 'role': u['role'], 'theme': u['theme']}
            return redirect(url_for('dashboard'))
        err = 'Benutzername oder Passwort falsch ❌'
    return render_template('login.html', err=err)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    db = get_db()
    year = current_year(db)
    progress = {}
    if year:
        for stg in STAGES:
            rows = db.execute('SELECT status, COUNT(*) c FROM checklist WHERE school_year_id=? AND stage=? GROUP BY status',
                              (year['id'], stg['key'])).fetchall()
            counts = {r['status']: r['c'] for r in rows}
            total = sum(counts.values()) or 1
            done = counts.get('erledigt', 0) + counts.get('teilweise', 0) * 0.5
            progress[stg['key']] = {'pct': round(done / total * 100), 'counts': counts, 'total': total}
    years = db.execute('SELECT * FROM school_years ORDER BY id DESC').fetchall()
    db.close()
    return render_template('dashboard.html', stages=STAGES, progress=progress, year=year,
                           years=years, docs=list_docs())

@app.route('/downloads')
@login_required
def downloads():
    return render_template('downloads.html', docs=list_docs())

@app.route('/docs/<path:filename>')
@login_required
def serve_doc(filename):
    return send_from_directory(DOCS_DIR, filename, as_attachment=True)

@app.route('/klasse/<stage>')
@login_required
def klasse(stage):
    if stage not in [s['key'] for s in STAGES]:
        abort(404)
    db = get_db()
    year = current_year(db)
    items, evals, refs = [], [], {}
    if year:
        items = db.execute('SELECT * FROM checklist WHERE school_year_id=? AND stage=? ORDER BY id',
                           (year['id'], stage)).fetchall()
        evals = db.execute('SELECT * FROM evaluations WHERE school_year_id=? AND stage=? ORDER BY id',
                           (year['id'], stage)).fetchall()
        refs = {r['qkey']: r['answer'] for r in
                db.execute('SELECT qkey,answer FROM reflections WHERE school_year_id=? AND stage=?',
                           (year['id'], stage)).fetchall()}
    db.close()
    stage_meta = next(s for s in STAGES if s['key'] == stage)
    return render_template('klasse.html', stage=stage, stage_meta=stage_meta, year=year,
                           items=items, evals=evals, refs=refs, rq=REFLECTION_QUESTIONS,
                           status_icon=STATUS_ICON)

@app.route('/api/checklist/update', methods=['POST'])
@login_required
def api_update():
    data = request.get_json(force=True)
    db = get_db()
    now = datetime.datetime.now().isoformat(timespec='seconds')
    db.execute('UPDATE checklist SET status=?, note=?, updated_by=?, updated_at=? WHERE id=?',
               (data.get('status') if data.get('status') in STATUS else 'offen',
                data.get('note', ''), session['user']['username'], now, data['id']))
    log(db, 'checklist_update', f"id={data['id']} status={data.get('status')}")
    db.close()
    return jsonify({'ok': True})

@app.route('/api/evaluation/update', methods=['POST'])
@login_required
def api_eval():
    data = request.get_json(force=True)
    db = get_db()
    db.execute('UPDATE evaluations SET done=?, result=? WHERE id=?',
               (1 if data.get('done') else 0, data.get('result', ''), data['id']))
    log(db, 'evaluation_update', f"id={data['id']}")
    db.close()
    return jsonify({'ok': True})

@app.route('/api/reflection/update', methods=['POST'])
@login_required
def api_reflect():
    data = request.get_json(force=True)
    db = get_db()
    db.execute('UPDATE reflections SET answer=? WHERE school_year_id=? AND stage=? AND qkey=?',
               (data.get('answer', ''), data['year_id'], data['stage'], data['qkey']))
    log(db, 'reflection_update', f"stage={data['stage']} qkey={data['qkey']}")
    db.close()
    return jsonify({'ok': True})

@app.route('/api/theme', methods=['POST'])
@login_required
def api_theme():
    theme = request.get_json(force=True).get('theme', 'sporty')
    db = get_db()
    db.execute('UPDATE users SET theme=? WHERE id=?', (theme, session['user']['id']))
    db.commit()
    db.close()
    session['user'] = dict(session['user'], theme=theme)
    session.modified = True
    return jsonify({'ok': True})

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    msg = None
    if request.method == 'POST':
        db = get_db()
        me = db.execute('SELECT * FROM users WHERE id=?', (session['user']['id'],)).fetchone()
        if check_password_hash(me['password_hash'], request.form['old_pw']):
            db.execute('UPDATE users SET password_hash=? WHERE id=?',
                       (generate_password_hash(request.form['new_pw']), session['user']['id']))
            db.commit()
            msg = 'Passwort geändert ✅'
        else:
            msg = 'Altes Passwort falsch ❌'
        db.close()
    return render_template('settings.html', msg=msg)

@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_year':
            label = request.form['label'].strip()
            cur = db.execute('INSERT INTO school_years(label, active) VALUES(?,0)', (label,))
            db.commit()
            seed_year(db, cur.lastrowid)
            log(db, 'add_year', label)
            flash(f'Schuljahr {label} angelegt & Curriculum eingespielt ✅')
        elif action == 'activate_year':
            db.execute('UPDATE school_years SET active=0')
            db.execute('UPDATE school_years SET active=1 WHERE id=?', (request.form['year_id'],))
            log(db, 'activate_year', request.form['year_id'])
            flash('Aktives Schuljahr gesetzt ✅')
        elif action == 'copy_year':
            src, label = int(request.form['src_id']), request.form['label'].strip()
            cur = db.execute('INSERT INTO school_years(label, active) VALUES(?,0)', (label,))
            db.commit(); new_id = cur.lastrowid
            seed_year(db, new_id)
            db.execute('''UPDATE checklist SET status=(SELECT status FROM checklist c2 WHERE c2.school_year_id=? AND c2.stage=checklist.stage AND c2.item_code=checklist.item_code)
                          WHERE school_year_id=?''', (src, new_id))
            db.commit()
            log(db, 'copy_year', f'von id={src} nach {label}')
            flash(f'Schuljahr {label} als Kopie angelegt (Status übernommen) 📄')
        elif action == 'add_user':
            db.execute('INSERT INTO users(username,display_name,password_hash,role) VALUES(?,?,?,?)',
                       (request.form['username'].strip(), request.form['display_name'].strip(),
                        generate_password_hash(request.form['password']), request.form['role']))
            log(db, 'add_user', request.form['username'])
            flash('Benutzer angelegt 👤')
        elif action == 'toggle_user':
            db.execute("UPDATE users SET active=1-active WHERE id=? AND username!='admin'", (request.form['user_id'],))
            log(db, 'toggle_user', request.form['user_id'])
        elif action == 'reset_pw':
            db.execute('UPDATE users SET password_hash=? WHERE id=?',
                       (generate_password_hash(request.form['new_password']), request.form['user_id']))
            log(db, 'reset_pw', request.form['user_id'])
            flash('Passwort zurückgesetzt 🔑')
        db.commit()
    users = db.execute('SELECT * FROM users ORDER BY id').fetchall()
    years = db.execute('SELECT y.*, (SELECT COUNT(*) FROM checklist c WHERE c.school_year_id=y.id) items FROM school_years y ORDER BY y.id DESC').fetchall()
    audit = db.execute('SELECT * FROM audit_log ORDER BY id DESC LIMIT 40').fetchall()
    db.close()
    return render_template('admin.html', users=users, years=years, audit=audit)

@app.route('/export/<stage>.json')
@login_required
def export_json(stage):
    db = get_db()
    year = current_year(db)
    if not year:
        db.close()
        abort(400, 'Kein Schuljahr aktiv')
    data = {
        'stage': stage, 'school_year': year['label'],
        'checklist': [dict(r) for r in db.execute('SELECT item_code,item_title,hours,status,note FROM checklist WHERE school_year_id=? AND stage=?', (year['id'], stage))],
        'evaluations': [dict(r) for r in db.execute('SELECT area,instrument,done,result FROM evaluations WHERE school_year_id=? AND stage=?', (year['id'], stage))],
        'reflections': [dict(r) for r in db.execute('SELECT qkey,answer FROM reflections WHERE school_year_id=? AND stage=?', (year['id'], stage))],
    }
    db.close()
    return app.response_class(json.dumps(data, ensure_ascii=False, indent=2),
                              mimetype='application/json',
                              headers={'Content-Disposition': f'attachment; filename=sport_{stage}.json'})

@app.route('/export/<stage>.csv')
@login_required
def export_csv(stage):
    db = get_db()
    year = current_year(db)
    if not year:
        db.close()
        abort(400, 'Kein Schuljahr aktiv')
    out = io.StringIO()
    w = csv.writer(out, delimiter=';')
    w.writerow(['UV', 'Titel', 'Stunden', 'Status', 'Notiz'])
    for r in db.execute('SELECT item_code,item_title,hours,status,note FROM checklist WHERE school_year_id=? AND stage=?', (year['id'], stage)):
        w.writerow([r['item_code'], r['item_title'], r['hours'], r['status'], r['note']])
    db.close()
    return app.response_class(out.getvalue().encode('utf-8-sig'), mimetype='text/csv',
                              headers={'Content-Disposition': f'attachment; filename=sport_{stage}.csv'})

@app.route('/export/backup.db')
@admin_required
def backup():
    return send_file(DB_PATH, as_attachment=True, download_name='sport_manager_backup.db')

@app.route('/api/progress')
@login_required
def api_progress():
    db = get_db()
    year = current_year(db)
    res = {}
    if year:
        for stg in STAGES:
            r = db.execute("SELECT COUNT(*) total, SUM(CASE WHEN status='erledigt' THEN 1 ELSE 0 END) done FROM checklist WHERE school_year_id=? AND stage=?", (year['id'], stg['key'])).fetchone()
            res[stg['key']] = {'total': r['total'], 'done': r['done'] or 0}
    db.close()
    return jsonify(res)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=os.environ.get('DEBUG') == '1')
