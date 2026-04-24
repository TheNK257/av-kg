// const CATEGORY_COLORS = {
//   'vehicle.car':                '#3b82f6',
//   'vehicle.truck':              '#2563eb',
//   'vehicle.bus.rigid':          '#1d4ed8',
//   'vehicle.bus.bendy':          '#1e40af',
//   'vehicle.construction':       '#f59e0b',
//   'vehicle.motorcycle':         '#8b5cf6',
//   'vehicle.bicycle':            '#a78bfa',
//   'vehicle.trailer':            '#6366f1',
//   'vehicle.emergency.ambulance':'#ef4444',
//   'vehicle.emergency.police':   '#dc2626',
//   'human.pedestrian.adult':     '#f87171',
//   'human.pedestrian.child':     '#fca5a5',
//   'human.pedestrian.construction_worker': '#fb923c',
//   'human.pedestrian.police_officer':      '#f97316',
//   'movable_object.barrier':     '#6b7280',
//   'movable_object.trafficcone': '#f59e0b',
//   'movable_object.pushable_pullable': '#9ca3af',
//   'movable_object.debris':      '#4b5563',
//   'static_object.bicycle_rack': '#64748b',
// };

// const DEFAULT_COLOR = '#94a3b8';

// function getColor(category) {
//   if (!category) return DEFAULT_COLOR;
//   if (CATEGORY_COLORS[category]) return CATEGORY_COLORS[category];
//   for (const key of Object.keys(CATEGORY_COLORS)) {
//     if (category.startsWith(key) || key.startsWith(category)) return CATEGORY_COLORS[key];
//   }
//   return DEFAULT_COLOR;
// }

// function shortCategory(cat) {
//   if (!cat) return '?';
//   const parts = cat.split('.');
//   return parts[parts.length - 1];
// }

// // ── vis.js setup ──

// const visNodes = new vis.DataSet();
// const visEdges = new vis.DataSet();

// const container = document.getElementById('graph');
// const network = new vis.Network(container, { nodes: visNodes, edges: visEdges }, {
//   physics: false,
//   nodes: {
//     shape: 'dot',
//     size: 14,
//     font: { color: '#ccc', size: 11 },
//     borderWidth: 2,
//   },
//   edges: {
//     color: { color: '#3a3d4a', highlight: '#7c8db5' },
//     font: { color: '#666', size: 9, strokeWidth: 0 },
//     smooth: { type: 'continuous' },
//   },
//   interaction: { hover: true, tooltipDelay: 100 },
// });

// // ── state ──

// const MAX_BUFFER = 500;
// const frameBuffer = [];
// let currentIndex = -1;
// let playing = true;
// let lastData = null;
// const hiddenCategories = new Set();
// const allCategories = new Set();

// // ── playback controls ──

// function togglePlay() {
//   playing = !playing;
//   const btn = document.getElementById('btn-play');
//   btn.textContent = playing ? '⏸ Pause' : '▶ Play';
//   btn.classList.toggle('active', playing);
//   document.getElementById('btn-prev').disabled = playing;
//   document.getElementById('btn-next').disabled = playing;

//   if (playing) {
//     currentIndex = frameBuffer.length - 1;
//     renderCurrentFrame();
//   }
//   updateCounter();
// }

// function stepFrame(delta) {
//   if (playing) return;
//   const next = currentIndex + delta;
//   if (next < 0 || next >= frameBuffer.length) return;
//   currentIndex = next;
//   renderCurrentFrame();
//   updateCounter();
// }

// function updateCounter() {
//   const el = document.getElementById('frame-counter');
//   if (frameBuffer.length === 0) { el.textContent = ''; return; }
//   el.textContent = `Frame ${currentIndex + 1} / ${frameBuffer.length}`;
// }

// // ── category filter ──

// function toggleCategory(cat) {
//   if (hiddenCategories.has(cat)) hiddenCategories.delete(cat);
//   else hiddenCategories.add(cat);
//   renderCurrentFrame();
// }

