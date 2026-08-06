const API = '';

function showTab(name) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + name).classList.remove('hidden');
  document.querySelectorAll('.tab')[['match','upload','library','review','metrics'].indexOf(name)].classList.add('active');
  if (name === 'library') loadLibrary();
  if (name === 'review') loadReviews();
  if (name === 'metrics') loadMetrics();
  if (name === 'upload') loadCosts();
}

async function matchPost() {
  const post_id = 'post_' + Date.now();
  const title = document.getElementById('post-title').value;
  const text = document.getElementById('post-text').value;
  const target_subject = document.getElementById('target-subject').value || undefined;
  const target_category = document.getElementById('target-category').value || undefined;

  const el = document.getElementById('match-result');
  el.classList.remove('hidden');
  el.textContent = '⏳ Running semantic matching...';
  try {
    const query = new URLSearchParams({ title, text });
    if (target_subject) query.append('target_subject', target_subject);
    if (target_category) query.append('target_category', target_category);
    
    const r = await fetch(API + '/posts/' + post_id + '/images?' + query.toString(), {method:'GET'});
    const data = await r.json();
    const status = data.status;
    const icon = status === 'MATCHED' ? '✅' : status === 'REJECTED' ? '🚫' : '❓';
    el.innerHTML = `
      <div style="color: ${status==='MATCHED'?'var(--success)':status==='REJECTED'?'var(--danger)':'var(--warning)'}; font-weight:600; margin-bottom:0.5rem">
        ${icon} Status: ${status}
      </div>
      ${data.reject_reason ? `<div style="color:var(--warning)">⚠️ Reason: ${data.reject_reason}</div>` : ''}
      ${data.matched_image ? `
        <div style="margin-top:0.5rem">
          <strong>Best Match:</strong><br/>
          📁 ${data.matched_image.filename}<br/>
          🏷️ Subject: ${data.matched_image.subject} | ${data.matched_image.category}<br/>
          💬 ${data.matched_image.caption}<br/>
          📈 Similarity: ${(data.matched_image.similarity_score * 100).toFixed(1)}% | Confidence: ${(data.matched_image.confidence_score * 100).toFixed(0)}%
        </div>` : ''}
      <details style="margin-top:0.5rem"><summary style="cursor:pointer;color:var(--text-muted)">All candidates (${data.all_candidates?.length || 0})</summary>
        <pre style="font-size:0.75rem;overflow:auto;max-height:200px">${JSON.stringify(data.all_candidates, null, 2)}</pre>
      </details>`;
  } catch(e) { el.textContent = '❌ Error: ' + e.message; }
}

const SCENARIOS = {
  fox_correct: { title: 'The Cunning Red Fox of Northern Forests', text: 'Red foxes are fascinating creatures known for their agility and intelligence. The Vulpes vulpes species inhabits forests across the world.', target_subject: 'fox', target_category: 'animal' },
  wolf_blocked: { title: 'Red Fox Biology and Behavior', text: 'Foxes are smaller than wolves but equally cunning. The wolf and fox are both canids but diverged millions of years ago.', target_subject: 'fox', target_category: 'animal' },
  no_match: { title: 'Quantum Computing Breakthroughs in 2025', text: 'Superconducting qubits have reached new levels of coherence time, enabling practical quantum advantage over classical algorithms.', target_subject: undefined, target_category: undefined },
  mountain: { title: 'Hiking the High Alpine Peaks of Switzerland', text: 'The Swiss Alps offer some of the most breathtaking mountain scenery in the world, with peaks rising above 4000 meters.', target_subject: 'mountain', target_category: 'nature' },
};

async function testScenario(name) {
  const el = document.getElementById('scenario-result');
  el.classList.remove('hidden');
  el.textContent = '⏳ Testing scenario: ' + name + '...';
  const s = SCENARIOS[name];
  try {
    const query = new URLSearchParams({ title: s.title, text: s.text });
    if (s.target_subject) query.append('target_subject', s.target_subject);
    if (s.target_category) query.append('target_category', s.target_category);
    
    const r = await fetch(API + '/posts/test_' + name + '/images?' + query.toString(), {method:'GET'});
    const data = await r.json();
    const status = data.status;
    const icon = status === 'MATCHED' ? '✅' : status === 'REJECTED' ? '🚫' : '❓';
    el.innerHTML = `<strong>Scenario: ${name}</strong><br/>
      <span style="color:${status==='MATCHED'?'var(--success)':status==='REJECTED'?'var(--danger)':'var(--warning)'}">${icon} ${status}</span>
      ${data.reject_reason ? `<br/>⚠️ ${data.reject_reason}` : ''}
      ${data.matched_image ? `<br/>📁 → ${data.matched_image.filename} (sim: ${(data.matched_image.similarity_score*100).toFixed(1)}%)` : ''}`;
  } catch(e) { el.textContent = '❌ Error: ' + e.message; }
}

let selectedFile = null;
function handleFileSelect(e) {
  selectedFile = e.target.files[0];
  showPreview(selectedFile);
}
function handleDrop(e) {
  e.preventDefault();
  selectedFile = e.dataTransfer.files[0];
  showPreview(selectedFile);
}
function showPreview(file) {
  if (!file) return;
  document.getElementById('upload-preview').classList.remove('hidden');
  document.getElementById('preview-name').textContent = file.name + ' (' + (file.size/1024).toFixed(1) + ' KB)';
  const reader = new FileReader();
  reader.onload = e => document.getElementById('preview-img').src = e.target.result;
  reader.readAsDataURL(file);
}
async function submitUpload() {
  if (!selectedFile) return;
  const el = document.getElementById('upload-result');
  el.classList.remove('hidden');
  el.textContent = '⏳ Queuing Vision AI analysis...';
  const fd = new FormData();
  fd.append('file', selectedFile);
  try {
    const r = await fetch(API + '/api/ingest/upload', {method:'POST', body: fd});
    const data = await r.json();
    if (!r.ok) { el.textContent = '❌ ' + (data.detail || 'Upload failed'); return; }
    el.innerHTML = `✅ <strong>${data.image.filename}</strong> queued!<br/>
      ⏳ Status: ${data.status}<br/>
      <span class="text-muted" style="font-size:0.8rem">Image processed. Check Library to see it.</span>`;
    setTimeout(loadImageCount, 2000);
  } catch(e) { el.textContent = '❌ Error: ' + e.message; }
}

