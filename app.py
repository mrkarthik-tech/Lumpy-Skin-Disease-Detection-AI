"""
Lumpy Skin Disease Detection AI
Flask Backend — Main Application
PengwinTech Solutions | Academic Project 2026
"""

import os
import uuid
from datetime import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, jsonify, send_file, abort)
from werkzeug.utils import secure_filename

import database as db
import model as ai

# ── App Setup ─────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR  = os.path.join(BASE_DIR, 'static', 'uploads')
REPORT_DIR  = os.path.join(BASE_DIR, 'static', 'reports')
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

app = Flask(__name__)
app.secret_key = 'lsd-ai-secret-2026-pengwintech'
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def generate_animal_id():
    return f"CAT-{datetime.now().strftime('%y%m%d')}-{str(uuid.uuid4())[:4].upper()}"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    stats = db.get_dashboard_stats()
    return render_template('index.html', stats=stats)


@app.route('/about')
def about():
    return render_template('about.html')


# ── Detection Module ──────────────────────────────────────────────────────────

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if request.method == 'GET':
        return render_template('detect.html')

    if 'image' not in request.files:
        flash('No image file selected.', 'danger')
        return redirect(request.url)

    file = request.files['image']
    if file.filename == '':
        flash('No file chosen.', 'danger')
        return redirect(request.url)

    if not allowed_file(file.filename):
        flash('Invalid file type. Upload PNG, JPG, JPEG, WEBP, or BMP.', 'danger')
        return redirect(request.url)

    # Save uploaded file
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex[:10]}_{secure_filename(file.filename)}"
    save_path = os.path.join(UPLOAD_DIR, unique_name)
    file.save(save_path)

    # Run AI prediction
    prediction = ai.predict(save_path)

    # Generate animal ID (user can override)
    animal_id = request.form.get('animal_id', '').strip() or generate_animal_id()

    # Persist to DB
    detection_id = db.insert_detection(
        animal_id   = animal_id,
        image_name  = unique_name,
        image_path  = save_path,
        result      = prediction['result'],
        confidence  = prediction['confidence'],
        lesion_count= prediction['lesion_count'],
        severity    = prediction['severity'],
        notes       = request.form.get('notes', '')
    )

    return redirect(url_for('result', detection_id=detection_id))


@app.route('/result/<int:detection_id>')
def result(detection_id):
    record = db.get_detection_by_id(detection_id)
    if not record:
        abort(404)
    return render_template('result.html', record=record)


# ── Report Module ─────────────────────────────────────────────────────────────

@app.route('/report/<int:detection_id>')
def report(detection_id):
    record = db.get_detection_by_id(detection_id)
    if not record:
        abort(404)
    return render_template('report.html', record=record,
                           generated_at=datetime.now().strftime('%d %B %Y, %H:%M:%S'))


@app.route('/report/download/<int:detection_id>')
def download_report(detection_id):
    """Generate and stream an HTML report as a downloadable file."""
    record = db.get_detection_by_id(detection_id)
    if not record:
        abort(404)

    html_content = render_template('report_print.html', record=record,
                                   generated_at=datetime.now().strftime('%d %B %Y, %H:%M:%S'))

    report_filename = f"LSD_Report_{record['animal_id']}_{detection_id}.html"
    report_path = os.path.join(REPORT_DIR, report_filename)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    db.insert_report(detection_id, record['animal_id'], report_filename)

    return send_file(report_path, as_attachment=True,
                     download_name=report_filename, mimetype='text/html')


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    stats = db.get_dashboard_stats()
    recent = db.get_all_detections()[:10]
    return render_template('dashboard.html', stats=stats, recent=recent)


@app.route('/api/stats')
def api_stats():
    """JSON endpoint for chart data."""
    return jsonify(db.get_dashboard_stats())


# ── Admin Panel ───────────────────────────────────────────────────────────────

@app.route('/admin')
def admin():
    search = request.args.get('q', '')
    records = db.get_all_detections(search=search)
    stats = db.get_dashboard_stats()
    return render_template('admin.html', records=records, search=search, stats=stats)


@app.route('/admin/delete/<int:detection_id>', methods=['POST'])
def admin_delete(detection_id):
    record = db.get_detection_by_id(detection_id)
    if record:
        # Optionally remove image files
        try:
            if os.path.exists(record['image_path']):
                os.remove(record['image_path'])
            ann_path = os.path.join(UPLOAD_DIR, f"annotated_{record['image_name']}")
            if os.path.exists(ann_path):
                os.remove(ann_path)
        except Exception:
            pass
        db.delete_detection(detection_id)
        flash(f"Record #{detection_id} deleted.", 'success')
    return redirect(url_for('admin'))


@app.route('/admin/view/<int:detection_id>')
def admin_view(detection_id):
    return redirect(url_for('result', detection_id=detection_id))


# ── Error Handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16 MB.', 'danger')
    return redirect(url_for('detect'))


# ── Startup ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    db.init_db()
    ai.load_model()
    app.run(debug=True, host='0.0.0.0', port=5000)
