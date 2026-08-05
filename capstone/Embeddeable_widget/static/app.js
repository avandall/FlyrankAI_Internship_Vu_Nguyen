document.addEventListener('DOMContentLoaded', () => {
  const leadForm = document.getElementById('lead-form');
  const btnHoneypot = document.getElementById('btn-honeypot-test');
  const btnRateLimit = document.getElementById('btn-ratelimit-test');
  const btnRefresh = document.getElementById('btn-refresh');
  const leadsBody = document.getElementById('leads-body');

  leadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await sendLead(
      document.getElementById('lead-name').value,
      document.getElementById('lead-email').value,
      document.getElementById('honeypot').value
    );
  });

  btnHoneypot.addEventListener('click', async () => {
    await sendLead('Spam Bot', 'bot@spam.com', 'I am spam');
  });

  btnRateLimit.addEventListener('click', async () => {
    alert('Spamming 6 submissions to trigger 5 req/min Rate Limit (429)!');
    for (let i = 1; i <= 6; i++) {
      await sendLead(`User ${i}`, `user${i}@flyrank.ai`, '');
    }
  });

  async function sendLead(name, email, honeypot) {
    try {
      const res = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          widget_id: 'w_demo_101',
          visitor_name: name,
          visitor_email: email,
          honeypot_field: honeypot || null,
          origin_domain: 'https://flyrank.ai',
          client_ip: '127.0.0.1'
        })
      });
      const data = await res.json();
      if (res.ok) {
        alert('Submitted lead ID: ' + data.submission.submission_id + ' (Geo: ' + data.submission.geo_country + ')');
        loadLeads();
      } else {
        alert(`API Error (${res.status}): ${data.detail}`);
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function loadLeads() {
    try {
      const res = await fetch('/api/leads/tenant_demo');
      const data = await res.json();
      leadsBody.innerHTML = '';
      if (!data.leads || data.leads.length === 0) {
        leadsBody.innerHTML = '<tr><td colspan="3" class="text-muted">No leads captured yet.</td></tr>';
        return;
      }
      data.leads.forEach(l => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${l.visitor_email}</strong></td>
          <td>${l.ip_address}</td>
          <td><span class="badge badge-success">${l.geo_country} (${l.geo_city})</span></td>
        `;
        leadsBody.appendChild(tr);
      });
    } catch (e) {
      console.error(e);
    }
  }

  btnRefresh.addEventListener('click', loadLeads);
  loadLeads();
});
