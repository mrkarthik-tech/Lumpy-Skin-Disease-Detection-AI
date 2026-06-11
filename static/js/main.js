/* ═══════════════════════════════════════════════════════════════
   Lumpy Skin Disease Detection AI  —  Main JavaScript
   PengwinTech Solutions 2026
   ═══════════════════════════════════════════════════════════════ */

'use strict';

/* ── Image Upload / Preview ──────────────────────────────────── */
const uploadZone    = document.getElementById('uploadZone');
const fileInput     = document.getElementById('imageInput');
const previewWrap   = document.getElementById('previewWrap');
const previewImg    = document.getElementById('previewImg');
const previewBox    = document.getElementById('previewBox');
const uploadDefault = document.getElementById('uploadDefault');
const submitBtn     = document.getElementById('submitBtn');

function handleFile(file) {
  if (!file || !file.type.startsWith('image/')) {
    showToast('Please select a valid image file.', 'danger');
    return;
  }
  if (file.size > 16 * 1024 * 1024) {
    showToast('File too large. Max 16 MB.', 'danger');
    return;
  }
  const reader = new FileReader();
  reader.onload = (e) => {
    if (previewImg)    { previewImg.src = e.target.result; }
    if (previewBox)    { previewBox.classList.remove('d-none'); }
    if (uploadDefault) { uploadDefault.classList.add('d-none'); }
    if (submitBtn)     { submitBtn.removeAttribute('disabled'); }
  };
  reader.readAsDataURL(file);
}

if (uploadZone) {
  uploadZone.addEventListener('click', () => fileInput && fileInput.click());

  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
  });

  uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
  });

  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (fileInput) {
      const dt = new DataTransfer();
      dt.items.add(file);
      fileInput.files = dt.files;
    }
    handleFile(file);
  });
}

if (fileInput) {
  fileInput.addEventListener('change', () => handleFile(fileInput.files[0]));
}

/* ── Detection Form — Loading State ─────────────────────────── */
const detectionForm = document.getElementById('detectionForm');
const loadingOverlay = document.getElementById('loadingOverlay');

if (detectionForm) {
  detectionForm.addEventListener('submit', (e) => {
    if (!fileInput || !fileInput.files.length) {
      e.preventDefault();
      showToast('Please upload a cattle image first.', 'warning');
      return;
    }
    if (loadingOverlay) loadingOverlay.classList.remove('d-none');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analysing…';
    }
  });
}

/* ── Confidence Bar Animation ────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const bars = document.querySelectorAll('.confidence-bar[data-width]');
  bars.forEach(bar => {
    const target = parseFloat(bar.dataset.width);
    setTimeout(() => { bar.style.width = target + '%'; }, 150);
  });

  // Animate stat counters
  document.querySelectorAll('.counter-animate').forEach(el => {
    const target = parseInt(el.dataset.target, 10);
    if (isNaN(target)) return;
    let current = 0;
    const step = Math.ceil(target / 40);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current.toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 30);
  });
});

/* ── Dashboard Charts (Chart.js) ─────────────────────────────── */
function initDashboardCharts(stats) {
  if (!stats) return;

  // ── Donut Chart — Result Distribution ──
  const donutCtx = document.getElementById('donutChart');
  if (donutCtx) {
    new Chart(donutCtx, {
      type: 'doughnut',
      data: {
        labels: ['Positive', 'Healthy', 'Uncertain'],
        datasets: [{
          data: [stats.positive, stats.healthy, stats.uncertain],
          backgroundColor: ['#d13b3b', '#2d8a63', '#e07b2a'],
          borderWidth: 0,
          hoverOffset: 6
        }]
      },
      options: {
        cutout: '72%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { padding: 16, font: { size: 12 }, usePointStyle: true }
          },
          tooltip: { callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.raw}` } }
        }
      }
    });
  }

  // ── Line Chart — 7-Day Trend ──
  const lineCtx = document.getElementById('trendChart');
  if (lineCtx && stats.trend && stats.trend.length) {
    const days    = stats.trend.map(t => t.day).reverse();
    const totals  = stats.trend.map(t => t.cnt).reverse();
    const positives = stats.trend.map(t => t.pos).reverse();

    new Chart(lineCtx, {
      type: 'line',
      data: {
        labels: days,
        datasets: [
          {
            label: 'Total Scans',
            data: totals,
            borderColor: '#2d8a63',
            backgroundColor: 'rgba(45,138,99,.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: '#2d8a63'
          },
          {
            label: 'Positive',
            data: positives,
            borderColor: '#d13b3b',
            backgroundColor: 'rgba(209,59,59,.06)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: '#d13b3b'
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          x: { grid: { display: false } },
          y: { beginAtZero: true, ticks: { stepSize: 1 } }
        },
        plugins: { legend: { position: 'top' } }
      }
    });
  }

  // ── Bar Chart — Severity Breakdown ──
  const barCtx = document.getElementById('severityChart');
  if (barCtx && stats.severity && stats.severity.length) {
    const sevLabels = stats.severity.map(s => s.severity || 'Unknown');
    const sevCounts = stats.severity.map(s => s.cnt);
    const sevColors = sevLabels.map(l => ({
      None: '#2d8a63', Mild: '#f0c040', Moderate: '#e07b2a', Severe: '#d13b3b'
    }[l] || '#8fa4b3'));

    new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: sevLabels,
        datasets: [{
          label: 'Cases',
          data: sevCounts,
          backgroundColor: sevColors,
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: { grid: { display: false } },
          y: { beginAtZero: true, ticks: { stepSize: 1 } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }
}

/* ── Admin — Confirm Delete ──────────────────────────────────── */
document.querySelectorAll('.btn-delete-record').forEach(btn => {
  btn.addEventListener('click', (e) => {
    if (!confirm('Delete this record permanently? This cannot be undone.')) {
      e.preventDefault();
    }
  });
});

/* ── Toast Notification ──────────────────────────────────────── */
function showToast(message, type = 'success') {
  const map = { success: '#2d8a63', danger: '#d13b3b', warning: '#e07b2a', info: '#3b7dd1' };
  const toast = document.createElement('div');
  toast.style.cssText = `
    position:fixed; bottom:1.5rem; right:1.5rem; z-index:9999;
    background:${map[type] || map.success}; color:#fff;
    padding:.75rem 1.3rem; border-radius:8px; font-size:.88rem;
    font-weight:600; box-shadow:0 4px 18px rgba(0,0,0,.2);
    transition:opacity .3s ease; opacity:1; max-width:320px;
  `;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 350); }, 3200);
}

/* ── Admin Search — Live Filter ──────────────────────────────── */
const adminSearch = document.getElementById('adminSearch');
if (adminSearch) {
  let debounce;
  adminSearch.addEventListener('input', () => {
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      const q = adminSearch.value.trim();
      window.location.href = '/admin' + (q ? `?q=${encodeURIComponent(q)}` : '');
    }, 450);
  });
}

/* ── Print Report ────────────────────────────────────────────── */
const printBtn = document.getElementById('printReportBtn');
if (printBtn) {
  printBtn.addEventListener('click', () => window.print());
}

/* ── Auto-dismiss flash alerts ───────────────────────────────── */
document.querySelectorAll('.alert-auto-dismiss').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});