// function buildFilters() {
//   const list = document.getElementById('filter-list');
//   list.innerHTML = '';
//   const sorted = [...allCategories].sort();
//   for (const cat of sorted) {
//     const checked = !hiddenCategories.has(cat) ? 'checked' : '';
//     const color = getColor(cat);
//     list.innerHTML += `
//       <label class="filter-item">
//         <input type="checkbox" ${checked} onchange="toggleCategory('${cat}')" />
//         <span class="legend-dot" style="background:${color}"></span>
//         ${shortCategory(cat)}
//       </label>`;
//   }
// }

// // ── render ──

// const SCALE = 8;

// function renderCurrentFrame() {
//   if (currentIndex < 0 || currentIndex >= frameBuffer.length) return;
//   const data = frameBuffer[currentIndex];
//   lastData = data;

//   const filteredNodes = data.nodes.filter(n => !hiddenCategories.has(n.category));
//   const filteredIds = new Set(filteredNodes.map(n => n.id));
//   const filteredEdges = data.edges.filter(e => filteredIds.has(e.to));

//   const newNodes = [{
//     id: 'ego', label: 'EGO', x: 0, y: 0, fixed: true, size: 20,
//     color: { background: '#22c55e', border: '#16a34a' },
//     font: { color: '#fff', size: 13, bold: true },
//   }];

//   for (const n of filteredNodes) {
//     const c = getColor(n.category);
//     newNodes.push({
//       id: n.id,
//       label: shortCategory(n.category),
//       x: n.rel_x * SCALE,
//       y: -n.rel_y * SCALE,
//       fixed: true,
//       color: { background: c, border: c },
//       font: { color: '#ccc', size: 10 },
//     });
//   }

//   const newEdges = filteredEdges.map((e, i) => ({
//     id: `e-${i}`,
//     from: e.from,
//     to: e.to,
//     label: `${e.distance}m`,
//     title: `${e.zone} · ${e.direction}`,
//   }));

//   visNodes.clear();
//   visEdges.clear();
//   visNodes.add(newNodes);
//   visEdges.add(newEdges);

//   // update header info
//   const frameEl = document.getElementById('frame-info');
//   const ts = data.ego?.timestamp;
//   const time = ts ? new Date(ts * 1000).toLocaleTimeString() : '';
//   frameEl.textContent = `${filteredNodes.length}/${data.nodes.length} objects · ${time}`;
// }

// // ── info panel ──

// function showNodeInfo(nodeId) {
//   const panel = document.getElementById('panel-content');
//   if (nodeId === 'ego' && lastData?.ego) {
//     const e = lastData.ego;
//     panel.innerHTML = makeTable({ Type: 'Ego Vehicle', X: e.x?.toFixed(2), Y: e.y?.toFixed(2), Timestamp: e.timestamp });
//     return;
//   }
//   const n = lastData?.nodes.find(n => n.id === nodeId);
//   if (!n) return;
//   panel.innerHTML = makeTable({
//     Category: n.category, 'Rel X': n.rel_x?.toFixed(2), 'Rel Y': n.rel_y?.toFixed(2),
//     'Vel X': n.vel_x?.toFixed(2), 'Vel Y': n.vel_y?.toFixed(2),
//   });
// }

// function showEdgeInfo(edgeId) {
//   const panel = document.getElementById('panel-content');
//   const idx = parseInt(edgeId.replace('e-', ''), 10);
//   const filteredEdges = lastData?.edges.filter(e => {
//     const n = lastData.nodes.find(n => n.id === e.to);
//     return n && !hiddenCategories.has(n.category);
//   });
//   const e = filteredEdges?.[idx];
//   if (!e) return;
//   panel.innerHTML = makeTable({
//     From: e.from, To: shortCategory(lastData.nodes.find(n => n.id === e.to)?.category),
//     Distance: e.distance + ' m', Zone: e.zone, Direction: e.direction,
//   });
// }

// function makeTable(obj) {
//   return `<table>${Object.entries(obj).map(([k, v]) => `<tr><td>${k}</td><td>${v ?? '—'}</td></tr>`).join('')}</table>`;
// }

