"""
Generate an interactive HTML report for AMLSS 2026 selected students.
Reads CSV data and produces a single self-contained HTML file with:
  - Tier distribution chart (donut + bar)
  - Top colleges bar chart
  - Searchable/filterable student table
"""

import csv
import json
from collections import Counter

# ── Tier classification rules (keyword-based) ──────────────────────────────
TIER1_KEYWORDS = [
    "indian institute of technology",
    "iit ",
    "iit,",
    "(iit)",
    "iit-",
    "iit -",
    "iisc",
    "indian institute of science",
    "bits pilani",
    "birla institute of technology & science",
    "indian statistical institute",
]

TIER2_KEYWORDS = [
    "national institute of technology",
    "(nit)",
    "nit ",
    "nit,",
    "indian institute of information technology",
    "(iiit)",
    "iiit ",
    "iiit,",
    "international institute of information technology",
    "indraprastha institute of information technology",
    "atal bihari vajpayee",
    "delhi technological university",
    "(dtu)",
    "netaji subhas university",
    "(nsut)",
    "jadavpur university",
    "thapar",
    "manipal institute of technology",
    "vellore institute of technology",
    "(vit)",
    "birla institute of technology",
    "(bit)",
    "punjab engineering college",
    "pec,",
    "malaviya national institute",
    "motilal nehru national institute",
    "maulana azad national institute",
    "igdtuw",
    "indira gandhi delhi technical university",
    "harcourt butler",
    "ism dhanbad",
    "jaypee institute of information technology",
    "lnm institute of information technology",
    "amrita vishwa vidyapeetham",
    "amrita university",
    "sastra deemed",
    "shiv nadar university",
    "kalinga institute of industrial technology",
    "(kiit)",
    "guru gobind singh indraprastha",
    "(ggsipu)",
    "university institute of engineering and technology (uiet), chandigarh",
    "college of engineering, guindy",
    "psg college of technology",
    "anna university",
]

def classify_tier(institute: str) -> str:
    inst_lower = institute.lower()
    for kw in TIER1_KEYWORDS:
        if kw in inst_lower:
            return "Tier 1"
    for kw in TIER2_KEYWORDS:
        if kw in inst_lower:
            return "Tier 2"
    return "Tier 3"


