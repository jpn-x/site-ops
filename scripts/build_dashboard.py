#!/usr/bin/env python3
"""Build a static dashboard HTML from sites.json and health check results."""

import json
import subprocess
import os
from datetime import datetime

def get_site_status(url):
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "15", url],
            capture_output=True, text=True, timeout=20
        )
        code = int(result.stdout.strip())
        return code, code >= 200 and code < 400
    except Exception:
        return 0, False

def get_workflow_status(repo, token=None):
    try:
        cmd = ["gh", "api", f"repos/{repo}/actions/workflows/update.yml/runs?per_page=1&status=completed",
               "--jq", ".workflow_runs[0] | [.conclusion, .updated_at] | @tsv"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("\t")
            return parts[0], parts[1] if len(parts) > 1 else ""
        return "unknown", ""
    except Exception:
        return "unknown", ""

def main():
    with open("sites.json") as f:
        data = json.load(f)

    now = datetime.now().strftime("%Y-%m-%d %H:%M JST")
    sites = data["sites"]

    rows = []
    total = ok_count = fail_count = 0

    for site in sites:
        total += 1
        code, is_ok = get_site_status(site["url"])

        wf_status = ""
        wf_date = ""
        if site.get("auto_update"):
            wf_status, wf_date = get_workflow_status(site["repo"])
            if wf_date:
                wf_date = wf_date[:16].replace("T", " ")

        if is_ok:
            ok_count += 1
            status_badge = f'<span class="badge ok">✅ {code}</span>'
        else:
            fail_count += 1
            status_badge = f'<span class="badge fail">❌ {code}</span>'

        update_cell = ""
        if site.get("auto_update"):
            wf_icon = "✅" if wf_status == "success" else "❌" if wf_status == "failure" else "⚠️"
            update_cell = f'{wf_icon} {wf_status} <small>{wf_date}</small>'

        rows.append(f"""
        <tr class="{'fail-row' if not is_ok else ''}">
          <td>{site['name']}</td>
          <td>{status_badge}</td>
          <td><a href="{site['url']}" target="_blank">🔗 開く</a></td>
          <td>{update_cell}</td>
          <td><a href="https://github.com/{site['repo']}" target="_blank">{site['repo']}</a></td>
          <td>{site.get('category', '')}</td>
        </tr>""")

    rows_html = "\n".join(rows)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Site-Ops Dashboard</title>
<style>
  :root {{ --bg: #0d1117; --card: #161b22; --border: #30363d; --text: #e6edf3; --green: #3fb950; --red: #f85149; --yellow: #d29922; --blue: #58a6ff; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); padding: 20px; }}
  .header {{ text-align: center; margin-bottom: 30px; }}
  .header h1 {{ font-size: 1.8em; margin-bottom: 8px; }}
  .header .time {{ color: #8b949e; font-size: 0.9em; }}
  .summary {{ display: flex; gap: 16px; justify-content: center; margin-bottom: 24px; flex-wrap: wrap; }}
  .summary .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px 24px; text-align: center; min-width: 120px; }}
  .summary .card .num {{ font-size: 2em; font-weight: bold; }}
  .summary .card .label {{ color: #8b949e; font-size: 0.85em; margin-top: 4px; }}
  .card .num.green {{ color: var(--green); }}
  .card .num.red {{ color: var(--red); }}
  table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 8px; overflow: hidden; }}
  th {{ background: #21262d; padding: 12px 16px; text-align: left; font-size: 0.85em; color: #8b949e; text-transform: uppercase; }}
  td {{ padding: 10px 16px; border-top: 1px solid var(--border); }}
  tr:hover {{ background: #1c2128; }}
  tr.fail-row {{ background: rgba(248,81,73,0.1); }}
  .badge {{ padding: 3px 8px; border-radius: 12px; font-size: 0.85em; }}
  .badge.ok {{ background: rgba(63,185,80,0.15); color: var(--green); }}
  .badge.fail {{ background: rgba(248,81,73,0.15); color: var(--red); }}
  a {{ color: var(--blue); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .actions {{ text-align: center; margin-top: 24px; }}
  .actions a {{ display: inline-block; background: #238636; color: white; padding: 10px 24px; border-radius: 6px; margin: 6px; font-weight: 500; }}
  .actions a:hover {{ background: #2ea043; text-decoration: none; }}
  small {{ color: #8b949e; }}
</style>
</head>
<body>
  <div class="header">
    <h1>🛰️ Site-Ops Dashboard</h1>
    <div class="time">最終チェック: {now}</div>
  </div>

  <div class="summary">
    <div class="card"><div class="num">{total}</div><div class="label">Total Sites</div></div>
    <div class="card"><div class="num green">{ok_count}</div><div class="label">正常</div></div>
    <div class="card"><div class="num red">{fail_count}</div><div class="label">エラー</div></div>
  </div>

  <table>
    <thead>
      <tr><th>サイト名</th><th>ステータス</th><th>リンク</th><th>自動更新</th><th>リポジトリ</th><th>カテゴリ</th></tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>

  <div class="actions">
    <a href="https://github.com/jpn-x/site-ops/actions/workflows/health-check.yml">🔄 ヘルスチェック実行</a>
    <a href="https://github.com/jpn-x/site-ops/actions/workflows/trigger-update.yml">🚀 更新トリガー</a>
    <a href="https://github.com/jpn-x/site-ops/actions/workflows/auto-fix.yml">🔧 修正実行</a>
  </div>
</body>
</html>"""

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard built: {ok_count}/{total} OK, {fail_count} failures")

if __name__ == "__main__":
    main()