// network.on('click', params => {
//   if (params.nodes.length) showNodeInfo(params.nodes[0]);
//   else if (params.edges.length) showEdgeInfo(params.edges[0]);
// });

// // ── WebSocket ──

// const statusEl = document.getElementById('status');

// function connect() {
//   const ws = new WebSocket(`ws://${location.host}/ws/graph`);

//   ws.onopen = () => {
//     statusEl.textContent = '🟢 Live';
//     statusEl.className = 'connected';
//   };

//   ws.onmessage = (event) => {
//     const data = JSON.parse(event.data);

//     // track categories for filter
//     for (const n of data.nodes) allCategories.add(n.category);
//     buildFilters();

//     // buffer
//     frameBuffer.push(data);
//     if (frameBuffer.length > MAX_BUFFER) frameBuffer.shift();

//     if (playing) {
//       currentIndex = frameBuffer.length - 1;
//       renderCurrentFrame();
//     }
//     updateCounter();
//   };

//   ws.onclose = () => {
//     statusEl.textContent = '🔴 Disconnected';
//     statusEl.className = 'error';
//     setTimeout(connect, 2000);
//   };

//   ws.onerror = () => ws.close();
// }
// window.togglePlay = togglePlay;
// window.stepFrame = stepFrame;
// window.toggleCategory = toggleCategory;
// connect();

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

const visNodes = new vis.DataSet();
const visEdges = new vis.DataSet();

const container = document.getElementById('graph');
const network = new vis.Network(container, { nodes: visNodes, edges: visEdges }, {
  physics: false,
  nodes: {
    shape: 'dot', size: 14,
    font: { color: '#ccc', size: 11 },
    borderWidth: 2,
  },
  edges: {
    color: { color: '#3a3d4a', highlight: '#7c8db5' },
    font: { color: '#666', size: 9, strokeWidth: 0 },
    smooth: { type: 'continuous' },
  },
  interaction: { hover: true, tooltipDelay: 100 },
});

// ── state ──

let ws = null;
let lastData = null;
let isPaused = false;
const hiddenCategories = new Set();
const allCategories = new Set();

// ── send command to backend ──

function send(obj) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(obj));
  }
}

// ── playback controls ──

function togglePlay() {
  isPaused = !isPaused;
  send({ action: isPaused ? 'pause' : 'play' });
  updateButtons();
}

function stepFrame(delta) {
  if (!isPaused) return;
  send({ action: 'step', delta });
}

function updateButtons() {
  const btn = document.getElementById('btn-play');
  btn.textContent = isPaused ? '▶ Play' : '⏸ Pause';
  btn.classList.toggle('active', !isPaused);
  document.getElementById('btn-prev').disabled = !isPaused;
  document.getElementById('btn-next').disabled = !isPaused;
}

// ── category filter ──

function toggleCategory(cat) {
  if (hiddenCategories.has(cat)) hiddenCategories.delete(cat);
  else hiddenCategories.add(cat);
  if (lastData) renderGraph(lastData);
}

function buildFilters() {
  const list = document.getElementById('filter-list');
  list.innerHTML = '';
  for (const cat of [...allCategories].sort()) {
    const checked = !hiddenCategories.has(cat) ? 'checked' : '';
    const color = getColor(cat);
    list.innerHTML += `
      <label class="filter-item">
        <input type="checkbox" ${checked} onchange="toggleCategory('${cat}')" />
        <span class="legend-dot" style="background:${color}"></span>
        ${shortCategory(cat)}
      </label>`;
  }
}

// ── render ──

const SCALE = 8;