# ── Read CSV ────────────────────────────────────────────────────────────────
students = []
with open("amlss_2026_students.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        tier = classify_tier(row["Institute"])
        students.append({
            "sno": int(row["S.No"]),
            "name": row["Name"],
            "institute": row["Institute"],
            "profile": row["Profile URL"],
            "tier": tier,
        })

# ── Aggregate stats ─────────────────────────────────────────────────────────
tier_counts = Counter(s["tier"] for s in students)
institute_counts = Counter(s["institute"] for s in students)
top_colleges = institute_counts.most_common(25)

# Institute-level tier mapping for the top colleges chart
inst_tier_map = {}
for s in students:
    if s["institute"] not in inst_tier_map:
        inst_tier_map[s["institute"]] = s["tier"]

top_colleges_data = [
    {"name": name, "count": count, "tier": inst_tier_map[name]}
    for name, count in top_colleges
]

# Shorten long names for chart labels
def short_name(n):
    replacements = {
        "Indian Institute of Technology": "IIT",
        "National Institute of Technology": "NIT",
        "Indian Institute of Information Technology": "IIIT",
        "International Institute of Information Technology": "Int'l IIIT",
        "Indraprastha Institute of Information Technology": "IIIT-D",
        "Atal Bihari Vajpayee-Indian Institute of Information Technology and Management": "ABV-IIITM Gwalior",
        "Thapar Institute of Engineering and Technology (TIET), Patiala": "Thapar (TIET)",
        "Vellore Institute of Technology (VIT), Vellore": "VIT Vellore",
        "SRM Institute of Science and Technology (SRMIST), Kattankulathur, Chennai": "SRMIST Chennai",
        "Netaji Subhas University of Technology (NSUT), Delhi": "NSUT Delhi",
        "Delhi Technological University (DTU), New Delhi": "DTU Delhi",
        "Indira Gandhi Delhi Technical University for Women (IGDTUW), Delhi": "IGDTUW Delhi",
        "Indian Institute of Technology, Banaras Hindu University (IIT - BHU)": "IIT BHU",
        "Indian Institute of Technology, Indian School of Mines (IIT ISM), Dhanbad": "IIT ISM Dhanbad",
        "Indian Institute of Information Technology, Design and Manufacturing (IIITDM), Jabalpur": "IIITDM Jabalpur",
        "Kalinga Institute of Industrial Technology (KIIT), Bhubaneswar": "KIIT Bhubaneswar",
        "Sardar Vallabhbhai National Institute of Technology (SVNIT), Surat": "SVNIT Surat",
        "Manipal University (MU), Jaipur": "Manipal Jaipur",
        "Motilal Nehru National Institute of Technology": "MNNIT Allahabad",
        "Dr. B.R. Ambedkar National Institute of Technology (NIT), Jalandhar": "NIT Jalandhar",
        "Malaviya National Institute of Technology (MNIT), Jaipur": "MNIT Jaipur",
        "Birla Institute of Technology (BIT), Mesra, Ranchi": "BIT Mesra",
        "Jaypee Institute of Information Technology (JIIT), Noida": "JIIT Noida",
        "Guru Gobind Singh Indraprastha University (GGSIPU), Delhi": "GGSIPU Delhi",
    }
    for long, s in replacements.items():
        if long in n:
            campus = n.replace(long, "").strip(", ()")
            if s.startswith("IIT") and campus:
                return f"IIT {campus.strip(', ()')}"
            if s.startswith("NIT") and campus:
                return f"NIT {campus.strip(', ()')}"
            if s.startswith("IIIT") and not s.startswith("IIIT-") and not s.startswith("Int'l") and campus:
                return f"IIIT {campus.strip(', ()')}"
            if s.startswith("Int'l IIIT") and campus:
                return f"Int'l IIIT {campus.strip(', ()')}"
            return s
    return n[:40] + "…" if len(n) > 40 else n

top_chart_labels = [short_name(c["name"]) for c in top_colleges_data]
top_chart_counts = [c["count"] for c in top_colleges_data]
top_chart_tiers  = [c["tier"] for c in top_colleges_data]

# ── Generate HTML ────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AMLSS 2026 — Student Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #232733;
    --border: #2e3344;
    --text: #e4e6ef;
    --text-dim: #8b8fa3;
    --accent1: #6c5ce7;
    --accent2: #00cec9;
    --accent3: #fd79a8;
    --t1: #6c5ce7;
    --t2: #00b894;
    --t3: #fdcb6e;
    --radius: 14px;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: 'Inter', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }}

  /* ─ Header ─ */
  .hero {{
    background: linear-gradient(135deg, #1a1040 0%, #0f1117 50%, #0a1a2a 100%);
    padding: 48px 24px 40px;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid var(--border);
  }}
  .hero::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 600px 300px at 50% 0%, rgba(108,92,231,.18), transparent),
                radial-gradient(ellipse 400px 200px at 80% 100%, rgba(0,206,201,.10), transparent);
    pointer-events: none;
  }}
  .hero h1 {{
    font-size: clamp(1.6rem, 4vw, 2.6rem);
    font-weight: 800;
    background: linear-gradient(135deg, #a29bfe, #6c5ce7, #00cec9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    position: relative;
  }}
  .hero p {{
    color: var(--text-dim);
    margin-top: 10px;
    font-size: 1rem;
    position: relative;
  }}
  .hero .badge {{
    display: inline-flex;
    gap: 6px;
    align-items: center;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 6px 16px;
    font-size: .82rem;
    color: var(--accent2);
    font-weight: 600;
    margin-top: 16px;
    position: relative;
  }}
  .badge .dot {{ width:7px; height:7px; border-radius:50%; background: var(--accent2); }}

  /* ─ Stats bar ─ */
  .stats-bar {{
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
    padding: 20px 24px;
    max-width: 900px;
    margin: -24px auto 0;
    position: relative;
    z-index: 2;
  }}
  .stat-card {{
    flex: 1 1 160px;
    max-width: 200px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 16px;
    text-align: center;
    transition: transform .2s, border-color .2s;
  }}
  .stat-card:hover {{ transform: translateY(-3px); border-color: var(--accent1); }}
  .stat-card .num {{ font-size: 1.7rem; font-weight: 800; }}
  .stat-card .label {{ font-size: .75rem; color: var(--text-dim); margin-top: 4px; text-transform: uppercase; letter-spacing: .5px; }}
  .stat-card.t1 .num {{ color: var(--t1); }}
  .stat-card.t2 .num {{ color: var(--t2); }}
  .stat-card.t3 .num {{ color: var(--t3); }}
  .stat-card.total .num {{ color: var(--accent2); }}

  /* ─ Container ─ */
  .container {{ max-width: 1200px; margin: 0 auto; padding: 32px 24px; }}

  /* ─ Section ─ */
  .section {{ margin-bottom: 40px; }}
  .section-title {{
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .section-title .icon {{
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
  }}
  .section-title .icon.purple {{ background: rgba(108,92,231,.15); }}
  .section-title .icon.teal   {{ background: rgba(0,206,201,.15); }}
  .section-title .icon.pink   {{ background: rgba(253,121,168,.15); }}

  /* ─ Charts grid ─ */
  .charts-grid {{
    display: grid;
    grid-template-columns: 340px 1fr;
    gap: 20px;
  }}
  @media (max-width: 840px) {{
    .charts-grid {{ grid-template-columns: 1fr; }}
  }}
  .chart-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
  }}
  .chart-card h3 {{
    font-size: .85rem;
    font-weight: 600;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: .5px;
    margin-bottom: 16px;
  }}

  /* ─ Legend ─ */
  .tier-legend {{
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 20px;
  }}
  .tier-legend .item {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: .85rem;
  }}
  .tier-legend .swatch {{
    width: 12px; height: 12px; border-radius: 3px;
  }}
  .tier-legend .item .pct {{
    margin-left: auto;
    font-weight: 700;
    font-size: .95rem;
  }}
  .tier-legend .item .cnt {{
    color: var(--text-dim);
    font-size: .78rem;
    margin-left: 4px;
  }}

  /* ─ Top colleges bar ─ */
  .bar-wrapper {{
    position: relative;
    height: 520px;
  }}

  /* ─ Table ─ */
  .table-controls {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 16px;
  }}
  .search-box {{
    flex: 1 1 260px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px;
    color: var(--text);
    font-size: .88rem;
    font-family: inherit;
    outline: none;
    transition: border-color .2s;
  }}
  .search-box:focus {{ border-color: var(--accent1); }}
  .search-box::placeholder {{ color: var(--text-dim); }}

  .filter-btn {{
    padding: 9px 18px;
    border-radius: 10px;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text);
    font-size: .82rem;
    font-family: inherit;
    font-weight: 500;
    cursor: pointer;
    transition: all .2s;
  }}
  .filter-btn:hover {{ border-color: var(--accent1); }}
  .filter-btn.active {{
    background: var(--accent1);
    border-color: var(--accent1);
    color: #fff;
  }}
  .filter-btn.active.t2 {{ background: var(--t2); border-color: var(--t2); }}
  .filter-btn.active.t3 {{ background: var(--t3); border-color: var(--t3); color: #1a1d27; }}

  .table-wrapper {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
  }}
  .table-info {{
    padding: 12px 18px;
    font-size: .78rem;
    color: var(--text-dim);
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
  }}
  thead th {{
    position: sticky;
    top: 0;
    background: var(--surface2);
    padding: 12px 16px;
    text-align: left;
    font-size: .75rem;
    font-weight: 600;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: .5px;
    border-bottom: 1px solid var(--border);
  }}
  tbody td {{
    padding: 11px 16px;
    font-size: .85rem;
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
  }}
  tbody tr {{ transition: background .15s; }}
  tbody tr:hover {{ background: var(--surface2); }}
  tbody tr:last-child td {{ border-bottom: none; }}
  .tier-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .3px;
  }}
  .tier-badge.t1 {{ background: rgba(108,92,231,.15); color: var(--t1); }}
  .tier-badge.t2 {{ background: rgba(0,184,148,.15); color: var(--t2); }}
  .tier-badge.t3 {{ background: rgba(253,203,110,.15); color: var(--t3); }}

  .profile-link {{
    color: var(--accent2);
    text-decoration: none;
    font-weight: 500;
    transition: color .2s;
  }}
  .profile-link:hover {{ color: #81ecec; text-decoration: underline; }}

  .scroll-table {{
    max-height: 620px;
    overflow-y: auto;
  }}
  .scroll-table::-webkit-scrollbar {{ width: 6px; }}
  .scroll-table::-webkit-scrollbar-track {{ background: var(--surface); }}
  .scroll-table::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}

  /* ─ Pagination ─ */
  .pagination {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 6px;
    padding: 16px;
    border-top: 1px solid var(--border);
  }}
  .page-btn {{
    min-width: 34px;
    height: 34px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text);
    font-size: .8rem;
    font-family: inherit;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all .2s;
  }}
  .page-btn:hover {{ border-color: var(--accent1); }}
  .page-btn.active {{ background: var(--accent1); border-color: var(--accent1); color: #fff; }}
  .page-btn:disabled {{ opacity: .4; cursor: default; }}

  /* ─ Footer ─ */
  .footer {{
    text-align: center;
    padding: 24px;
    font-size: .75rem;
    color: var(--text-dim);
    border-top: 1px solid var(--border);
    margin-top: 20px;
  }}

  /* ─ Tier info cards ─ */
  .tier-info {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 14px;
    margin-top: 20px;
  }}
  .tier-info-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    border-left: 3px solid;
  }}
  .tier-info-card.t1 {{ border-left-color: var(--t1); }}
  .tier-info-card.t2 {{ border-left-color: var(--t2); }}
  .tier-info-card.t3 {{ border-left-color: var(--t3); }}
  .tier-info-card h4 {{ font-size: .85rem; font-weight: 700; margin-bottom: 6px; }}
  .tier-info-card p {{ font-size: .76rem; color: var(--text-dim); line-height: 1.5; }}
