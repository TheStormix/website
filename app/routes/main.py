from flask import Blueprint, render_template, request, redirect, session, send_from_directory
from datetime import datetime, timedelta
import sqlite3
from flask_mail import Message
from app import mail
import os
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

# Дозволені розширення файлів
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/request', methods=['GET', 'POST'])
def request_form():
    user_name = ""
    user_email = ""

    # Якщо користувач залогінений, витягуємо його дані
    if 'user_id' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username, email FROM users WHERE id=?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        if user:
            user_name = user[0]
            user_email = user[1]

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        description = request.form['description']
        complexity = request.form['complexity']

        # Розрахунок часу і вартості
        if complexity == 'low':
            estimated_time = '1-2 дні'
            estimated_cost = 100
        elif complexity == 'medium':
            estimated_time = '3-5 днів'
            estimated_cost = 300
        else:
            estimated_time = '7+ днів'
            estimated_cost = 600

        meeting_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")

        # Завантаження файлу
        uploaded_file = request.files.get('file_upload')
        file_path = None

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            uploads_dir = os.path.join('static', 'uploads')  # тепер uploads/ просто в корені
            os.makedirs(uploads_dir, exist_ok=True)
            saved_path = os.path.join(uploads_dir, filename)
            uploaded_file.save(saved_path)
            file_path = filename  # тільки ім'я файлу у базу

        # Збереження в базу
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (name, email, description, complexity, estimated_time, estimated_cost, meeting_date, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, description, complexity, estimated_time, estimated_cost, meeting_date, file_path))
        conn.commit()
        conn.close()

        # Відправка листа
        try:
            msg = Message(
                "Підтвердження заявки",
                sender=os.getenv('MAIL_DEFAULT_SENDER'),
                recipients=[email]
            )
            msg.body = f"""
Дякуємо, {name}!

Ваша заявка успішно прийнята. Очікуйте дзвінок від представника {meeting_date}.

🛠️ Складність: {complexity}
⏱️ Орієнтовна тривалість: {estimated_time}
💰 Орієнтовна вартість: {estimated_cost} грн

З повагою,
IT-компанія
"""
            mail.send(msg)
        except Exception as e:
            print("Помилка надсилання email:", e)

        return render_template(
            'confirmation.html',
            name=name,
            estimated_time=estimated_time,
            estimated_cost=estimated_cost,
            meeting_date=meeting_date,
            complexity=complexity
        )

    return render_template('request.html', user_name=user_name, user_email=user_email)

# ➡️ Додаємо новий маршрут для скачування файлу
@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join('static', 'uploads'), filename, as_attachment=True)
