/* ============================================================
   FPMS – Admin Dashboard JS
   ============================================================ */

async function loadDashboard() {
  try {
    const d = await api('GET', '/api/dashboard/stats/');

    document.getElementById('stat-farmers').textContent  = fmtNum(d.total_farmers);
    document.getElementById('stat-credit').textContent   = fmtKES(d.total_credit);
    document.getElementById('stat-stock').textContent    = fmtNum(d.total_stock) + ' kg';
    document.getElementById('stat-payments').textContent = fmtKES(d.total_paid);

    // Recent deliveries
    const dtbody = document.getElementById('recent-deliveries');
    if (d.recent_deliveries && d.recent_deliveries.length) {
      dtbody.innerHTML = d.recent_deliveries.map(del => `
        <tr>
          <td>${del.farmer_name}</td>
          <td>${fmtDate(del.delivery_date)}</td>
          <td>${fmtNum(del.weight)}</td>
          <td>${badge(del.milling_status)}</td>
        </tr>`).join('');
    } else {
      dtbody.innerHTML = emptyRow(4, 'No deliveries recorded yet.');
    }

    // Pending bookings
    const pbody = document.getElementById('pending-bookings');
    if (d.pending_bookings_list && d.pending_bookings_list.length) {
      pbody.innerHTML = d.pending_bookings_list.map(b => `
        <tr>
          <td>${b.farmer_name}</td>
          <td>${b.machinery_type}</td>
          <td>${fmtDate(b.requested_date)}</td>
          <td>${badge(b.status)}</td>
          <td>
            <button class="btn-sm btn-approve" onclick="quickApprove(${b.id})">✓ Approve</button>
            <button class="btn-sm btn-reject"  onclick="quickReject(${b.id})" style="margin-left:4px">✕ Reject</button>
          </td>
        </tr>`).join('');
    } else {
      pbody.innerHTML = emptyRow(5, 'No pending machinery bookings.');
    }

  } catch (e) {
    console.error('Dashboard load error:', e);
  }
}

async function quickApprove(id) {
  try {
    await api('POST', `/api/bookings/${id}/action/`, { action: 'approve' });
    showToast('✅ Booking approved!');
    loadDashboard();
  } catch (e) { showToast('Error: ' + e.message); }
}

async function quickReject(id) {
  try {
    await api('POST', `/api/bookings/${id}/action/`, { action: 'reject' });
    showToast('Booking rejected.');
    loadDashboard();
  } catch (e) { showToast('Error: ' + e.message); }
}

// Init
loadDashboard();
