// ── Hamburger menu ──
const menuBtn = document.getElementById('menu-button');
const navMenu = document.getElementById('nav-menu');

if (menuBtn && navMenu) {
  // add inner span for middle bar
  menuBtn.innerHTML = '<span></span>';
  menuBtn.addEventListener('click', () => {
    navMenu.classList.toggle('open');
  });
}

// ── Current year in footer ──
const yearEl = document.getElementById('current-year');
if (yearEl) yearEl.textContent = new Date().getFullYear() + ' ';

// ── Active nav link ──
const currentPage = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('nav a').forEach(a => {
  a.classList.remove('active');
  if (a.getAttribute('href') === currentPage) a.classList.add('active');
});

// ── Solutions page: load cards + filter + modal ──
const container = document.getElementById('class-schedule-container');
const modal     = document.getElementById('class-details-modal');
const closeBtn  = document.getElementById('modal-close-button');

if (container && modal) {
  let allSolutions = [];

  // ── Fetch & render ──
  async function loadSolutions() {
    try {
      const res  = await fetch('data/solutions.json');
      const data = await res.json();
      allSolutions = data;
      buildFilterBar(data);
      renderCards(data);
    } catch (err) {
      container.innerHTML = '<p style="color:var(--muted);text-align:center;padding:2rem;">Could not load solutions.</p>';
    }
  }

  // ── Build dynamic filter buttons ──
  function buildFilterBar(data) {
    const impacts = ['All', ...new Set(data.map(s => s.impact))];
    const bar = document.createElement('div');
    bar.className = 'filter-bar';

    impacts.forEach(impact => {
      const btn = document.createElement('button');
      btn.className = 'filter-btn' + (impact === 'All' ? ' active' : '');
      btn.textContent = impact;
      btn.dataset.filter = impact;
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filtered = impact === 'All' ? data : data.filter(s => s.impact === impact);
        renderCards(filtered);
      });
      bar.appendChild(btn);
    });

    container.before(bar);
  }

  // ── Render card grid ──
  function renderCards(solutions) {
    container.innerHTML = '';
    if (!solutions.length) {
      container.innerHTML = '<p style="color:var(--muted);text-align:center;padding:2rem;grid-column:1/-1;">No solutions found.</p>';
      return;
    }
    solutions.forEach(s => {
      const card = document.createElement('article');
      card.className = 'solution-card';
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      card.setAttribute('aria-label', `View details for ${s.name}`);
      card.innerHTML = `
        <img src="${s.image}" alt="${s.name}" loading="lazy" onerror="this.src='images/placeholder.png'">
        <div class="card-body">
          <span class="card-category">${s.category}</span>
          <h3 class="card-name">${s.name}</h3>
          <span class="card-impact">${s.impact}</span>
          <p class="card-desc">${s.description.slice(0, 90)}…</p>
          <p class="card-more-btn">Learn more →</p>
        </div>`;

      const openModal = () => showModal(s);
      card.addEventListener('click', openModal);
      card.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') openModal(); });
      container.appendChild(card);
    });
  }

  // ── Show modal with solution details ──
  function showModal(s) {
    document.getElementById('modal-img').src         = s.image;
    document.getElementById('modal-img').alt         = s.name;
    document.getElementById('modal-img').onerror     = function(){ this.src='images/placeholder.png'; };
    document.getElementById('modal-title').textContent         = s.name;
    document.getElementById('modal-business-impact').textContent = s.impact;
    document.getElementById('modal-rating').textContent        = s.rating ?? '⭐⭐⭐⭐';
    document.getElementById('modal-industry').textContent      = s.industry;
    document.getElementById('modal-technology').textContent    = s.technology;
    document.getElementById('modal-benefit').textContent       = s.benefit;
    document.getElementById('modal-description').textContent   = s.description;
    modal.showModal();
  }

  // ── Close modal ──
  closeBtn?.addEventListener('click', () => modal.close());
  modal?.addEventListener('click', e => { if (e.target === modal) modal.close(); });

  loadSolutions();
}

// ── Thank-you page: display submitted params ──
if (document.querySelector('.thank-you-section')) {
  const params = new URLSearchParams(location.search);
  const nameEl = document.getElementById('submitted-name');
  const svcEl  = document.getElementById('submitted-service');
  if (nameEl && params.get('fullName')) nameEl.textContent = params.get('fullName');
  if (svcEl  && params.get('interest'))  svcEl.textContent  = params.get('interest').replace(/-/g, ' ');
}