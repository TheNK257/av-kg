const CATEGORY_COLORS = {
  'vehicle.car':                '#3b82f6',
  'vehicle.truck':              '#2563eb',
  'vehicle.bus.rigid':          '#1d4ed8',
  'vehicle.bus.bendy':          '#1e40af',
  'vehicle.construction':       '#f59e0b',
  'vehicle.motorcycle':         '#8b5cf6',
  'vehicle.bicycle':            '#a78bfa',
  'vehicle.trailer':            '#6366f1',
  'vehicle.emergency.ambulance':'#ef4444',
  'vehicle.emergency.police':   '#dc2626',
  'human.pedestrian.adult':     '#f87171',
  'human.pedestrian.child':     '#fca5a5',
  'human.pedestrian.construction_worker': '#fb923c',
  'human.pedestrian.police_officer':      '#f97316',
  'movable_object.barrier':     '#6b7280',
  'movable_object.trafficcone': '#f59e0b',
  'movable_object.pushable_pullable': '#9ca3af',
  'movable_object.debris':      '#4b5563',
  'static_object.bicycle_rack': '#64748b',
};

const DEFAULT_COLOR = '#94a3b8';

function getColor(category) {
  if (!category) return DEFAULT_COLOR;
  if (CATEGORY_COLORS[category]) return CATEGORY_COLORS[category];
  for (const key of Object.keys(CATEGORY_COLORS)) {
    if (category.startsWith(key) || key.startsWith(category)) return CATEGORY_COLORS[key];
  }
  return DEFAULT_COLOR;
}

function shortCategory(cat) {
  if (!cat) return '?';
  const parts = cat.split('.');
  return parts[parts.length - 1];
}

// ── vis.js setup ──

const nodes = new vis.DataSet();
const edges = new vis.DataSet();

const container = document.getElementById('graph');
const network = new vis.Network(container, { nodes, edges }, {
  physics: false,
  nodes: {
    shape: 'dot',
    size: 14,
    font: { color: '#ccc', size: 11 },
    borderWidth: 2,
  },
  edges: {
    color: { color: '#3a3d4a', highlight: '#7c8db5' },
    font: { color: '#666', size: 9, strokeWidth: 0 },
    smooth: { type: 'continuous' },
  },
  interaction: {
    hover: true,
    tooltipDelay: 100,
  },
});

// ── state ──

let lastData = null;

// ── render ──

const SCALE = 8;

function render(data) {
  lastData = data;

  const newNodes = [
    {
      id: 'ego',
      label: 'EGO',
      x: 0,
      y: 0,
      fixed: true,
      size: 20,
      color: { background: '#22c55e', border: '#16a34a' },
      font: { color: '#fff', size: 13, bold: true },
    }
  ];

  for (const n of data.nodes) {
    const c = getColor(n.category);
    newNodes.push({
      id: n.id,
      label: shortCategory(n.category),
      x: n.rel_x * SCALE,
      y: -n.rel_y * SCALE,   // flip y so "ahead" is up
      fixed: true,
      color: { background: c, border: c },
      font: { color: '#ccc', size: 10 },
    });
  }

  const newEdges = data.edges.map((e, i) => ({
    id: `e-${i}`,
    from: e.from,
    to: e.to,
    label: `${e.distance}m`,
    title: `${e.zone} · ${e.direction}`,
  }));

  nodes.clear();
  edges.clear();
  nodes.add(newNodes);
  edges.add(newEdges);
}

// ── info panel ──

function showNodeInfo(nodeId) {
  const panel = document.getElementById('panel-content');
  if (nodeId === 'ego' && lastData?.ego) {
    const e = lastData.ego;
    panel.innerHTML = makeTable({
      Type: 'Ego Vehicle',
      X: e.x?.toFixed(2),
      Y: e.y?.toFixed(2),
      Timestamp: e.timestamp,
    });
    return;
  }
  const n = lastData?.nodes.find(n => n.id === nodeId);
  if (!n) return;
  panel.innerHTML = makeTable({
    Category: n.category,
    'Rel X': n.rel_x?.toFixed(2),
    'Rel Y': n.rel_y?.toFixed(2),
    'Vel X': n.vel_x?.toFixed(2),
    'Vel Y': n.vel_y?.toFixed(2),
  });
}

function showEdgeInfo(edgeId) {
  const panel = document.getElementById('panel-content');
  const idx = parseInt(edgeId.replace('e-', ''), 10);
  const e = lastData?.edges[idx];
  if (!e) return;
  panel.innerHTML = makeTable({
    From: e.from,
    To: shortCategory(lastData.nodes.find(n => n.id === e.to)?.category),
    Distance: e.distance + ' m',
    Zone: e.zone,
    Direction: e.direction,
  });
}

function makeTable(obj) {
  const rows = Object.entries(obj)
    .map(([k, v]) => `<tr><td>${k}</td><td>${v ?? '—'}</td></tr>`)
    .join('');
  return `<table>${rows}</table>`;
}

network.on('click', params => {
  if (params.nodes.length) showNodeInfo(params.nodes[0]);
  else if (params.edges.length) showEdgeInfo(params.edges[0]);
});

// ── legend ──

function buildLegend() {
  const seen = new Set();
  const items = Object.entries(CATEGORY_COLORS).filter(([k]) => {
    const base = k.split('.').slice(0, 2).join('.');
    if (seen.has(base)) return false;
    seen.add(base);
    return true;
  });

  const html = items.map(([k, c]) =>
    `<div class="legend-item"><span class="legend-dot" style="background:${c}"></span>${shortCategory(k)}</div>`
  ).join('');

  document.getElementById('panel-content').insertAdjacentHTML('afterend',
    `<div class="legend"><h4>Categories</h4>${html}</div>`
  );
}
buildLegend();

// ── WebSocket ──

const statusEl = document.getElementById('status');
const frameEl = document.getElementById('frame-info');

function connect() {
  const ws = new WebSocket(`ws://${location.host}/ws/graph`);

  ws.onopen = () => {
    statusEl.textContent = '🟢 Live';
    statusEl.className = 'connected';
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    render(data);
    frameEl.textContent = `${data.nodes.length} objects · ${new Date(data.ego.timestamp * 1000).toLocaleTimeString()}`;
  };

  ws.onclose = () => {
    statusEl.textContent = '🔴 Disconnected';
    statusEl.className = 'error';
    setTimeout(connect, 2000);
  };

  ws.onerror = () => ws.close();
}

connect();