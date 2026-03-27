/* ============================================================
   FPMS – Farmer Deliveries JS
   ============================================================ */

async function loadFarmerDeliveries() {
  const tbody = document.getElementById('fd-table');
  try {
    const result = await api('GET', '/api/deliveries/');
    const { deliveries, totals } = result;

    document.getElementById('fd-total').textContent   = fmtNum(totals.total_stock) + ' kg';
    document.getElementById('fd-pending').textContent = fmtNum(totals.pending) + ' kg';
    document.getElementById('fd-done').textContent    = fmtNum(totals.completed) + ' kg';

    if (!deliveries.length) {
      tbody.innerHTML = emptyRow(5, 'No deliveries recorded yet.'); return;
    }
    tbody.innerHTML = deliveries.map(d => `
      <tr>
        <td>${fmtDate(d.delivery_date)}</td>
        <td>${fmtNum(d.weight)}</td>
        <td>${d.variety}</td>
        <td>${badge(d.milling_status)}</td>
        <td>${fmtKES(parseFloat(d.weight) * 40)}</td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(5, 'Error loading deliveries.');
    console.error(e);
  }
}

loadFarmerDeliveries();
