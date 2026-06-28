// ══════════════════════════════════════════
// SYNAPTECH LANDING PAGE — landing.js
// ══════════════════════════════════════════

// ── FOOTER YEAR ──
document.getElementById('footer-year').textContent = new Date().getFullYear();

// ══════════════════════════════════════════
// TRANSLATIONS
// ══════════════════════════════════════════
const T = {
  pt: {
    eyebrow:         'Automação com IA · Para Negócios Reais',
    hero_title:      'Automatizamos o trabalho que sua equipe não deveria estar fazendo',
    hero_desc:       'Agentes de WhatsApp, automações de processo e integrações inteligentes — construídos para o seu negócio em dias, não meses.',
    hero_cta:        'Quero uma Proposta Gratuita',
    hero_cta2:       'Ver Soluções',
    form_badge:      'Proposta Gratuita',
    form_top_title:  'Fale com a gente agora',
    form_top_desc:   'Conta em qual processo sua equipe perde mais tempo. A gente volta com uma proposta concreta em até 1 dia útil — sem custo, sem compromisso.',
    form_bottom_title: 'Pronto para automatizar?',
    form_bottom_desc:  'Você já viu o que é possível. Agora é só dar o primeiro passo — sem burocracia, sem compromisso.',
    check1:          'Sem compromisso',
    check2:          'Proposta personalizada',
    check3:          'Resposta em até 1 dia útil',
    field_name:      'Nome *',
    field_wpp:       'WhatsApp *',
    field_need:      'O que você precisa? *',
    sel_placeholder: 'Selecione o tipo de solução',
    opt1:            '🤖 Agente de WhatsApp — quero automatizar atendimento',
    opt2:            '⚙️ Automação de processo — tenho uma tarefa repetitiva',
    opt3:            '🔗 Integração de sistemas — quero conectar ferramentas',
    opt4:            '📊 Inteligência de dados — quero entender meus números',
    opt5:            '💡 Não sei ainda — quero conversar e descobrir',
    form_btn:        'Quero uma Proposta Gratuita',
    form_disclaimer: 'Sem spam. Respondemos em até 1 dia útil.',
    success_title:   'Mensagem Recebida!',
    success_desc:    'Retornamos com uma proposta em até 1 dia útil.',
    prob_title:      'Você se identifica com isso?',
    prob_sub:        'Se sim, existe uma automação que resolve — e pode estar rodando na sua empresa em dias.',
    prob1_title:     'Sua equipe ainda lança dados manualmente?',
    prob1_desc:      'Cada venda gera minutos de digitação repetitiva. Multiplica por 20 vendas por dia — são horas perdidas todo mês.',
    prob2_title:     'Seu atendimento para quando a equipe vai embora?',
    prob2_desc:      'Clientes mandam mensagem à noite e no fim de semana. Sem resposta, escolhem o concorrente.',
    prob3_title:     'Sua agenda de visitas depende de ligação?',
    prob3_desc:      'Cada visita técnica exige uma rodada de ligações para confirmar. Um agente faz isso em 3 minutos.',
    sol_title:       'Nossas Soluções',
    sol_sub:         'Três sistemas prontos para implantar — e a possibilidade de construir o seu do zero.',
    p1_tag:          'Operações de Venda',
    p1_headline:     'Lançamento automático de notas de venda',
    p1_desc:         'A cada venda fechada, o SalesSync registra automaticamente no seu sistema. Sua equipe para de digitar e começa a vender mais.',
    p1_result:       '−15min por venda',
    p2_tag:          'Saúde',
    p2_headline:     'Agente inteligente no WhatsApp para clínicas',
    p2_desc:         'Atende pacientes 24/7, confirma consultas, envia lembretes e escala para humano quando necessário.',
    p2_result:       '24/7 sem recepcionista',
    p3_tag:          'Serviços em Campo',
    p3_headline:     'Agendamento de visitas técnicas pelo WhatsApp',
    p3_desc:         'Recebe o pedido, qualifica o serviço, verifica disponibilidade e confirma o agendamento. Tudo automaticamente.',
    p3_result:       '3min do pedido ao calendário',
    p4_tag:          'Sob Medida',
    p4_name:         'O Seu Projeto',
    p4_headline:     'Tem outro problema para resolver?',
    p4_desc:         'Esses são exemplos do que já construímos. Se a sua necessidade é diferente, a gente projeta uma solução do zero para o seu processo.',
    p4_cta:          'Vamos Conversar',
    mind_eyebrow:    'Rede Neural · Processando',
    mind_title:      'Uma segunda mente trabalhando por você',
    mind_desc:       'Enquanto sua equipe foca em estratégia, nossa IA roda em segundo plano — qualificando leads, respondendo clientes e atualizando seus sistemas.',
    mind_cta:        'Quero isso no meu negócio',
    cnt1:            'conexões',
    cnt2:            'sinais/s',
    cnt3:            'nós ativos',
    chat_title:      'Veja funcionando',
    chat_desc:       'Uma conversa real com o ClinicBot. O paciente agenda, recebe confirmação, e seu sistema é atualizado — sem ninguém da sua equipe tocar em nada.',
    chat_c1:         'Atendimento 24h, 7 dias por semana',
    chat_c2:         'Confirmação automática de consultas',
    chat_c3:         'Lembrete enviado 24h antes',
    chat_c4:         'Escalada para humano quando necessário',
    chat_hdr:        'ClinicBot · Online',
    msg1:            'Oi! Quero marcar consulta com o Dr. Silva.',
    msg2:            'Dr. Silva tem disponibilidade quinta às 14h ou sexta às 10h. Qual prefere?',
    msg3:            'Quinta às 14h!',
    msg4:            '✅ Confirmado! Consulta na quinta às 14h com Dr. Silva. Você receberá um lembrete 24h antes.',
    why_title:       'Por que a Synaptech?',
    why_sub:         'Não começamos com uma ferramenta. Começamos pelo seu problema.',
    r1_title:        'Rápido de implementar',
    r1_desc:         'Dias para entrar em produção, não meses. Sem burocracia de grandes projetos de TI.',
    r2_title:        'Tudo seu',
    r2_desc:         'O sistema entregue é seu — documentado e sem dependência de fornecedor.',
    r3_title:        'Feito para o seu negócio',
    r3_desc:         'Nada genérico. Cada solução é adaptada ao seu processo, não o contrário.',
    r4_title:        'Suporte real',
    r4_desc:         'Você fala com quem construiu. Sem call center, sem ticket number.',
    ph_name:         'Seu nome',
  },
  en: {
    eyebrow:         'AI Automation · For Real Businesses',
    hero_title:      'We automate the work your team shouldn\'t be doing',
    hero_desc:       'WhatsApp agents, process automations and intelligent integrations — built for your business in days, not months.',
    hero_cta:        'Get a Free Proposal',
    hero_cta2:       'See Solutions',
    form_badge:      'Free Proposal',
    form_top_title:  'Talk to us now',
    form_top_desc:   'Tell us where your team loses the most time. We\'ll come back with a concrete proposal within 1 business day — free, no commitment.',
    form_bottom_title: 'Ready to automate?',
    form_bottom_desc:  'You\'ve seen what\'s possible. Now just take the first step — no bureaucracy, no commitment.',
    check1:          'No commitment',
    check2:          'Tailored proposal',
    check3:          'Response within 1 business day',
    field_name:      'Name *',
    field_wpp:       'WhatsApp *',
    field_need:      'What do you need? *',
    sel_placeholder: 'Select the solution type',
    opt1:            '🤖 WhatsApp Agent — I want to automate customer service',
    opt2:            '⚙️ Process Automation — I have a repetitive task to eliminate',
    opt3:            '🔗 System Integration — I want to connect my tools',
    opt4:            '📊 Data Intelligence — I want better insights from my data',
    opt5:            '💡 Not sure yet — I\'d like to talk and find out',
    form_btn:        'Get a Free Proposal',
    form_disclaimer: 'No spam. We respond within 1 business day.',
    success_title:   'Message Received!',
    success_desc:    'We\'ll come back with a proposal within 1 business day.',
    prob_title:      'Does this sound familiar?',
    prob_sub:        'If so, there\'s an automation that solves it — and it can be running in your business within days.',
    prob1_title:     'Is your team still entering data manually?',
    prob1_desc:      'Every sale generates minutes of repetitive typing. Multiply by 20 sales a day — that\'s hours wasted every month.',
    prob2_title:     'Does your support stop when the team leaves?',
    prob2_desc:      'Clients send messages at night and on weekends. Without a response, they choose a competitor.',
    prob3_title:     'Does your visit schedule depend on phone calls?',
    prob3_desc:      'Every technical visit requires a round of calls to confirm. An agent does it in 3 minutes.',
    sol_title:       'Our Solutions',
    sol_sub:         'Three ready-to-deploy systems — and the possibility of building yours from scratch.',
    p1_tag:          'Sales Operations',
    p1_headline:     'Automatic sales note entry',
    p1_desc:         'Every time a sale closes, SalesSync automatically registers it in your system. Your team stops typing and starts selling more.',
    p1_result:       '−15min per sale',
    p2_tag:          'Healthcare',
    p2_headline:     'Intelligent WhatsApp agent for clinics',
    p2_desc:         'Handles patients 24/7, confirms appointments, sends reminders and escalates to a human when needed.',
    p2_result:       '24/7 without a receptionist',
    p3_tag:          'Field Services',
    p3_headline:     'Technical visit scheduling via WhatsApp',
    p3_desc:         'Receives the request, qualifies the service, checks availability and confirms the appointment. All automatically.',
    p3_result:       '3min from request to calendar',
    p4_tag:          'Custom Built',
    p4_name:         'Your Project',
    p4_headline:     'Have a different problem to solve?',
    p4_desc:         'These are examples of what we\'ve already built. If your need is different, we design a solution from scratch for your process.',
    p4_cta:          'Let\'s Talk',
    mind_eyebrow:    'Neural Network · Processing',
    mind_title:      'A second mind working for you',
    mind_desc:       'While your team focuses on strategy, our AI runs quietly in the background — qualifying leads, answering clients and updating your systems.',
    mind_cta:        'I want this in my business',
    cnt1:            'connections',
    cnt2:            'signals/s',
    cnt3:            'active nodes',
    chat_title:      'See it working',
    chat_desc:       'A real conversation with ClinicBot. The patient books, gets confirmation, and your system is updated — without anyone on your team lifting a finger.',
    chat_c1:         '24/7 availability, 7 days a week',
    chat_c2:         'Automatic appointment confirmation',
    chat_c3:         'Reminder sent 24h before',
    chat_c4:         'Escalates to human when needed',
    chat_hdr:        'ClinicBot · Online',
    msg1:            'Hi! I\'d like to schedule with Dr. Silva.',
    msg2:            'Dr. Silva has availability Thursday at 2 PM or Friday at 10 AM. Which works better?',
    msg3:            'Thursday at 2 PM!',
    msg4:            '✅ Confirmed! Appointment Thursday at 2 PM with Dr. Silva. You\'ll receive a reminder 24h before.',
    why_title:       'Why Synaptech?',
    why_sub:         'We don\'t start with a tool. We start with your problem.',
    r1_title:        'Fast to implement',
    r1_desc:         'Days to go live, not months. No big IT project bureaucracy.',
    r2_title:        'All yours',
    r2_desc:         'The system we deliver is yours — documented and without vendor lock-in.',
    r3_title:        'Built for your business',
    r3_desc:         'Nothing generic. Every solution is adapted to your process, not the other way around.',
    r4_title:        'Real support',
    r4_desc:         'You talk to whoever built it. No call center, no ticket number.',
    ph_name:         'Your name',
  }
};

