from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import sqlite3
from app.utils.i18n import load_translations
from datetime import datetime
import pytz
import os

bp = Blueprint('admin', __name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    lang = session.get('lang', 'uk')
    t = load_translations(lang)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        env_username = os.environ.get('ADMIN_USERNAME')
        env_password = os.environ.get('ADMIN_PASSWORD')

        if username == env_username and password == env_password:
            session['admin'] = True
            return redirect(url_for('admin.admin_panel'))

        flash(t['admin'].get('invalid_login', 'Неправильний логін або пароль.'), 'error')
        return redirect(url_for('admin.admin_login'))

    return render_template('admin_login.html', t=t)

@bp.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))

    lang = session.get('lang', 'uk')
    t = load_translations(lang)

    conn = get_db_connection()

    # Отримуємо всі заявки
    reqs = conn.execute('''
        SELECT id, name, email, description,
               complexity, estimated_time, estimated_cost, meeting_date,
               status, COALESCE(rating, 0) AS rating,
               file_path
        FROM requests
        ORDER BY id DESC
    ''').fetchall()

    # === Автоматичне оновлення статусу ===
    now = datetime.now()
    for req in reqs:
        try:
            meeting_dt = datetime.strptime(req['meeting_date'], "%d.%m.%Y %H:%M")
        except ValueError:
            continue  # пропускаємо заявки без часу

        if req['status'] == 'в очікуванні дзвінка' and meeting_dt < now:
            conn.execute('UPDATE requests SET status = ? WHERE id = ?', ('в роботі', req['id']))
    conn.commit()

    # Повторно отримуємо вже оновлені заявки
    reqs = conn.execute('''
        SELECT id, name, email, description,
               complexity, estimated_time, estimated_cost, meeting_date,
               status, COALESCE(rating, 0) AS rating,
               file_path
        FROM requests
        ORDER BY id DESC
    ''').fetchall()

    users = conn.execute('''
        SELECT
            name,
            email,
            COUNT(*) AS total_requests,
            ROUND(AVG(COALESCE(rating,0)),2) AS avg_rating
        FROM requests
        GROUP BY email, name
        ORDER BY total_requests DESC, avg_rating DESC
    ''').fetchall()

    stats_raw = conn.execute('''
        SELECT product_type, COUNT(*) as count
        FROM requests
        GROUP BY product_type
    ''').fetchall()

    complexity_raw = conn.execute('''
        SELECT complexity, COUNT(*) as count
        FROM requests
        GROUP BY complexity
    ''').fetchall()

    conn.close()

    stats = [dict(row) for row in stats_raw]
    complexity_stats = [dict(row) for row in complexity_raw]

    return render_template(
        'admin.html',
        t=t,
        requests=reqs,
        users=users,
        stats=stats,
        complexity_stats=complexity_stats
    )

@bp.route('/request/<int:request_id>/status', methods=['POST'])
def change_status(request_id):
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))

    lang = session.get('lang', 'uk')
    t = load_translations(lang)

    new_status = request.form.get('status')
    conn = get_db_connection()
    conn.execute('UPDATE requests SET status = ? WHERE id = ?', (new_status, request_id))
    conn.commit()
    conn.close()
    flash(t['admin'].get('status_changed', 'Статус заявки змінено на').replace('{id}', str(request_id)).replace('{status}', new_status), 'success')
    return redirect(url_for('admin.admin_panel'))

@bp.route('/request/<int:request_id>/complete', methods=['POST'])
def complete_request(request_id):
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))

    lang = session.get('lang', 'uk')
    t = load_translations(lang)

    try:
        rating = int(request.form.get('rating'))
        if rating < 1 or rating > 5:
            raise ValueError
    except:
        flash(t['admin'].get('invalid_rating', 'Невірний рейтинг. Виберіть 1–5 зірок.'), 'error')
        return redirect(url_for('admin.admin_panel'))

    conn = get_db_connection()
    conn.execute('''
        UPDATE requests
           SET status = 'виконано',
               rating = ?
         WHERE id = ?
    ''', (rating, request_id))
    conn.commit()
    conn.close()
    flash(t['admin'].get('request_completed', 'Заявка виконана, рейтинг клієнту: {rating}★.').replace('{id}', str(request_id)).replace('{rating}', str(rating)), 'success')
    return redirect(url_for('admin.admin_panel'))

@bp.route('/delete/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))

    lang = session.get('lang', 'uk')
    t = load_translations(lang)

    conn = get_db_connection()
    conn.execute('DELETE FROM requests WHERE id = ?', (request_id,))
    conn.commit()
    conn.close()
    flash(t['admin'].get('request_deleted', 'Заявку {id} видалено.').replace('{id}', str(request_id)), 'success')
    return redirect(url_for('admin.admin_panel'))

@bp.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin.admin_login'))
