// ── Hamburger menu ──
const menuBtn = document.getElementById('menu-button');
const navMenu = document.getElementById('nav-menu');
const navEl   = document.querySelector('nav');

if (menuBtn && navMenu) {
  menuBtn.addEventListener('click', () => {
    navMenu.classList.toggle('open');
    menuBtn.classList.toggle('open');
    navEl.classList.toggle('open');
  });
}

// ── Current year in footer ──
const yearEl = document.getElementById('current-year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

// ── Active nav link ──
const currentPage = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('nav a').forEach(a => {
  a.classList.remove('active');
  if (a.getAttribute('href') === currentPage) a.classList.add('active');
});

// ══════════════════════════════════════════
// LANGUAGE SYSTEM
// ══════════════════════════════════════════
const translations = {
  en: {
    nav_home: 'Home',
    nav_solutions: 'Solutions',
    nav_contact: 'Contact',

    // Hero
    eyebrow_label: 'AI Automation · Built for Real Businesses',
    hero_title: 'We Automate the Work Your Team Shouldn\'t Be Doing',
    hero_desc: 'Synaptech builds practical AI systems — WhatsApp agents, process automations, and intelligent integrations — that reduce manual work and free your team to focus on what actually moves the business forward.',
    hero_cta: 'Talk to Us',
    hero_cta2: 'See Our Work',

    // Stats — specific impact per project
    stat1_num: '−15min', stat1_label: 'Per sale eliminated by SalesSync',
    stat2_num: '24/7',   stat2_label: 'Patient support — no receptionist needed',
    stat3_num: '3min',   stat3_label: 'From WhatsApp message to scheduled visit',
    stat4_num: 'Days',   stat4_label: 'To go live — not months',

    // About
    about_title: 'What Synaptech Does',
    about_p1: 'We don\'t sell software packages. We build systems tailored to how your business actually works — connecting your tools, automating your bottlenecks, and deploying AI where it creates real impact.',
    about_p2: 'Our work spans WhatsApp intelligent agents, sales process automation, clinic scheduling systems, and field service coordination — all built with the same philosophy: if your team is doing something repetitive, a machine should be doing it instead.',
    about_p3: 'We use n8n, Claude AI, and modern integration platforms to build solutions that are fast to implement, easy to maintain, and built to scale with your operation.',

    // Mission & Vision
    mission_title: 'Our Mission',
    mission_desc: 'To eliminate repetitive work from every business we touch — replacing manual processes with intelligent systems that run quietly in the background, 24 hours a day.',
    vision_title: 'Our Vision',
    vision_desc: 'A future where small and mid-sized businesses operate with the same AI leverage as large enterprises — without needing a tech team to make it happen.',

    // Second Mind
    mind_eyebrow: 'Neural Network · Processing',
    mind_title: 'A Second Mind Working for You',
    mind_desc: 'While your team handles strategy and relationships, our AI layer runs quietly in the background — qualifying leads, updating systems, answering clients, and making decisions based on the rules you set.',
    mind_stat1: 'connections',
    mind_stat2: 'signals/s',
    mind_stat3: 'active nodes',

    // Projects
    proj_title: 'Our Solutions',
    proj_sub: 'Three ready-to-deploy systems built for real operational problems. Each one can be adapted to your business in days, not months.',

    p1_tag: 'Sales Operations',
    p1_headline: 'Automatic Sales Note Entry — No More Manual Typing',
    p1_desc: 'Every time a sale is closed, SalesSync automatically registers the sales note in your system — pulling data from the sale, filling in the fields, and confirming the entry. Your team stops touching a keyboard and starts closing more deals.',
    p1_result: 'Eliminates manual data entry after every sale',
    p1_tech: 'n8n · CRM Integration · Custom API',

    p2_tag: 'Healthcare',
    p2_headline: 'Intelligent WhatsApp Agent for Clinics — No Receptionist Needed After Hours',
    p2_desc: 'ClinicBot answers patients on WhatsApp at any hour — confirming appointments, collecting symptoms, sending reminders, and escalating to a human when needed. Your clinic is always available, even when your team isn\'t.',
    p2_result: 'Handles scheduling and patient triage automatically',
    p2_tech: 'WhatsApp API · Claude AI · n8n',

    p3_tag: 'Field Services',
    p3_headline: 'Technical Visit Scheduling via WhatsApp — From Request to Calendar in Minutes',
    p3_desc: 'FieldBot receives a visit request on WhatsApp, qualifies the service type, checks technician availability, and confirms the appointment — all automatically. Your operations team sees a filled calendar without a single phone call.',
    p3_result: 'Schedules field visits with zero manual coordination',
    p3_tech: 'WhatsApp API · Claude AI · n8n · Calendar Integration',

    // Chat teaser
    teaser_title: 'See It Working',
    teaser_desc: 'This is what a real conversation with ClinicBot looks like. The patient books an appointment, gets a confirmation, and your system is updated — all without anyone on your team lifting a finger.',
    teaser_cta: 'Build Your Agent',
    chat_header: 'ClinicBot · Online',
    demo_msg1: 'Hi! I\'d like to schedule an appointment with Dr. Silva.',
    demo_reply1: 'Of course! Dr. Silva has availability on Thursday at 2 PM or Friday at 10 AM. Which works better for you?',
    demo_msg2: 'Thursday at 2 PM please.',
    demo_msg2_reply: 'Done! ✅ Appointment confirmed for Thursday at 2 PM with Dr. Silva. You\'ll receive a reminder 24 hours before. See you then!',

    // Tools
    tools_label: 'Built with',

    // Why
    why_title: 'Why Synaptech',
    why_p1: 'We don\'t start with a tool and look for a problem to apply it to. We start with your operation, find where time and money are being wasted on repetitive work, and build the most practical solution to fix it.',
    why_p2: 'Every system we deliver is yours — documented, maintained, and built so your team understands what it does. No black boxes, no vendor lock-in.',

    // Solutions page
    sol_hero_title: 'Our Solutions',
    sol_hero_sub: 'Three systems. Three real problems solved. Each one ready to adapt to your business in days, not months.',
    sol_cta_title: 'Don\'t See Exactly What You Need?',
    sol_cta_desc: 'We don\'t start with a tool and look for a problem to apply it to. Tell us what your team does manually every day, and we\'ll build the right solution for it.',

    // Contact page
    con_title: 'Let\'s Talk About Your Operation',
    con_desc: 'Tell us what your team is spending time on that a machine should be doing instead. We\'ll come back with a concrete proposal.',
    form_legend1: 'Your Information',
    form_name: 'Full Name *',
    form_email: 'Email *',
    form_company: 'Company Name',
    form_phone: 'Phone / WhatsApp',
    form_legend2: 'Your Challenge',
    form_int: 'Which solution interests you most?',
    form_sel: 'Select one',
    f1: 'SalesSync — Sales Note Automation',
    f2: 'ClinicBot — WhatsApp Agent for Clinics',
    f3: 'FieldBot — Technical Visit Scheduling',
    f4: 'Something else — I\'ll describe below',
    form_msg: 'What does your team do manually today that you\'d like to automate? *',
    form_ph: 'Example: every time we close a sale, someone has to manually enter the data in our system. It takes 15 minutes per sale and we close 20 a day.',
    form_sub: 'Send Message',

    // Thank you
    ty_title: 'Message Received.',
    ty_sub: 'We\'ll review what you sent and come back with a concrete proposal — usually within 1 business day.',
    ty_back: 'Back to Home',

    footer_text: 'Synaptech | AI Automation & Business Intelligence | Matheus O. Malaquias',
  },

  pt: {
    nav_home: 'Início',
    nav_solutions: 'Soluções',
    nav_contact: 'Contato',

    // Hero
    eyebrow_label: 'Automação com IA · Para Negócios Reais',
    hero_title: 'Automatizamos o Trabalho Que Sua Equipe Não Deveria Estar Fazendo',
    hero_desc: 'A Synaptech constrói sistemas práticos de IA — agentes no WhatsApp, automações de processos e integrações inteligentes — que eliminam trabalho manual e liberam sua equipe para focar no que realmente move o negócio.',
    hero_cta: 'Fale Conosco',
    hero_cta2: 'Ver Soluções',

    // Stats
    stat1_num: '−15min', stat1_label: 'Por venda eliminados pelo SalesSync',
    stat2_num: '24/7',   stat2_label: 'Atendimento ao paciente — sem recepcionista',
    stat3_num: '3min',   stat3_label: 'Do WhatsApp ao agendamento confirmado',
    stat4_num: 'Dias',   stat4_label: 'Para entrar em produção — não meses',

    // About
    about_title: 'O Que a Synaptech Faz',
    about_p1: 'Não vendemos pacotes de software. Construímos sistemas sob medida para como o seu negócio realmente funciona — conectando suas ferramentas, automatizando seus gargalos e aplicando IA onde gera impacto real.',
    about_p2: 'Nosso trabalho abrange agentes inteligentes no WhatsApp, automação de processos de venda, sistemas de agendamento para clínicas e coordenação de visitas técnicas — tudo com a mesma filosofia: se sua equipe faz algo repetitivo, uma máquina deveria estar fazendo no lugar dela.',
    about_p3: 'Usamos n8n, Claude AI e plataformas modernas de integração para criar soluções rápidas de implementar, fáceis de manter e prontas para crescer com sua operação.',

    // Mission & Vision
    mission_title: 'Nossa Missão',
    mission_desc: 'Eliminar o trabalho repetitivo de cada negócio que atendemos — substituindo processos manuais por sistemas inteligentes que rodam em silêncio, 24 horas por dia.',
    vision_title: 'Nossa Visão',
    vision_desc: 'Um futuro onde pequenas e médias empresas operam com o mesmo poder de IA que grandes corporações — sem precisar de um time de tecnologia para isso acontecer.',

    // Second Mind
    mind_eyebrow: 'Rede Neural · Processando',
    mind_title: 'Uma Segunda Mente Trabalhando por Você',
    mind_desc: 'Enquanto sua equipe cuida de estratégia e relacionamentos, nossa camada de IA roda em segundo plano — qualificando leads, atualizando sistemas, respondendo clientes e tomando decisões com base nas regras que você definiu.',
    mind_stat1: 'conexões',
    mind_stat2: 'sinais/s',
    mind_stat3: 'nós ativos',

    // Projects
    proj_title: 'Nossas Soluções',
    proj_sub: 'Três sistemas prontos para implantar, construídos para problemas operacionais reais. Cada um pode ser adaptado ao seu negócio em dias, não meses.',

    p1_tag: 'Operações de Venda',
    p1_headline: 'Lançamento Automático de Notas de Venda — Sem Digitação Manual',
    p1_desc: 'A cada venda fechada, o SalesSync lança automaticamente a nota de venda no sistema — buscando os dados da negociação, preenchendo os campos e confirmando o registro. Sua equipe para de digitar e começa a vender mais.',
    p1_result: 'Elimina o lançamento manual após cada venda',
    p1_tech: 'n8n · Integração CRM · API Personalizada',

    p2_tag: 'Saúde',
    p2_headline: 'Agente Inteligente no WhatsApp para Clínicas — Sem Recepcionista Fora do Horário',
    p2_desc: 'O ClinicBot atende pacientes no WhatsApp a qualquer hora — confirmando consultas, coletando sintomas, enviando lembretes e escalando para um humano quando necessário. Sua clínica está sempre disponível, mesmo quando sua equipe não está.',
    p2_result: 'Gerencia agendamentos e triagem de pacientes automaticamente',
    p2_tech: 'WhatsApp API · Claude AI · n8n',

    p3_tag: 'Serviços em Campo',
    p3_headline: 'Agendamento de Visitas Técnicas pelo WhatsApp — Do Pedido ao Calendário em Minutos',
    p3_desc: 'O FieldBot recebe o pedido de visita no WhatsApp, qualifica o tipo de serviço, verifica a disponibilidade do técnico e confirma o agendamento — tudo automaticamente. Sua equipe de operações vê a agenda preenchida sem fazer nenhuma ligação.',
    p3_result: 'Agenda visitas técnicas com zero coordenação manual',
    p3_tech: 'WhatsApp API · Claude AI · n8n · Integração de Calendário',

    // Chat teaser
    teaser_title: 'Veja Funcionando',
    teaser_desc: 'Assim é uma conversa real com o ClinicBot. O paciente marca a consulta, recebe a confirmação e seu sistema é atualizado — tudo sem sua equipe levantar um dedo.',
    teaser_cta: 'Construir Meu Agente',
    chat_header: 'ClinicBot · Online',
    demo_msg1: 'Oi! Gostaria de marcar uma consulta com o Dr. Silva.',
    demo_reply1: 'Claro! O Dr. Silva tem disponibilidade na quinta às 14h ou na sexta às 10h. Qual fica melhor para você?',
    demo_msg2: 'Quinta às 14h, por favor.',
    demo_msg2_reply: 'Feito! ✅ Consulta confirmada para quinta-feira às 14h com o Dr. Silva. Você receberá um lembrete 24 horas antes. Até lá!',

    // Tools
    tools_label: 'Construído com',

    // Why
    why_title: 'Por Que a Synaptech',
    why_p1: 'Não começamos com uma ferramenta e procuramos um problema para aplicar. Começamos pela sua operação, identificamos onde tempo e dinheiro são desperdiçados com trabalho repetitivo e construímos a solução mais prática para resolver.',
    why_p2: 'Tudo que entregamos é seu — documentado, mantido e construído para que sua equipe entenda o que faz. Sem caixas pretas, sem dependência de fornecedor.',

    // Solutions page
    sol_hero_title: 'Nossas Soluções',
    sol_hero_sub: 'Três sistemas. Três problemas reais resolvidos. Cada um pronto para se adaptar ao seu negócio em dias, não meses.',
    sol_cta_title: 'Não Encontrou o Que Precisa?',
    sol_cta_desc: 'Não começamos com uma ferramenta e procuramos um problema. Conte o que sua equipe faz manualmente todo dia e construímos a solução certa para isso.',

    // Contact page
    con_title: 'Vamos Conversar Sobre a Sua Operação',
    con_desc: 'Conte o que sua equipe gasta tempo fazendo que uma máquina deveria estar fazendo no lugar. A gente volta com uma proposta concreta.',
    form_legend1: 'Suas Informações',
    form_name: 'Nome Completo *',
    form_email: 'E-mail *',
    form_company: 'Nome da Empresa',
    form_phone: 'Telefone / WhatsApp',
    form_legend2: 'Seu Desafio',
    form_int: 'Qual solução te interessa mais?',
    form_sel: 'Selecione uma',
    f1: 'SalesSync — Automação de Notas de Venda',
    f2: 'ClinicBot — Agente WhatsApp para Clínicas',
    f3: 'FieldBot — Agendamento de Visitas Técnicas',
    f4: 'Outra coisa — vou descrever abaixo',
    form_msg: 'O que sua equipe faz manualmente hoje que você gostaria de automatizar? *',
    form_ph: 'Exemplo: toda vez que fechamos uma venda, alguém precisa lançar manualmente os dados no sistema. Leva 15 minutos por venda e fechamos 20 por dia.',
    form_sub: 'Enviar Mensagem',

    // Thank you
    ty_title: 'Mensagem Recebida.',
    ty_sub: 'Vamos analisar o que você enviou e retornar com uma proposta concreta — geralmente em até 1 dia útil.',
    ty_back: 'Voltar ao Início',

    footer_text: 'Synaptech | Automação com IA & Inteligência de Negócios | Matheus O. Malaquias',
  }
};

// ── Apply language to DOM ──
function applyLanguage(lang) {
  const t = translations[lang];
  if (!t) return;
  localStorage.setItem('synaptech-lang', lang);

  const btn = document.getElementById('lang-toggle');
  if (btn) btn.textContent = lang === 'en' ? '🇧🇷 PT' : '🇺🇸 EN';

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (t[key] === undefined) return;
    if (el.tagName === 'TEXTAREA') {
      el.placeholder = t[key];
    } else if (el.tagName === 'OPTION') {
      el.textContent = t[key];
    } else {
      el.textContent = t[key];
    }
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (t[key]) el.placeholder = t[key];
  });

  const footerP = document.querySelector('footer p');
  if (footerP) {
    footerP.innerHTML = `&copy; ${new Date().getFullYear()} ${t.footer_text}`;
  }
}

