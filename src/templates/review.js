// review.js — minimal renderer
async function loadEntries() {
  try {
    const resp = await fetch('entries.json');
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    return await resp.json();
  } catch (e) {
    console.error('Failed to load entries.json', e);
    document.getElementById('loading').textContent = 'Failed to load entries.json. Try serving this folder via a local HTTP server (python -m http.server).';
    return null;
  }
}

function escapeHtml(s) {
  if (!s) return '';
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function createHitsTable(hits) {
  const table = document.createElement('table');
  table.className = 'hits-table';
  const thead = document.createElement('thead');
  thead.innerHTML = '<tr><th>#</th><th>file-name</th><th>Text (snippet)</th></tr>';
  table.appendChild(thead);
  const tbody = document.createElement('tbody');
  hits.forEach((h, i) => {
    const tr = document.createElement('tr');
    const numTd = document.createElement('td'); numTd.textContent = (i+1);
    const fileTd = document.createElement('td');
    const fp = h.meta.file_path || '';
    if (fp) {
      const a = document.createElement('a');
      // open via file:// (browser may restrict depending on security)
      a.href = 'file://' + fp + (h.meta.page ? '#page=' + h.meta.page : '');
      a.textContent = fp.split('/').pop();
      a.target = '_blank';
      a.rel = 'noreferrer noopener';
      fileTd.appendChild(a);
    } else {
      fileTd.textContent = '(no file)';
    }
    const textTd = document.createElement('td');
    textTd.innerHTML = escapeHtml(h.snippet || '').replace(/\n/g, '<br>');
    tr.appendChild(numTd); tr.appendChild(fileTd); tr.appendChild(textTd);
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  return table;
}

function renderEntry(entry) {
  const card = document.createElement('div');
  card.className = 'card';
  const h = document.createElement('div');
  h.className = 'card-header'; h.innerHTML = '<strong>Chunk #' + entry.idx + '</strong>';
  card.appendChild(h);

  const pre = document.createElement('pre');
  pre.className = 'chunk-text';
  pre.textContent = entry.text;
  card.appendChild(pre);

  const hitsTitle = document.createElement('div');
  hitsTitle.className = 'small'; hitsTitle.textContent = 'Top hits (ranked):';
  card.appendChild(hitsTitle);

  const table = createHitsTable(entry.hits || []);
  card.appendChild(table);

  return card;
}

document.addEventListener('DOMContentLoaded', async () => {
  const payload = await loadEntries();
  if (!payload) return;
  document.getElementById('meta').textContent = 'Project: ' + payload.project + ' — Target: ' + payload.target;
  const content = document.getElementById('content');
  content.innerHTML = '';
  payload.entries.forEach(e => {
    content.appendChild(renderEntry(e));
  });
});
