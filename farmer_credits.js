/* ============================================================
   FPMS – Farmer Credits JS
   ============================================================ */

async function loadFarmerCredits() {
  const tbody = document.getElementById('fc-table');
  try {
    const result = await api('GET', '/api/credits/');
    const { credits, totals } = result;

    document.getElementById('fc-total').textContent       = fmtKES(totals.total_issued);
    document.getElementById('fc-outstanding').textContent = fmtKES(totals.outstanding);
    document.getElementById('fc-repaid').textContent      = fmtKES(totals.repaid);

    if (!credits.length) { tbody.innerHTML = emptyRow(5, 'No credits have been issued to you yet.'); return; }
    tbody.innerHTML = credits.map(c => `
      <tr>
        <td>${c.credit_type}</td>
        <td>${fmtKES(c.amount)}</td>
        <td>${fmtDate(c.date_issued)}</td>
        <td style="color:${c.outstanding > 0 ? 'var(--red)' : 'var(--primary)'};font-weight:600">
          ${fmtKES(c.outstanding)}
        </td>
        <td>${badge(c.status)}</td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(5, 'Error loading credits.');
    console.error(e);
  }
}

loadFarmerCredits();