</style>
</head>
<body>

<div class="hero">
  <h1>Amazon ML Summer School 2026</h1>
  <p>Selection Test — Student Report & Institute Analysis</p>
  <div class="badge"><span class="dot"></span> {len(students)} Students Selected</div>
</div>

<div class="stats-bar">
  <div class="stat-card total"><div class="num">{len(students)}</div><div class="label">Total Selected</div></div>
  <div class="stat-card t1"><div class="num">{tier_counts.get("Tier 1",0)}</div><div class="label">Tier 1</div></div>
  <div class="stat-card t2"><div class="num">{tier_counts.get("Tier 2",0)}</div><div class="label">Tier 2</div></div>
  <div class="stat-card t3"><div class="num">{tier_counts.get("Tier 3",0)}</div><div class="label">Tier 3</div></div>
</div>

<div class="container">

  <!-- Tier Distribution -->
  <div class="section">
    <div class="section-title"><span class="icon purple">📊</span> Tier Distribution</div>
    <div class="charts-grid">
      <div class="chart-card">
        <h3>Breakdown</h3>
        <canvas id="donutChart" width="280" height="280"></canvas>
        <div class="tier-legend">
          <div class="item"><span class="swatch" style="background:var(--t1)"></span> Tier 1 — IITs, BITS, IISc, ISI <span class="pct">{tier_counts.get("Tier 1",0)/len(students)*100:.1f}%</span><span class="cnt">({tier_counts.get("Tier 1",0)})</span></div>
          <div class="item"><span class="swatch" style="background:var(--t2)"></span> Tier 2 — NITs, IIITs, DTU, VIT… <span class="pct">{tier_counts.get("Tier 2",0)/len(students)*100:.1f}%</span><span class="cnt">({tier_counts.get("Tier 2",0)})</span></div>
          <div class="item"><span class="swatch" style="background:var(--t3)"></span> Tier 3 — Others <span class="pct">{tier_counts.get("Tier 3",0)/len(students)*100:.1f}%</span><span class="cnt">({tier_counts.get("Tier 3",0)})</span></div>
        </div>
      </div>
      <div class="chart-card">
        <h3>Top 25 Institutes</h3>
        <div class="bar-wrapper"><canvas id="barChart"></canvas></div>
      </div>
    </div>
    <div class="tier-info">
      <div class="tier-info-card t1"><h4>🏛️ Tier 1</h4><p>IITs (all campuses), BITS Pilani (all campuses), IISc Bangalore, Indian Statistical Institute</p></div>
      <div class="tier-info-card t2"><h4>🎓 Tier 2</h4><p>NITs, IIITs, IIIT-D, DTU, NSUT, IGDTUW, Thapar, VIT, Jadavpur, KIIT, Manipal IT, BIT Mesra, JIIT, PEC, Amrita, SASTRA, and other top deemed/state universities</p></div>
      <div class="tier-info-card t3"><h4>📚 Tier 3</h4><p>All other engineering colleges, state universities, and private institutions not in Tier 1 or 2</p></div>
    </div>
  </div>

  <!-- Student Table -->
  <div class="section">
    <div class="section-title"><span class="icon teal">👥</span> All Students</div>
    <div class="table-controls">
      <input class="search-box" id="searchInput" type="text" placeholder="🔍  Search by name or institute…">
      <button class="filter-btn active" data-tier="all" onclick="setFilter('all', this)">All</button>
      <button class="filter-btn" data-tier="Tier 1" onclick="setFilter('Tier 1', this)">Tier 1</button>
      <button class="filter-btn t2" data-tier="Tier 2" onclick="setFilter('Tier 2', this)">Tier 2</button>
      <button class="filter-btn t3" data-tier="Tier 3" onclick="setFilter('Tier 3', this)">Tier 3</button>
    </div>
    <div class="table-wrapper">
      <div class="table-info">
        <span id="tableCount">Showing {len(students)} students</span>
        <span>Page <span id="currentPage">1</span> of <span id="totalPages">1</span></span>
      </div>
      <div class="scroll-table" id="scrollTable">
        <table>
          <thead><tr>
            <th style="width:50px">#</th>
            <th>Name</th>
            <th>Institute</th>
            <th style="width:80px">Tier</th>
            <th style="width:70px">Profile</th>
          </tr></thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>
      <div class="pagination" id="pagination"></div>
    </div>
  </div>