const savedLang = localStorage.getItem('synaptech-lang') || 'en';
applyLanguage(savedLang);

const langBtn = document.getElementById('lang-toggle');
if (langBtn) {
  langBtn.addEventListener('click', () => {
    const current = localStorage.getItem('synaptech-lang') || 'en';
    applyLanguage(current === 'en' ? 'pt' : 'en');
  });
}

// ══════════════════════════════════════════
// HERO NEURAL CANVAS (index.html only)
// ══════════════════════════════════════════
const heroCanvas = document.getElementById('neural-canvas');
if (heroCanvas) {
  const ctx = heroCanvas.getContext('2d');
  let W, H, nodes, animId;

  function resizeHero() {
    W = heroCanvas.offsetWidth;
    H = heroCanvas.offsetHeight;
    heroCanvas.width = W;
    heroCanvas.height = H;
  }

  function randomNode() {
    return {
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      r: Math.random() * 2.5 + 1,
      pulse: Math.random() * Math.PI * 2,
    };
  }

  function initHeroNodes() {
    const count = Math.min(Math.floor((W * H) / 12000), 60);
    nodes = Array.from({ length: count }, randomNode);
  }

  function drawHero() {
    ctx.clearRect(0, 0, W, H);
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < 140) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(124,58,237,${(1 - d / 140) * 0.35})`;
          ctx.lineWidth = 0.8;
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.stroke();
        }
      }
    }
    nodes.forEach(n => {
      n.pulse += 0.03;
      const glow = Math.abs(Math.sin(n.pulse));
      const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 4);
      g.addColorStop(0, `rgba(159,103,255,${0.7 + glow * 0.3})`);
      g.addColorStop(1, 'rgba(124,58,237,0)');
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r * 4, 0, Math.PI * 2);
      ctx.fillStyle = g; ctx.fill();
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(196,181,253,${0.6 + glow * 0.4})`; ctx.fill();
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
    });
    animId = requestAnimationFrame(drawHero);
  }

  const heroSection = heroCanvas.closest('.hero');
  const heroIO = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) { if (!animId) drawHero(); }
    else { cancelAnimationFrame(animId); animId = null; }
  }, { threshold: 0.1 });
  if (heroSection) heroIO.observe(heroSection);

  window.addEventListener('resize', () => { resizeHero(); initHeroNodes(); });
  resizeHero(); initHeroNodes();

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    cancelAnimationFrame(animId); heroCanvas.style.display = 'none';
  }
}

