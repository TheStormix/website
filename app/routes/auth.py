from flask import Blueprint, render_template, request, redirect, session, flash, url_for,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import string
from flask_mail import Message
from app import mail

bp = Blueprint('auth', __name__)

def send_confirmation_email(email, code):
    subject = "Код підтвердження реєстрації"
    body = f"Ваш код підтвердження: {code}"

    msg = Message(subject=subject, recipients=[email], body=body)
    mail.send(msg)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # 🔥 Перевірка чи email вже існує
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email=?', (email,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            flash("Користувач із таким email вже зареєстрований.", "error")
            return redirect(url_for('auth.register'))

        # Зберігаємо тимчасово дані в сесії
        session['temp_username'] = username
        session['temp_email'] = email
        session['temp_password'] = password

        # Генеруємо код підтвердження
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        session['confirmation_code'] = code

        # Відправляємо код на email
        try:
            send_confirmation_email(email, code)
        except Exception as e:
            flash("Не вдалося надіслати email з кодом. Спробуйте пізніше.", "error")
            return redirect(url_for('auth.register'))

        flash("На вашу пошту надіслано код підтвердження.", "info")
        return redirect(url_for('auth.confirm_code'))

    return render_template('register.html')


@bp.route('/confirm_code', methods=['GET', 'POST'])
def confirm_code():
    if request.method == 'POST':
        entered_code = request.form.get('code')

        if entered_code == session.get('confirmation_code'):
            username = session.pop('temp_username', None)
            email = session.pop('temp_email', None)
            password = session.pop('temp_password', None)

            if not all([username, email, password]):
                flash("Сталася помилка. Будь ласка, зареєструйтесь знову.", "error")
                return redirect(url_for('auth.register'))

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                               (username, email, password))
                conn.commit()
                user_id = cursor.lastrowid
            except sqlite3.IntegrityError:
                conn.close()
                flash("Користувач з таким email вже існує", "error")
                return redirect(url_for('auth.register'))
            conn.close()

            session['user_id'] = user_id
            session['username'] = username

            flash("Реєстрація успішна!", "success")
            return redirect(url_for('user.profile'))
        else:
            flash("Невірний код підтвердження. Спробуйте ще раз.", "error")
            return redirect(url_for('auth.confirm_code'))

    return render_template('confirm_code.html')

@bp.route('/resend_code', methods=['POST'])
def resend_code():
    email = session.get('temp_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Неможливо надіслати код. Спробуйте зареєструватися знову.'}), 400

    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    session['confirmation_code'] = code

    try:
        send_confirmation_email(email, code)
        return jsonify({'status': 'success', 'message': 'Код підтвердження надіслано повторно.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Не вдалося повторно надіслати код. Спробуйте пізніше.'}), 500


@bp.route('/user-login', methods=['GET', 'POST'])
def user_login():
    next_page = request.args.get('next')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        next_page = request.form.get('next')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password FROM users WHERE email=?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]

            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('user.profile'))
        else:
            flash("Невірний email або пароль", "error")
            return redirect(url_for('auth.user_login', next=next_page))

    return render_template('user_login.html', next=next_page)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email=?', (email,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            flash("Користувача з таким email не знайдено.", "error")
            return redirect(url_for('auth.forgot_password'))

        # Генеруємо новий пароль
        new_password = ''.join(random.choices(string.ascii_letters, k=8))
        hashed_password = generate_password_hash(new_password)

        # Оновлення в базі
        cursor.execute('UPDATE users SET password=? WHERE email=?', (hashed_password, email))
        conn.commit()
        conn.close()

        # Надсилаємо новий пароль
        try:
            send_new_password(email, new_password)
            flash("Новий пароль надіслано на вашу пошту.", "success")
        except Exception:
            flash("Не вдалося надіслати email. Спробуйте пізніше.", "error")

        return redirect(url_for('auth.user_login'))

    return render_template('forgot_password.html')

def send_new_password(email, new_password):
    subject = "Ваш новий пароль"
    body = f"Ваш новий пароль: {new_password}\n\nРекомендуємо змінити його після входу в особистому кабінеті."

    msg = Message(subject=subject, recipients=[email], body=body)
    mail.send(msg)
