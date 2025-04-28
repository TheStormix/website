from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import sqlite3

bp = Blueprint('admin', __name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin.admin_panel'))
        flash('Неправильний логін або пароль.', 'error')
        return redirect(url_for('admin.admin_login'))
    return render_template('admin_login.html')

@bp.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))

    conn = get_db_connection()

    # 1) Всі заявки
    reqs = conn.execute('''
        SELECT id, name, email, description,
           complexity, estimated_time, estimated_cost, meeting_date,
           status, COALESCE(rating,0) AS rating,
           file_path
        FROM requests
        ORDER BY id DESC
    ''').fetchall()


    # 2) Унікальні "користувачі" з таблиці requests,
    #    з підрахунком кількості заявок і середнім рейтингом
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

    conn.close()
    return render_template('admin.html', requests=reqs, users=users)

@bp.route('/request/<int:request_id>/status', methods=['POST'])
def change_status(request_id):
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))

    new_status = request.form.get('status')
    conn = get_db_connection()
    conn.execute('UPDATE requests SET status = ? WHERE id = ?', (new_status, request_id))
    conn.commit()
    conn.close()
    flash(f'Статус заявки #{request_id} змінено на «{new_status}».', 'success')
    return redirect(url_for('admin.admin_panel'))

@bp.route('/request/<int:request_id>/complete', methods=['POST'])
def complete_request(request_id):
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))

    try:
        rating = int(request.form.get('rating'))
        if rating < 1 or rating > 5:
            raise ValueError
    except:
        flash('Невірний рейтинг. Виберіть 1–5 зірок.', 'error')
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
    flash(f'Заявка #{request_id} виконана, рейтинг клієнту: {rating}★.', 'success')
    return redirect(url_for('admin.admin_panel'))

@bp.route('/delete/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM requests WHERE id = ?', (request_id,))
    conn.commit()
    conn.close()
    flash(f'Заявку #{request_id} видалено.', 'success')
    return redirect(url_for('admin.admin_panel'))

@bp.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin.admin_login'))
