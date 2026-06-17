"""Render the report to a shippable file. Markdown offline, a PDF with a key.

Offline, the report is written as Markdown, which is enough to read and commit.
With a key, the code execution tool renders a one-page PDF in the sandbox and the
Files API downloads it. Guarded so the demo never calls the model: a failure or
no key leaves the Markdown in place.
"""

from __future__ import annotations

import os

from ..platform import client as _client


def render_report(report_text: str, *, out_dir: str = "out", basename: str = "weekly_report") -> dict:
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, basename + ".md")
    with open(md_path, "w") as f:
        f.write(report_text)

    c = _client.client()
    if c is None:
        return {"live": False, "path": md_path, "format": "markdown"}
    try:
        pdf_path = _render_pdf(c, report_text, out_dir, basename)
        return {"live": True, "path": pdf_path, "format": "pdf", "markdown": md_path}
    except Exception as e:
        return {"live": False, "path": md_path, "format": "markdown", "error": str(e)}


def _render_pdf(c, report_text: str, out_dir: str, basename: str) -> str:
    prompt = ("Render the report below as a clean one-page PDF named "
              f"{basename}.pdf using reportlab, monospace, preserve the layout. "
              "Save it so it can be downloaded.\n\n" + report_text)
    resp = c.messages.create(
        model=_client.MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
        tools=[{"type": "code_execution_20260120", "name": "code_execution"}],
    )
    file_id = _first_output_file_id(resp)
    if not file_id:
        raise RuntimeError("code execution produced no downloadable file")
    pdf_path = os.path.join(out_dir, basename + ".pdf")
    content = c.beta.files.download(file_id)
    content.write_to_file(pdf_path)
    return pdf_path


def _first_output_file_id(resp):
    for block in getattr(resp, "content", []):
        if getattr(block, "type", "") != "bash_code_execution_tool_result":
            continue
        result = getattr(block, "content", None)
        for ref in getattr(result, "content", None) or []:
            fid = getattr(ref, "file_id", None)
            if fid:
                return fid
    return None