function renderGraph(data) {
  lastData = data;

  const filteredNodes = data.nodes.filter(n => !hiddenCategories.has(n.category));
  const filteredIds = new Set(filteredNodes.map(n => n.id));
  const filteredEdges = data.edges.filter(e => filteredIds.has(e.to));

  const newNodes = [{
    id: 'ego', label: 'EGO', x: 0, y: 0, fixed: true, size: 20,
    color: { background: '#22c55e', border: '#16a34a' },
    font: { color: '#fff', size: 13, bold: true },
  }];

  for (const n of filteredNodes) {
    const c = getColor(n.category);
    newNodes.push({
      id: n.id,
      label: shortCategory(n.category),
      x: n.rel_x * SCALE,
      y: -n.rel_y * SCALE,
      fixed: true,
      color: { background: c, border: c },
      font: { color: '#ccc', size: 10 },
    });
  }

  const newEdges = filteredEdges.map((e, i) => ({
    id: `e-${i}`, from: e.from, to: e.to,
    label: `${e.distance}m`,
    title: `${e.zone} · ${e.direction}`,
  }));

  visNodes.clear();
  visEdges.clear();
  visNodes.add(newNodes);
  visEdges.add(newEdges);
}

// ── info panel ──

function showNodeInfo(nodeId) {
  const panel = document.getElementById('panel-content');
  if (nodeId === 'ego' && lastData?.ego) {
    const e = lastData.ego;
    panel.innerHTML = makeTable({ Type: 'Ego Vehicle', X: e.x?.toFixed(2), Y: e.y?.toFixed(2), Timestamp: e.timestamp });
    return;
  }
  const n = lastData?.nodes.find(n => n.id === nodeId);
  if (!n) return;
  panel.innerHTML = makeTable({
    Category: n.category, 'Rel X': n.rel_x?.toFixed(2), 'Rel Y': n.rel_y?.toFixed(2),
    'Vel X': n.vel_x?.toFixed(2), 'Vel Y': n.vel_y?.toFixed(2),
  });
}

function showEdgeInfo(edgeId) {
  const panel = document.getElementById('panel-content');
  const idx = parseInt(edgeId.replace('e-', ''), 10);
  const filteredEdges = lastData?.edges.filter(e => {
    const n = lastData.nodes.find(n => n.id === e.to);
    return n && !hiddenCategories.has(n.category);
  });
  const e = filteredEdges?.[idx];
  if (!e) return;
  panel.innerHTML = makeTable({
    From: e.from, To: shortCategory(lastData.nodes.find(n => n.id === e.to)?.category),
    Distance: e.distance + ' m', Zone: e.zone, Direction: e.direction,
  });
}

function makeTable(obj) {
  return `<table>${Object.entries(obj).map(([k, v]) => `<tr><td>${k}</td><td>${v ?? '—'}</td></tr>`).join('')}</table>`;
}

network.on('click', params => {
  if (params.nodes.length) showNodeInfo(params.nodes[0]);
  else if (params.edges.length) showEdgeInfo(params.edges[0]);
});

// ── WebSocket ──

const statusEl = document.getElementById('status');
const frameEl = document.getElementById('frame-info');
const counterEl = document.getElementById('frame-counter');

function connect() {
  ws = new WebSocket(`ws://${location.host}/ws/graph`);

  ws.onopen = () => {
    statusEl.textContent = '🟢 Live';
    statusEl.className = 'connected';
    // sync state if page reloaded while paused
    if (isPaused) send({ action: 'pause' });
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    for (const n of data.nodes) allCategories.add(n.category);
    buildFilters();

    // sync pause state from server
    if (data.paused !== undefined && data.paused !== isPaused) {
      isPaused = data.paused;
      updateButtons();
    }

    renderGraph(data);

    const ts = data.ego?.timestamp;
    const time = ts ? new Date(ts * 1000).toLocaleTimeString() : '';
    const visible = data.nodes.filter(n => !hiddenCategories.has(n.category)).length;
    frameEl.textContent = `${visible}/${data.nodes.length} objects · ${time}`;
    counterEl.textContent = data.frame_index >= 0
      ? `Frame ${data.frame_index + 1} / ${data.frame_total}`
      : '';
  };

  ws.onclose = () => {
    statusEl.textContent = '🔴 Disconnected';
    statusEl.className = 'error';
    setTimeout(connect, 2000);
  };

  ws.onerror = () => ws.close();
}

connect();

// ── expose to HTML onclick ──

window.togglePlay = togglePlay;
window.stepFrame = stepFrame;
window.toggleCategory = toggleCategory;