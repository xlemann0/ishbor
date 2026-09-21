import os
import time
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'maxfiy_kalit_soz_super_xavfsiz_2026'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ro'yxatdan o'tgan foydalanuvchilar bazasi
USERS_DB = [
    {'id': 1, 'name': 'Dilshod', 'phone': '+998901234567', 'password': '123'}
]

JOBS_DB = [
    {
        'id': 1,
        'title': 'Senior Python Developer (AI & Backend)',
        'company': 'Tech Solutions Global',
        'ad_type': 'Ish o‘rni',
        'category': 'IT va Dasturlash',
        'region': 'Toshkent shahri',
        'salary': '12 000 000 - 18 000 000 so\'m',
        'description': 'Sun\'iy intellekt texnologiyalarida yuqori darajadagi dasturlarni yaratish.',
        'phone': '+998901234567',
        'check_img': '',
        'status': 'active',
        'user_id': 1
    }
]

AD_TYPES = [
    "Ish o‘rni", 
    "Avtomobil (Mashinalar)", 
    "Ko'chmas mulk (Kvartira / Uy)", 
    "Savdo va Buyumlar", 
    "Xizmatlar va Reklama"
]

CATEGORIES = [
    "IT va Dasturlash", "Transport", "Ko'chmas mulk", "Elektronika", 
    "Kiyim-kechak", "Xizmatlar", "Boshqa"
]

REGIONS = [
    "Toshkent shahri", "Farg'ona viloyati", "Andijon viloyati", 
    "Namangan viloyati", "Samarqand viloyati", "Buxoro viloyati", 
    "Qashqadaryo viloyati", "Surxondaryo viloyati", "Jizzax viloyati", 
    "Sirdaryo viloyati", "Navoiy viloyati", "Xorazm viloyati", 
    "Qoraqalpog'iston Respublikasi"
]

@app.route('/')
def index():
    query = request.args.get('q', '').lower()
    selected_region = request.args.get('region', 'Barchasi')
    selected_ad_type = request.args.get('ad_type', 'Barchasi')
    
    filtered_jobs = [j for j in JOBS_DB if j['status'] == 'active']
    
    if query:
        filtered_jobs = [j for j in filtered_jobs if query in j['title'].lower() or query in j['description'].lower()]
    if selected_region and selected_region != 'Barchasi':
        filtered_jobs = [j for j in filtered_jobs if j['region'] == selected_region]
    if selected_ad_type and selected_ad_type != 'Barchasi':
        filtered_jobs = [j for j in filtered_jobs if j['ad_type'] == selected_ad_type]

    return render_template('index.html', jobs=filtered_jobs, ad_types=AD_TYPES, regions=REGIONS, 
                           selected_region=selected_region, selected_ad_type=selected_ad_type, query=query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        user = next((u for u in USERS_DB if u['phone'] == phone and u['password'] == password), None)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['is_admin'] = False
            return redirect(url_for('index'))
        else:
            error = "Telefon raqam yoki parol noto'g'ri!"
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        if any(u['phone'] == phone for u in USERS_DB):
            error = "Bu raqam allaqachon ro'yxatdan o'tgan!"
        else:
            new_user = {'id': len(USERS_DB) + 1, 'name': name, 'phone': phone, 'password': password}
            USERS_DB.append(new_user)
            session['user_id'] = new_user['id']
            session['user_name'] = new_user['name']
            session['is_admin'] = False
            return redirect(url_for('index'))
    return render_template('register.html', error=error)

@app.route('/add-job', methods=['GET', 'POST'])
def add_job():
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        check_filename = ''
        check_file = request.files.get('check_img')
        if check_file and check_file.filename != '':
            filename = secure_filename(check_file.filename)
            unique_filename = f"{int(time.time())}_{filename}"
            check_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            check_filename = unique_filename

        new_job = {
            'id': len(JOBS_DB) + 1,
            'title': request.form.get('title'),
            'company': request.form.get('company'),
            'ad_type': request.form.get('ad_type'),
            'category': request.form.get('category'),
            'region': request.form.get('region'),
            'salary': request.form.get('salary'),
            'description': request.form.get('description'),
            'phone': request.form.get('phone'),
            'check_img': check_filename,
            'status': 'pending',
            'user_id': session.get('user_id')
        }
        JOBS_DB.append(new_job)
        return redirect(url_for('my_ads'))
        
    return render_template('add_job.html', ad_types=AD_TYPES, categories=CATEGORIES, regions=REGIONS)

@app.route('/my-ads')
def my_ads():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_jobs = [j for j in JOBS_DB if j['user_id'] == session.get('user_id')]
    return render_template('my_ads.html', jobs=user_jobs)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'dilshod2026':
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            error = "Admin login yoki paroli xato!"
    return render_template('admin_login.html', error=error)

# Admin panelga e'lonlar bilan birga ro'yxatdan o'tgan foydalanuvchilar ham uzatiladi
@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_panel.html', jobs=JOBS_DB, users=USERS_DB)

@app.route('/admin/approve-job/<int:job_id>')
def admin_approve_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    for j in JOBS_DB:
        if j['id'] == job_id:
            j['status'] = 'active'
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-job/<int:job_id>')
def admin_delete_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    global JOBS_DB
    JOBS_DB = [j for j in JOBS_DB if j['id'] != job_id]
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit-job/<int:job_id>', methods=['GET', 'POST'])
def admin_edit_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    job = next((j for j in JOBS_DB if j['id'] == job_id), None)
    if not job:
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        job['title'] = request.form.get('title')
        job['company'] = request.form.get('company')
        job['salary'] = request.form.get('salary')
        job['region'] = request.form.get('region')
        job['description'] = request.form.get('description')
        return redirect(url_for('admin_panel'))
    return render_template('admin_edit_job.html', job=job, regions=REGIONS)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