let currentLang = 'pt';

function setLang(lang) {
  currentLang = lang;
  const t = T[lang];
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
  document.documentElement.lang = lang === 'pt' ? 'pt-BR' : 'en';
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (t[key] !== undefined) el.textContent = t[key];
  });
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    const key = el.getAttribute('data-i18n-ph');
    if (t[key] !== undefined) el.placeholder = t[key];
  });
  updateChat(lang);
}

setLang('pt');

// ══════════════════════════════════════════
// FORM HANDLING — conectado ao n8n
// ══════════════════════════════════════════
const WEBHOOK_URL = 'https://n8n-yvdu.srv1552695.hstgr.cloud/webhook/synaptech';

async function submitForm(e, formId) {
  e.preventDefault();
  const form    = document.getElementById('form-' + formId);
  const success = document.getElementById('success-' + formId);
  const btn     = form.querySelector('button[type="submit"]');

  const nome    = form.querySelector('[name="nome"]').value.trim();
  const wpp     = form.querySelector('[name="whatsapp"]').value.trim();
  const solucao = form.querySelector('[name="solucao"]').value;

  if (!nome || !wpp || !solucao) return;

  // Feedback visual no botão
  const originalText = btn.textContent;
  btn.textContent = '⏳ Enviando...';
  btn.disabled = true;

  try {
    await fetch(WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nome,
        whatsapp: wpp,
        solucao,
        idioma:   currentLang,
        origem:   'landing_page',
        data:     new Date().toISOString()
      })
    });
  } catch (err) {
    // Mesmo com erro de rede, mostra sucesso para o usuário
    console.warn('Webhook error:', err);
  }

  // Meta Pixel lead event
  if (typeof fbq !== 'undefined') {
    fbq('track', 'Lead', { content_name: solucao });
  }

  // Mostra sucesso
  form.style.display = 'none';
  success.style.display = 'flex';
}

