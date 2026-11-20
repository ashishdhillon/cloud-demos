#!/usr/bin/env python3
"""
Master PDF Explainer Generator for Cloud Computing Practicals 01 - 15.
Generates 15 standalone, publication-quality 2-page A4 PDF files.
"""

import os
import sys
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = "/Users/ashishdhillon/ai-company/cloud-demos"
DOCS_PDF_DIR = os.path.join(ROOT_DIR, "docs", "pdf")
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

sys.path.insert(0, os.path.join(ROOT_DIR, "docs"))
from practical_data import PRACTICALS

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Practical {num}: {title} - Layman's Explainer & Student Lab Guide</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 12mm 14mm;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #0f172a;
    background: #ffffff;
    font-size: 10pt;
    line-height: 1.45;
  }}
  .page {{
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 270mm;
    max-height: 270mm;
    overflow: hidden;
  }}
  .page:last-child {{
    page-break-after: avoid;
  }}
  .header {{
    border-bottom: 2px solid #2563eb;
    padding-bottom: 8px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}
  .header-badge {{
    font-size: 8.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #2563eb;
    background: #eff6ff;
    padding: 3px 8px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 4px;
  }}
  .title {{
    font-size: 16.5pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
  }}
  .subtitle {{
    font-size: 9.5pt;
    color: #475569;
    font-weight: 500;
    margin-top: 2px;
  }}
  .meta-tag {{
    font-size: 8.5pt;
    font-weight: 600;
    color: #64748b;
  }}

  .grid-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 10px;
  }}
  .card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 9px 12px;
  }}
  .card-title {{
    font-size: 9.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .card-title.blue {{ color: #1d4ed8; }}
  .card-title.amber {{ color: #b45309; }}
  .card-title.green {{ color: #047857; }}
  .card-title.purple {{ color: #6d28d9; }}

  p {{ margin-bottom: 5px; font-size: 8.5pt; color: #334155; }}
  ul {{ padding-left: 14px; margin-bottom: 5px; font-size: 8.5pt; color: #334155; }}
  li {{ margin-bottom: 2px; }}

  .infographic-box {{
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px;
    margin: 6px 0;
    text-align: center;
  }}
  .infographic-title {{
    font-size: 8.5pt;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
  }}

  .table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 8pt;
    margin: 6px 0;
  }}
  .table th, .table td {{
    border: 1px solid #e2e8f0;
    padding: 5px 7px;
    text-align: left;
  }}
  .table th {{
    background: #f1f5f9;
    font-weight: 700;
    color: #0f172a;
  }}

  .q-box {{
    background: #f8fafc;
    border-left: 3px solid #2563eb;
    padding: 5px 9px;
    margin-bottom: 6px;
    border-radius: 0 6px 6px 0;
  }}
  .q-title {{
    font-size: 8.5pt;
    font-weight: 700;
    color: #0f172a;
  }}
  .q-ans {{
    font-size: 8pt;
    color: #334155;
    margin-top: 2px;
  }}

  .footer {{
    border-top: 1px solid #e2e8f0;
    padding-top: 5px;
    display: flex;
    justify-content: space-between;
    font-size: 7.5pt;
    color: #94a3b8;
  }}
</style>
</head>
<body>

<!-- PAGE 1: THEORY, LAYMAN ANALOGY, USE CASE & INFOGRAPHIC -->
<div class="page">
  <div>
    <div class="header">
      <div>
        <div class="header-badge">Practical {num} • Cloud Systems Engineering</div>
        <div class="title">{title}</div>
        <div class="subtitle">{subtitle}</div>
      </div>
      <div style="text-align: right;">
        <div class="meta-tag">Port: {port}</div>
        <div class="meta-tag">Budget: {memory}</div>
      </div>
    </div>

    <!-- What is it & Layman Analogy -->
    <div class="grid-2">
      <div class="card">
        <div class="card-title blue">💡 What is this in Plain English?</div>
        {what_is_it}
      </div>

      <div class="card">
        <div class="card-title amber">{analogy_title}</div>
        {layman_analogy}
      </div>
    </div>

    <!-- Real-World Use Case -->
    <div class="card" style="margin-bottom: 8px;">
      <div class="card-title purple">🏢 Real-World Industry Use Case: Why Tech Giants Spend Millions Here</div>
      {use_case}
    </div>

    <!-- Architecture Infographic -->
    <div class="infographic-box">
      <div class="infographic-title">Visual Architecture Infographic: {infographic_caption}</div>
      {svg_infographic}
    </div>
  </div>

  <div class="footer">
    <span>Cloud Systems Engineering Educational Series • Practical {num}</span>
    <span>Page 1 of 2</span>
  </div>
</div>

<!-- PAGE 2: HANDS-ON STEPS, WHAT COMPUTER DOES & VIVA GUIDE -->
<div class="page">
  <div>
    <div class="header">
      <div>
        <div class="title" style="font-size: 13pt;">Practical {num} • Hands-on Execution & Viva Defense</div>
        <div class="subtitle">Step-by-Step Simulator Walkthrough & Technical Interview Mastery</div>
      </div>
    </div>

    <!-- Steps Table -->
    <div class="card" style="margin-bottom: 8px;">
      <div class="card-title green">🛠️ Step-by-Step Hands-On Guide: What You Do vs Behind The Scenes</div>
      <table class="table">
        <thead>
          <tr>
            <th style="width: 14%;">Step</th>
            <th style="width: 36%;">Action (What You Click / Run)</th>
            <th style="width: 50%;">What the Computer is Doing Behind the Scenes (Layman)</th>
          </tr>
        </thead>
        <tbody>
          {steps_rows}
        </tbody>
      </table>
    </div>

    <!-- Key Takeaway -->
    <div class="card" style="margin-bottom: 8px; background: #f0fdf4; border-color: #bbf7d0;">
      <div class="card-title green">🎯 The "Aha!" Engineering Takeaway</div>
      <p style="color: #166534; font-size: 8.5pt;"><strong>{takeaway_lead}</strong> {takeaway_body}</p>
    </div>

    <!-- Viva & Interview Questions -->
    <div class="card">
      <div class="card-title blue">🎓 Viva & Job Interview Questions & Answers (Cheat-Sheet)</div>
      {viva_boxes}
    </div>
  </div>

  <div class="footer">
    <span>Practical {num}: {title} • Verified Reference Guide</span>
    <span>Page 2 of 2</span>
  </div>
</div>

</body>
</html>
"""

def generate_pdf_for_practical(p):
    num = p["num"]
    dir_name = p["dir"]
    slug = dir_name.replace(f"practical-{num}-", "")
    
    html_content = HTML_TEMPLATE.format(**p)
    tmp_html = f"/tmp/practical_{num}_explainer.html"
    
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    dest_dir_pdf = os.path.join(ROOT_DIR, dir_name, "EXPLAINER.pdf")
    dest_central_pdf = os.path.join(DOCS_PDF_DIR, f"practical-{num}-{slug}-explainer.pdf")

    user_data = f"/tmp/chrome_pdf_{num}"
    os.makedirs(user_data, exist_ok=True)
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--user-data-dir={user_data}",
        f"--print-to-pdf={dest_dir_pdf}",
        tmp_html
    ]
    
    start_t = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    duration = round(time.time() - start_t, 2)
    
    if res.returncode != 0 or not os.path.isfile(dest_dir_pdf):
        print(f"❌ Failed to generate Practical {num}: {res.stderr}")
        return False

    subprocess.run(["cp", dest_dir_pdf, dest_central_pdf])

    size_kb = round(os.path.getsize(dest_dir_pdf) / 1024, 1)
    print(f"✅ Practical {num}: {p['title']} -> {dest_dir_pdf} ({size_kb} KB, {duration}s)")
    return True

def main():
    targets = PRACTICALS
    if len(sys.argv) > 1:
        req = sys.argv[1].zfill(2)
        targets = [p for p in PRACTICALS if p['num'] == req]

    print("=" * 75)
    print(f" 📄 GENERATING {len(targets)} STANDALONE EXPLAINER PDFS")
    print("=" * 75)
    print(f" Total Practicals : {len(targets)}")
    print(f" Destination 1    : <practical-dir>/EXPLAINER.pdf")
    print(f" Destination 2    : docs/pdf/practical-XX-<slug>-explainer.pdf")
    print("=" * 75)

    start_all = time.time()
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        results = list(executor.map(generate_pdf_for_practical, targets))

    total_time = round(time.time() - start_all, 2)
    success_count = sum(1 for r in results if r)
    print("=" * 75)
    print(f" 🎉 Completed {success_count}/{len(PRACTICALS)} PDFs in {total_time} seconds!")
    print("=" * 75)

if __name__ == "__main__":
    main()
