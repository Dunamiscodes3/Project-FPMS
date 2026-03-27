/* ============================================================
   FPMS – Farmer Agronomic Info JS
   ============================================================ */

async function loadFarmerSeeds() {
  const tbody = document.getElementById('fa-seeds');
  try {
    const seeds = await api('GET', '/api/seeds/');
    if (!seeds.length) {
      tbody.innerHTML = emptyRow(4, 'No seed distributions recorded for you yet.'); return;
    }
    tbody.innerHTML = seeds.map(s => `
      <tr>
        <td>${s.variety}</td>
        <td>${fmtNum(s.quantity_kg)}</td>
        <td>${fmtDate(s.distribution_date)}</td>
        <td>${badge(s.supplier_quality)}</td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(4, 'Error loading seed records.');
    console.error(e);
  }
}

async function loadFarmerSoilLogs() {
  const tbody = document.getElementById('fa-soil');
  try {
    const logs = await api('GET', '/api/soil-logs/');
    if (!logs.length) {
      tbody.innerHTML = emptyRow(5, 'No soil health logs recorded for you yet.'); return;
    }
    tbody.innerHTML = logs.map(l => `
      <tr>
        <td>${fmtDate(l.log_date)}</td>
        <td>${l.ph_level ?? '—'}</td>
        <td>${badge(l.moisture_level)}</td>
        <td style="font-size:12px">${l.fertilizer_rec || '—'}</td>
        <td>${badge(l.water_status)}</td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(5, 'Error loading soil logs.');
    console.error(e);
  }
}

loadFarmerSeeds();
loadFarmerSoilLogs();