// ══════════════════════════════════════════
// CHAT DEMO
// ══════════════════════════════════════════
function updateChat(lang) {
  const t = T[lang];
  const msgs = document.querySelectorAll('.msg');
  const keys = ['msg1', 'msg2', 'msg3'];
  msgs.forEach((el, i) => { if (keys[i] && t[keys[i]]) el.textContent = t[keys[i]]; });
}

setTimeout(() => {
  const typing  = document.getElementById('typing');
  const chatBody = document.getElementById('chat-body');
  if (!typing || !chatBody) return;
  typing.remove();
  const reply = document.createElement('div');
  reply.className = 'msg msg--ai';
  reply.setAttribute('data-i18n', 'msg4');
  reply.textContent = T[currentLang].msg4;
  chatBody.appendChild(reply);
}, 2800);

// ══════════════════════════════════════════
// GRAPH CANVAS ANIMATION
// ══════════════════════════════════════════
const ACCENT = { r: 159, g: 103, b: 255 };
const CYAN_C = { r: 6,   g: 182, b: 212 };
const GREY   = { r: 100, g: 120, b: 160 };

function rnd(a, b) { return a + Math.random() * (b - a); }
function lerp(a, b, t) { return a + (b - a) * t; }

function buildScene(W, H, hubCount, satCount) {
  return {
    nodes: [
      ...Array.from({ length: hubCount }, (_, i) => ({
        x: W*.12 + Math.random()*W*.76,
        y: H*.12 + Math.random()*H*.76,
        vx: (Math.random()-.5)*.18, vy: (Math.random()-.5)*.18,
        r: rnd(6,13), pulse: Math.random()*Math.PI*2, ps: rnd(.015,.028),
        col: i%3===0 ? CYAN_C : ACCENT, hub: true
      })),
      ...Array.from({ length: satCount }, () => ({
        x: Math.random()*W, y: Math.random()*H,
        vx: (Math.random()-.5)*.55, vy: (Math.random()-.5)*.55,
        r: rnd(1.8,4), pulse: Math.random()*Math.PI*2, ps: rnd(.025,.05),
        col: Math.random()<.5 ? ACCENT : GREY, hub: false
      }))
    ],
    pulses: [],
    frame: 0,
    cc: 0, sc: 0, nc: 0, ct: 0, st: 0, nt: 0
  };
}

