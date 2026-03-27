/* ============================================================
   FPMS – Payments JS
   ============================================================ */

async function loadPayments() {
  const summary = document.getElementById('payment-summary');
  const history = document.getElementById('payment-history');
  try {
    const result = await api('GET', '/api/payments/');

    document.getElementById('total-paid').textContent    = fmtKES(result.total_paid);
    document.getElementById('total-pending').textContent = fmtKES(result.total_pending);

    // Summary table
    if (!result.summary.length) {
      summary.innerHTML = emptyRow(7);
    } else {
      summary.innerHTML = result.summary.map(s => `
        <tr>
          <td><strong>${s.farmer_name}</strong></td>
          <td>${fmtNum(s.total_delivered)}</td>
          <td>${fmtKES(s.gross)}</td>
          <td style="color:var(--red)">${fmtKES(s.credit_deduction)}</td>
          <td><strong>${fmtKES(s.net_payable)}</strong></td>
          <td>${badge(s.status)}</td>
          <td>
            ${s.net_payable > 0
              ? `<button class="btn-sm btn-pay"
                   onclick="openPayModal('${s.farmer_id}','${s.farmer_name}',${s.net_payable})">
                   Pay ${fmtKES(s.net_payable)}
                 </button>`
              : '<span style="color:var(--text-muted);font-size:12px">—</span>'
            }
          </td>
        </tr>`).join('');
    }

    // History table
    if (!result.history.length) {
      history.innerHTML = emptyRow(5, 'No payment history yet.');
    } else {
      history.innerHTML = result.history.map(p => `
        <tr>
          <td>${p.farmer_name}</td>
          <td><strong>${fmtKES(p.amount)}</strong></td>
          <td>${fmtDate(p.date_paid)}</td>
          <td>${p.method}</td>
          <td><code>${p.reference || '—'}</code></td>
        </tr>`).join('');
    }
  } catch (e) {
    summary.innerHTML = emptyRow(7, 'Error loading payments.');
    console.error(e);
  }
}

function openPayModal(farmerId, farmerName, amount) {
  document.getElementById('pay-farmer-id').value = farmerId;
  document.getElementById('pay-amount').value    = amount;
  document.getElementById('pay-info').innerHTML  =
    `<strong>Farmer:</strong> ${farmerName}<br>
     <strong>Net Payable:</strong> <span style="font-size:16px;font-weight:700">${fmtKES(amount)}</span>`;
  document.getElementById('pay-ref').value = '';
  openModal('pay-modal');
}

async function confirmPayment() {
  const farmer_id = document.getElementById('pay-farmer-id').value;
  const amount    = document.getElementById('pay-amount').value;
  const method    = document.getElementById('pay-method').value;
  const reference = document.getElementById('pay-ref').value.trim();

  try {
    const p = await api('POST', '/api/payments/', { farmer_id, amount, method, reference });
    closeModal('pay-modal');
    showToast(`✅ Payment of ${fmtKES(p.amount)} processed for ${p.farmer_name}`);
    loadPayments();
  } catch (e) {
    showToast('❌ ' + e.message);
  }
}

// Init
loadPayments();
