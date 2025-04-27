from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import sqlite3

bp = Blueprint('admin', __name__)

@bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin.admin_panel'))
        else:
            flash('Неправильний логін або пароль.', 'error')
            return redirect(url_for('admin.admin_login'))
    return render_template('admin_login.html')

@bp.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Вибірка всіх полів, включаючи status
    cursor.execute(
        "SELECT id, name, email, description, complexity, estimated_time, estimated_cost, meeting_date, status FROM requests"
    )
    requests_data = cursor.fetchall()
    conn.close()
    return render_template('admin.html', requests=requests_data)

@bp.route('/request/<int:request_id>/status', methods=['POST'])
def change_status(request_id):
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))
    new_status = request.form.get('status')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE requests SET status=? WHERE id=?",
        (new_status, request_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin_panel'))

@bp.route('/delete/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    if not session.get('admin'):
        return redirect(url_for('admin.admin_login'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM requests WHERE id=?", (request_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin_panel'))

@bp.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin.admin_login'))