function mountCanvas(canvasId, opts) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const ctx = canvas.getContext('2d');
  const parent = canvas.parentElement;
  const as = opts.dimmed ? 0.4 : 1;
  let state, animId;

  function resize() {
    canvas.width  = parent.offsetWidth  || 600;
    canvas.height = parent.offsetHeight || 320;
    state = buildScene(canvas.width, canvas.height, opts.hubs || 5, opts.sats || 28);
  }

  function draw() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    const hubs = state.nodes.filter(n => n.hub);
    const sats  = state.nodes.filter(n => !n.hub);
    const hd = Math.min(W,H)*.6, sd = Math.min(W,H)*.28;
    let cons = 0;

    for (let i=0;i<hubs.length;i++) for (let j=i+1;j<hubs.length;j++) {
      const dx=hubs[i].x-hubs[j].x, dy=hubs[i].y-hubs[j].y, d=Math.sqrt(dx*dx+dy*dy);
      if (d<hd) {
        cons++;
        const c=hubs[i].col;
        ctx.beginPath();
        ctx.strokeStyle=`rgba(${c.r},${c.g},${c.b},${(1-d/hd)*.55*as})`;
        ctx.lineWidth=1.1;
        ctx.moveTo(hubs[i].x,hubs[i].y); ctx.lineTo(hubs[j].x,hubs[j].y); ctx.stroke();
        if (Math.random()<.003) state.pulses.push({from:hubs[i],to:hubs[j],t:0,sp:rnd(.006,.013)});
      }
    }

    for (const p of sats) for (const h of hubs) {
      const dx=p.x-h.x, dy=p.y-h.y, d=Math.sqrt(dx*dx+dy*dy);
      if (d<sd) {
        cons++;
        const c=h.col;
        ctx.beginPath();
        ctx.strokeStyle=`rgba(${c.r},${c.g},${c.b},${(1-d/sd)*.2*as})`;
        ctx.lineWidth=.5;
        ctx.moveTo(p.x,p.y); ctx.lineTo(h.x,h.y); ctx.stroke();
      }
    }

    const alive = [];
    for (const pu of state.pulses) {
      pu.t+=pu.sp; if(pu.t>=1) continue; alive.push(pu);
      const px=lerp(pu.from.x,pu.to.x,pu.t), py=lerp(pu.from.y,pu.to.y,pu.t), c=pu.from.col;
      const g=ctx.createRadialGradient(px,py,0,px,py,5);
      g.addColorStop(0,`rgba(${c.r},${c.g},${c.b},${.9*as})`);
      g.addColorStop(1,`rgba(${c.r},${c.g},${c.b},0)`);
      ctx.beginPath(); ctx.arc(px,py,5,0,Math.PI*2); ctx.fillStyle=g; ctx.fill();
    }
    state.pulses = alive;

    for (const n of state.nodes) {
      n.pulse+=n.ps; const gw=(Math.sin(n.pulse)+1)/2, c=n.col;
      if (n.hub) {
        const oR=n.r*(1.7+gw*.5);
        const g=ctx.createRadialGradient(n.x,n.y,n.r*.4,n.x,n.y,oR*1.9);
        g.addColorStop(0,`rgba(${c.r},${c.g},${c.b},${(.16+gw*.1)*as})`);
        g.addColorStop(1,`rgba(${c.r},${c.g},${c.b},0)`);
        ctx.beginPath(); ctx.arc(n.x,n.y,oR*1.9,0,Math.PI*2); ctx.fillStyle=g; ctx.fill();
        ctx.beginPath(); ctx.arc(n.x,n.y,oR,0,Math.PI*2);
        ctx.strokeStyle=`rgba(${c.r},${c.g},${c.b},${(.22+gw*.15)*as})`; ctx.lineWidth=.8; ctx.stroke();
        const core=ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,n.r);
        core.addColorStop(0,`rgba(255,255,255,${(.9+gw*.1)*as})`);
        core.addColorStop(.45,`rgba(${c.r},${c.g},${c.b},${.9*as})`);
        core.addColorStop(1,`rgba(${c.r},${c.g},${c.b},${.6*as})`);
        ctx.beginPath(); ctx.arc(n.x,n.y,n.r,0,Math.PI*2); ctx.fillStyle=core; ctx.fill();
      } else {
        const g=ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,n.r*3);
        g.addColorStop(0,`rgba(${c.r},${c.g},${c.b},${(.5+gw*.3)*as})`);
        g.addColorStop(1,`rgba(${c.r},${c.g},${c.b},0)`);
        ctx.beginPath(); ctx.arc(n.x,n.y,n.r*3,0,Math.PI*2); ctx.fillStyle=g; ctx.fill();
        ctx.beginPath(); ctx.arc(n.x,n.y,n.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(${c.r},${c.g},${c.b},${(.65+gw*.3)*as})`; ctx.fill();
      }
      n.x+=n.vx; n.y+=n.vy;
      const pad=n.r*2;
      if(n.x<pad||n.x>W-pad) n.vx*=-1;
      if(n.y<pad||n.y>H-pad) n.vy*=-1;
    }

    state.frame++;
    if (state.frame%45===0) {
      state.ct=cons; state.st=Math.floor(rnd(10,42)); state.nt=state.nodes.length;
    }
    state.cc=Math.round(lerp(state.cc,state.ct,.1));
    state.sc=Math.round(lerp(state.sc,state.st,.07));
    state.nc=Math.round(lerp(state.nc,state.nt,.1));

    if (opts.counters) {
      const [c1,c2,c3] = opts.counters;
      if (document.getElementById(c1)) document.getElementById(c1).textContent = state.cc;
      if (document.getElementById(c2)) document.getElementById(c2).textContent = state.sc;
      if (document.getElementById(c3)) document.getElementById(c3).textContent = state.nc;
    }

    animId = requestAnimationFrame(draw);
  }

  let running = false;
  const io = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting && !running) {
      running = true; draw();
    } else if (!entries[0].isIntersecting && running) {
      running = false;
      cancelAnimationFrame(animId); animId = null;
    }
  }, { threshold: 0.05 });
  io.observe(parent);

  window.addEventListener('resize', () => { resize(); });
  resize();
}

mountCanvas('hero-canvas', { hubs: 5, sats: 32, dimmed: false });
mountCanvas('mind-canvas', {
  hubs: 6, sats: 30, dimmed: false,
  counters: ['cnt-connections', 'cnt-signals', 'cnt-nodes']
});

// ══════════════════════════════════════════
// SCROLL FADE-IN
// ══════════════════════════════════════════
const fadeTargets = document.querySelectorAll(
  '.problem-card, .sol-card, .reason-card, .mind-section, .chat-section, .form-section, .problem-section, .solutions-section, .reasons-section'
);

if (fadeTargets.length) {
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.08 });

  fadeTargets.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity .6s ease, transform .6s ease';
    io.observe(el);
  });
}