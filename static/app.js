// ── State ──────────────────────────────────────────────
let network = null;
let currentView = 'graph';
let pendingDeleteId = null;
let pendingOverwriteData = null;
let currentDetailId = null;
let hubDept = 'engineering';
let hubDoc = 'skill';

// ── SSE Helper ─────────────────────────────────────────
async function streamSSE(url, body, onEvent) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  });
  if (!resp.ok) throw new Error(await resp.text());
  const reader = resp.body.getReader();
  const dec = new TextDecoder();
  let buf = '';
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    buf += dec.decode(value);
    const lines = buf.split('\n');
    buf = lines.pop();
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try { onEvent(JSON.parse(line.slice(6))); } catch {}
      }
    }
  }
}

// ── Router ─────────────────────────────────────────────
function navigate(view) {
  document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  const section = document.getElementById(`view-${view}`);
  if (section) section.classList.add('active');
  const navEl = document.querySelector(`[data-view="${view}"]`);
  if (navEl) navEl.classList.add('active');
  currentView = view;
  if (view === 'graph') initGraph();
  if (view === 'hub') loadHub();
  if (view === 'data') loadStats();
}

document.querySelectorAll('.nav-item').forEach(el => {
  el.addEventListener('click', () => navigate(el.dataset.view));
});

// ── Stats ───────────────────────────────────────────────
async function refreshStats() {
  const [stats, pend] = await Promise.all([
    fetch('/api/stats').then(r => r.json()),
    fetch('/api/pending').then(r => r.json()),
  ]);
  document.getElementById('stat-total').textContent = stats.total ?? '—';
  document.getElementById('stat-knowledge').textContent = stats.knowledge ?? '—';
  document.getElementById('stat-meetings').textContent = stats.meetings ?? '—';
  const badge = document.getElementById('pending-badge');
  if (pend.length > 0) {
    badge.textContent = pend.length;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
}

// ── Graph ───────────────────────────────────────────────
async function initGraph() {
  const data = await fetch('/api/graph').then(r => r.json());
  const colorMap = { knowledge: '#58a6ff', meetings: '#3fb950', agency: '#a371f7' };
  const nodes = new vis.DataSet(data.nodes.map(n => ({
    id: n.id,
    label: n.label,
    title: n.title,
    color: { background: colorMap[n.group] || '#8b949e', border: 'transparent',
             highlight: { background: colorMap[n.group], border: '#fff' } },
    font: { color: '#f0f6fc', size: 12 },
    shape: 'dot',
    size: 10,
  })));
  const edges = new vis.DataSet(data.edges.map(e => ({
    from: e.from, to: e.to,
    color: { color: '#30363d', highlight: '#58a6ff' },
    smooth: { type: 'dynamic' },
  })));
  const container = document.getElementById('graph-canvas');
  if (network) network.destroy();
  network = new vis.Network(container, {nodes, edges}, {
    physics: { barnesHut: { gravitationalConstant: -8000, springLength: 200, damping: 0.15 } },
    interaction: { hover: true, tooltipDelay: 300 },
    edges: { arrows: { to: { enabled: true, scaleFactor: 0.5 } } },
  });
  network.on('click', ({nodes: clicked}) => {
    if (clicked.length) showDetail(clicked[0]);
  });
  document.getElementById('graph-node-count').textContent = `${data.nodes.length} nodes`;
}

// Graph controls
document.getElementById('zoom-in').addEventListener('click', () => network?.moveTo({scale: network.getScale() * 1.3}));
document.getElementById('zoom-out').addEventListener('click', () => network?.moveTo({scale: network.getScale() * 0.7}));
document.getElementById('zoom-fit').addEventListener('click', () => network?.fit());

// Graph filter
document.getElementById('graph-filter').addEventListener('change', (e) => {
  // Reinit with filter — simple approach: hide non-matching nodes
  initGraph(); // ponytail: full reinit is fine at this scale
});

// ── Detail Panel ────────────────────────────────────────
async function showDetail(docId) {
  const r = await fetch(`/api/docs/${encodeURIComponent(docId)}`);
  if (!r.ok) return;
  const {content, metadata} = await r.json();
  currentDetailId = docId;
  document.getElementById('detail-title').textContent = metadata.title;
  document.getElementById('detail-dept').textContent = metadata.dept;
  document.getElementById('detail-dept').className = 'badge-pill badge-blue';
  document.getElementById('detail-type').textContent = metadata.type;
  document.getElementById('detail-type').className = 'badge-pill badge-green';
  document.getElementById('detail-updated').textContent = `Updated ${metadata.updated_at}`;
  document.getElementById('detail-content').innerHTML = marked.parse(content);
  const panel = document.getElementById('detail-panel');
  panel.classList.remove('hidden');
  setTimeout(() => panel.classList.add('open'), 10);
}

document.getElementById('detail-close').addEventListener('click', () => {
  const panel = document.getElementById('detail-panel');
  panel.classList.remove('open');
  setTimeout(() => panel.classList.add('hidden'), 260);
});

// Detail delete → modal
document.getElementById('detail-delete').addEventListener('click', () => {
  pendingDeleteId = currentDetailId;
  document.getElementById('modal-body').textContent =
    `Delete "${currentDetailId}"? This cannot be undone.`;
  document.getElementById('modal-overlay').classList.remove('hidden');
});

document.getElementById('modal-cancel').addEventListener('click', () => {
  document.getElementById('modal-overlay').classList.add('hidden');
  pendingDeleteId = null;
});

document.getElementById('modal-confirm').addEventListener('click', async () => {
  if (!pendingDeleteId) return;
  await fetch(`/api/docs/${encodeURIComponent(pendingDeleteId)}`, {method: 'DELETE'});
  document.getElementById('modal-overlay').classList.add('hidden');
  document.getElementById('detail-panel').classList.add('hidden');
  pendingDeleteId = null;
  await initGraph();
  await refreshStats();
});

// ── Init ────────────────────────────────────────────────
refreshStats();
navigate('graph');
