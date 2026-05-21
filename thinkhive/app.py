from flask import Flask, render_template, request, redirect, session, flash, send_from_directory, jsonify
import sqlite3, os, json, zipfile
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'thinkhive_secret_2024'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'zip', 'png', 'jpg', 'jpeg'}
CODE_FOLDER = 'code_uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CODE_FOLDER'] = CODE_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(CODE_FOLDER):
    os.makedirs(CODE_FOLDER)

DEPARTMENTS = [
    "Computer Science Engineering",
    "Computer Science Engineering (AI & ML)",
    "Computer Science Engineering (Data Science)",
    "Information Technology",
    "Electronics & Communication Engineering",
    "Electrical & Electronics Engineering",
    "Electronics & Telematics Engineering"
]
YEARS = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
DOMAINS = [
    "Artificial Intelligence", "Machine Learning", "Deep Learning",
    "Web Development", "Mobile Development", "Cloud Computing",
    "Cybersecurity", "Internet of Things", "Data Science",
    "Blockchain", "Embedded Systems", "Networking", "Robotics", "Other"
]
PROJECT_TYPES = ["Research Project", "Regular Project"]

PHASES = [
    "Phase 1 - Project Selection",
    "Phase 2 - Abstract Submission",
    "Phase 3 - Implementation Part 1",
    "Phase 4 - Implementation Part 2",
    "Phase 5 - Final Project",
    "Phase 6 - Document & Report Submission",
    "Phase 7 - Paper Submission (IEEE Format)"
]

SW_FRONTEND = ["HTML / CSS", "JavaScript", "TypeScript", "React.js", "Angular",
               "Vue.js", "Next.js", "Bootstrap", "Tailwind CSS", "Flutter",
               "React Native", "Android (XML)", "Swift (iOS)", "Other"]
SW_BACKEND  = ["Python", "Java", "Node.js", "PHP", "Go", "Ruby", "C#", "Rust",
               "Django", "Flask", "FastAPI", "Spring Boot", "Express.js",
               "Laravel", "ASP.NET", "Other"]
SW_DATABASES = ["MySQL", "PostgreSQL", "MongoDB", "SQLite", "Firebase",
                "Redis", "Oracle", "MS SQL Server", "Supabase", "Other"]
SW_LANGUAGES = ["Python", "Java", "C", "C++", "JavaScript", "TypeScript",
                "Kotlin", "Swift", "Go", "Rust", "PHP", "Ruby", "Other"]
SW_FRAMEWORKS = ["React", "Angular", "Vue.js", "Node.js", "Django", "Flask",
                 "Spring Boot", "FastAPI", "Flutter", "React Native",
                 "TensorFlow", "PyTorch", "Scikit-learn", "Other"]
HW_COMPONENTS = ["Arduino", "Raspberry Pi", "ESP32", "ESP8266", "STM32",
                 "NodeMCU", "FPGA", "PIC Microcontroller", "Sensors & Actuators",
                 "GSM/GPS Module", "Bluetooth/Wi-Fi Module", "Other"]
HW_CATEGORIES = ["Embedded Systems", "Robotics", "IoT Device", "Power Electronics",
                 "Signal Processing", "Communication Systems", "Automation", "Other"]


