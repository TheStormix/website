from flask import Blueprint, render_template, request, redirect, session, send_from_directory, url_for
from datetime import datetime, timedelta
import sqlite3
from flask_mail import Message
from app import mail
import os
from werkzeug.utils import secure_filename
from app.utils.i18n import load_translations
import uuid
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pytz

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_event_to_calendar(name, email, description, datetime_str):
    print(f"📅 add_event_to_calendar called with: {name=}, {email=}, {datetime_str=}")

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = 'app/secrets/calendar.json'

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build('calendar', 'v3', credentials=credentials)

        calendar_id = 'paguta306@gmail.com'

        # Парсинг дати та часового поясу
        parsed_dt = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
        tz = pytz.timezone("Europe/Kyiv")
        start_dt = tz.localize(parsed_dt)
        end_dt = start_dt + timedelta(minutes=30)

        start = start_dt.isoformat()
        end = end_dt.isoformat()

        # Перевірка чи вже є подія на цей час
        existing = service.events().list(
            calendarId=calendar_id,
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        if existing.get("items"):
            print("❌ Час уже зайнятий. Подія не буде створена.")
            return False

        # Створення події
        event = {
            'summary': f"Дзвінок з {name}",
            'description': f"{description}\nEmail: {email}",
            'start': {'dateTime': start, 'timeZone': 'Europe/Kyiv'},
            'end': {'dateTime': end, 'timeZone': 'Europe/Kyiv'},
        }

        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print("✅ Подія створена:", created_event.get("htmlLink"))
        return True

    except Exception as e:
        print("❌ Calendar API error:", e)
        return False


@bp.route('/')
def home():
    lang = session.get('lang', 'uk')
    t = load_translations(lang)
    return render_template('index.html', t=t)

@bp.route('/request', methods=['GET', 'POST'])
def request_form():
    lang = session.get('lang', 'uk')
    t = load_translations(lang)
    rt = t.get('request', {})
    user_name = ""
    user_email = ""

    if 'user_id' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username, email FROM users WHERE id=?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        if user:
            user_name, user_email = user

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        product_type = request.form.get('product_type')
        description = request.form['description']
        contact_time = request.form.get('contact_time')

        # Обрати годину на основі вибору
        hour_map = {'morning': 10, 'day': 13, 'evening': 17}
        hour = hour_map.get(contact_time, 10)

        # Скласти повну дату і час
        meeting_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        full_datetime_str = f"{meeting_date} {hour:02d}:00"

        # Динамічний розрахунок вартості
        base_cost = 0
        if product_type == 'website':
            base_cost += 200
            site_type = request.form.get('site_type')
            pages = request.form.get('pages')
            if site_type == 'ecommerce':
                base_cost += 150
            elif site_type == 'corporate':
                base_cost += 100
            if pages == '3+':
                base_cost += 100
            if request.form.get('admin_panel') == '1':
                base_cost += 120
            if request.form.get('auth') == '1':
                base_cost += 80

        elif product_type == 'app':
            base_cost += 300
            platform = request.form.get('platform')
            if platform == 'both':
                base_cost += 200
            elif platform in ['android', 'ios']:
                base_cost += 100
            if request.form.get('login') == '1':
                base_cost += 100
            if request.form.get('user_profile') == '1':
                base_cost += 120

        elif product_type == 'bot':
            base_cost += 150
            bot_commands = request.form.get('bot_commands')
            if bot_commands == 'many':
                base_cost += 100
            if request.form.get('bot_database') == '1':
                base_cost += 120
            if request.form.get('bot_payments') == '1':
                base_cost += 150

        if base_cost < 300:
            complexity = 'low'
            estimated_time = rt.get('days_1_2', '1-2 days')
        elif base_cost < 600:
            complexity = 'medium'
            estimated_time = rt.get('days_3_5', '3-5 days')
        else:
            complexity = 'high'
            estimated_time = rt.get('days_7_plus', '7+ days')

        estimated_cost = base_cost
        file_path = None

        uploaded_file = request.files.get('file_upload')
        if uploaded_file and uploaded_file.filename and allowed_file(uploaded_file.filename):
            ext = uploaded_file.filename.rsplit('.', 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            uploads_dir = os.path.join(os.getcwd(), 'static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            saved_path = os.path.join(uploads_dir, unique_name)
            try:
                uploaded_file.save(saved_path)
                file_path = unique_name
            except Exception as e:
                print("❌ File save error:", e)

        # Додаємо подію в календар, якщо час вільний
        event_created = add_event_to_calendar(name, email, description, full_datetime_str)
        if not event_created:
            error = rt.get('time_taken_error', "The selected time is already taken. Please choose another slot.")
            return render_template('request.html', user_name=user_name, user_email=user_email, t=t, error=error)

        # Записуємо в базу
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (name, email, product_type, description, complexity, estimated_time, estimated_cost, meeting_date, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, product_type, description, complexity, estimated_time, estimated_cost, meeting_date, file_path))
        conn.commit()
        conn.close()

        # Надсилання email
        try:
            msg = Message(
                rt.get("email_subject", "Confirmation of request"),
                sender=os.getenv('MAIL_DEFAULT_SENDER'),
                recipients=[email]
            )
            msg.body = f"""
{rt.get("email_greeting", "Thank you")}, {name}!

{rt.get("email_confirmed", "Your request has been received successfully.")} 
{rt.get("email_call_expected", "Expect a call from our representative on")} {meeting_date} о {hour}:00.

🛠️ {rt.get("email_complexity", "Complexity")}: {complexity}
⏱️ {rt.get("email_time", "Estimated duration")}: {estimated_time}
💰 {rt.get("email_cost", "Estimated cost")}: {estimated_cost} usd

{rt.get("email_footer", "Best regards,\nIT Company")}
"""
            mail.send(msg)
        except Exception as e:
            print("Email send error:", e)

        return render_template(
            'confirmation.html',
            name=name,
            estimated_time=estimated_time,
            estimated_cost=estimated_cost,
            meeting_date=f"{meeting_date} о {hour}:00",
            complexity=complexity,
            t=t
        )

    return render_template('request.html', user_name=user_name, user_email=user_email, t=t)


@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join('static', 'uploads'), filename, as_attachment=True)

@bp.route('/switch-language', methods=['POST'])
def switch_language():
    lang = request.form.get('lang')
    if lang in ['uk', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.home'))
