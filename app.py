from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'maxfiy_kalit_soz'  # Sessiyalar ishlashi uchun

# Namuna ma'lumotlar bazasi (Siz o'zingizning bazangiz bilan almashtirasiz)
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
        'user_id': 1  # Bu e'lonni 1-foydalanuvchi qo'shgan
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

# Tizimga kirish (Test uchun oddiy login)
@app.route('/login')
def login():
    session['user_id'] = 1  # Test maqsadida 1-foydalanuvchi sifatida kirishamiz
    session['user_name'] = "Dilshod"
    return redirect(url_for('index'))

# Tizimdan chiqish
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# E'lon berish sahifasi (Faqat tizimga kirganlar uchun)
@app.route('/add-job', methods=['GET', 'POST'])
def add_job():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Agar kirmagan bo'lsa login sahifasiga yo'naltiramiz
    
    if request.method == 'POST':
        # Yangi e'lonni qo'shish logikasi shu yerga yoziladi
        return redirect(url_for('index'))
        
    return render_template('add_job.html', categories=CATEGORIES, regions=REGIONS)

# Mening e'lonlarim sahifasi
@app.route('/my-jobs')
def my_jobs():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user_id = session.get('user_id')
    user_jobs = [j for j in JOBS_DB if j.get('user_id') == current_user_id]
    
    return render_template('my_jobs.html', jobs=user_jobs)

if __name__ == '__main__':
    app.run(debug=True)