// ══════════════════════════════════════════
// SCROLL FADE-IN
// ══════════════════════════════════════════
const fadeEls = document.querySelectorAll('.fade-in');
if (fadeEls.length) {
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, { threshold: 0.1 });
  fadeEls.forEach(el => io.observe(el));
}

// ══════════════════════════════════════════
// DEMO CHAT AUTO-TYPE
// ══════════════════════════════════════════
(function demoChatTyping() {
  const demoChat = document.getElementById('demo-chat');
  if (!demoChat) return;
  const typingEl = demoChat.querySelector('.ai-typing');
  if (!typingEl) return;
  setTimeout(() => {
    const lang = localStorage.getItem('synaptech-lang') || 'en';
    const t = translations[lang];
    typingEl.remove();
    const reply = document.createElement('div');
    reply.className = 'chat-msg ai';
    reply.setAttribute('data-i18n', 'demo_msg2_reply');
    reply.textContent = t.demo_msg2_reply;
    demoChat.appendChild(reply);
  }, 2500);
})();

// ══════════════════════════════════════════
// THANK YOU PAGE
// ══════════════════════════════════════════
if (document.querySelector('.thankyou-hero')) {
  const params = new URLSearchParams(location.search);
  const nameEl = document.getElementById('submitted-name');
  const svcEl  = document.getElementById('submitted-service');
  if (nameEl && params.get('fullName')) nameEl.textContent = params.get('fullName');
  if (svcEl && params.get('interest'))  svcEl.textContent = params.get('interest').replace(/-/g, ' ');
}