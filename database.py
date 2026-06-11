"""
Database Module - Lumpy Skin Disease Detection AI
Handles SQLite database initialization and queries
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'lsd_detection.db')


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with all required tables"""
    conn = get_db()
    cursor = conn.cursor()

    # Detections table - stores every image scan
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id   TEXT NOT NULL,
            image_name  TEXT NOT NULL,
            image_path  TEXT NOT NULL,
            result      TEXT NOT NULL,          -- 'Positive' | 'Healthy' | 'Uncertain'
            confidence  REAL NOT NULL,
            lesion_count INTEGER DEFAULT 0,
            severity    TEXT DEFAULT 'None',    -- None | Mild | Moderate | Severe
            notes       TEXT,
            created_at  TEXT NOT NULL
        )
    ''')

    # Reports table - stores generated PDF/HTML reports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_id    INTEGER NOT NULL,
            animal_id       TEXT NOT NULL,
            report_filename TEXT NOT NULL,
            created_at      TEXT NOT NULL,
            FOREIGN KEY (detection_id) REFERENCES detections(id)
        )
    ''')

    # Dashboard stats cache (refreshed on demand)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL UNIQUE,
            total       INTEGER DEFAULT 0,
            positive    INTEGER DEFAULT 0,
            healthy     INTEGER DEFAULT 0,
            uncertain   INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


# ── CRUD helpers ──────────────────────────────────────────────────────────────

def insert_detection(animal_id, image_name, image_path, result,
                     confidence, lesion_count=0, severity='None', notes=''):
    conn = get_db()
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO detections
            (animal_id, image_name, image_path, result, confidence,
             lesion_count, severity, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (animal_id, image_name, image_path, result, confidence,
          lesion_count, severity, notes, created_at))
    detection_id = cursor.lastrowid
    conn.commit()
    conn.close()
    _update_daily_stats(result)
    return detection_id


def insert_report(detection_id, animal_id, report_filename):
    conn = get_db()
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO reports (detection_id, animal_id, report_filename, created_at)
        VALUES (?, ?, ?, ?)
    ''', (detection_id, animal_id, report_filename, created_at))
    conn.commit()
    conn.close()


def get_all_detections(search=''):
    conn = get_db()
    cursor = conn.cursor()
    if search:
        cursor.execute('''
            SELECT * FROM detections
            WHERE animal_id LIKE ? OR result LIKE ? OR image_name LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        cursor.execute('SELECT * FROM detections ORDER BY created_at DESC')
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_detection_by_id(detection_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM detections WHERE id = ?', (detection_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_detection(detection_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM detections WHERE id = ?', (detection_id,))
    cursor.execute('DELETE FROM reports WHERE detection_id = ?', (detection_id,))
    conn.commit()
    conn.close()


def get_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM detections')
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as cnt FROM detections WHERE result='Positive'")
    positive = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM detections WHERE result='Healthy'")
    healthy = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM detections WHERE result='Uncertain'")
    uncertain = cursor.fetchone()['cnt']

    # Last 7 days trend
    cursor.execute('''
        SELECT DATE(created_at) as day, COUNT(*) as cnt,
               SUM(CASE WHEN result='Positive' THEN 1 ELSE 0 END) as pos
        FROM detections
        GROUP BY DATE(created_at)
        ORDER BY day DESC LIMIT 7
    ''')
    trend = [dict(r) for r in cursor.fetchall()]

    # Severity breakdown
    cursor.execute('''
        SELECT severity, COUNT(*) as cnt FROM detections GROUP BY severity
    ''')
    severity = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        'total': total,
        'positive': positive,
        'healthy': healthy,
        'uncertain': uncertain,
        'detection_rate': round((positive / total * 100) if total > 0 else 0, 1),
        'trend': trend,
        'severity': severity
    }


def _update_daily_stats(result):
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('INSERT OR IGNORE INTO daily_stats (date) VALUES (?)', (today,))
    cursor.execute('UPDATE daily_stats SET total = total + 1 WHERE date = ?', (today,))
    if result == 'Positive':
        cursor.execute('UPDATE daily_stats SET positive = positive + 1 WHERE date = ?', (today,))
    elif result == 'Healthy':
        cursor.execute('UPDATE daily_stats SET healthy = healthy + 1 WHERE date = ?', (today,))
    else:
        cursor.execute('UPDATE daily_stats SET uncertain = uncertain + 1 WHERE date = ?', (today,))
    conn.commit()
    conn.close()
