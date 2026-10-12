import math, json, subprocess

# 1. Fetch GitHub metrics
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
total_contribs = cal["totalContributions"] # 617
private_contribs = cc["restrictedContributionsCount"] # 500
commits = cc["totalCommitContributions"] # 79
prs = data["pullRequests"]["totalCount"] # 19
issues = data["issues"]["totalCount"] # 3

repos_nodes = data["repositories"]["nodes"]
total_repos = len(repos_nodes) # 99
private_repos = sum(1 for r in repos_nodes if r["isPrivate"]) # 83
public_repos = total_repos - private_repos # 16
stars = sum(r["stargazerCount"] for r in repos_nodes) # 54

# Streak calculation
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

current_streak = 0
for date, count in reversed(days):
    if count > 0:
        current_streak += 1
    else:
        break

# Language breakdown
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

# Donut geometry
cx = 505
cy = 185
r = 56
stroke_width = 16
circ = 2 * math.pi * r

slices = []
offset = 0.0
for item in lang_data:
    length = (item["pct"] / 100.0) * circ
    dasharray = f"{length:.2f} {circ - length:.2f}"
    dashoffset = f"{-offset:.2f}"
    slices.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{item["color"]}" stroke-width="{stroke_width}" '
        f'stroke-dasharray="{dasharray}" stroke-dashoffset="{dashoffset}" transform="rotate(-90 {cx} {cy})" />'
    )
    offset += length

# Legend
col1 = lang_data[:6]
col2 = lang_data[6:]

col1_svg = []
col2_svg = []
y_start = 100
y_gap = 26

for i, item in enumerate(col1):
    y = y_start + (i * y_gap)
    label = f"{item['count']} repos"
    col1_svg.append(f'''
    <g transform="translate(600, {y})">
      <circle cx="5" cy="5" r="4.5" fill="{item['color']}" />
      <text x="16" y="9" class="lang-name">{item['name']}</text>
      <text x="110" y="9" class="lang-count">{label}</text>
      <text x="155" y="9" class="lang-pct">{item['pct']:.1f}%</text>
    </g>''')

for i, item in enumerate(col2):
    y = y_start + (i * y_gap)
    label = f"{item['count']} repo" if item['count'] == 1 else f"{item['count']} repos"
    col2_svg.append(f'''
    <g transform="translate(775, {y})">
      <circle cx="5" cy="5" r="4.5" fill="{item['color']}" />
      <text x="16" y="9" class="lang-name">{item['name']}</text>
      <text x="95" y="9" class="lang-count">{label}</text>
      <text x="140" y="9" class="lang-pct">{item['pct']:.1f}%</text>
    </g>''')

width = 940
height = 320

svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 17px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #58a6ff; }}
    .sub {{ font: 500 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #8b949e; }}
    .card-val {{ font: 700 20px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #f0f6fc; }}
    .card-sub {{ font: 400 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #7d8590; }}
    .card-label {{ font: 500 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #8b949e; }}
    .lang-name {{ font: 600 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #e6edf3; }}
    .lang-count {{ font: 400 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #8b949e; text-anchor: end; }}
    .lang-pct {{ font: 600 11.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; fill: #58a6ff; text-anchor: end; }}
    .box {{ fill: #161b22; stroke: #30363d; stroke-width: 1; }}
  </style>

  <!-- Outer Card Frame -->
  <rect width="{width}" height="{height}" rx="14" fill="#0d1117" stroke="#30363d" stroke-width="1.5" />

  <!-- Vertical Divider -->
  <line x1="415" y1="20" x2="415" y2="{height - 20}" stroke="#21262d" stroke-width="1.5" stroke-dasharray="4 4" />

  <!-- ================= LEFT PANEL: GITHUB STATS & CONTRIBUTIONS ================= -->
  <!-- Left Header -->
  <g transform="translate(28, 38)">
    <circle cx="8" cy="8" r="8" fill="#238636" fill-opacity="0.2" />
    <circle cx="8" cy="8" r="4" fill="#3fb950" />
    <text x="24" y="13" class="header">GitHub Activity &amp; Stats</text>
    <text x="360" y="13" class="sub" text-anchor="end">Private &amp; Public Active</text>
  </g>

  <!-- 4 Metric Cards (2x2 Grid) -->
  <!-- Card 1: Total Contributions -->
  <rect x="28" y="70" width="175" height="80" rx="10" class="box" />
  <g transform="translate(42, 92)">
    <text x="0" y="12" class="card-val">{total_contribs}</text>
    <text x="60" y="12" class="card-sub">({private_contribs} private)</text>
    <text x="0" y="42" class="card-label">🔥 Total Contributions</text>
  </g>

  <!-- Card 2: Repositories -->
  <rect x="215" y="70" width="175" height="80" rx="10" class="box" />
  <g transform="translate(229, 92)">
    <text x="0" y="12" class="card-val">{total_repos}</text>
    <text x="40" y="12" class="card-sub">({private_repos} private)</text>
    <text x="0" y="42" class="card-label">📦 Total Repositories</text>
  </g>

  <!-- Card 3: Stars Earned -->
  <rect x="28" y="162" width="175" height="80" rx="10" class="box" />
  <g transform="translate(42, 184)">
    <text x="0" y="12" class="card-val">{stars}</text>
    <text x="0" y="42" class="card-label">⭐ Total Stars Earned</text>
  </g>

  <!-- Card 4: Pull Requests -->
  <rect x="215" y="162" width="175" height="80" rx="10" class="box" />
  <g transform="translate(229, 184)">
    <text x="0" y="12" class="card-val">{prs}</text>
    <text x="35" y="12" class="card-sub">({issues} issues)</text>
    <text x="0" y="42" class="card-label">🔀 Pull Requests</text>
  </g>

  <!-- Streak & Year Row at Bottom -->
  <rect x="28" y="254" width="362" height="46" rx="8" class="box" />
  <g transform="translate(42, 282)">
    <text x="0" y="0" class="card-label">⚡ Year Commits: <tspan fill="#f0f6fc" font-weight="700">{commits}</tspan></text>
    <text x="180" y="0" class="card-label">🏆 Longest Streak: <tspan fill="#f0f6fc" font-weight="700">{longest_streak} Days</tspan></text>
  </g>

  <!-- ================= RIGHT PANEL: MOST USED LANGUAGES (CIRCULAR) ================= -->
  <!-- Right Header -->
  <g transform="translate(440, 38)">
    <text x="0" y="13" class="header">Most Used Languages</text>
    <text x="475" y="13" class="sub" text-anchor="end">Private Repositories</text>
  </g>

  <!-- Donut Chart -->
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#21262d" stroke-width="{stroke_width}" />
  {''.join(slices)}
  
  <!-- Donut Center Icon (Code Brackets) -->
  <g transform="translate({cx}, {cy})">
    <polyline points="3 8 9 2 3 -4" fill="none" stroke="#58a6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
    <polyline points="-3 -4 -9 2 -3 8" fill="none" stroke="#58a6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
  </g>

  <!-- Language Legend Columns -->
  {''.join(col1_svg)}
  {''.join(col2_svg)}
</svg>
'''

with open("/tmp/koderguru_repo/github-stats.svg", "w") as f:
    f.write(svg)

print("Generated all-in-one github-stats.svg successfully!")
