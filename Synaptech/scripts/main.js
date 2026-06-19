// ── Hamburger menu ──
const menuBtn = document.getElementById('menu-button');
const navMenu = document.getElementById('nav-menu');

if (menuBtn && navMenu) {
  menuBtn.innerHTML = '<span></span>';
  menuBtn.addEventListener('click', () => {
    navMenu.classList.toggle('open');
    menuBtn.classList.toggle('open');
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

// ── LANGUAGE SYSTEM ──
const translations = {
  en: {
    nav_home: 'Home',
    nav_solutions: 'Solutions',
    nav_contact: 'Contact',
    hero_title: 'AI Automation for Modern Businesses',
    hero_desc: 'Helping companies reduce manual work, improve customer experiences, and scale operations through AI-powered systems and intelligent automation.',
    hero_cta: 'Schedule a Consultation',
    about_title: 'About Synaptech',
    about_p1: 'Synaptech is an AI automation and business intelligence company focused on helping organizations operate more efficiently through technology.',
    about_p2: 'We specialize in AI agents, workflow automation, system integrations, data intelligence, and operational systems that reduce repetitive work and improve business performance.',
    about_p3: 'Our solutions help businesses optimize sales processes, customer support, onboarding experiences, lead management, and internal operations through practical applications of artificial intelligence.',
    mission_title: 'Our Mission',
    mission_desc: 'To help businesses eliminate repetitive work and unlock growth through intelligent automation, AI solutions, and connected systems.',
    vision_title: 'Our Vision',
    vision_desc: 'To become a trusted technology partner for companies seeking innovation, efficiency, scalability, and better decision-making through artificial intelligence.',
    services_title: 'Our Solutions',
    s1_title: 'AI Agents',
    s1_desc: 'Intelligent virtual assistants for customer support, lead qualification, appointment scheduling, and internal business tasks.',
    s2_title: 'Workflow Automation',
    s2_desc: 'Automate repetitive tasks and create seamless workflows between teams, departments, and software platforms.',
    s3_title: 'System Integrations',
    s3_desc: 'Connect CRMs, communication platforms, databases, spreadsheets, and operational systems into one ecosystem.',
    s4_title: 'Data Intelligence',
    s4_desc: 'Transform business data into actionable insights through dashboards, reporting, and AI-powered analytics.',
    why_title: 'Why Choose Synaptech?',
    why_p1: 'We focus on practical solutions that generate measurable results. Instead of adding complexity, we build systems that simplify operations, improve efficiency, and allow teams to focus on strategic work.',
    why_p2: "Whether you're looking to automate customer support, improve your sales pipeline, connect business systems, or gain better visibility into your data, Synaptech provides solutions tailored to your business goals.",
    solutions_page_title: 'Our Solutions',
    solutions_page_desc: 'Explore the automation, AI, integration, and business intelligence solutions offered by Synaptech. Click any card to learn more.',
    filter_all: 'All',
    learn_more: 'Learn more →',
    modal_impact: 'Business Impact',
    modal_rating: 'Rating',
    modal_industry: 'Industry',
    modal_technology: 'Technology',
    modal_benefit: 'Benefit',
    contact_page_title: "Let's Discuss Your Business Goals",
    contact_page_desc: "Whether you're looking to automate workflows, improve customer support, integrate business systems, or gain better insights from your data, Synaptech can help.",
    form_legend1: 'Your Information',
    form_company: 'Company Name',
    form_name: 'Full Name *',
    form_email: 'Email *',
    form_phone: 'Phone Number',
    form_legend2: 'Your Message',
    form_interest: "I'm interested in…",
    form_select: 'Select a Service',
    form_opt1: 'AI Agents',
    form_opt2: 'Workflow Automation',
    form_opt3: 'System Integrations',
    form_opt4: 'Data Intelligence',
    form_opt5: 'Customer Support Automation',
    form_opt6: 'Sales Process Optimization',
    form_opt7: 'General Consultation',
    form_message: 'Tell us about your business needs *',
    form_placeholder: 'Describe your current challenges, goals, or processes you would like to automate.',
    form_submit: 'Request Consultation',
    footer_text: 'Synaptech | AI Automation & Business Intelligence | Matheus O. Malaquias',
  },
  pt: {
    nav_home: 'Início',
    nav_solutions: 'Soluções',
    nav_contact: 'Contato',
    hero_title: 'Automação com IA para Empresas Modernas',
    hero_desc: 'Ajudamos empresas a reduzir trabalho manual, melhorar a experiência do cliente e escalar operações com sistemas inteligentes de automação.',
    hero_cta: 'Agendar uma Consulta',
    about_title: 'Sobre a Synaptech',
    about_p1: 'A Synaptech é uma empresa de automação com IA e inteligência de negócios focada em ajudar organizações a operar com mais eficiência através da tecnologia.',
    about_p2: 'Somos especializados em agentes de IA, automação de fluxos de trabalho, integrações de sistemas, inteligência de dados e sistemas operacionais que reduzem trabalho repetitivo e melhoram a performance.',
    about_p3: 'Nossas soluções ajudam empresas a otimizar processos de vendas, suporte ao cliente, onboarding, gestão de leads e operações internas através de aplicações práticas de inteligência artificial.',
    mission_title: 'Nossa Missão',
    mission_desc: 'Ajudar empresas a eliminar trabalho repetitivo e desbloquear crescimento por meio de automação inteligente, soluções de IA e sistemas conectados.',
    vision_title: 'Nossa Visão',
    vision_desc: 'Tornar-nos um parceiro tecnológico de confiança para empresas que buscam inovação, eficiência, escalabilidade e melhores decisões através da inteligência artificial.',
    services_title: 'Nossas Soluções',
    s1_title: 'Agentes de IA',
    s1_desc: 'Assistentes virtuais inteligentes para suporte ao cliente, qualificação de leads, agendamento e tarefas internas.',
    s2_title: 'Automação de Fluxos',
    s2_desc: 'Automatize tarefas repetitivas e crie fluxos contínuos entre equipes, departamentos e plataformas de software.',
    s3_title: 'Integrações de Sistemas',
    s3_desc: 'Conecte CRMs, plataformas de comunicação, bancos de dados, planilhas e sistemas operacionais em um único ecossistema.',
    s4_title: 'Inteligência de Dados',
    s4_desc: 'Transforme dados de negócios em insights acionáveis através de dashboards, relatórios e análises com IA.',
    why_title: 'Por que escolher a Synaptech?',
    why_p1: 'Focamos em soluções práticas que geram resultados mensuráveis. Em vez de adicionar complexidade, construímos sistemas que simplificam operações, melhoram a eficiência e permitem que as equipes se concentrem no trabalho estratégico.',
    why_p2: 'Seja para automatizar suporte ao cliente, melhorar seu pipeline de vendas, conectar sistemas de negócios ou ter melhor visibilidade dos seus dados, a Synaptech oferece soluções sob medida para seus objetivos.',
    solutions_page_title: 'Nossas Soluções',
    solutions_page_desc: 'Explore as soluções de automação, IA, integração e inteligência de negócios da Synaptech. Clique em qualquer card para saber mais.',
    filter_all: 'Todos',
    learn_more: 'Saiba mais →',
    modal_impact: 'Impacto no Negócio',
    modal_rating: 'Avaliação',
    modal_industry: 'Setor',
    modal_technology: 'Tecnologia',
    modal_benefit: 'Benefício',
    contact_page_title: 'Vamos Conversar sobre seus Objetivos',
    contact_page_desc: 'Se você quer automatizar fluxos, melhorar o suporte, integrar sistemas ou ter mais visibilidade dos seus dados, a Synaptech pode ajudar.',
    form_legend1: 'Suas Informações',
    form_company: 'Nome da Empresa',
    form_name: 'Nome Completo *',
    form_email: 'E-mail *',
    form_phone: 'Telefone',
    form_legend2: 'Sua Mensagem',
    form_interest: 'Tenho interesse em…',
    form_select: 'Selecione um Serviço',
    form_opt1: 'Agentes de IA',
    form_opt2: 'Automação de Fluxos',
    form_opt3: 'Integrações de Sistemas',
    form_opt4: 'Inteligência de Dados',
    form_opt5: 'Automação de Suporte ao Cliente',
    form_opt6: 'Otimização de Processos de Vendas',
    form_opt7: 'Consulta Geral',
    form_message: 'Conte-nos sobre as necessidades do seu negócio *',
    form_placeholder: 'Descreva seus desafios atuais, objetivos ou processos que deseja automatizar.',
    form_submit: 'Solicitar Consulta',
    footer_text: 'Synaptech | Automação com IA & Inteligência de Negócios | Matheus O. Malaquias',
  }
};

function applyLanguage(lang) {
  const t = translations[lang];
  if (!t) return;
  localStorage.setItem('synaptech-lang', lang);

  // Atualiza botão
  const btn = document.getElementById('lang-toggle');
  if (btn) btn.textContent = lang === 'en' ? '🇧🇷 PT' : '🇺🇸 EN';

  // Nav links
  const navLinks = document.querySelectorAll('nav a');
  const navKeys = ['nav_home', 'nav_solutions', 'nav_contact'];
  navLinks.forEach((a, i) => { if (navKeys[i]) a.textContent = t[navKeys[i]]; });

  // Todos os elementos com data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (t[key] === undefined) return;
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      el.placeholder = t[key];
    } else if (el.tagName === 'OPTION') {
      el.textContent = t[key];
    } else {
      el.textContent = t[key];
    }
  });

  // Footer
  const footerP = document.querySelector('footer p');
  if (footerP) {
    const year = new Date().getFullYear();
    footerP.innerHTML = `&copy; ${year} ${t.footer_text}`;
  }

  // Recarrega cards na página de soluções
  if (typeof renderCards === 'function' && typeof allSolutions !== 'undefined' && allSolutions.length) {
    buildFilterBar(allSolutions);
    renderCards(allSolutions);
  }
}