def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL, role TEXT NOT NULL,
        roll TEXT, department TEXT, year TEXT,
        teacher_id TEXT, coordinator TEXT,
        email TEXT, phone TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, description TEXT,
        department TEXT, domain TEXT,
        project_type TEXT, project_nature TEXT, year TEXT,
        filename TEXT, code_zip TEXT, student_id INTEGER,
        guide_name TEXT,
        phase TEXT DEFAULT "Phase 1 - Project Selection",
        feedback TEXT, rating INTEGER,
        status TEXT DEFAULT "Pending",
        visited INTEGER DEFAULT 0,
        next_review TEXT,
        review_notes TEXT,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        sw_languages TEXT, sw_frameworks TEXT, sw_databases TEXT,
        sw_deployment TEXT, sw_github TEXT, sw_demo_url TEXT,
        sw_frontend TEXT, sw_backend TEXT, sw_arch TEXT,
        hw_components TEXT, hw_category TEXT,
        hw_microcontroller TEXT, hw_power_source TEXT, hw_prototype TEXT,
        FOREIGN KEY(student_id) REFERENCES users(id)
    )''')
    # Group members table
    c.execute('''CREATE TABLE IF NOT EXISTS project_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        roll TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )''')

    # Auto-migrate existing tables
    existing_user_cols = {row[1] for row in c.execute("PRAGMA table_info(users)")}
    for col, td in [("email","TEXT"),("phone","TEXT"),("created_at","TEXT")]:
        if col not in existing_user_cols:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} {td}")

    existing_proj_cols = {row[1] for row in c.execute("PRAGMA table_info(projects)")}
    for col, td in [
        ("description","TEXT"),("project_nature","TEXT"),("uploaded_at","TEXT"),
        ("guide_name","TEXT"),("phase","TEXT"),
        ("visited","INTEGER"),("next_review","TEXT"),("review_notes","TEXT"),
        ("sw_languages","TEXT"),("sw_frameworks","TEXT"),("sw_databases","TEXT"),
        ("sw_deployment","TEXT"),("sw_github","TEXT"),("sw_demo_url","TEXT"),
        ("sw_frontend","TEXT"),("sw_backend","TEXT"),("sw_arch","TEXT"),
        ("hw_components","TEXT"),("hw_category","TEXT"),("hw_microcontroller","TEXT"),
        ("hw_power_source","TEXT"),("hw_prototype","TEXT"),
        ("status","TEXT"),("year","TEXT"),("rating","INTEGER"),
        ("code_zip","TEXT"),
    ]:
        if col not in existing_proj_cols:
            c.execute(f"ALTER TABLE projects ADD COLUMN {col} {td}")

    conn.commit()
    conn.close()


init_db()


def allowed_file(f):
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user(uid):
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return u


# ── AUTH ──────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        d = request.form
        conn = get_db()
        if conn.execute("SELECT id FROM users WHERE username=?", (d['username'],)).fetchone():
            conn.close()
            flash('Username already taken.', 'error')
            return render_template('signup.html', departments=DEPARTMENTS, years=YEARS)
        conn.execute("""INSERT INTO users(name,username,password,role,roll,department,year,
                        teacher_id,coordinator,email,phone) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                     (d['name'],d['username'],d['password'],d['role'],
                      d.get('roll',''),d.get('department',''),d.get('year',''),
                      d.get('teacher_id',''),d.get('coordinator',''),
                      d.get('email',''),d.get('phone','')))
        conn.commit(); conn.close()
        flash('Account created! Please login.', 'success')
        return redirect('/login')
    return render_template('signup.html', departments=DEPARTMENTS, years=YEARS)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'].strip(), request.form['password']
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['role']    = user['role']
            session['name']    = user['name']
            return redirect('/student' if user['role'] == 'student' else '/faculty')
        flash('Invalid username or password.', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ── SETTINGS ──────────────────────────────────────────

@app.route('/settings')
def settings():
    if not session.get('user_id'): return redirect('/login')
    return render_template('settings.html', user=get_user(session['user_id']),
                           departments=DEPARTMENTS, years=YEARS)


@app.route('/settings/update', methods=['POST'])
def update_settings():
    if not session.get('user_id'): return redirect('/login')
    d = request.form
    conn = get_db()
    conn.execute("""UPDATE users SET name=?,email=?,phone=?,department=?,year=?,coordinator=?
                    WHERE id=?""",
                 (d['name'],d.get('email',''),d.get('phone',''),
                  d.get('department',''),d.get('year',''),
                  d.get('coordinator',''),session['user_id']))
    conn.commit(); conn.close()
    session['name'] = d['name']
    flash('Profile updated.', 'success')
    return redirect('/settings')


# ── ANALYTICS ─────────────────────────────────────────

@app.route('/analytics')
def analytics():
    if not session.get('user_id'): return redirect('/login')
    conn = get_db()

    # Projects per domain
    domain_rows = conn.execute(
        "SELECT domain, COUNT(*) as cnt FROM projects WHERE domain IS NOT NULL AND domain != '' GROUP BY domain ORDER BY cnt DESC"
    ).fetchall()

    # Projects per department
    dept_rows = conn.execute(
        "SELECT department, COUNT(*) as cnt FROM projects WHERE department IS NOT NULL AND department != '' GROUP BY department ORDER BY cnt DESC"
    ).fetchall()

    # Average rating per domain
    rating_rows = conn.execute(
        "SELECT domain, ROUND(AVG(rating),1) as avg_r, COUNT(*) as cnt FROM projects WHERE rating IS NOT NULL GROUP BY domain ORDER BY avg_r DESC"
    ).fetchall()

    # Submission trend (by month)
    trend_rows = conn.execute(
        "SELECT strftime('%Y-%m', uploaded_at) as month, COUNT(*) as cnt FROM projects WHERE uploaded_at IS NOT NULL GROUP BY month ORDER BY month"
    ).fetchall()

    # Phase distribution
    phase_rows = conn.execute(
        "SELECT phase, COUNT(*) as cnt FROM projects WHERE phase IS NOT NULL GROUP BY phase"
    ).fetchall()

    # Nature split
    nature_rows = conn.execute(
        "SELECT project_nature, COUNT(*) as cnt FROM projects WHERE project_nature IS NOT NULL GROUP BY project_nature"
    ).fetchall()

    # Overall stats
    total     = conn.execute("SELECT COUNT(*) as c FROM projects").fetchone()['c']
    reviewed  = conn.execute("SELECT COUNT(*) as c FROM projects WHERE feedback IS NOT NULL AND feedback != ''").fetchone()['c']
    avg_rating = conn.execute("SELECT ROUND(AVG(rating),2) as r FROM projects WHERE rating IS NOT NULL").fetchone()['r'] or 0
    conn.close()

    most_active = domain_rows[0]['domain'] if domain_rows else '—'

    return render_template('analytics.html',
        domain_labels  = json.dumps([r['domain'] for r in domain_rows]),
        domain_counts  = json.dumps([r['cnt']    for r in domain_rows]),
        dept_labels    = json.dumps([r['department'] for r in dept_rows]),
        dept_counts    = json.dumps([r['cnt']        for r in dept_rows]),
        rating_labels  = json.dumps([r['domain'] for r in rating_rows]),
        rating_values  = json.dumps([r['avg_r']  for r in rating_rows]),
        trend_labels   = json.dumps([r['month']  for r in trend_rows]),
        trend_counts   = json.dumps([r['cnt']    for r in trend_rows]),
        phase_labels   = json.dumps([r['phase']  for r in phase_rows]),
        phase_counts   = json.dumps([r['cnt']    for r in phase_rows]),
        nature_labels  = json.dumps([r['project_nature'] for r in nature_rows]),
        nature_counts  = json.dumps([r['cnt']            for r in nature_rows]),
        total=total, reviewed=reviewed, avg_rating=avg_rating,
        most_active=most_active
    )


# ── STUDENT ───────────────────────────────────────────

@app.route('/student')
def student():
    if session.get('role') != 'student': return redirect('/')
    conn = get_db()
    dept_filter = request.args.get('dept','')
    type_filter = request.args.get('type','')
    q = "SELECT p.*, u.name as student_name FROM projects p LEFT JOIN users u ON p.student_id=u.id WHERE 1=1"
    params = []
    if dept_filter: q += " AND p.department=?"; params.append(dept_filter)
    if type_filter: q += " AND p.project_type=?"; params.append(type_filter)
    q += " ORDER BY p.uploaded_at DESC"
    projects    = conn.execute(q, params).fetchall()
    my_projects = conn.execute(
        "SELECT * FROM projects WHERE student_id=? ORDER BY uploaded_at DESC",
        (session['user_id'],)).fetchall()

    # Fetch members for all relevant projects
    all_ids = list({p['id'] for p in list(projects) + list(my_projects)})
    members_map = {}
    if all_ids:
        placeholders = ','.join('?' * len(all_ids))
        rows = conn.execute(f"SELECT * FROM project_members WHERE project_id IN ({placeholders})", all_ids).fetchall()
        for r in rows:
            members_map.setdefault(r['project_id'], []).append({'name': r['name'], 'roll': r['roll']})

    stats = {
        'total':    len(my_projects),
        'reviewed': sum(1 for p in my_projects if p['feedback']),
        'pending':  sum(1 for p in my_projects if not p['feedback'])
    }
    conn.close()
    return render_template('student.html',
        projects=projects, my_projects=my_projects,
        members_map=members_map,
        departments=DEPARTMENTS, domains=DOMAINS,
        project_types=PROJECT_TYPES, years=YEARS, phases=PHASES,
        sw_languages=SW_LANGUAGES, sw_frameworks=SW_FRAMEWORKS,
        sw_databases=SW_DATABASES, sw_frontend=SW_FRONTEND, sw_backend=SW_BACKEND,
        hw_components=HW_COMPONENTS, hw_categories=HW_CATEGORIES,
        dept_filter=dept_filter, type_filter=type_filter, stats=stats)


@app.route('/upload', methods=['POST'])
def upload():
    if session.get('role') != 'student': return redirect('/')
    if 'file' not in request.files or request.files['file'].filename == '':
        flash('Please select a file.', 'error'); return redirect('/student')
    file = request.files['file']
    if not allowed_file(file.filename):
        flash('File type not allowed.', 'error'); return redirect('/student')
    filename = secure_filename(file.filename)
    base, ext = os.path.splitext(filename)
    filename = f"{base}_{session['user_id']}_{int(datetime.now().timestamp())}{ext}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    d = request.form

    # Handle code ZIP upload
    code_zip_name = ''
    code_file = request.files.get('code_zip')
    if code_file and code_file.filename.endswith('.zip'):
        cz_name = secure_filename(code_file.filename)
        cz_base, cz_ext = os.path.splitext(cz_name)
        code_zip_name = f"{cz_base}_{session['user_id']}_{int(datetime.now().timestamp())}{cz_ext}"
        code_file.save(os.path.join(app.config['CODE_FOLDER'], code_zip_name))

    conn = get_db()
    cur = conn.execute("""INSERT INTO projects(
        title,description,department,domain,project_type,project_nature,year,
        guide_name,phase,filename,code_zip,student_id,uploaded_at,
        sw_languages,sw_frameworks,sw_databases,sw_deployment,sw_github,sw_demo_url,
        sw_frontend,sw_backend,sw_arch,
        hw_components,hw_category,hw_microcontroller,hw_power_source,hw_prototype)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d['title'],d.get('description',''),d['department'],d['domain'],
         d['project_type'],d.get('project_nature','Software'),d['year'],
         d.get('guide_name',''),d.get('phase', PHASES[0]),
         filename, code_zip_name, session['user_id'],
         datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
         ','.join(d.getlist('sw_languages')),','.join(d.getlist('sw_frameworks')),
         d.get('sw_database',''),d.get('sw_deployment',''),
         d.get('sw_github',''),d.get('sw_demo_url',''),
         ','.join(d.getlist('sw_frontend')),','.join(d.getlist('sw_backend')),
         d.get('sw_arch',''),
         ','.join(d.getlist('hw_components')),d.get('hw_category',''),
         d.get('hw_microcontroller',''),d.get('hw_power_source',''),d.get('hw_prototype','')))
    project_id = cur.lastrowid

    # Save group members
    member_names = d.getlist('member_name')
    member_rolls = d.getlist('member_roll')
    for name, roll in zip(member_names, member_rolls):
        name = name.strip()
        if name:
            conn.execute("INSERT INTO project_members(project_id,name,roll) VALUES(?,?,?)",
                         (project_id, name, roll.strip()))

    conn.commit(); conn.close()
    flash('Project submitted successfully!', 'success')
    return redirect('/student')


@app.route('/delete_project/<int:id>', methods=['POST'])
def delete_project(id):
    if session.get('role') != 'student': return redirect('/')
    conn = get_db()
    p = conn.execute("SELECT * FROM projects WHERE id=? AND student_id=?",
                     (id, session['user_id'])).fetchone()
    if p:
        try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], p['filename']))
        except: pass
        if p['code_zip']:
            try: os.remove(os.path.join(app.config['CODE_FOLDER'], p['code_zip']))
            except: pass
        conn.execute("DELETE FROM project_members WHERE project_id=?", (id,))
        conn.execute("DELETE FROM projects WHERE id=?", (id,))
        conn.commit()
        flash('Project deleted.', 'success')
    conn.close()
    return redirect('/student')


# ── FACULTY ───────────────────────────────────────────

@app.route('/faculty')
def faculty():
    if session.get('role') != 'faculty': return redirect('/')
    conn = get_db()
    dept_filter   = request.args.get('dept','')
    type_filter   = request.args.get('type','')
    nature_filter = request.args.get('nature','')
    status_filter = request.args.get('status','')
    phase_filter  = request.args.get('phase','')
    visited_filter = request.args.get('visited','')
    q = """SELECT p.*, u.name as student_name, u.roll, u.year as student_year, u.email as student_email
           FROM projects p LEFT JOIN users u ON p.student_id=u.id WHERE 1=1"""
    params = []
    if dept_filter:    q += " AND p.department=?";     params.append(dept_filter)
    if type_filter:    q += " AND p.project_type=?";   params.append(type_filter)
    if nature_filter:  q += " AND p.project_nature=?"; params.append(nature_filter)
    if status_filter:  q += " AND p.status=?";         params.append(status_filter)
    if phase_filter:   q += " AND p.phase=?";          params.append(phase_filter)
    if visited_filter != '':
        q += " AND p.visited=?"; params.append(int(visited_filter))
    q += " ORDER BY p.uploaded_at DESC"
    projects = conn.execute(q, params).fetchall()
    total    = conn.execute("SELECT COUNT(*) as c FROM projects").fetchone()['c']
    reviewed = conn.execute("SELECT COUNT(*) as c FROM projects WHERE feedback IS NOT NULL AND feedback != ''").fetchone()['c']
    visited  = conn.execute("SELECT COUNT(*) as c FROM projects WHERE visited=1").fetchone()['c']

    # Fetch members
    all_ids = [p['id'] for p in projects]
    members_map = {}
    if all_ids:
        placeholders = ','.join('?' * len(all_ids))
        rows = conn.execute(f"SELECT * FROM project_members WHERE project_id IN ({placeholders})", all_ids).fetchall()
        for r in rows:
            members_map.setdefault(r['project_id'], []).append({'name': r['name'], 'roll': r['roll']})

    conn.close()
    stats = {'total': total, 'reviewed': reviewed,
             'pending': total - reviewed, 'visited': visited}
    return render_template('faculty.html', projects=projects,
        members_map=members_map,
        departments=DEPARTMENTS, project_types=PROJECT_TYPES, phases=PHASES,
        dept_filter=dept_filter, type_filter=type_filter,
        nature_filter=nature_filter, status_filter=status_filter,
        phase_filter=phase_filter, visited_filter=visited_filter, stats=stats)


@app.route('/feedback/<int:id>', methods=['POST'])
def feedback(id):
    if session.get('role') != 'faculty': return redirect('/')
    d = request.form
    conn = get_db()
    conn.execute("""UPDATE projects SET feedback=?,rating=?,status=?,phase=?,
                    visited=?,next_review=?,review_notes=? WHERE id=?""",
                 (d['feedback'], d['rating'], d.get('status','Reviewed'),
                  d.get('phase',''), int(d.get('visited', 0)),
                  d.get('next_review',''), d.get('review_notes',''), id))
    conn.commit(); conn.close()
    flash('Review saved successfully.', 'success')
    return redirect('/faculty')


@app.route('/mark_visited/<int:id>', methods=['POST'])
def mark_visited(id):
    if session.get('role') != 'faculty': return redirect('/')
    visited = int(request.form.get('visited', 1))
    conn = get_db()
    conn.execute("UPDATE projects SET visited=? WHERE id=?", (visited, id))
    conn.commit(); conn.close()
    return redirect('/faculty')


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/code_download/<filename>')
def code_download(filename):
    if not session.get('user_id'): return redirect('/login')
    return send_from_directory(app.config['CODE_FOLDER'], filename)


@app.route('/code_tree/<int:project_id>')
def code_tree(project_id):
    """Returns JSON file tree of the uploaded code ZIP."""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    p = conn.execute("SELECT code_zip FROM projects WHERE id=?", (project_id,)).fetchone()
    conn.close()
    if not p or not p['code_zip']:
        return jsonify({'error': 'No code uploaded'}), 404
    zip_path = os.path.join(app.config['CODE_FOLDER'], p['code_zip'])
    if not os.path.exists(zip_path):
        return jsonify({'error': 'File not found'}), 404

    def build_tree(names):
        root = {}
        for name in sorted(names):
            parts = name.split('/')
            node = root
            for part in parts:
                if not part: continue
                node = node.setdefault(part, {})
        return root

    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = [n for n in zf.namelist() if not n.startswith('__MACOSX')]
    tree = build_tree(names)
    return jsonify({'tree': tree, 'zip': p['code_zip']})


if __name__ == '__main__':
    app.run(debug=True)
