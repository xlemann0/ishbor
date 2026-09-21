from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'maxfiy_kalit_soz_bu_yerga'  # Sessiyalar uchun

# Namuna ma'lumotlar bazasi
JOBS_DB = [
    {
        'id': 1,
        'title': 'Python Dasturchi (Backend)',
        'company': 'Tech Solutions LLC',
        'category': 'IT va Dasturlash',
        'region': 'Toshkent shahri',
        'job_type': 'To\'liq stavka',
        'salary': '8 000 000 - 12 000 000 so\'m',
        'experience': '1-3 yil',
        'description': 'Python va Flask/Django texnologiyalarini yaxshi biladigan dasturchilarni ishga taklif qilamiz.',
        'phone': '+998901234567',
        'user_id': 1
    },
    {
        'id': 2,
        'title': 'Sotuv menejeri',
        'company': 'Farg\'ona savdo uyi',
        'category': 'Savdo va Menedjment',
        'region': 'Farg\'ona viloyati',
        'job_type': 'To\'liq stavka',
        'salary': '5 000 000 so\'m',
        'experience': 'Tajribasiz',
        'description': 'Mijozlar bilan muloqot qilish va savdolarni boshqarish uchun faol yigit-qizlarni ishga olamiz.',
        'phone': '+998919876543',
        'user_id': 2
    }
]

CATEGORIES = [
    "IT va Dasturlash", 
    "Savdo va Menedjment", 
    "Ofis va Buxgalteriya", 
    "Ta'lim va Fan", 
    "Qurilish va Ishlab chiqarish", 
    "Transport va Logistika", 
    "Boshqa"
]

REGIONS = [
    "Toshkent shahri", "Farg'ona viloyati", "Andijon viloyati", 
    "Namangan viloyati", "Samarqand viloyati", "Buxoro viloyati", 
    "Qashqadaryo viloyati", "Surxondaryo viloyati", "Jizzax viloyati", 
    "Sirdaryo viloyati", "Navoiy viloyati", "Xorazm viloyati", 
    "Qoraqalpog'iston Respublikasi"
]

# Bosh sahifa
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
                           regions=REGIONS)

# Oddiy foydalanuvchi sifatida kirish (Test uchun)
@app.route('/login')
def login():
    session['user_id'] = 1  
    session['user_name'] = "Dilshod"
    session['is_admin'] = False  # Oddiy foydalanuvchi admin EMAS!
    return redirect(url_for('index'))

# --- ADMIN KIRISH QISMI ---
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # O'zingizning admin loginingiz va parolingizni shu yerga yozasiz
        if username == 'admin' && password == 'dilshod2026':
            session['is_admin'] = True
            session['user_name'] = "Admin"
            return redirect(url_for('admin_panel'))
        else:
            error = "Login yoki parol noto'g'ri!"
            
    return render_template('admin_login.html', error=error)

# Admin panel (Faqat haqiqiy adminlargagina ochiladi)
@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))  # Agar admin bo'lmasa, admin login sahifasiga otib yuboradi
    
    return render_template('admin_panel.html', jobs=JOBS_DB)

# Admin uchun e'lonni o'chirish
@app.route('/admin/delete-job/<int:job_id>')
def admin_delete_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    global JOBS_DB
    JOBS_DB = [j for j in JOBS_DB if j['id'] != job_id]
    return redirect(url_for('admin_panel'))

# Tizimdan chiqish
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
