import math, json, subprocess

query = """
query {
  viewer {
    login
    name
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoryContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        isPrivate
        primaryLanguage {
          name
        }
      }
    }
    pullRequests(first: 1) {
      totalCount
    }
    issues(first: 1) {
      totalCount
    }
  }
}
"""

res = subprocess.check_output(["gh", "api", "graphql", "-f", f"query={query}"])
data = json.loads(res)["data"]["viewer"]

cc = data["contributionsCollection"]
cal = cc["contributionCalendar"]
total_contribs = cal["totalContributions"]
private_contribs = cc["restrictedContributionsCount"]
commits = cc["totalCommitContributions"]
prs = data["pullRequests"]["totalCount"]
issues = data["issues"]["totalCount"]

repos_nodes = data["repositories"]["nodes"]
total_repos = len(repos_nodes)
private_repos = sum(1 for r in repos_nodes if r["isPrivate"])
stars = sum(r["stargazerCount"] for r in repos_nodes)

days = []
for w in cal["weeks"]:
    for d in w["contributionDays"]:
        days.append((d["date"], d["contributionCount"]))
days.sort(key=lambda x: x[0])

longest_streak = 0
temp_streak = 0
for date, count in days:
    if count > 0:
        temp_streak += 1
        longest_streak = max(longest_streak, temp_streak)
    else:
        temp_streak = 0

lang_counts = {}
for r in repos_nodes:
    pl = r.get("primaryLanguage")
    name = pl["name"] if pl else "Other/Data"
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

data_langs = []
for name in display_order:
    cnt = lang_counts.get(name, 0)
    if cnt > 0:
        pct = (cnt / total_repos) * 100
        color = colors.get(name, "#8b949e")
        data_langs.append({
            "name": name,
            "pct": pct,
            "color": color
        })

width = 880
height = 320

cx = 495
cy = 180
r = 58
stroke_width = 14
circ = 2 * math.pi * r

gap = 2.0
num_segments = len(data_langs)
total_gap = gap * num_segments
available_circ = circ - total_gap

slices = []
offset = 0.0

for item in data_langs:
    seg_len = (item["pct"] / 100.0) * available_circ
    if seg_len < 1.0:
        seg_len = 1.0
    dasharray = f"{seg_len:.2f} {circ - seg_len:.2f}"
    dashoffset = f"{-offset:.2f}"
    slices.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{item["color"]}" stroke-width="{stroke_width}" '
        f'stroke-dasharray="{dasharray}" stroke-dashoffset="{dashoffset}" transform="rotate(-90 {cx} {cy})" />'
    )
    offset += (seg_len + gap)

col1 = data_langs[:6]
col2 = data_langs[6:]

col1_svg = []
col2_svg = []
y_start = 96
y_gap = 26

for i, item in enumerate(col1):
    y = y_start + (i * y_gap)
    col1_svg.append(f'''
    <g transform="translate(585, {y})">
      <circle cx="5" cy="5" r="4.5" fill="{item['color']}" />
      <text x="16" y="9" class="lang-name">{item['name']}</text>
      <text x="125" y="9" class="lang-pct">{item['pct']:.1f}%</text>
    </g>''')

for i, item in enumerate(col2):
    y = y_start + (i * y_gap)
    col2_svg.append(f'''
    <g transform="translate(735, {y})">
      <circle cx="5" cy="5" r="4.5" fill="{item['color']}" />
      <text x="16" y="9" class="lang-name">{item['name']}</text>
      <text x="120" y="9" class="lang-pct">{item['pct']:.1f}%</text>
    </g>''')

svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="card-border" x1="0" y1="0" x2="{width}" y2="{height}" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#30363d" />
      <stop offset="50%" stop-color="#1f6feb" stop-opacity="0.4" />
      <stop offset="100%" stop-color="#30363d" />
    </linearGradient>
  </defs>

  <style>
    .header {{ font: 600 15.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; fill: #58a6ff; }}
    .sub-tag {{ font: 600 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; fill: #8b949e; }}
    .card-val {{ font: 700 22px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; fill: #f0f6fc; }}
    .card-sub {{ font: 500 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; fill: #7d8590; }}
    .card-label {{ font: 500 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; fill: #8b949e; }}
    .lang-name {{ font: 600 12.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; fill: #e6edf3; }}
    .lang-pct {{ font: 600 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; fill: #58a6ff; text-anchor: end; }}
    .donut-main {{ font: 700 18px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; fill: #f0f6fc; text-anchor: middle; }}
    .donut-sub {{ font: 600 8.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; fill: #58a6ff; letter-spacing: 1px; text-anchor: middle; }}
    .box {{ fill: #161b22; stroke: #30363d; stroke-width: 1; }}
    .box-bottom {{ fill: #11161d; stroke: #21262d; stroke-width: 1; }}
  </style>

  <rect width="{width}" height="{height}" rx="14" fill="#0d1117" stroke="url(#card-border)" stroke-width="1.2" />
  <line x1="395" y1="20" x2="395" y2="{height - 20}" stroke="#21262d" stroke-width="1" stroke-dasharray="3 3" />

  <!-- LEFT PANEL -->
  <g transform="translate(28, 36)">
    <svg x="0" y="0" width="16" height="16" viewBox="0 0 16 16" fill="#58a6ff">
      <path d="M8 0c-.3 0-.6.1-.8.4C6 1.7 4 4.5 4 7.5 4 10 5.8 12 8 12s4-2 4-4.5c0-3-2-5.8-3.2-7.1-.2-.3-.5-.4-.8-.4zM8 10.5c-1.4 0-2.5-1.1-2.5-2.5 0-1.8 1.4-3.8 2.5-5 1.1 1.2 2.5 3.2 2.5 5 0 1.4-1.1 2.5-2.5 2.5z"/>
    </svg>
    <text x="24" y="13" class="header">GitHub Activity &amp; Stats</text>
    <text x="340" y="13" class="sub-tag" text-anchor="end">90+ Pvt Repos</text>
  </g>

  <!-- 1. Total Contributions -->
  <rect x="28" y="65" width="165" height="78" rx="10" class="box" />
  <g transform="translate(42, 85)">
    <svg x="0" y="0" width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="#3fb950" stroke-width="1.8">
      <circle cx="8" cy="8" r="3"/>
      <line x1="1" y1="8" x2="5" y2="8"/>
      <line x1="11" y1="8" x2="15" y2="8"/>
    </svg>
    <text x="24" y="13" class="card-val">{total_contribs}</text>
    <text x="135" y="13" class="card-sub" text-anchor="end">500+ Pvt</text>
    <text x="0" y="44" class="card-label">Total Contributions</text>
  </g>

  <!-- 2. Repositories -->
  <rect x="203" y="65" width="165" height="78" rx="10" class="box" />
  <g transform="translate(217, 85)">
    <svg x="0" y="0" width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="#58a6ff" stroke-width="1.8">
      <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 0-.75.75v1.25H4.5A2.5 2.5 0 0 1 2 13.5v-11zm2.5 11h5.5V1.5H4.5A1 1 0 0 0 3.5 2.5v11a1 1 0 0 0 1 1z"/>
    </svg>
    <text x="24" y="13" class="card-val">90+</text>
    <text x="135" y="13" class="card-sub" text-anchor="end">Pvt Repos</text>
    <text x="0" y="44" class="card-label">Repositories</text>
  </g>

  <!-- 3. Stars -->
  <rect x="28" y="153" width="165" height="78" rx="10" class="box" />
  <g transform="translate(42, 173)">
    <svg x="0" y="0" width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="#e3b341" stroke-width="1.8">
      <polygon points="8 1.5 10.1 5.8 14.8 6.5 11.4 9.8 12.2 14.5 8 12.3 3.8 14.5 4.6 9.8 1.2 6.5 5.9 5.8 8 1.5"/>
    </svg>
    <text x="24" y="13" class="card-val">{stars}</text>
    <text x="0" y="44" class="card-label">Stars Earned</text>
  </g>

  <!-- 4. Pull Requests -->
  <rect x="203" y="153" width="165" height="78" rx="10" class="box" />
  <g transform="translate(217, 173)">
    <svg x="0" y="0" width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="#a371f7" stroke-width="1.8">
      <circle cx="12" cy="12" r="2"/>
      <circle cx="4" cy="4" r="2"/>
      <path d="M4 6v8M12 10V8a2 2 0 0 0-2-2H4"/>
    </svg>
    <text x="24" y="13" class="card-val">{prs}</text>
    <text x="135" y="13" class="card-sub" text-anchor="end">{issues} Issues</text>
    <text x="0" y="44" class="card-label">Pull Requests</text>
  </g>

  <!-- Bottom Streak Strip -->
  <rect x="28" y="243" width="340" height="48" rx="8" class="box-bottom" />
  <g transform="translate(44, 272)">
    <svg x="0" y="-12" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="#58a6ff" stroke-width="1.6">
      <polyline points="4 6 7 9 4 12"/>
      <line x1="9" y1="12" x2="13" y2="12"/>
    </svg>
    <text x="20" y="0" class="card-label">Year Commits: <tspan fill="#f0f6fc" font-weight="700">{commits}</tspan></text>
    
    <svg x="170" y="-12" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="#f0883e" stroke-width="1.6">
      <polygon points="9 1 3 9 8 9 7 15 13 7 8 7 9 1"/>
    </svg>
    <text x="190" y="0" class="card-label">Longest Streak: <tspan fill="#f0f6fc" font-weight="700">{longest_streak} Days</tspan></text>
  </g>

  <!-- RIGHT PANEL -->
  <g transform="translate(425, 36)">
    <svg x="0" y="0" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="#58a6ff" stroke-width="1.8">
      <polyline points="5 4 1 8 5 12"/>
      <polyline points="11 4 15 8 11 12"/>
    </svg>
    <text x="24" y="13" class="header">Most Used Languages</text>
    <text x="420" y="13" class="sub-tag" text-anchor="end">90+ Pvt Repos</text>
  </g>

  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#161b22" stroke-width="{stroke_width}" />
  {''.join(slices)}

  <circle cx="{cx}" cy="{cy}" r="45" fill="#0d1117" />
  <text x="{cx}" y="{cy + 2}" class="donut-main">90+</text>
  <text x="{cx}" y="{cy + 17}" class="donut-sub">PVT REPOS</text>

  {''.join(col1_svg)}
  {''.join(col2_svg)}
</svg>
'''

import os
out_path = os.path.join(os.path.dirname(__file__), "..", "github-stats.svg")
with open(out_path, "w") as f:
    f.write(svg)
print("Updated scripts/generate_dashboard.py successfully!")
