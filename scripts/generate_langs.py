import os, json, urllib.request

token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
headers = {"User-Agent": "Koderguru-Lang-Stats"}
if token:
    headers["Authorization"] = f"Bearer {token}"

# Fetch all repositories
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
total_bytes = 0
lang_bytes = {}
repo_counts = {}

for r in repos:
    pl = r.get("language")
    if pl:
        repo_counts[pl] = repo_counts.get(pl, 0) + 1
    
    # Fetch languages breakdown for repository
    langs_url = r.get("languages_url")
    if langs_url:
        try:
            l_req = urllib.request.Request(langs_url, headers=headers)
            with urllib.request.urlopen(l_req) as l_resp:
                r_langs = json.loads(l_resp.read().decode())
            for name, size in r_langs.items():
                lang_bytes[name] = lang_bytes.get(name, 0) + size
                total_bytes += size
        except Exception:
            pass

colors = {
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "Kotlin": "#A97BFF",
    "HTML": "#e34c26",
    "Swift": "#F05138",
    "Dart": "#00B4AB",
    "CSS": "#563d7c",
    "Go": "#00ADD8",
    "Jupyter Notebook": "#DA5B0B",
    "Shell": "#89e051",
    "C++": "#f34b7d",
    "Makefile": "#427819",
    "C": "#555555"
}

display_langs = [
    "TypeScript", "JavaScript", "Python", "Kotlin", 
    "HTML", "Swift", "Dart", "CSS", 
    "Go", "C++", "Jupyter Notebook", "Shell"
]

lang_data = []
for name in display_langs:
    b = lang_bytes.get(name, 0)
    pct = (b / total_bytes) * 100 if total_bytes > 0 else 0
    color = colors.get(name, "#8b949e")
    rc = repo_counts.get(name, 0)
    lang_data.append({
        "name": name,
        "bytes": b,
        "pct": pct,
        "color": color,
        "repos": rc
    })

width = 500
height = 245
bar_width = 440
bar_x = 30
bar_y = 65
bar_height = 10
rx = 5

progress_rects = []
current_x = bar_x
for l in lang_data:
    seg_w = (l["pct"] / 100.0) * bar_width
    if seg_w < 1.5 and l["pct"] > 0:
        seg_w = 1.5
    progress_rects.append(f'<rect x="{current_x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_height}" fill="{l["color"]}" />')
    current_x += seg_w

col1 = lang_data[:6]
col2 = lang_data[6:12]

col1_svg = []
y_start = 102
y_gap = 22

for i, item in enumerate(col1):
    y = y_start + (i * y_gap)
    repo_txt = f"({item['repos']} repos)" if item['repos'] > 0 else ""
    col1_svg.append(f'''
    <g transform="translate(30, {y})">
      <circle cx="5" cy="5" r="5" fill="{item['color']}" />
      <text x="18" y="9" class="lang-name">{item['name']}</text>
      <text x="135" y="9" class="lang-pct">{item['pct']:.1f}%</text>
      <text x="175" y="9" class="lang-repo">{repo_txt}</text>
    </g>''')

col2_svg = []
for i, item in enumerate(col2):
    y = y_start + (i * y_gap)
    repo_txt = f"({item['repos']} repos)" if item['repos'] > 0 else ""
    col2_svg.append(f'''
    <g transform="translate(265, {y})">
      <circle cx="5" cy="5" r="5" fill="{item['color']}" />
      <text x="18" y="9" class="lang-name">{item['name']}</text>
      <text x="135" y="9" class="lang-pct">{item['pct']:.1f}%</text>
      <text x="175" y="9" class="lang-repo">{repo_txt}</text>
    </g>''')

svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 17px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #58a6ff; }}
    .sub {{ font: 400 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #8b949e; }}
    .lang-name {{ font: 600 12.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #e6edf3; }}
    .lang-pct {{ font: 500 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #8b949e; text-anchor: end; }}
    .lang-repo {{ font: 400 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #6e7681; }}
  </style>
  <rect width="{width}" height="{height}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1" />
  
  <!-- Header -->
  <text x="30" y="38" class="header">Most Used Languages</text>
  <text x="470" y="38" class="sub" text-anchor="end">Across all {total_repos} Repositories</text>
  
  <!-- Progress Bar Container with clip path -->
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
print("Updated languages.svg via script successfully!")
