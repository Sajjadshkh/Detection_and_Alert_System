import sqlite3
import sys, os

DATABASE_PATH = os.path.join(os.getcwd(), "alerts.db")

def create_table():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # table for telegram
    c.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'pending', -- وضعیت: pending یا sent
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # table for email
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            status TEXT DEFAULT 'pending', -- وضعیت: pending یا sent
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # table for sms
    c.execute('''
        CREATE TABLE IF NOT EXISTS sms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'pending', -- وضعیت: pending یا sent
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# telegram methodes
def save_telegram(message):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO alerts (message, status) VALUES (?, 'pending')
    ''', (message,))
    conn.commit()
    conn.close()

def get_pending_telegram():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT id, message FROM alerts WHERE status = "pending"')
    alerts = c.fetchall()
    conn.close()
    return alerts

def mark_telegram_as_sent(alert_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE alerts SET status = "sent" WHERE id = ?
    ''', (alert_id,))
    conn.commit()
    conn.close()


# email methodes
def save_email(subject, body):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO emails (subject, body, status) VALUES (?, ?, 'pending')
    ''', (subject, body))
    conn.commit()
    conn.close()

def get_pending_emails():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT id, subject, body FROM emails WHERE status = "pending"')
    emails = c.fetchall()
    conn.close()
    return emails

def mark_email_as_sent(email_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE emails SET status = "sent" WHERE id = ?
    ''', (email_id,))
    conn.commit()
    conn.close()


# sms methodes
def save_sms(message):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO sms (message, status) VALUES (?, 'pending')
    ''', (message,))
    conn.commit()
    conn.close()

def get_pending_sms():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT id, message FROM sms WHERE status = "pending"')
    sms_list = c.fetchall()
    conn.close()
    return sms_list

def mark_sms_as_sent(sms_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE sms SET status = "sent" WHERE id = ?
    ''', (sms_id,))
    conn.commit()
    conn.close()