/* ============================================================
   FPMS – Farmer Dashboard JS
   ============================================================ */

async function loadFarmerDashboard() {
  try {
    const d = await api('GET', '/api/dashboard/stats/');

    document.getElementById('f-credit').textContent    = fmtKES(d.outstanding_credit);
    document.getElementById('f-delivered').textContent = fmtNum(d.total_delivered) + ' kg';
    document.getElementById('f-net').textContent       = fmtKES(d.net_payable);
    document.getElementById('f-milling').textContent   = d.last_milling_status || '—';

    // Recent deliveries
    const dtbody = document.getElementById('f-deliveries');
    dtbody.innerHTML = d.recent_deliveries.length
      ? d.recent_deliveries.map(del => `
          <tr>
            <td>${fmtDate(del.delivery_date)}</td>
            <td>${fmtNum(del.weight)}</td>
            <td>${badge(del.milling_status)}</td>
          </tr>`).join('')
      : emptyRow(3, 'No deliveries yet.');

    // Credits
    const ctbody = document.getElementById('f-credits');
    ctbody.innerHTML = d.credits.length
      ? d.credits.map(c => `
          <tr>
            <td>${c.credit_type}</td>
            <td>${fmtKES(c.amount)}</td>
            <td style="color:${c.outstanding > 0 ? 'var(--red)' : 'var(--primary)'}">
              ${fmtKES(c.outstanding)}
            </td>
          </tr>`).join('')
      : emptyRow(3, 'No credits issued.');

    // Bookings
    const bkbody = document.getElementById('f-bookings');
    bkbody.innerHTML = d.bookings.length
      ? d.bookings.map(b => `
          <tr>
            <td>${b.machinery_type}</td>
            <td>${fmtDate(b.requested_date)}</td>
            <td>${badge(b.status)}</td>
          </tr>`).join('')
      : emptyRow(3, 'No machinery bookings yet.');

  } catch (e) {
    console.error('Farmer dashboard error:', e);
  }
}

loadFarmerDashboard();