</div>

<div class="footer">
  Data sourced from <a href="https://unstop.com/hackathons/crp-amazon-ml-summer-school-2026-amazon-1688859/online-assessment/439416" target="_blank" style="color:var(--accent2)">Unstop</a> · Generated on July 2, 2026
</div>

<script>
// ── DATA ──
const students = {json.dumps(students)};
const tierCounts = {json.dumps(dict(tier_counts))};
const topLabels = {json.dumps(top_chart_labels)};
const topCounts = {json.dumps(top_chart_counts)};
const topTiers = {json.dumps(top_chart_tiers)};

const TIER_COLORS = {{ "Tier 1": "#6c5ce7", "Tier 2": "#00b894", "Tier 3": "#fdcb6e" }};
const PER_PAGE = 50;
let currentFilter = "all";
let currentSearch = "";
let currentPage = 1;

// ── Donut Chart ──
new Chart(document.getElementById("donutChart"), {{
  type: "doughnut",
  data: {{
    labels: ["Tier 1", "Tier 2", "Tier 3"],
    datasets: [{{
      data: [tierCounts["Tier 1"]||0, tierCounts["Tier 2"]||0, tierCounts["Tier 3"]||0],
      backgroundColor: ["#6c5ce7", "#00b894", "#fdcb6e"],
      borderColor: "#1a1d27",
      borderWidth: 3,
      hoverOffset: 8,
    }}]
  }},
  options: {{
    cutout: "62%",
    responsive: true,
    maintainAspectRatio: true,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        backgroundColor: "#232733",
        titleColor: "#e4e6ef",
        bodyColor: "#8b8fa3",
        borderColor: "#2e3344",
        borderWidth: 1,
        padding: 12,
        cornerRadius: 10,
        callbacks: {{
          label: ctx => ` ${{ctx.label}}: ${{ctx.raw}} (${{(ctx.raw/{len(students)}*100).toFixed(1)}}%)`
        }}
      }}
    }}
  }}
}});

