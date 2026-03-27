/* ============================================================
   FPMS – Farmer Machinery Booking JS
   ============================================================ */

async function loadMyBookings() {
  const tbody = document.getElementById('my-bookings');
  try {
    const result = await api('GET', '/api/bookings/');
    const { bookings } = result;
    if (!bookings.length) {
      tbody.innerHTML = emptyRow(5, 'No bookings submitted yet.'); return;
    }
    tbody.innerHTML = bookings.map(b => `
      <tr>
        <td>${b.machinery_type}</td>
        <td>${fmtDate(b.requested_date)}</td>
        <td>${b.plot_number || '—'}</td>
        <td>${badge(b.status)}</td>
        <td>${fmtDate(b.submitted_on)}</td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(5, 'Error loading bookings.');
    console.error(e);
  }
}

async function submitBooking() {
  const machinery_type  = document.getElementById('b-type').value;
  const requested_date  = document.getElementById('b-date').value;
  const plot_number     = document.getElementById('b-plot').value.trim();
  const notes           = document.getElementById('b-notes').value.trim();

  if (!requested_date) { showToast('⚠️ Please select a date.'); return; }

  try {
    await api('POST', '/api/bookings/', {
      machinery_type, requested_date, plot_number, notes
    });
    showToast('✅ Booking request submitted! The cooperative will review and confirm.');
    document.getElementById('b-notes').value = '';
    document.getElementById('b-plot').value  = '';
    loadMyBookings();
  } catch (e) {
    showToast('❌ ' + e.message);
  }
}

// Set default date to today
document.getElementById('b-date').valueAsDate = new Date();
loadMyBookings();
