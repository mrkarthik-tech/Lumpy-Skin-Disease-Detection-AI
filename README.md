# 🐄 Lumpy Skin Disease Detection AI

**AI-Powered Cattle Health Screening Platform**  
PengwinTech Solutions · Final Year B.E. Computer Science · February 2026

---

## 📋 Project Overview

A web-based computer vision application that analyses cattle images and identifies visible signs of **Lumpy Skin Disease (LSD)** using a trained **YOLOv8** object detection model. Built for educational and research purposes only.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js |
| Backend | Python 3.11, Flask 3.x |
| AI / ML | YOLOv8 (Ultralytics), PyTorch, OpenCV, NumPy, Pandas |
| Database | SQLite 3 |
| Deployment | Render.com / Localhost |

---

## 📁 Project Structure

```
lumpy_disease_ai/
│
├── app.py                  # Flask application (routes & controllers)
├── database.py             # SQLite database module (CRUD helpers)
├── model.py                # YOLOv8 inference engine
├── requirements.txt        # Python dependencies
├── render.yaml             # Render.com deployment config
│
├── models/
│   └── lsd_yolov8.pt       # ← Place your trained YOLOv8 model here
│
├── static/
│   ├── css/
│   │   └── main.css        # Main stylesheet
│   ├── js/
│   │   └── main.js         # Frontend JavaScript
│   ├── uploads/            # Uploaded & annotated images (auto-created)
│   └── reports/            # Downloaded HTML reports (auto-created)
│
└── templates/
    ├── base.html           # Shared navigation & footer layout
    ├── index.html          # Home page
    ├── about.html          # Project info & tech explanation
    ├── detect.html         # Image upload & detection form
    ├── result.html         # Detection result viewer
    ├── report.html         # Formatted report viewer
    ├── report_print.html   # Downloadable standalone report
    ├── dashboard.html      # Analytics dashboard with charts
    ├── admin.html          # Admin panel (all records)
    └── 404.html            # Error page
```

---

## ⚙️ Setup Instructions

### 1. Clone / Download the Project

```bash
git clone https://github.com/your-repo/lumpy-disease-ai.git
cd lumpy_disease_ai
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** PyTorch installation varies by platform. If the above fails, install PyTorch separately first:
> ```bash
> # CPU only (lighter, works on all platforms)
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
> pip install -r requirements.txt
> ```

### 4. Add Your YOLOv8 Model (Optional)

Place your trained model file at:
```
models/lsd_yolov8.pt
```

If no custom model is present, the app automatically runs in **DEMO mode** — simulating realistic predictions for UI development and grading demonstrations.

### 5. Run the Application

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 🗄️ Database Schema

The SQLite database (`lsd_detection.db`) is auto-created on first run with three tables:

### `detections`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment record ID |
| animal_id | TEXT | User-provided or auto-generated tag |
| image_name | TEXT | Filename of uploaded image |
| image_path | TEXT | Full disk path of image |
| result | TEXT | Positive / Healthy / Uncertain |
| confidence | REAL | Model confidence (0.0–1.0) |
| lesion_count | INTEGER | Number of bounding boxes detected |
| severity | TEXT | None / Mild / Moderate / Severe |
| notes | TEXT | Optional field notes |
| created_at | TEXT | ISO datetime string |

### `reports`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| detection_id | INTEGER FK | References `detections.id` |
| animal_id | TEXT | Denormalised for quick lookup |
| report_filename | TEXT | Downloaded HTML filename |
| created_at | TEXT | Generation timestamp |

### `daily_stats`
| Column | Type | Description |
|--------|------|-------------|
| date | TEXT UNIQUE | YYYY-MM-DD date key |
| total | INTEGER | Total scans that day |
| positive / healthy / uncertain | INTEGER | Counts per result |

---

## 🚀 Deployment on Render.com

1. Push project to a GitHub repository.
2. Log in to [render.com](https://render.com) → **New Web Service**.
3. Connect your GitHub repo.
4. Render detects `render.yaml` automatically.
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
7. Deploy — your app will be live at `https://your-app.onrender.com`.

> **Important:** Render's free tier has ephemeral storage — uploaded images and the SQLite database are lost on redeploy. For persistent storage, mount a Render Disk or migrate to PostgreSQL.

---

## 🤖 Training Your Own YOLOv8 Model

```python
from ultralytics import YOLO

# Load base model
model = YOLO('yolov8n.pt')

# Train on your LSD dataset
model.train(
    data='lsd_dataset.yaml',   # Path to YOLO dataset config
    epochs=100,
    imgsz=640,
    batch=16,
    name='lsd_yolov8',
    project='runs/train'
)

# Export trained model
model.export(format='onnx')    # Optional: for production deployment
```

### Dataset YAML structure (`lsd_dataset.yaml`)
```yaml
path: ./dataset
train: images/train
val:   images/val
test:  images/test

nc: 2
names: ['healthy_skin', 'lsd_lesion']
```

---

## 📱 Modules & Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page with live stats |
| `/about` | GET | Project & technology explanation |
| `/detect` | GET/POST | Upload image & run AI detection |
| `/result/<id>` | GET | View detection result |
| `/report/<id>` | GET | View formatted report |
| `/report/download/<id>` | GET | Download HTML report |
| `/dashboard` | GET | Analytics charts & statistics |
| `/admin` | GET | All records + search |
| `/admin/delete/<id>` | POST | Delete a record |
| `/api/stats` | GET | JSON stats endpoint |

---

## ⚠️ Disclaimer

This system is built **for educational and research purposes only**.  
It is **not** a certified veterinary diagnostic tool.  
Always consult a licensed veterinarian before making treatment, quarantine, or regulatory reporting decisions.

---

*PengwinTech Solutions · Final Year Computer Science Engineering · February 2026*
