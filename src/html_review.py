# src/html_review_templates.py
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

_TEMPLATE_DIR_NAME = "templates"  # under the package directory


def write_citation_review_files(
    project_name: str,
    target_pdf_path: str,
    chunks: List[Any],
    hits_per_chunk: List[List[Dict[str, Any]]],
    out_dir: Optional[str] = None,
) -> str:
    """
    Create a review folder for the target PDF. The folder will contain:
      - index.html, review.js, style.css (copied from templates_dir)
      - entries.json (the data)
    Returns path to index.html
    """
    pkg_dir = Path(__file__).resolve().parent
    pkg_templates = pkg_dir / _TEMPLATE_DIR_NAME

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
