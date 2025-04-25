from flask import Blueprint, render_template, request, redirect, session, flash
import sqlite3

bp = Blueprint('admin', __name__)

@bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect('/admin')
        else:
            flash('Неправильний логін або пароль.')
            return redirect('/admin-login')
    return render_template('admin_login.html')

@bp.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect('/admin-login')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests")
    requests_data = cursor.fetchall()
    conn.close()
    return render_template('admin.html', requests=requests_data)

@bp.route('/delete/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    if not session.get('admin'):
        return redirect('/admin-login')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM requests WHERE id=?", (request_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@bp.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin-login')

