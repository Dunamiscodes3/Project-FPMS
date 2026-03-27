/* ============================================================
   FPMS – Agronomic Support JS
   ============================================================ */

async function loadSeeds() {
  const tbody = document.getElementById('seeds-table');
  try {
    const seeds = await api('GET', '/api/seeds/');
    if (!seeds.length) { tbody.innerHTML = emptyRow(5); return; }
    tbody.innerHTML = seeds.map(s => `
      <tr>
        <td><strong>${s.farmer_name}</strong></td>
        <td>${s.variety}</td>
        <td>${fmtNum(s.quantity_kg)}</td>
        <td>${fmtDate(s.distribution_date)}</td>
        <td>${badge(s.supplier_quality)}</td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(5, 'Error loading seed records.');
  }
}

async function loadSoilLogs() {
  const tbody = document.getElementById('soil-table');
  try {
    const logs = await api('GET', '/api/soil-logs/');
    if (!logs.length) { tbody.innerHTML = emptyRow(6); return; }
    tbody.innerHTML = logs.map(l => `
      <tr>
        <td><strong>${l.farmer_name}</strong></td>
        <td>${fmtDate(l.log_date)}</td>
        <td>${l.ph_level ?? '—'}</td>
        <td>${badge(l.moisture_level)}</td>
        <td style="max-width:200px;font-size:12px">${l.fertilizer_rec || '—'}</td>
        <td>${badge(l.water_status)}</td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(6, 'Error loading soil logs.');
  }
}

async function loadYield() {
  const tbody = document.getElementById('yield-table');
  try {
    const farmers = await api('GET', '/api/farmers/');
    if (!farmers.length) { tbody.innerHTML = emptyRow(5); return; }
    tbody.innerHTML = farmers.map(f => {
      const expected = parseFloat(f.farm_size) * 1800;
      // We'll fetch deliveries totals from farmer detail on dashboard
      // For now we show from summary in farmers list
      return `
        <tr>
          <td><strong>${f.full_name}</strong></td>
          <td>${f.farm_size} acres</td>
          <td>${fmtNum(expected)}</td>
          <td id="yield-actual-${f.id}">Loading…</td>
          <td id="yield-perf-${f.id}">Loading…</td>
        </tr>`;
    }).join('');
    // Async fill yield actuals
    farmers.forEach(async f => {
      try {
        const detail = await api('GET', `/api/farmers/${f.id}/`);
        const actual = detail.total_delivered;
        const expected = parseFloat(f.farm_size) * 1800;
        const pct = expected > 0 ? Math.round((actual / expected) * 100) : 0;
        const actEl = document.getElementById(`yield-actual-${f.id}`);
        const perfEl = document.getElementById(`yield-perf-${f.id}`);
        if (actEl) actEl.textContent = fmtNum(actual);
        if (perfEl) perfEl.innerHTML = progressBar(pct);
      } catch (_) {}
    });
  } catch (e) {
    tbody.innerHTML = emptyRow(5, 'Error loading yield data.');
  }
}

async function recordSeed() {
  const farmer_id       = document.getElementById('s-farmer').value;
  const variety         = document.getElementById('s-variety').value;
  const quantity_kg     = document.getElementById('s-qty').value;
  const supplier_quality = document.getElementById('s-quality').value;

  if (!farmer_id || !quantity_kg) {
    showToast('⚠️ Please select a farmer and enter quantity.'); return;
  }
  try {
    const s = await api('POST', '/api/seeds/', { farmer_id, variety, quantity_kg, supplier_quality });
    closeModal('seed-modal');
    showToast(`✅ Seed distribution recorded for ${s.farmer_name}`);
    document.getElementById('s-qty').value = '';
    loadSeeds();
  } catch (e) { showToast('❌ ' + e.message); }
}

async function recordSoilLog() {
  const farmer_id     = document.getElementById('sh-farmer').value;
  const ph_level      = document.getElementById('sh-ph').value;
  const moisture_level = document.getElementById('sh-moisture').value;
  const water_status  = document.getElementById('sh-water').value;
  const fertilizer_rec = document.getElementById('sh-fert').value.trim();

  if (!farmer_id) { showToast('⚠️ Please select a farmer.'); return; }
  try {
    const l = await api('POST', '/api/soil-logs/', {
      farmer_id, ph_level: ph_level || null,
      moisture_level, water_status, fertilizer_rec
    });
    closeModal('soil-modal');
    showToast(`✅ Soil log recorded for ${l.farmer_name}`);
    document.getElementById('sh-ph').value = '';
    document.getElementById('sh-fert').value = '';
    loadSoilLogs();
  } catch (e) { showToast('❌ ' + e.message); }
}

// Populate selects then load data
(async () => {
  await populateFarmerSelects('s-farmer', 'sh-farmer');
  loadSeeds();
  loadSoilLogs();
  loadYield();
})();
