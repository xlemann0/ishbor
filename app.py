import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'maxfiy-kalit-soz-ishbor-live'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/receipts'
app.config['ADMIN_PASSWORD'] = 'admin123'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    telegram = db.Column(db.String(50), nullable=True)
    receipt = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending')

# Sayt sozlamalari (karta va narx uchun)
class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)

with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()
    
    if not Setting.query.filter_by(key='card_number').first():
        db.session.add(Setting(key='card_number', value='9860 1203 4567 8910'))
    if not Setting.query.filter_by(key='card_holder').first():
        db.session.add(Setting(key='card_holder', value='Kamoliddin R.'))
    if not Setting.query.filter_by(key='job_price').first():
        db.session.add(Setting(key='job_price', value='20,000 UZS'))
    db.session.commit()

REGIONS = [
    "Toshkent shahri", "Farg'ona viloyati", "Andijon viloyati", "Namangan viloyati", 
    "Samarqand viloyati", "Buxoro viloyati", "Qashqadaryo viloyati", "Surxondaryo viloyati", 
    "Jizzax viloyati", "Sirdaryo viloyati", "Navoiy viloyati", "Xorazm viloyati", "Qoraqalpog'iston Respublikasi"
]

CATEGORIES = [
    "IT va Dasturlash", "Savdo va Menedjment", "Ofis va Buxgalteriya", 
    "Ta'lim va Fan", "Qurilish va Ishlab chiqarish", "Transport va Logistika", "Boshqa"
]

@app.route('/')
def index():
    keyword = request.args.get('q', '').strip()
    region = request.args.get('region', '').strip()
    category = request.args.get('category', '').strip()

    query = Job.query.filter_by(status='active')

    if keyword:
        query = query.filter(Job.title.ilike(f'%{keyword}%') | Job.description.ilike(f'%{keyword}%'))
    if region and region != 'Barchasi':
        query = query.filter_by(region=region)
    if category and category != 'Barchasi':
        query = query.filter_by(category=category)

    jobs = query.order_by(Job.id.desc()).all()
    return render_template('index.html', jobs=jobs, regions=REGIONS, categories=CATEGORIES)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        password = generate_password_hash(request.form.get('password'))

        if User.query.filter_by(phone=phone).first():
            flash("Bu telefon raqam allaqachon ro'yxatdan o'tgan!", "danger")
            return redirect(url_for('register'))

        new_user = User(fullname=fullname, phone=phone, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        session['user_name'] = new_user.fullname
        flash("Muvaffaqiyatli ro'yxatdan o'tdingiz!", "success")
        return redirect(url_for('add_job'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        user = User.query.filter_by(phone=phone).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.fullname
            flash("Tizimga muvaffaqiyatli kirdingiz!", "success")
            return redirect(url_for('add_job'))
        else:
            flash("Telefon raqam yoki parol xato!", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))

@app.route('/add-job', methods=['GET', 'POST'])
def add_job():
    if 'user_id' not in session:
        flash("E'lon berish uchun oldin ro'yxatdan o'ting yoki kiring!", "warning")
        return redirect(url_for('login'))
    
    settings = {s.key: s.value for s in Setting.query.all()}
    
    if request.method == 'POST':
        file = request.files.get('receipt')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_job = Job(
                title=request.form.get('title'),
                company=request.form.get('company'),
                category=request.form.get('category'),
                region=request.form.get('region'),
                job_type=request.form.get('job_type'),
                salary=request.form.get('salary'),
                experience=request.form.get('experience'),
                description=request.form.get('description'),
                phone=request.form.get('phone'),
                telegram=request.form.get('telegram'),
                receipt=filename,
                status='pending'
            )
            db.session.add(new_job)
            db.session.commit()
            
            flash("E'loningiz qabul qilindi! Adminlar tekshiruvidan so'ng saytda e'lon qilinadi.", "success")
            return redirect(url_for('index'))
        else:
            flash("Iltimos, to'lov cheki skrinshotini yuklang!", "danger")
            
    return render_template('add_job.html', regions=REGIONS, categories=CATEGORIES, settings=settings)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == app.config['ADMIN_PASSWORD']:
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("Parol noto'g'ri!", "danger")
    return render_template('admin_login.html')

@app.route('/admin-panel', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        card_holder = request.form.get('card_holder')
        job_price = request.form.get('job_price')
        
        Setting.query.filter_by(key='card_number').first().value = card_number
        Setting.query.filter_by(key='card_holder').first().value = card_holder
        Setting.query.filter_by(key='job_price').first().value = job_price
        db.session.commit()
        
        flash("To'lov karta ma'lumotlari muvaffaqiyatli yangilandi!", "success")
        return redirect(url_for('admin_panel'))

    jobs = Job.query.order_by(Job.id.desc()).all()
    settings = {s.key: s.value for s in Setting.query.all()}
    return render_template('admin_panel.html', jobs=jobs, settings=settings)

@app.route('/admin/approve/<int:job_id>')
def approve_job(job_id):
    if not session.get('is_admin'): return redirect(url_for('admin_login'))
    job = Job.query.get_or_404(job_id)
    job.status = 'active'
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<int:job_id>')
def delete_job(job_id):
    if not session.get('is_admin'): return redirect(url_for('admin_login'))
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
