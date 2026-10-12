import os, json, urllib.request

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

lang_data = []
for name in display_order:
    cnt = lang_counts.get(name, 0)
    if cnt > 0:
        pct = (cnt / total_repos) * 100
        color = colors.get(name, "#8b949e")
        lang_data.append({
            "name": name,
            "count": cnt,
            "pct": pct,
            "color": color
        })

width = 520
height = 250
bar_width = 460
bar_x = 30
bar_y = 65
bar_height = 12
rx = 6

progress_rects = []
current_x = bar_x
for l in lang_data:
    seg_w = (l["pct"] / 100.0) * bar_width
    progress_rects.append(f'<rect x="{current_x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_height}" fill="{l["color"]}" />')
    current_x += seg_w

col1 = lang_data[:6]
col2 = lang_data[6:]

col1_svg = []
y_start = 104
y_gap = 23

for i, item in enumerate(col1):
    y = y_start + (i * y_gap)
    label = f"{item['count']} repos"
    col1_svg.append(f'''
    <g transform="translate(30, {y})">
      <circle cx="5" cy="5" r="5" fill="{item['color']}" />
      <text x="18" y="9" class="lang-name">{item['name']}</text>
      <text x="145" y="9" class="lang-count">{label}</text>
      <text x="210" y="9" class="lang-pct">{item['pct']:.1f}%</text>
    </g>''')

col2_svg = []
for i, item in enumerate(col2):
    y = y_start + (i * y_gap)
    label = f"{item['count']} repo" if item['count'] == 1 else f"{item['count']} repos"
    col2_svg.append(f'''
    <g transform="translate(275, {y})">
      <circle cx="5" cy="5" r="5" fill="{item['color']}" />
      <text x="18" y="9" class="lang-name">{item['name']}</text>
      <text x="145" y="9" class="lang-count">{label}</text>
      <text x="210" y="9" class="lang-pct">{item['pct']:.1f}%</text>
    </g>''')

svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 17px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #58a6ff; }}
    .sub {{ font: 500 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #8b949e; }}
    .lang-name {{ font: 600 13px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #e6edf3; }}
    .lang-count {{ font: 400 11.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #8b949e; text-anchor: end; }}
    .lang-pct {{ font: 600 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #58a6ff; text-anchor: end; }}
  </style>
  <rect width="{width}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1" />
  
  <!-- Header -->
  <text x="30" y="38" class="header">Most Used Languages</text>
  <text x="{width - 30}" y="38" class="sub" text-anchor="end">All {total_repos} Repositories</text>
  
  <!-- Progress Bar Container -->
  <clipPath id="bar-clip">
    <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="{rx}" />
  </clipPath>
  
  <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="{rx}" fill="#21262d" />
  <g clip-path="url(#bar-clip)">
    {''.join(progress_rects)}
  </g>
  
  <!-- Language List -->
  {''.join(col1_svg)}
  {''.join(col2_svg)}
</svg>
'''

output_path = os.path.join(os.path.dirname(__file__), "..", "languages.svg")
with open(output_path, "w") as f:
    f.write(svg)
print("Updated scripts/generate_langs.py successfully!")
