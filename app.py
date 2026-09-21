import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'maxfiy-kalit-soz'  # Sessiyalar uchun xavfsizlik kaliti
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/receipts'
app.config['ADMIN_PASSWORD'] = 'admin123'  # Admin panelga kirish paroli (o'zingiz o'zgartirasiz)

db = SQLAlchemy(app)

# E'lonlar uchun Ma'lumotlar Bazasi (Database) Modeli
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    receipt = db.Column(db.String(200), nullable=False)  # To'lov cheki rasmining nomi
    status = db.Column(db.String(20), default='pending')  # pending (kutilmoqda), active (faol)

# Bazani yaratish
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

# 1. Bosh sahifa: Faqat tasdiqlangan (active) e'lonlarni ko'rsatish
@app.route('/')
def index():
    jobs = Job.query.filter_by(status='active').order_by(Job.id.desc()).all()
    return render_template('index.html', jobs=jobs)

# 2. E'lon berish sahifasi
@app.route('/add-job', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        region = request.form.get('region')
        salary = request.form.get('salary')
        description = request.form.get('description')
        phone = request.form.get('phone')
        
        # To'lov chekini yuklab olish
        file = request.files.get('receipt')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Ma'lumotlarni bazaga saqlash (status: pending - admin tasdig'i kutilmoqda)
            new_job = Job(
                title=title,
                category=category,
                region=region,
                salary=salary,
                description=description,
                phone=phone,
                receipt=filename,
                status='pending'
            )
            db.session.add(new_job)
            db.session.commit()
            
            flash("E'loningiz qabul qilindi! 20,000 so'm to'lov cheki tekshirilgach, saytda e'lon qilinadi.", "success")
            return redirect(url_for('index'))
        else:
            flash("Iltimos, to'lov cheki (skrinshot) rasmini yuklang!", "danger")
            
    return render_template('add_job.html')

# 3. Admin panelga kirish (Login)
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == app.config['ADMIN_PASSWORD']:
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("Parol noto'g'ri!", "danger")
    return render_template('admin_login.html')

# 4. Admin panel: E'lonlarni ko'rish va tasdiqlash
@app.route('/admin-panel')
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    # Barcha e'lonlarni chiqarish (kutilayotganlar va faollar)
    jobs = Job.query.order_by(Job.id.desc()).all()
    return render_template('admin_panel.html', jobs=jobs)

# 5. E'lonni tasdiqlash tugmasi uchun
@app.route('/admin/approve/<int:job_id>')
def approve_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    job = Job.query.get_or_404(job_id)
    job.status = 'active'
    db.session.commit()
    return redirect(url_for('admin_panel'))

# 6. E'lonni o'chirish / rad etish
@app.route('/admin/delete/<int:job_id>')
def delete_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('admin_panel'))

# 7. Admin chiqish (Logout)
@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
