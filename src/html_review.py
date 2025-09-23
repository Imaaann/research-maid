# src/html_review_templates.py
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

_TEMPLATE_DIR_NAME = "templates"  # under the package directory


# -------------------------
# Default template strings
# -------------------------
_INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Research-Maid — Citation Review</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <header>
      <h1 id="title">Research-Maid — Citation Review</h1>
      <div id="meta" class="small"></div>
    </header>

    <main id="content">
      <div id="loading">Loading entries…</div>
    </main>

    <footer class="small">This view is read-only: each chunk is shown with the ranked hits under it.</footer>
  </div>

  <script src="review.js"></script>
</body>
</html>
"""

_REVIEW_JS = """// review.js — minimal renderer
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
    textTd.innerHTML = escapeHtml(h.snippet || '').replace(/\\n/g, '<br>');
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
"""

_STYLE_CSS = """/* style.css — neutral minimal styling */
body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; background: #f6f7f9; color: #222; margin: 0; padding: 20px; }
.container { max-width: 980px; margin: 0 auto; }
header { display:flex; justify-content:space-between; align-items:baseline; margin-bottom: 12px; }
h1 { margin: 0; font-size: 1.1rem; }
.small { color: #666; font-size: 0.9rem; }
.card { background: #fff; border-radius: 6px; padding: 12px; margin-bottom: 12px; box-shadow: 0 1px 0 rgba(0,0,0,0.04); }
.card-header { margin-bottom: 8px; }
.chunk-text { background: #fbfbfe; padding: 10px; border-radius: 4px; white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace; }
.hits-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
.hits-table th, .hits-table td { border: 1px solid #eee; padding: 8px; text-align: left; vertical-align: top; }
.hits-table th { background: #fafafa; font-weight: 600; }
a { color: #1a73e8; text-decoration: none; }
a:hover { text-decoration: underline; }
footer { margin-top: 18px; color: #666; font-size: 0.85rem; }
"""


def _package_templates_dir() -> Path:
    """Return package templates directory path: (src/templates)"""
    pkg_dir = Path(__file__).resolve().parent
    return pkg_dir / _TEMPLATE_DIR_NAME


def ensure_package_templates(templates_dir: Optional[Path] = None) -> Path:
    """
    Ensure a templates directory exists (under package) and contains the default
    index.html, review.js and style.css if missing. Returns the templates_dir path.
    """
    if templates_dir is None:
        templates_dir = _package_templates_dir()

    templates_dir.mkdir(parents=True, exist_ok=True)

    # Write default files only if missing (so dev edits persist)
    files = {
        "index.html": _INDEX_HTML,
        "review.js": _REVIEW_JS,
        "style.css": _STYLE_CSS,
    }
    for fname, content in files.items():
        p = templates_dir / fname
        if not p.exists():
            p.write_text(content, encoding="utf-8")
    return templates_dir


def write_citation_review_files(
    project_name: str,
    target_pdf_path: str,
    chunks: List[Any],
    hits_per_chunk: List[List[Dict[str, Any]]],
    templates_dir: Optional[str] = None,
    out_dir: Optional[str] = None,
) -> str:
    """
    Create a review folder for the target PDF. The folder will contain:
      - index.html, review.js, style.css (copied from templates_dir)
      - entries.json (the data)
    Returns path to index.html
    """
    # ensure package templates exist (and write defaults if not)
    pkg_templates = ensure_package_templates(
        Path(templates_dir) if templates_dir else None
    )

    target_path = Path(target_pdf_path)
    default_out = target_path.with_name(target_path.stem + "_citation_review")
    out_folder = Path(out_dir) if out_dir else default_out
    out_folder.mkdir(parents=True, exist_ok=True)

    # Build minimal entries structure (safe fields)
    entries = []
    for idx, (chunk, hits) in enumerate(zip(chunks, hits_per_chunk), start=1):
        # normalize chunk text
        if isinstance(chunk, dict):
            text = chunk.get("text") or chunk.get("chunk") or ""
        elif isinstance(chunk, (list, tuple)) and len(chunk) > 0:
            text = chunk[0]
        else:
            text = str(chunk or "")
        # simplify hits
        simple_hits = []
        for h in (hits or [])[:20]:
            meta = h.get("metadata", {}) if isinstance(h, dict) else {}
            simple_meta = {
                "file_path": meta.get("file_path") or meta.get("source") or "",
                "page": meta.get("page"),
                "distance": h.get("distance"),
                "id": h.get("id"),
            }
            snippet = h.get("text") or ""
            if len(snippet) > 600:
                snippet = snippet[:600] + "…"
            simple_hits.append({"meta": simple_meta, "snippet": snippet})
        entries.append({"idx": idx, "text": text, "hits": simple_hits})

    payload = {"project": project_name, "target": str(target_path), "entries": entries}
    entries_path = out_folder / "entries.json"
    entries_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # copy template files into the out_folder (so review folder is self-contained)
    for fname in ("index.html", "review.js", "style.css"):
        src = pkg_templates / fname
        dst = out_folder / fname
        # copy (overwrite) so the review folder always has current template snapshot
        shutil.copyfile(src, dst)

    return str(out_folder / "index.html")
