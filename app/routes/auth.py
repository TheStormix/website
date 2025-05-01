from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import string
from flask_mail import Message
from app import mail
from app.utils.i18n import load_translations

bp = Blueprint('auth', __name__)

def send_confirmation_email(email, code, t):
    subject = t['auth'].get("email_subject_confirm", "Confirmation code")
    body = f"{t['auth'].get('email_code_body', 'Your confirmation code is')}: {code}"
    msg = Message(subject=subject, recipients=[email], body=body)
    mail.send(msg)

def send_new_password(email, new_password, t):
    subject = t['auth'].get("email_subject_new_password", "Your new password")
    body = f"{t['auth'].get('email_new_password_body', 'Your new password is')}: {new_password}\n\n{t['auth'].get('email_new_password_note', 'Please change it after login.')}"
    msg = Message(subject=subject, recipients=[email], body=body)
    mail.send(msg)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    lang = session.get('lang', 'uk')
    t = load_translations(lang)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email=?', (email,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            flash(t["auth"]["email_exists"], "error")
            return redirect(url_for('auth.register'))

        session['temp_username'] = username
        session['temp_email'] = email
        session['temp_password'] = password

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        session['confirmation_code'] = code

        try:
            send_confirmation_email(email, code, t)
        except Exception:
            flash(t["auth"]["email_send_failed"], "error")
            return redirect(url_for('auth.register'))

        flash(t["auth"]["email_sent"], "info")
        return redirect(url_for('auth.confirm_code'))

    return render_template('register.html', t=t)

@bp.route('/confirm_code', methods=['GET', 'POST'])
def confirm_code():
    lang = session.get('lang', 'uk')
    t = load_translations(lang)

    if request.method == 'POST':
        entered_code = request.form.get('code')

        if entered_code == session.get('confirmation_code'):
            username = session.pop('temp_username', None)
            email = session.pop('temp_email', None)
            password = session.pop('temp_password', None)

            if not all([username, email, password]):
                flash(t["auth"]["registration_error"], "error")
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
                flash(t["auth"]["email_exists"], "error")
                return redirect(url_for('auth.register'))
            conn.close()

            session['user_id'] = user_id
            session['username'] = username

            flash(t["auth"]["registration_success"], "success")
            return redirect(url_for('user.profile'))
        else:
            flash(t["auth"]["invalid_code"], "error")
            return redirect(url_for('auth.confirm_code'))

    return render_template('confirm_code.html', t=t)

@bp.route('/resend_code', methods=['POST'])
def resend_code():
    lang = session.get('lang', 'uk')
    t = load_translations(lang)

    email = session.get('temp_email')
    if not email:
        return jsonify({'status': 'error', 'message': t["auth"]["resend_fail"]}), 400

    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    session['confirmation_code'] = code

    try:
        send_confirmation_email(email, code, t)
        return jsonify({'status': 'success', 'message': t["auth"]["resend_success"]})
    except Exception:
        return jsonify({'status': 'error', 'message': t["auth"]["resend_fail_retry"]}), 500

@bp.route('/user-login', methods=['GET', 'POST'])
def user_login():
    lang = session.get('lang', 'uk')
    t = load_translations(lang)
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
            flash(t["auth"]["login_error"], "error")
            return redirect(url_for('auth.user_login', next=next_page))

    return render_template('user_login.html', next=next_page, t=t)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    lang = session.get('lang', 'uk')
    t = load_translations(lang)

    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email=?', (email,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            flash(t["auth"]["email_not_found"], "error")
            return redirect(url_for('auth.forgot_password'))

        new_password = ''.join(random.choices(string.ascii_letters, k=8))
        hashed_password = generate_password_hash(new_password)

        cursor.execute('UPDATE users SET password=? WHERE email=?', (hashed_password, email))
        conn.commit()
        conn.close()

        try:
            send_new_password(email, new_password, t)
            flash(t["auth"]["new_password_sent"], "success")
        except Exception:
            flash(t["auth"]["email_send_failed"], "error")

        return redirect(url_for('auth.user_login'))

    return render_template('forgot_password.html', t=t)
