import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'maxfiy-kalit-soz-ishbor'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/receipts'
app.config['ADMIN_PASSWORD'] = 'admin123'  # Admin panel paroli (xohlasangiz o'zgartirishingiz mumkin)

db = SQLAlchemy(app)

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

with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

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
    
    regions = ["Toshkent shahri", "Farg'ona viloyati", "Andijon viloyati", "Namangan viloyati", "Samarqand viloyati", "Buxoro viloyati", "Qashqadaryo viloyati", "Surxondaryo viloyati", "Jizzax viloyati", "Sirdaryo viloyati", "Navoiy viloyati", "Xorazm viloyati", "Qoraqalpog'iston Respublikasi"]
    categories = ["IT va Dasturlash", "Savdo va Menedjment", "Ofis va Buxgalteriya", "Ta'lim va Fan", "Qurilish va Ishlab chiqarish", "Transport va Logistika", "Boshqa"]

    return render_template('index.html', jobs=jobs, regions=regions, categories=categories)

@app.route('/add-job', methods=['GET', 'POST'])
def add_job():
    regions = ["Toshkent shahri", "Farg'ona viloyati", "Andijon viloyati", "Namangan viloyati", "Samarqand viloyati", "Buxoro viloyati", "Qashqadaryo viloyati", "Surxondaryo viloyati", "Jizzax viloyati", "Sirdaryo viloyati", "Navoiy viloyati", "Xorazm viloyati", "Qoraqalpog'iston Respublikasi"]
    categories = ["IT va Dasturlash", "Savdo va Menedjment", "Ofis va Buxgalteriya", "Ta'lim va Fan", "Qurilish va Ishlab chiqarish", "Transport va Logistika", "Boshqa"]
    
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        category = request.form.get('category')
        region = request.form.get('region')
        job_type = request.form.get('job_type')
        salary = request.form.get('salary')
        experience = request.form.get('experience')
        description = request.form.get('description')
        phone = request.form.get('phone')
        telegram = request.form.get('telegram')
        
        file = request.files.get('receipt')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_job = Job(
                title=title, company=company, category=category, region=region,
                job_type=job_type, salary=salary, experience=experience,
                description=description, phone=phone, telegram=telegram,
                receipt=filename, status='pending'
            )
            db.session.add(new_job)
            db.session.commit()
            
            flash("E'loningiz muvaffaqiyatli yuborildi! Adminlar tekshiruvidan so'ng saytda e'lon qilinadi.", "success")
            return redirect(url_for('index'))
        else:
            flash("Iltimos, to'lov cheki skrinshotini yuklang!", "danger")
            
    return render_template('add_job.html', regions=regions, categories=categories)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == app.config['ADMIN_PASSWORD']:
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("Parol noto'g'ri!", "danger")
    return render_template('admin_login.html')

@app.route('/admin-panel')
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    jobs = Job.query.order_by(Job.id.desc()).all()
    return render_template('admin_panel.html', jobs=jobs)

@app.route('/admin/approve/<int:job_id>')
def approve_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    job = Job.query.get_or_404(job_id)
    job.status = 'active'
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<int:job_id>')
def delete_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
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
