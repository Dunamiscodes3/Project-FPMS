/* ============================================================
   FPMS – Shared Utilities
   All pages load this first via base.html
   ============================================================ */

const PRICE_PER_KG = 40;

// ── Formatting ───────────────────────────────────────────────
function fmtKES(n) {
  return 'KES ' + Number(n || 0).toLocaleString('en-KE', { minimumFractionDigits: 0 });
}
function fmtNum(n) {
  return Number(n || 0).toLocaleString('en-KE');
}
function fmtDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-KE', { day: '2-digit', month: 'short', year: 'numeric' });
}
function badge(text) {
  const cls = {
    'pending':    'badge-pending',
    'approved':   'badge-approved',
    'completed':  'badge-approved',
    'paid':       'badge-paid',
    'active':     'badge-active',
    'rejected':   'badge-rejected',
    'processing': 'badge-processing',
    'partial':    'badge-partial',
    'outstanding':'badge-pending',
    'repaid':     'badge-approved',
    'adequate':   'badge-approved',
    'optimal':    'badge-approved',
    'low':        'badge-pending',
    'high':       'badge-pending',
    'needs attention': 'badge-pending',
    'critical':   'badge-rejected',
    'certified':  'badge-approved',
    'good':       'badge-active',
    'average':    'badge-pending',
    'poor':       'badge-rejected',
  }[text.toLowerCase()] || 'badge-pending';
  return `<span class="badge ${cls}">${text}</span>`;
}

// ── Toast ─────────────────────────────────────────────────────
function showToast(msg, duration = 3500) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.style.display = 'block';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.style.display = 'none'; }, duration);
}

// ── Modal helpers ─────────────────────────────────────────────
function openModal(id)  { document.getElementById(id).style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

// Close modal on backdrop click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.style.display = 'none';
  }
});

// ── Sidebar toggle ────────────────────────────────────────────
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ── Logout ───────────────────────────────────────────────────
async function doLogout() {
  await fetch('/api/auth/logout/', { method: 'POST', credentials: 'include' });
  window.location.href = '/';
}

// ── CSRF helper ───────────────────────────────────────────────
function getCookie(name) {
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return v ? v.pop() : '';
}

// ── API wrapper ───────────────────────────────────────────────
async function api(method, url, body = null) {
  const opts = {
    method,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  const data = await res.json();
  if (!data.success) throw new Error(data.error || 'Request failed');
  return data.data;
}

// ── Farmer dropdown loader (admin pages) ─────────────────────
async function populateFarmerSelects(...ids) {
  try {
    const farmers = await api('GET', '/api/farmers/');
    ids.forEach(id => {
      const sel = document.getElementById(id);
      if (!sel) return;
      sel.innerHTML = '<option value="">— Select Farmer —</option>';
      farmers.forEach(f => {
        sel.innerHTML += `<option value="${f.farmer_id}">${f.full_name} (${f.farmer_id})</option>`;
      });
    });
  } catch (e) {
    console.error('Could not load farmers for dropdowns:', e);
  }
}

// ── Progress bar helper ───────────────────────────────────────
function progressBar(pct) {
  const cls = pct >= 80 ? 'good' : pct >= 50 ? 'mid' : 'poor';
  return `<div class="progress-bar-wrap">
    <div class="progress-bar"><div class="progress-fill ${cls}" style="width:${Math.min(pct,100)}%"></div></div>
    <span style="font-size:12px;font-weight:600">${pct}%</span>
  </div>`;
}

// ── Empty row helper ──────────────────────────────────────────
function emptyRow(cols, msg = 'No records found.') {
  return `<tr><td colspan="${cols}" style="color:var(--text-muted);text-align:center;padding:24px;font-style:italic">${msg}</td></tr>`;
}
