from flask import Blueprint, render_template, session, redirect, request, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

bp = Blueprint('user', __name__)

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.user_login', next=url_for('main.request_form')))

    user_id = session['user_id']
    username = session['username']
    email, birthdate, current_hashed_password = get_user_info(user_id)

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        new_birthdate = request.form.get('birthdate')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Перевірка зміни пароля
        if old_password or new_password or confirm_password:
            if not old_password or not new_password or not confirm_password:
                flash("⚠️ Заповніть усі поля для зміни пароля.", "error")
                return redirect(url_for('user.profile'))

            if not check_password_hash(current_hashed_password, old_password):
                flash("❌ Старий пароль введено неправильно.", "error")
                return redirect(url_for('user.profile'))

            if new_password == old_password:
                flash("❌ Новий пароль не повинен збігатися зі старим.", "error")
                return redirect(url_for('user.profile'))

            if new_password != confirm_password:
                flash("❌ Новий пароль і підтвердження не збігаються.", "error")
                return redirect(url_for('user.profile'))

            hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password=? WHERE id=?", (hashed_password, user_id))
            flash("✅ Пароль успішно змінено!", "success")

        # Перевірка зміни дати народження
        if new_birthdate:
            cursor.execute("UPDATE users SET birthdate=? WHERE id=?", (new_birthdate, user_id))
            flash("✅ Дату народження оновлено!", "success")

        conn.commit()
        conn.close()
        return redirect(url_for('user.profile'))

    # Отримання заявок користувача
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT description, complexity, estimated_time, estimated_cost, meeting_date, status "
        "FROM requests WHERE email=?",
        (email,)
    )
    user_requests = cursor.fetchall()
    conn.close()

    # ➡️ Підрахунок заявок:
    total_requests = len(user_requests)
    active_requests = sum(1 for r in user_requests if r[5] != 'виконано')

    return render_template(
        'profile.html',
        username=username,
        email=email,
        birthdate=birthdate,
        requests=user_requests,
        active_requests=active_requests,
        total_requests=total_requests
    )

def get_user_info(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email, birthdate, password FROM users WHERE id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0], result[1], result[2]  # email, birthdate, password
    return None, None, None
