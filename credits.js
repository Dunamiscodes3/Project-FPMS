/* ============================================================
   FPMS – Credit Management JS
   ============================================================ */

async function loadCredits() {
  const tbody = document.getElementById('credits-table');
  const q = document.getElementById('search-credits').value.trim();
  try {
    const result = await api('GET', `/api/credits/${q ? '?q=' + encodeURIComponent(q) : ''}`);
    const { credits, totals } = result;

    // Update stat cards
    document.getElementById('total-issued').textContent     = fmtKES(totals.total_issued);
    document.getElementById('total-outstanding').textContent = fmtKES(totals.outstanding);
    document.getElementById('total-repaid').textContent     = fmtKES(totals.repaid);

    if (!credits.length) { tbody.innerHTML = emptyRow(6); return; }
    tbody.innerHTML = credits.map(c => `
      <tr>
        <td><strong>${c.farmer_name}</strong><br><small style="color:var(--text-muted)">${c.farmer_id}</small></td>
        <td>${c.credit_type}</td>
        <td>${fmtKES(c.amount)}</td>
        <td>${fmtDate(c.date_issued)}</td>
        <td><strong style="color:${c.outstanding > 0 ? 'var(--red)' : 'var(--primary)'}">${fmtKES(c.outstanding)}</strong></td>
        <td>${badge(c.status)}</td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = emptyRow(6, 'Error loading credits.');
    console.error(e);
  }
}

async function openIssueModal() {
  await populateFarmerSelects('c-farmer');
  openModal('credit-modal');
}

async function issueCredit() {
  const farmer_id   = document.getElementById('c-farmer').value;
  const credit_type = document.getElementById('c-type').value;
  const amount      = document.getElementById('c-amount').value;
  const description = document.getElementById('c-desc').value.trim();

  if (!farmer_id || !amount) {
    showToast('⚠️ Please select a farmer and enter an amount.'); return;
  }
  try {
    const c = await api('POST', '/api/credits/', { farmer_id, credit_type, amount, description });
    closeModal('credit-modal');
    showToast(`✅ Credit of ${fmtKES(c.amount)} issued to ${c.farmer_name}`);
    ['c-farmer','c-amount','c-desc'].forEach(id => {
      const el = document.getElementById(id); if (el) el.value = '';
    });
    loadCredits();
  } catch (e) {
    showToast('❌ ' + e.message);
  }
}

// Init
loadCredits();
