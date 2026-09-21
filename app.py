from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'maxfiy_kalit_soz_super_xavfsiz_2026'

# Namuna foydalanuvchilar bazasi (Ro'yxatdan o'tish uchun)
USERS_DB = [
    {'id': 1, 'name': 'Dilshod', 'phone': '+998901234567', 'password': '123'}
]

# E'lonlar bazasi (Narxlar va boshqa ma'lumotlar bilan)
JOBS_DB = [
    {
        'id': 1,
        'title': 'Senior Python Developer (AI & Backend)',
        'company': 'Tech Solutions Global',
        'category': 'IT va Dasturlash',
        'region': 'Toshkent shahri',
        'job_type': 'To\'liq stavka',
        'salary': '12 000 000 - 18 000 000 so\'m',
        'experience': '3-5 yil',
        'description': 'Sun\'iy intellekt va Flask/FastAPI texnologiyalarida yuqori darajadagi dasturlarni yaratish uchun kuchli mutaxassisni qidiramiz.',
        'phone': '+998901234567',
        'user_id': 1
    },
    {
        'id': 2,
        'title': 'Lead UI/UX Product Designer',
        'company': 'Creative Studio Lab',
        'category': 'Dizayn va Media',
        'region': 'Farg\'ona viloyati',
        'job_type': 'Masofaviy (Remote)',
        'salary': '8 000 000 so\'m',
        'experience': '1-3 yil',
        'description': 'Figma dasturida mukammal interfeyslar yaratadigan, zamonaviy trendlardan xabardor dizayner kerak.',
        'phone': '+998919876543',
        'user_id': 1
    }
]

CATEGORIES = [
    "IT va Dasturlash", 
    "Dizayn va Media", 
    "Savdo va Menedjment", 
    "Ofis va Buxgalteriya", 
    "Ta'lim va Fan", 
    "Qurilish va Ishlab chiqarish", 
    "Transport va Logistika"
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
    selected_category = request.args.get('category', 'Barchasi')
    
    filtered_jobs = JOBS_DB
    
    if query:
        filtered_jobs = [j for j in filtered_jobs if query in j['title'].lower() or query in j['description'].lower()]
    
    if selected_region and selected_region != 'Barchasi':
        filtered_jobs = [j for j in filtered_jobs if j['region'] == selected_region]
        
    if selected_category and selected_category != 'Barchasi':
        filtered_jobs = [j for j in filtered_jobs if j['category'] == selected_category]

    return render_template('index.html', 
                           jobs=filtered_jobs, 
                           categories=CATEGORIES, 
                           regions=REGIONS,
                           selected_region=selected_region,
                           selected_category=selected_category,
                           query=query)

# Tizimga kirish (Login)
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

# Ro'yxatdan o'tish (Register)
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

# E'lon qo'shish
@app.route('/add-job', methods=['GET', 'POST'])
def add_job():
    if not session.get('user_id') and not session.get('is_admin'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        new_job = {
            'id': len(JOBS_DB) + 1,
            'title': request.form.get('title'),
            'company': request.form.get('company'),
            'category': request.form.get('category'),
            'region': request.form.get('region'),
            'job_type': request.form.get('job_type'),
            'salary': request.form.get('salary'),
            'experience': request.form.get('experience'),
            'description': request.form.get('description'),
            'phone': request.form.get('phone'),
            'user_id': session.get('user_id', 1)
        }
        JOBS_DB.append(new_job)
        return redirect(url_for('index'))
        
    return render_template('add_job.html', categories=CATEGORIES, regions=REGIONS)

# Admin kirish
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'dilshod2026':
            session['is_admin'] = True
            session['user_name'] = "Admin"
            return redirect(url_for('admin_panel'))
        else:
            error = "Admin login yoki paroli noto'g'ri!"
            
    return render_template('admin_login.html', error=error)

# Admin panel
@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin_panel.html', jobs=JOBS_DB)

# Admin e'loni o'chirish
@app.route('/admin/delete-job/<int:job_id>')
def admin_delete_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    global JOBS_DB
    JOBS_DB = [j for j in JOBS_DB if j['id'] != job_id]
    return redirect(url_for('admin_panel'))

# Chiqish
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
