from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                           (username, email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("Користувач з таким email вже існує", "error")
            return redirect(url_for('auth.register'))
        conn.close()
        return redirect(url_for('auth.user_login'))
    
    return render_template('register.html')

@bp.route('/user-login', methods=['GET', 'POST'])
def user_login():
    next_page = request.args.get('next')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        next_page = request.form.get('next')  # Щоб витягнути next після POST

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