// ── Bar Chart ──
const barColors = topTiers.map(t => TIER_COLORS[t] || "#fdcb6e");
new Chart(document.getElementById("barChart"), {{
  type: "bar",
  data: {{
    labels: topLabels,
    datasets: [{{
      data: topCounts,
      backgroundColor: barColors.map(c => c + "cc"),
      borderColor: barColors,
      borderWidth: 1,
      borderRadius: 4,
    }}]
  }},
  options: {{
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        backgroundColor: "#232733",
        titleColor: "#e4e6ef",
        bodyColor: "#8b8fa3",
        borderColor: "#2e3344",
        borderWidth: 1,
        padding: 12,
        cornerRadius: 10,
      }}
    }},
    scales: {{
      x: {{
        grid: {{ color: "#2e334433" }},
        ticks: {{ color: "#8b8fa3", font: {{ size: 11 }} }}
      }},
      y: {{
        grid: {{ display: false }},
        ticks: {{ color: "#e4e6ef", font: {{ size: 11 }}, padding: 6 }}
      }}
    }}
  }}
}});

// ── Table ──
function getFiltered() {{
  return students.filter(s => {{
    const matchTier = currentFilter === "all" || s.tier === currentFilter;
    const q = currentSearch.toLowerCase();
    const matchSearch = !q || s.name.toLowerCase().includes(q) || s.institute.toLowerCase().includes(q);
    return matchTier && matchSearch;
  }});
}}

