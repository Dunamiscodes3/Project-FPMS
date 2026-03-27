/* ============================================================
   FPMS – Reports JS
   ============================================================ */

const REPORT_CONFIGS = {
  farmers: {
    title: '👨‍🌾 Farmer Registry Report',
    meta: d => `Total Farmers: ${d.length}`,
    html: d => `
      <table class="data-table">
        <thead><tr><th>Farmer ID</th><th>Name</th><th>ID Number</th><th>Phone</th><th>Location</th><th>Farm Size</th><th>Status</th><th>Joined</th></tr></thead>
        <tbody>${d.map(f => `<tr>
          <td>${f.farmer_id}</td><td>${f.full_name}</td><td>${f.id_number}</td>
          <td>${f.phone}</td><td>${f.location || '—'}</td>
          <td>${f.farm_size} acres</td><td>${f.status}</td><td>${fmtDate(f.join_date)}</td>
        </tr>`).join('')}</tbody>
      </table>`,
  },
  credits: {
    title: '💳 Credit Distribution Report',
    meta: d => `Total Issued: ${fmtKES(d.total_issued)} | Outstanding: ${fmtKES(d.outstanding)} | Repaid: ${fmtKES(d.total_issued - d.outstanding)}`,
    html: d => `
      <table class="data-table">
        <thead><tr><th>Farmer</th><th>Type</th><th>Amount (KES)</th><th>Outstanding (KES)</th><th>Date Issued</th><th>Status</th></tr></thead>
        <tbody>${d.credits.map(c => `<tr>
          <td>${c.farmer_name}</td><td>${c.credit_type}</td>
          <td>${fmtKES(c.amount)}</td><td>${fmtKES(c.outstanding)}</td>
          <td>${fmtDate(c.date_issued)}</td><td>${c.status}</td>
        </tr>`).join('')}</tbody>
      </table>`,
  },
  stock: {
    title: '📦 Stock & Production Report',
    meta: d => `Total Stock Received: ${fmtNum(d.total_stock)} kg`,
    html: d => `
      <table class="data-table">
        <thead><tr><th>Farmer</th><th>Date</th><th>Weight (kg)</th><th>Variety</th><th>Milling Status</th></tr></thead>
        <tbody>${d.deliveries.map(del => `<tr>
          <td>${del.farmer_name}</td><td>${fmtDate(del.delivery_date)}</td>
          <td>${fmtNum(del.weight)}</td><td>${del.variety}</td><td>${del.milling_status}</td>
        </tr>`).join('')}</tbody>
      </table>`,
  },
  payments: {
    title: '💰 Payment Summary Report',
    meta: d => `Total Payments Processed: ${fmtKES(d.total_paid)}`,
    html: d => `
      <table class="data-table">
        <thead><tr><th>Farmer</th><th>Amount (KES)</th><th>Method</th><th>Reference</th><th>Date Paid</th></tr></thead>
        <tbody>${d.payments.map(p => `<tr>
          <td>${p.farmer_name}</td><td>${fmtKES(p.amount)}</td>
          <td>${p.method}</td><td>${p.reference || '—'}</td><td>${fmtDate(p.date_paid)}</td>
        </tr>`).join('')}</tbody>
      </table>`,
  },
  machinery: {
    title: '🚜 Machinery Utilization Report',
    meta: d => `Total Bookings: ${d.total}`,
    html: d => `
      <table class="data-table">
        <thead><tr><th>Farmer</th><th>Machinery</th><th>Requested Date</th><th>Plot</th><th>Status</th><th>Submitted</th></tr></thead>
        <tbody>${d.bookings.map(b => `<tr>
          <td>${b.farmer_name}</td><td>${b.machinery_type}</td>
          <td>${fmtDate(b.requested_date)}</td><td>${b.plot_number || '—'}</td>
          <td>${b.status}</td><td>${fmtDate(b.submitted_on)}</td>
        </tr>`).join('')}</tbody>
      </table>`,
  },
  agronomic: {
    title: '🌱 Agronomic Performance Report',
    meta: d => `Total Seeds Distributed: ${fmtNum(d.total_qty)} kg`,
    html: d => `
      <table class="data-table">
        <thead><tr><th>Farmer</th><th>Variety</th><th>Quantity (kg)</th><th>Quality</th><th>Date</th></tr></thead>
        <tbody>${d.seeds.map(s => `<tr>
          <td>${s.farmer_name}</td><td>${s.variety}</td>
          <td>${fmtNum(s.quantity_kg)}</td><td>${s.supplier_quality}</td>
          <td>${fmtDate(s.distribution_date)}</td>
        </tr>`).join('')}</tbody>
      </table>`,
  },
};

async function generateReport(type) {
  const cfg = REPORT_CONFIGS[type];
  if (!cfg) return;
  const output    = document.getElementById('report-output');
  const titleEl   = document.getElementById('report-title');
  const metaEl    = document.getElementById('report-meta');
  const tableEl   = document.getElementById('report-table');

  titleEl.textContent = cfg.title;
  metaEl.textContent  = 'Generating…';
  tableEl.innerHTML   = '<p style="padding:16px;color:var(--text-muted)">Loading data…</p>';
  output.style.display = 'block';
  output.scrollIntoView({ behavior: 'smooth' });

  try {
    const data = await api('GET', `/api/reports/?type=${type}`);
    const today = new Date().toLocaleDateString('en-KE', { day:'numeric', month:'long', year:'numeric' });
    metaEl.textContent = cfg.meta(data) + `  |  Generated: ${today}`;
    tableEl.innerHTML  = cfg.html(data);
  } catch (e) {
    tableEl.innerHTML = `<p style="padding:16px;color:var(--red)">Error: ${e.message}</p>`;
  }
}
