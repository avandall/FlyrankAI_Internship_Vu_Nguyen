document.addEventListener('DOMContentLoaded', () => {
  const btnAdapt = document.getElementById('btn-adapt');
  const twText = document.getElementById('tw-text');
  const liText = document.getElementById('li-text');
  const twCount = document.getElementById('tw-count');
  const liCount = document.getElementById('li-count');

  btnAdapt.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/adapt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          campaign_id: 'c_' + Date.now(),
          tenant_id: 'tenant_demo',
          title: document.getElementById('campaign-title').value,
          master_text: document.getElementById('campaign-text').value,
          target_platforms: ['twitter', 'linkedin']
        })
      });
      const data = await res.json();

      twText.innerText = data.variants.twitter.adapted_text;
      twCount.innerText = `${data.variants.twitter.character_count} / 280`;

      liText.innerText = data.variants.linkedin.adapted_text;
      liCount.innerText = `${data.variants.linkedin.character_count} / 3000`;
    } catch (e) {
      console.error(e);
    }
  });

  const btnIdempotency = document.getElementById('btn-idempotency');
  const idempotencyOutput = document.getElementById('idempotency-output');

  btnIdempotency.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idempotency_key: document.getElementById('idempotency-key').value,
          campaign_id: 'c_demo',
          platform: 'twitter',
          content: { platform: 'twitter', adapted_text: 'Test content', character_count: 12 }
        })
      });
      const data = await res.json();
      idempotencyOutput.classList.remove('hidden');
      idempotencyOutput.innerText = JSON.stringify(data, null, 2);
    } catch (e) {
      console.error(e);
    }
  });

  const btnHmac = document.getElementById('btn-hmac');
  const hmacOutput = document.getElementById('hmac-output');

  btnHmac.addEventListener('click', async () => {
    try {
      const signRes = await fetch('/api/webhook/sign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event: 'post.published', post_id: 'tw_1001' })
      });
      const signData = await signRes.json();

      const verifyRes = await fetch('/api/webhook/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signData.signed_webhook)
      });
      const verifyData = await verifyRes.json();

      hmacOutput.classList.remove('hidden');
      hmacOutput.innerText = `Signature: ${signData.signed_webhook.signature}\nVerification: ${verifyData.valid ? 'VALID' : 'INVALID'}`;
    } catch (e) {
      console.error(e);
    }
  });
});
