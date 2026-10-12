import os, json, math, urllib.request

token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
headers = {"User-Agent": "Koderguru-Lang-Stats"}
if token:
    headers["Authorization"] = f"Bearer {token}"

repos = []
page = 1
while True:
    url = f"https://api.github.com/users/Koderguru/repos?per_page=100&page={page}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        batch = json.loads(resp.read().decode())
    if not batch:
        break
    repos.extend(batch)
    if len(batch) < 100:
        break
    page += 1

total_repos = len(repos)
lang_counts = {}

for r in repos:
    pl = r.get("language")
    name = pl if pl else "Other/Data"
    lang_counts[name] = lang_counts.get(name, 0) + 1

colors = {
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "HTML": "#e34c26",
    "Kotlin": "#A97BFF",
    "Python": "#3572A5",
    "CSS": "#563d7c",
    "Swift": "#F05138",
    "Dart": "#00B4AB",
    "Go": "#00ADD8",
    "C++": "#f34b7d",
    "Makefile": "#427819",
    "Other/Data": "#6e7681"
}

display_order = [
    "TypeScript", "JavaScript", "HTML", "Kotlin",
    "Python", "CSS", "Swift", "Dart",
    "Go", "C++", "Makefile", "Other/Data"
]

data = []
for name in display_order:
    cnt = lang_counts.get(name, 0)
    if cnt > 0:
        pct = (cnt / total_repos) * 100 if total_repos > 0 else 0
        color = colors.get(name, "#8b949e")
        data.append({
            "name": name,
            "count": cnt,
            "pct": pct,
            "color": color
        })

width = 540
height = 240

cx = 110
cy = 135
r = 62
stroke_width = 18
circ = 2 * math.pi * r

slices = []
offset = 0.0

for item in data:
    length = (item["pct"] / 100.0) * circ
    dasharray = f"{length:.2f} {circ - length:.2f}"
    dashoffset = f"{-offset:.2f}"
    slices.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{item["color"]}" stroke-width="{stroke_width}" '
        f'stroke-dasharray="{dasharray}" stroke-dashoffset="{dashoffset}" transform="rotate(-90 {cx} {cy})" />'
    )
    offset += length

col1 = data[:6]
col2 = data[6:]

col1_svg = []
col2_svg = []

y_start = 75
y_gap = 25

for i, item in enumerate(col1):
    y = y_start + (i * y_gap)
    label = f"{item['count']} repos"
    col1_svg.append(f'''
    <g transform="translate(230, {y})">
      <circle cx="5" cy="5" r="4.5" fill="{item['color']}" />
      <text x="16" y="9" class="lang-name">{item['name']}</text>
      <text x="110" y="9" class="lang-count">{label}</text>
      <text x="150" y="9" class="lang-pct">{item['pct']:.1f}%</text>
    </g>''')

for i, item in enumerate(col2):
    y = y_start + (i * y_gap)
    label = f"{item['count']} repo" if item['count'] == 1 else f"{item['count']} repos"
    col2_svg.append(f'''
    <g transform="translate(390, {y})">
      <circle cx="5" cy="5" r="4.5" fill="{item['color']}" />
      <text x="16" y="9" class="lang-name">{item['name']}</text>
      <text x="95" y="9" class="lang-count">{label}</text>
      <text x="135" y="9" class="lang-pct">{item['pct']:.1f}%</text>
    </g>''')

svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #58a6ff; }}
    .sub {{ font: 500 12.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #8b949e; }}
    .lang-name {{ font: 600 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #e6edf3; }}
    .lang-count {{ font: 400 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #8b949e; text-anchor: end; }}
    .lang-pct {{ font: 600 11.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #58a6ff; text-anchor: end; }}
    .donut-bg {{ stroke: #21262d; }}
    .donut-icon {{ fill: #8b949e; }}
  </style>
  <rect width="{width}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1" />
  
  <!-- Header -->
  <text x="28" y="36" class="header">Most Used Languages</text>
  <text x="{width - 28}" y="36" class="sub" text-anchor="end">Private Repositories</text>

  <!-- Donut Chart -->
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#21262d" stroke-width="{stroke_width}" />
  {''.join(slices)}
  
  <!-- Donut Center Icon (Code / Shield) -->
  <g transform="translate({cx - 14}, {cy - 14})">
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#58a6ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="16 18 22 12 16 6"></polyline>
      <polyline points="8 6 2 12 8 18"></polyline>
    </svg>
  </g>

  <!-- Legend Columns -->
  {''.join(col1_svg)}
  {''.join(col2_svg)}
</svg>
'''

output_path = os.path.join(os.path.dirname(__file__), "..", "languages.svg")
with open(output_path, "w") as f:
    f.write(svg)
print("Updated scripts/generate_langs.py to circular donut UI successfully!")
