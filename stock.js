/* ============================================================
   FPMS – Stock & Deliveries JS
   ============================================================ */

async function loadDeliveries() {
  const tbody = document.getElementById('deliveries-table');
  const q = document.getElementById('search-stock').value.trim();
  try {
    const result = await api('GET', `/api/deliveries/${q ? '?q=' + encodeURIComponent(q) : ''}`);
    const { deliveries, totals } = result;

    document.getElementById('total-stock').textContent   = fmtNum(totals.total_stock) + ' kg';
    document.getElementById('milling-pending').textContent = fmtNum(totals.pending) + ' kg';
    document.getElementById('milling-done').textContent  = fmtNum(totals.completed) + ' kg';

    if (!deliveries.length) { tbody.innerHTML = emptyRow(6); return; }
    tbody.innerHTML = deliveries.map(d => `
      <tr>
        <td><strong>${d.farmer_name}</strong></td>
        <td>${fmtDate(d.delivery_date)}</td>
        <td>${fmtNum(d.weight)}</td>
        <td>${d.variety}</td>
        <td>${badge(d.milling_status)}</td>
        <td>
          <select class="milling-select"
            onchange="updateMilling(${d.id}, this.value)"
            style="padding:4px 8px;border:1.5px solid var(--border);border-radius:6px;font-size:12px;font-family:inherit">
            <option ${d.milling_status === 'Pending'    ? 'selected' : ''}>Pending</option>
            <option ${d.milling_status === 'Processing' ? 'selected' : ''}>Processing</option>
            <option ${d.milling_status === 'Completed'  ? 'selected' : ''}>Completed</option>
          </select>
        </td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(6, 'Error loading deliveries.');
    console.error(e);
  }
}

async function updateMilling(id, status) {
  try {
    await api('PATCH', `/api/deliveries/${id}/`, { milling_status: status });
    showToast(`✅ Milling status updated → ${status}`);
    loadDeliveries();
  } catch (e) {
    showToast('❌ ' + e.message);
  }
}

async function openDeliveryModal() {
  await populateFarmerSelects('d-farmer');
  document.getElementById('d-date').valueAsDate = new Date();
  openModal('delivery-modal');
}

async function recordDelivery() {
  const farmer_id      = document.getElementById('d-farmer').value;
  const delivery_date  = document.getElementById('d-date').value;
  const weight         = document.getElementById('d-weight').value;
  const variety        = document.getElementById('d-variety').value;
  const milling_status = document.getElementById('d-milling').value;

  if (!farmer_id || !weight) {
    showToast('⚠️ Please select a farmer and enter weight.'); return;
  }
  try {
    const d = await api('POST', '/api/deliveries/', {
      farmer_id, delivery_date, weight, variety, milling_status
    });
    closeModal('delivery-modal');
    showToast(`✅ Delivery recorded — ${fmtNum(d.weight)} kg for ${d.farmer_name}`);
    ['d-farmer','d-weight'].forEach(id => {
      const el = document.getElementById(id); if (el) el.value = '';
    });
    loadDeliveries();
  } catch (e) {
    showToast('❌ ' + e.message);
  }
}

// Init
loadDeliveries();