async function loadLibrary() {
  const el = document.getElementById('image-library-grid');
  el.innerHTML = '<p class="text-muted">Loading...</p>';
  try {
    const r = await fetch(API + '/api/images');
    const data = await r.json();
    el.innerHTML = data.images.map(img => `
      <div class="img-card ${img.is_flagged ? 'flagged' : ''}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem">
          <h5>${img.filename}</h5>
          ${img.is_flagged ? '<span class="badge badge-danger">⚠️ Flagged</span>' : '<span class="badge badge-success">✅</span>'}
        </div>
        <div style="font-size:0.75rem;color:var(--text-muted)">
          🏷️ ${img.subject} / ${img.category}<br/>
          📊 Confidence: ${(img.confidence_score*100).toFixed(0)}%<br/>
          📏 ${img.width}×${img.height}px<br/>
          💬 <em>${(img.caption||'').substring(0,80)}${img.caption?.length>80?'...':''}</em>
        </div>
        <div style="margin-top:0.5rem;display:flex;gap:0.25rem;flex-wrap:wrap">
          ${(img.attributes||[]).map(a => `<span style="background:#1E293B;padding:0.1rem 0.4rem;border-radius:4px;font-size:0.7rem">${a}</span>`).join('')}
        </div>
      </div>`).join('');
  } catch(e) { el.innerHTML = '<p style="color:var(--danger)">Error: ' + e.message + '</p>'; }
}

async function submitReview() {
  const body = {
    image_id: document.getElementById('review-image-id').value,
    post_id: document.getElementById('review-post-id').value,
    approved: document.getElementById('review-decision').value === 'true',
    reject_reason: document.getElementById('review-reason').value || null,
  };
  const el = document.getElementById('review-result');
  el.classList.remove('hidden');
  try {
    const r = await fetch(API + '/images/review', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    const data = await r.json();
    el.innerHTML = `✅ Review submitted! ID: ${data.review_id}<br/>Decision: ${data.approved ? '✅ Approved' : '❌ Rejected'}`;
    loadReviews();
  } catch(e) { el.textContent = '❌ Error: ' + e.message; }
}

async function loadReviews() {
  const el = document.getElementById('reviews-list');
  try {
    const r = await fetch(API + '/images/reviews');
    const data = await r.json();
    if (!data.reviews.length) { el.innerHTML = '<p class="text-muted">No reviews yet.</p>'; return; }
    el.innerHTML = data.reviews.map(rv => `
      <div class="review-item">
        <div style="display:flex;justify-content:space-between">
          <span style="font-size:0.85rem;font-weight:600">${rv.image_id}</span>
          <span class="badge ${rv.approved ? 'badge-success' : 'badge-danger'}">${rv.approved ? '✅ Approved' : '❌ Rejected'}</span>
        </div>
        <div style="font-size:0.75rem;color:var(--text-muted)">Post: ${rv.post_id} · By: ${rv.reviewer}
        ${rv.reject_reason ? '<br/>Reason: ' + rv.reject_reason : ''}</div>
      </div>`).join('');
  } catch(e) { el.innerHTML = '<p style="color:var(--danger)">Error</p>'; }
}

async function loadMetrics() {
  try {
    const [precR, costR] = await Promise.all([fetch(API+'/metrics/precision'), fetch(API+'/api/costs')]);
    const prec = await precR.json();
    const cost = await costR.json();
    
    document.getElementById('precision-stats').innerHTML = `
      <div class="metric-big">${prec.precision_percent}</div>
      <p style="color:var(--text-muted);margin:0.5rem 0">Top-1 Precision</p>
      <div class="metric-row"><span>Total Reviews</span><span>${prec.total_reviews}</span></div>`;
    
    document.getElementById('cost-stats').innerHTML = `
      <div class="metric-big">${cost.total_cost_usd}</div>
      <p style="color:var(--text-muted);margin:0.5rem 0">Total AI API Cost (simulated)</p>
      ${Object.entries(cost.by_status||{}).map(([s, v]) => `
        <div class="metric-row"><span>${s}</span><span>${v.count} jobs / $${(v.cost_micro_usd/1000000).toFixed(6)}</span></div>`).join('')}`;
  } catch(e) { console.error(e); }
}

async function loadCosts() {
  try {
    const r = await fetch(API + '/api/costs');
    const data = await r.json();
    document.getElementById('cost-info').innerHTML = `
      <div style="background:#0D1421;border:1px solid var(--border);border-radius:8px;padding:0.75rem;font-size:0.8rem">
        💰 Total AI Cost: <strong>${data.total_cost_usd}</strong> · 
        ${Object.entries(data.by_status||{}).map(([s,v]) => `${s}: ${v.count}`).join(' · ')}
      </div>`;
  } catch(e) {}
}

async function loadImageCount() {
  try {
    const r = await fetch(API + '/api/images');
    const data = await r.json();
    document.getElementById('img-count').textContent = data.images.length + ' images in library';
  } catch(e) {}
}

loadImageCount();
