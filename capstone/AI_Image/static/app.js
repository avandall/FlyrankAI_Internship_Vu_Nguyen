document.addEventListener('DOMContentLoaded', () => {
  const imgGrid = document.getElementById('image-grid');
  const btnMatch = document.getElementById('btn-match');
  const resultBox = document.getElementById('result-box');
  const statusBadge = document.getElementById('status-badge');
  const reasonText = document.getElementById('reason-text');
  const jsonDetails = document.getElementById('json-details');

  async function loadImages() {
    try {
      const res = await fetch('/api/images');
      const images = await res.json();
      imgGrid.innerHTML = '';
      images.forEach(img => {
        const card = document.createElement('div');
        card.className = 'img-card';
        card.innerHTML = `
          <div class="badge ${img.is_flagged ? 'badge-danger' : 'badge-success'}">${img.is_flagged ? 'FLAGGED (<0.70)' : 'VALID'}</div>
          <h5 style="margin-top: 0.4rem">${img.subject.toUpperCase()}</h5>
          <p><strong>Category:</strong> ${img.category}</p>
          <p><strong>Conf:</strong> ${img.confidence_score}</p>
        `;
        imgGrid.appendChild(card);
      });
    } catch (e) {
      console.error(e);
    }
  }

  btnMatch.addEventListener('click', async () => {
    const post = {
      post_id: 'p_' + Date.now(),
      title: document.getElementById('post-title').value,
      text: document.getElementById('post-text').value,
      target_subject: document.getElementById('post-subject').value,
      target_category: document.getElementById('post-category').value
    };

    try {
      const res = await fetch('/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(post)
      });
      const data = await res.json();

      resultBox.classList.remove('hidden');

      if (data.status === 'MATCHED') {
        statusBadge.className = 'badge badge-success';
        statusBadge.innerText = '✅ MATCHED: ' + data.matched_image.subject;
        reasonText.innerText = `Matched file: ${data.matched_image.filename} (Score: ${data.matched_image.similarity_score})`;
      } else if (data.status === 'REJECTED') {
        statusBadge.className = 'badge badge-danger';
        statusBadge.innerText = '🛑 REJECTED BY MISMATCH GUARD';
        reasonText.innerText = data.reject_reason;
      } else {
        statusBadge.className = 'badge badge-warning';
        statusBadge.innerText = '⚠️ NO CONFIDENT MATCH';
        reasonText.innerText = data.reject_reason || 'Below threshold';
      }

      jsonDetails.innerText = JSON.stringify(data, null, 2);
    } catch (e) {
      console.error(e);
    }
  });

  loadImages();
});
