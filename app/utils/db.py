import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # таблиця користувачів з полем birthdate
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            birthdate TEXT
        )
    ''')

    # таблиця заявок з полями status та rating
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            description TEXT,
            complexity TEXT,
            estimated_time TEXT,
            estimated_cost REAL,
            meeting_date TEXT,
            status TEXT DEFAULT 'в очікуванні дзвінка',
            rating INTEGER DEFAULT NULL
        )
    ''')

    # Якщо таблиця вже існувала без стовпчиків status або rating — додаємо їх разово
    try:
        cursor.execute(
            "ALTER TABLE requests ADD COLUMN status TEXT DEFAULT 'в очікуванні дзвінка'"
        )
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute(
            "ALTER TABLE requests ADD COLUMN rating INTEGER DEFAULT NULL"
        )
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
