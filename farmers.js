/* ============================================================
   FPMS – Farmers Management JS
   ============================================================ */

async function loadFarmers() {
  const tbody = document.getElementById('farmers-table');
  const q = document.getElementById('search-farmers').value.trim();
  try {
    const farmers = await api('GET', `/api/farmers/${q ? '?q=' + encodeURIComponent(q) : ''}`);
    if (!farmers.length) {
      tbody.innerHTML = emptyRow(7); return;
    }
    tbody.innerHTML = farmers.map(f => `
      <tr>
        <td><code>${f.farmer_id}</code></td>
        <td><strong>${f.full_name}</strong></td>
        <td>${f.id_number}</td>
        <td>${f.phone}</td>
        <td>${f.farm_size}</td>
        <td>${badge(f.status)}</td>
        <td>
          <button class="btn-sm btn-view" onclick="viewFarmer(${f.id})">View</button>
        </td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(7, 'Error loading farmers.');
    console.error(e);
  }
}

async function viewFarmer(id) {
  const body = document.getElementById('view-modal-body');
  body.innerHTML = '<p style="text-align:center;padding:20px">Loading…</p>';
  openModal('view-modal');
  try {
    const f = await api('GET', `/api/farmers/${id}/`);
    body.innerHTML = `
      <div class="stats-grid" style="margin-bottom:16px">
        <div class="stat-card blue">
          <div class="stat-icon">📦</div>
          <div class="stat-info">
            <div class="stat-value">${fmtNum(f.total_delivered)} kg</div>
            <div class="stat-label">Total Delivered</div>
          </div>
        </div>
        <div class="stat-card amber">
          <div class="stat-icon">💳</div>
          <div class="stat-info">
            <div class="stat-value">${fmtKES(f.outstanding_credit)}</div>
            <div class="stat-label">Credit Outstanding</div>
          </div>
        </div>
      </div>
      <table class="data-table" style="margin-bottom:16px">
        <tr><td style="font-weight:600;width:40%">Farmer ID</td><td>${f.farmer_id}</td></tr>
        <tr><td style="font-weight:600">Full Name</td><td>${f.full_name}</td></tr>
        <tr><td style="font-weight:600">National ID</td><td>${f.id_number}</td></tr>
        <tr><td style="font-weight:600">Phone</td><td>${f.phone}</td></tr>
        <tr><td style="font-weight:600">Location</td><td>${f.location || '—'}</td></tr>
        <tr><td style="font-weight:600">Farm Size</td><td>${f.farm_size} acres</td></tr>
        <tr><td style="font-weight:600">Plot Number</td><td>${f.plot_number || '—'}</td></tr>
        <tr><td style="font-weight:600">Status</td><td>${badge(f.status)}</td></tr>
        <tr><td style="font-weight:600">Joined</td><td>${fmtDate(f.join_date)}</td></tr>
      </table>
      <p style="font-weight:700;color:var(--primary-dark);margin-bottom:8px">Recent Deliveries</p>
      <table class="data-table">
        <thead><tr><th>Date</th><th>Weight (kg)</th><th>Variety</th><th>Milling</th></tr></thead>
        <tbody>
          ${f.deliveries.length
            ? f.deliveries.slice(0,5).map(d => `<tr>
                <td>${fmtDate(d.delivery_date)}</td>
                <td>${fmtNum(d.weight)}</td>
                <td>${d.variety}</td>
                <td>${badge(d.milling_status)}</td>
              </tr>`).join('')
            : emptyRow(4, 'No deliveries yet.')
          }
        </tbody>
      </table>`;
  } catch (e) {
    body.innerHTML = '<p style="color:red;padding:20px">Error loading farmer details.</p>';
  }
}

async function registerFarmer() {
  const name     = document.getElementById('f-name').value.trim();
  const idNum    = document.getElementById('f-id').value.trim();
  const phone    = document.getElementById('f-phone').value.trim();
  const location = document.getElementById('f-location').value.trim();
  const size     = document.getElementById('f-size').value;
  const plot     = document.getElementById('f-plot').value.trim();
  const pass     = document.getElementById('f-pass').value.trim();

  if (!name || !idNum || !phone) {
    showToast('⚠️ Name, ID Number and Phone are required.'); return;
  }
  try {
    const farmer = await api('POST', '/api/farmers/', {
      full_name: name, id_number: idNum, phone,
      location, farm_size: size || 0,
      plot_number: plot, password: pass,
    });
    closeModal('farmer-modal');
    showToast(`✅ ${farmer.full_name} registered (ID: ${farmer.farmer_id})`);
    // clear form
    ['f-name','f-id','f-phone','f-location','f-size','f-plot','f-pass']
      .forEach(id => { const el = document.getElementById(id); if(el) el.value = ''; });
    loadFarmers();
  } catch (e) {
    showToast('❌ ' + e.message);
  }
}

// Init
loadFarmers();
