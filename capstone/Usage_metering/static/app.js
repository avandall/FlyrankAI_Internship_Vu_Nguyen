document.addEventListener('DOMContentLoaded', () => {
  const quotaReq = document.getElementById('quota-req');
  const quotaTok = document.getElementById('quota-tok');
  const btnIngest = document.getElementById('btn-ingest');
  const btnExceed = document.getElementById('btn-exceed');
  const costOutput = document.getElementById('cost-output');
  const btnUpgrade = document.getElementById('btn-upgrade');
  const btnCancel = document.getElementById('btn-cancel');
  const btnInvoice = document.getElementById('btn-invoice');
  const invoiceCard = document.getElementById('invoice-card');

  async function updateQuota() {
    try {
      const res = await fetch('/api/tenant/tenant_demo');
      const data = await res.json();
      quotaReq.innerText = `${data.quota.current_requests} / ${data.quota.max_requests}`;
      quotaTok.innerText = `${data.quota.current_tokens.toLocaleString()} / ${data.quota.max_tokens.toLocaleString()}`;
    } catch (e) {
      console.error(e);
    }
  }

  btnIngest.addEventListener('click', async () => {
    try {
      const event = {
        idempotency_key: 'evt_' + Date.now(),
        tenant_id: 'tenant_demo',
        event_type: 'llm_inference',
        input_tokens: parseInt(document.getElementById('inp-tok').value) || 0,
        cached_input_tokens: parseInt(document.getElementById('cached-tok').value) || 0,
        output_tokens: parseInt(document.getElementById('out-tok').value) || 0,
        reasoning_tokens: parseInt(document.getElementById('reason-tok').value) || 0,
        timestamp: Math.floor(Date.now() / 1000)
      };

      const res = await fetch('/api/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event)
      });
      const data = await res.json();
      if (res.ok) {
        costOutput.classList.remove('hidden');
        costOutput.innerText = `Ingested: ${data.status}\nMicro-cents: ${data.cost.total_cost_micro_cents} µ¢\nUSD: ${data.cost.total_cost_usd_formatted}`;
        updateQuota();
      } else {
        alert(`Quota Exceeded (${res.status}): ${data.detail}`);
      }
    } catch (e) {
      console.error(e);
    }
  });

  btnExceed.addEventListener('click', async () => {
    alert('Ingesting 60,000 tokens on FREE Plan (Max 50,000 limit)! Expecting 429 Quota Exceeded.');
    const res = await fetch('/api/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        idempotency_key: 'evt_overflow_' + Date.now(),
        tenant_id: 'tenant_demo',
        event_type: 'llm_inference',
        input_tokens: 60000,
        timestamp: Math.floor(Date.now() / 1000)
      })
    });
    const data = await res.json();
    alert(`Response (${res.status}): ${data.detail}`);
    updateQuota();
  });

  btnUpgrade.addEventListener('click', async () => {
    await fetch('/api/webhook/stripe?event_id=str_' + Date.now() + '&event_type=customer.subscription.updated&tenant_id=tenant_demo&plan_tier=pro', { method: 'POST' });
    alert('Tenant upgraded to PRO plan!');
    updateQuota();
  });

  btnCancel.addEventListener('click', async () => {
    await fetch('/api/webhook/stripe?event_id=str_' + Date.now() + '&event_type=customer.subscription.deleted&tenant_id=tenant_demo', { method: 'POST' });
    alert('Tenant reverted to FREE plan!');
    updateQuota();
  });

  btnInvoice.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/invoice/tenant_demo');
      const invoice = await res.json();
      invoiceCard.innerText = JSON.stringify(invoice, null, 2);
    } catch (e) {
      console.error(e);
    }
  });

  updateQuota();
});