function renderTable() {{
  const filtered = getFiltered();
  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  if (currentPage > totalPages) currentPage = totalPages;
  const start = (currentPage - 1) * PER_PAGE;
  const page = filtered.slice(start, start + PER_PAGE);

  const tbody = document.getElementById("tableBody");
  tbody.innerHTML = page.map((s, i) => `
    <tr>
      <td style="color:var(--text-dim)">${{start + i + 1}}</td>
      <td style="font-weight:500">${{s.name}}</td>
      <td>${{s.institute}}</td>
      <td><span class="tier-badge ${{s.tier === 'Tier 1' ? 't1' : s.tier === 'Tier 2' ? 't2' : 't3'}}">${{s.tier}}</span></td>
      <td><a class="profile-link" href="${{s.profile}}" target="_blank">↗</a></td>
    </tr>
  `).join("");

  document.getElementById("tableCount").textContent = `Showing ${{filtered.length}} students`;
  document.getElementById("currentPage").textContent = currentPage;
  document.getElementById("totalPages").textContent = totalPages;

  // Pagination
  const pag = document.getElementById("pagination");
  if (totalPages <= 1) {{ pag.innerHTML = ""; return; }}

  let btns = `<button class="page-btn" onclick="goPage(${{currentPage-1}})" ${{currentPage===1?'disabled':''}}>‹</button>`;
  const range = 3;
  let pStart = Math.max(1, currentPage - range);
  let pEnd = Math.min(totalPages, currentPage + range);
  if (pStart > 1) btns += `<button class="page-btn" onclick="goPage(1)">1</button>`;
  if (pStart > 2) btns += `<span style="color:var(--text-dim)">…</span>`;
  for (let p = pStart; p <= pEnd; p++)
    btns += `<button class="page-btn ${{p===currentPage?'active':''}}" onclick="goPage(${{p}})">${{p}}</button>`;
  if (pEnd < totalPages - 1) btns += `<span style="color:var(--text-dim)">…</span>`;
  if (pEnd < totalPages) btns += `<button class="page-btn" onclick="goPage(${{totalPages}})">${{totalPages}}</button>`;
  btns += `<button class="page-btn" onclick="goPage(${{currentPage+1}})" ${{currentPage===totalPages?'disabled':''}}>›</button>`;
  pag.innerHTML = btns;
}}

function goPage(p) {{
  currentPage = p;
  renderTable();
  document.getElementById("scrollTable").scrollTop = 0;
}}

function setFilter(tier, btn) {{
  currentFilter = tier;
  currentPage = 1;
  document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  renderTable();
}}

document.getElementById("searchInput").addEventListener("input", function() {{
  currentSearch = this.value;
  currentPage = 1;
  renderTable();
}});

renderTable();
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Generated index.html ({len(html):,} bytes)")
print(f"   Students: {len(students)}")
print(f"   Tier 1: {tier_counts.get('Tier 1',0)}, Tier 2: {tier_counts.get('Tier 2',0)}, Tier 3: {tier_counts.get('Tier 3',0)}")
print(f"   Unique institutes: {len(set(s['institute'] for s in students))}")
