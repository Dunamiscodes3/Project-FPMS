/* ============================================================
   FPMS – Machinery Bookings JS
   ============================================================ */

let activeFilter = 'all';

async function loadBookings(filter) {
  if (filter !== undefined) activeFilter = filter;
  const tbody = document.getElementById('bookings-table');
  const url = activeFilter === 'all'
    ? '/api/bookings/'
    : `/api/bookings/?status=${encodeURIComponent(activeFilter)}`;
  try {
    const result = await api('GET', url);
    const { bookings, counts } = result;

    document.getElementById('count-pending').textContent  = counts.pending;
    document.getElementById('count-approved').textContent = counts.approved;
    document.getElementById('count-rejected').textContent = counts.rejected;

    if (!bookings.length) { tbody.innerHTML = emptyRow(7); return; }
    tbody.innerHTML = bookings.map(b => `
      <tr>
        <td><strong>${b.farmer_name}</strong><br><small style="color:var(--text-muted)">${b.farmer_id}</small></td>
        <td>${b.machinery_type}</td>
        <td>${fmtDate(b.requested_date)}</td>
        <td>${b.plot_number || '—'}</td>
        <td style="max-width:160px;font-size:12px">${b.notes || '—'}</td>
        <td>${badge(b.status)}</td>
        <td>
          ${b.status === 'Pending'
            ? `<button class="btn-sm btn-approve" onclick="approveBooking(${b.id})">✓ Approve</button>
               <button class="btn-sm btn-reject"  onclick="rejectBooking(${b.id})" style="margin-left:4px">✕ Reject</button>`
            : `<span style="color:var(--text-muted);font-size:12px">${b.status}</span>`
          }
        </td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(7, 'Error loading bookings.');
    console.error(e);
  }
}

function filterBookings(filter, btn) {
  document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
  if (btn) btn.classList.add('active');
  loadBookings(filter);
}

async function approveBooking(id) {
  try {
    await api('POST', `/api/bookings/${id}/action/`, { action: 'approve' });
    showToast('✅ Booking approved!');
    loadBookings();
  } catch (e) { showToast('❌ ' + e.message); }
}

async function rejectBooking(id) {
  try {
    await api('POST', `/api/bookings/${id}/action/`, { action: 'reject' });
    showToast('Booking rejected.');
    loadBookings();
  } catch (e) { showToast('❌ ' + e.message); }
}

// Init
loadBookings();