// ── Init language ──
const savedLang = localStorage.getItem('synaptech-lang') || 'en';
applyLanguage(savedLang);

const langBtn = document.getElementById('lang-toggle');
if (langBtn) {
  langBtn.addEventListener('click', () => {
    const current = localStorage.getItem('synaptech-lang') || 'en';
    applyLanguage(current === 'en' ? 'pt' : 'en');
  });
}

// ── Solutions page: load cards + filter + modal ──
const container = document.getElementById('class-schedule-container');
const modal     = document.getElementById('class-details-modal');
const closeBtn  = document.getElementById('modal-close-button');

if (container && modal) {
  let allSolutions = [];

  async function loadSolutions() {
    try {
      const res  = await fetch('./data/solutions.json');
      const data = await res.json();
      allSolutions = data;
      buildFilterBar(data);
      renderCards(data);
    } catch (err) {
      container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:2rem;">Could not load solutions.</p>';
    }
  }

  function buildFilterBar(data) {
    const existing = document.querySelector('.filter-bar');
    if (existing) existing.remove();
    const lang = localStorage.getItem('synaptech-lang') || 'en';
    const t = translations[lang];
    const impacts = [t.filter_all, ...new Set(data.map(s => s.impact))];
    const bar = document.createElement('div');
    bar.className = 'filter-bar';
    impacts.forEach((impact, i) => {
      const btn = document.createElement('button');
      btn.className = 'filter-btn' + (i === 0 ? ' active' : '');
      btn.textContent = impact;
      btn.dataset.filter = i === 0 ? 'all' : impact;
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filtered = i === 0 ? data : data.filter(s => s.impact === impact);
        renderCards(filtered);
      });
      bar.appendChild(btn);
    });
    container.before(bar);
  }

  function renderCards(solutions) {
    const lang = localStorage.getItem('synaptech-lang') || 'en';
    const t = translations[lang];
    container.innerHTML = '';
    if (!solutions.length) {
      container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:2rem;grid-column:1/-1;">No solutions found.</p>';
      return;
    }
    solutions.forEach(s => {
      const name = lang === 'pt' && s.name_pt ? s.name_pt : s.name;
      const desc = lang === 'pt' && s.description_pt ? s.description_pt : s.description;
      const card = document.createElement('article');
      card.className = 'solution-card';
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      card.setAttribute('aria-label', `View details for ${name}`);
      card.innerHTML = `
        <img src="${s.image}" alt="${name}" loading="lazy" onerror="this.src='images/synaptech.png'">
        <div class="card-body">
          <span class="card-category">${s.category}</span>
          <h3 class="card-name">${name}</h3>
          <span class="card-impact">${s.impact}</span>
          <p class="card-desc">${desc.slice(0, 90)}…</p>
          <p class="card-more-btn">${t.learn_more}</p>
        </div>`;
      const openModal = () => showModal(s);
      card.addEventListener('click', openModal);
      card.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') openModal(); });
      container.appendChild(card);
    });
  }

  function showModal(s) {
    const lang = localStorage.getItem('synaptech-lang') || 'en';
    const t = translations[lang];
    const name = lang === 'pt' && s.name_pt ? s.name_pt : s.name;
    const desc = lang === 'pt' && s.description_pt ? s.description_pt : s.description;
    const benefit = lang === 'pt' && s.benefit_pt ? s.benefit_pt : s.benefit;
    document.getElementById('modal-img').src = s.image;
    document.getElementById('modal-img').alt = name;
    document.getElementById('modal-img').onerror = function(){ this.src='images/synaptech.png'; };
    document.getElementById('modal-title').textContent = name;
    document.getElementById('modal-business-impact').textContent = s.impact;
    document.getElementById('modal-rating').textContent = s.rating ?? '⭐⭐⭐⭐';
    document.getElementById('modal-industry').textContent = s.industry;
    document.getElementById('modal-technology').textContent = s.technology;
    document.getElementById('modal-benefit').textContent = benefit;
    document.getElementById('modal-description').textContent = desc;
    document.querySelector('[data-i18n="modal_impact"]').textContent = t.modal_impact + ':';
    document.querySelector('[data-i18n="modal_rating"]').textContent = t.modal_rating + ':';
    document.querySelector('[data-i18n="modal_industry"]').textContent = t.modal_industry + ':';
    document.querySelector('[data-i18n="modal_technology"]').textContent = t.modal_technology + ':';
    document.querySelector('[data-i18n="modal_benefit"]').textContent = t.modal_benefit + ':';
    modal.showModal();
  }

  closeBtn?.addEventListener('click', () => modal.close());
  modal?.addEventListener('click', e => { if (e.target === modal) modal.close(); });
  loadSolutions();
}

// ── Thank-you page ──
if (document.querySelector('.thankyou-section')) {
  const params = new URLSearchParams(location.search);
  const nameEl = document.getElementById('submitted-name');
  const svcEl  = document.getElementById('submitted-service');
  if (nameEl && params.get('fullName')) nameEl.textContent = params.get('fullName');
  if (svcEl  && params.get('interest'))  svcEl.textContent = params.get('interest').replace(/-/g, ' ');
}