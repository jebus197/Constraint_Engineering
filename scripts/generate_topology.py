#!/usr/bin/env python3
"""Generate CDSFL Whole-Body Topology diagram as SVG.

Maps the biological paradigm to system components:
  Central Nervous System  →  Insect Brain (reactive relay)
  Peripheral Neurons      →  Model Panel (5 frontier LLMs)
  Skin / Epithelium       →  Skin Barrier (malformed finding filter)
  Innate Immune           →  DC (triage) + NK (dedup/memory)
  Adaptive Immune         →  B Cell (math/logic) + CT Cell (code FFF)
  Immune Coordination     →  Helper T (synthesis) + Regulatory T (autoimmune)
  Endocrine System        →  Fix Evaluation + Health Monitor
  Circulatory System      →  Finding Registry (provenance flow)
  Metabolism              →  S_k Pipeline (solution reliability)
  Homeostasis             →  Convergence Gate (ρ, γ, open_ch)

Output: docs/CDSFL_Topology.svg
"""

import textwrap
from pathlib import Path

# ── Layout constants ──────────────────────────────────────────────────────────

W, H = 1200, 1720
CX = W // 2  # centre x

# Colours (medical-chart inspired)
C_BRAIN = "#3B7DD8"
C_NEURON = "#6C5CE7"
C_SKIN = "#FDEBD0"
C_SKIN_BORDER = "#E59866"
C_INNATE = "#27AE60"
C_ADAPTIVE = "#2ECC71"
C_COORD = "#1ABC9C"
C_ENDOCRINE = "#E67E22"
C_CIRC = "#E74C3C"
C_SK = "#8E44AD"
C_CONVERGENCE = "#2C3E50"
C_FUTURE = "#BDC3C7"
C_BG = "#FAFBFC"
C_TEXT = "#2C3E50"
C_SUBTEXT = "#7F8C8D"

# ── SVG helpers ───────────────────────────────────────────────────────────────

def rect(x, y, w, h, fill, stroke="#DDD", rx=12, opacity=1.0):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5" opacity="{opacity}"/>')

def rrect(x, y, w, h, fill, stroke, sw=2, rx=14):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def circle(cx, cy, r, fill, stroke="#FFF", sw=2):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')

def text(x, y, content, size=14, fill=C_TEXT, anchor="middle", weight="normal", font="system-ui, -apple-system, sans-serif"):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{content}</text>')

def line(x1, y1, x2, y2, stroke="#BDC3C7", sw=2, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

def arrow(x1, y1, x2, y2, stroke="#BDC3C7", sw=2):
    mid = "marker-end" if y2 > y1 else "marker-start"
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{sw}" marker-end="url(#arrowhead)"/>')

def arrow_down(x, y1, y2, stroke="#BDC3C7", sw=2):
    return arrow(x, y1, x, y2, stroke, sw)

def group_label(x, y, label, fill):
    return (text(x, y, label, size=11, fill=fill, weight="bold") )

# ── Cell box (immune cell with bio name + CDSFL role) ────────────────────────

def cell_box(x, y, w, h, bio_name, cdsfl_role, tools, fill, border):
    lines = [
        rrect(x, y, w, h, fill, border, sw=2, rx=10),
        text(x + w//2, y + 20, bio_name, size=13, fill=C_TEXT, weight="bold"),
        text(x + w//2, y + 38, cdsfl_role, size=11, fill=C_SUBTEXT),
    ]
    if tools:
        lines.append(text(x + w//2, y + 54, tools, size=10, fill=border, weight="normal"))
    return "\n".join(lines)


# ── Build SVG ─────────────────────────────────────────────────────────────────

parts = []

# Defs (arrowhead marker)
parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     width="{W}" height="{H}" style="background:{C_BG}">
<defs>
  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#95A5A6"/>
  </marker>
  <marker id="arrowred" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="{C_CIRC}"/>
  </marker>
  <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%">
    <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
  </filter>
</defs>
""")

# Title
parts.append(text(CX, 36, "CDSFL — Whole-Body Topology", size=24, fill=C_TEXT, weight="bold"))
parts.append(text(CX, 58, "Constraint-Driven Synthesis and Falsification — Biological Architecture Map", size=13, fill=C_SUBTEXT))

# ═══════════════════════════════════════════════════════════════════════════════
# BRAIN (Central Nervous System)
# ═══════════════════════════════════════════════════════════════════════════════

by = 80
bw, bh = 380, 90
bx = CX - bw//2
parts.append(rrect(bx, by, bw, bh, "#EBF5FB", C_BRAIN, sw=3, rx=16))
parts.append(text(CX, by + 28, "Insect Brain", size=18, fill=C_BRAIN, weight="bold"))
parts.append(text(CX, by + 48, "Central Nervous System", size=12, fill=C_SUBTEXT))
parts.append(text(CX, by + 64, "Reactive relay · Checkpoint · Dispatch sequencing · Domain classification", size=10, fill=C_SUBTEXT))

# ═══════════════════════════════════════════════════════════════════════════════
# NEURONS (Model Panel)
# ═══════════════════════════════════════════════════════════════════════════════

ny = by + bh + 30
models = [
    ("CC2", "Claude Opus 4.6"),
    ("Codex", "GPT-5.4"),
    ("Gemini", "3.1 Pro"),
    ("DeepSeek", "Reasoner"),
    ("ChatGPT", "GPT-5.4"),
]
nw = 130
spacing = (W - 120) // 5
nx_start = 60 + (spacing - nw) // 2

parts.append(group_label(CX, ny - 6, "PERIPHERAL NEURONS — Model Panel", C_NEURON))

for i, (name, sub) in enumerate(models):
    nx = nx_start + i * spacing
    # Connection line brain → neuron
    parts.append(line(CX, by + bh, nx + nw//2, ny + 8, stroke=C_BRAIN, sw=1.5))
    # Neuron box
    parts.append(rrect(nx, ny + 8, nw, 52, "#F0EDFF", C_NEURON, sw=2, rx=8))
    parts.append(text(nx + nw//2, ny + 32, name, size=13, fill=C_NEURON, weight="bold"))
    parts.append(text(nx + nw//2, ny + 48, sub, size=10, fill=C_SUBTEXT))

# ═══════════════════════════════════════════════════════════════════════════════
# SKIN BARRIER (outermost)
# ═══════════════════════════════════════════════════════════════════════════════

sy = ny + 85
sw_box, sh_box = W - 80, 120
sx = 40

parts.append(rrect(sx, sy, sw_box, sh_box, C_SKIN, C_SKIN_BORDER, sw=3, rx=20))
parts.append(text(CX, sy + 24, "Skin Barrier — Epithelial Defence", size=16, fill="#A0522D", weight="bold"))
parts.append(text(CX, sy + 44, "First line of innate immunity", size=12, fill=C_SUBTEXT))
parts.append(text(CX, sy + 64, "Filters malformed findings: uncitable file:line, missing evidence, structural defects", size=11, fill="#8B6914"))
parts.append(text(CX, sy + 82, "Findings that pass the barrier enter the immune pipeline below", size=10, fill=C_SUBTEXT))
# Down arrow from skin
parts.append(arrow_down(CX, sy + sh_box, sy + sh_box + 30, stroke=C_SKIN_BORDER))

# ═══════════════════════════════════════════════════════════════════════════════
# IMMUNE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

iy = sy + sh_box + 35
iw, ih = W - 80, 700
ix = 40

# Immune system background
parts.append(rrect(ix, iy, iw, ih, "#F0FFF0", "#27AE60", sw=2, rx=16))
parts.append(text(CX, iy + 22, "IMMUNE SYSTEM", size=16, fill=C_INNATE, weight="bold"))

# ── Stage 1: Dendritic Cell (Triage) ─────────────────────────────────────────

dc_y = iy + 36
dc_w, dc_h = 500, 62
dc_x = CX - dc_w//2
parts.append(cell_box(dc_x, dc_y, dc_w, dc_h,
    "Dendritic Cell (DC) — Triage",
    "Classify findings by claim type · Route to verification",
    "Regex pattern matching · Statistical · Logical · Mathematical · Code-Behavioural · Structural",
    "#E8F8F5", C_INNATE))
parts.append(group_label(dc_x - 80, dc_y + 35, "STAGE 1", C_INNATE))

# Down arrows to Stage 2
for dx_off in [-200, 0, 200]:
    parts.append(arrow_down(CX + dx_off, dc_y + dc_h, dc_y + dc_h + 25, stroke="#95A5A6"))

# ── Stage 2: Parallel Cells (CT, B, NK) ──────────────────────────────────────

s2_y = dc_y + dc_h + 28
cw2, ch2 = 320, 82

# CT Cell
ct_x = ix + 20
parts.append(cell_box(ct_x, s2_y, cw2, ch2,
    "Cytotoxic T Cell (CT) — Code FFF",
    "Reads source · Verifies cited bugs exist at cited locations",
    "Claude CLI with file access · AST inspection · 300s timeout",
    "#E8F8F5", C_ADAPTIVE))

# NK Cell
nk_x = ix + 20 + cw2 + 15
nk_w = iw - cw2 - 55
parts.append(cell_box(nk_x, s2_y, nk_w, ch2,
    "NK Cell — Pattern Memory",
    "Dedup · Known FP matching · Adaptive-like memory across experiments",
    "Jaccard/TF-IDF · Persistent FP DB · Graduated decay",
    "#E8F8F5", C_INNATE))

parts.append(group_label(ct_x - 4, s2_y - 6, "STAGE 2 (parallel)", C_INNATE))

# Down arrows from Stage 2 to B-Cell complex
for dx_off in [-200, 0, 200]:
    parts.append(arrow_down(CX + dx_off, s2_y + ch2, s2_y + ch2 + 22, stroke="#95A5A6"))

# ── B-Cell Complex (Adaptive Immune — Domain Specialist Cells) ────────────────
# The B-Cell is the adaptive immune hub. Each domain specialist cell is a
# B-Cell subtype with its own tools, like biological B-Cell class switching.

bc_y = s2_y + ch2 + 26
bc_w_full = iw - 40
bc_h_full = 200
bc_x_full = ix + 20

parts.append(rrect(bc_x_full, bc_y, bc_w_full, bc_h_full, "#F0FFF4", C_ADAPTIVE, sw=2, rx=12))
parts.append(text(bc_x_full + bc_w_full//2, bc_y + 20, "B-Cell Complex — Adaptive Immune Verification", size=14, fill=C_ADAPTIVE, weight="bold"))
parts.append(text(bc_x_full + bc_w_full//2, bc_y + 38, "Domain specialist cells · Class-switching (IgM → IgG) · Each contributes hard gates + effect evidence to S_k", size=11, fill=C_SUBTEXT))
parts.append(group_label(bc_x_full - 4, bc_y + 12, "STAGE 2b", C_ADAPTIVE))

# ── Neuroimmune Routing: Brain → B-Cell Complex ──────────────────────────────
# The insect brain classifies the task domain (from experiment config) and
# activates the appropriate specialist cells. This is the neuroimmune axis.
neuro_x = ix + 8  # left edge routing line
parts.append(f'<path d="M {bx} {by + bh//2} '
             f'Q {neuro_x} {by + bh//2} {neuro_x} {(by + bh + bc_y)//2} '
             f'Q {neuro_x} {bc_y + 10} {bc_x_full} {bc_y + 10}" '
             f'fill="none" stroke="{C_BRAIN}" stroke-width="2" '
             f'stroke-dasharray="6,3" marker-end="url(#arrowhead)"/>')
parts.append(text(neuro_x + 3, (by + bh + bc_y) // 2 - 30, "Neuroimmune", size=9, fill=C_BRAIN, anchor="start"))
parts.append(text(neuro_x + 3, (by + bh + bc_y) // 2 - 18, "Axis", size=9, fill=C_BRAIN, anchor="start"))
parts.append(text(neuro_x + 3, (by + bh + bc_y) // 2, "Domain", size=9, fill=C_BRAIN, anchor="start"))
parts.append(text(neuro_x + 3, (by + bh + bc_y) // 2 + 12, "Activation", size=9, fill=C_BRAIN, anchor="start"))

# Specialist domain cells — fully integrated, not future
domain_cells = [
    ("Software Cell",    "Python / Code",      "AST · pytest · ruff",   "mypy · bandit · dis",     True),
    ("Mathematics Cell", "Math / Logic",        "SymPy · z3 · mpmath",   "uncertainties · Lean",    True),
    ("Chemistry Cell",   "Chemical",            "SMILES · chempy",       "Stoichiometry · Thermo",  False),
    ("Physics Cell",     "Physical",            "pint · units",          "Dimensional analysis",    False),
    ("Biology Cell",     "Biological",          "biopython",             "Sequence · Structure",    False),
    ("Engineering Cell", "Engineering",         "HW/SW interface",       "Tolerance · Safety",      False),
]

dc_w = (bc_w_full - 50) // 3
dc_h = 66
dc_gap = 10
row1_y = bc_y + 50
row2_y = row1_y + dc_h + dc_gap

for i, (name, domain, tools1, tools2, implemented) in enumerate(domain_cells):
    row = i // 3
    col = i % 3
    dx = bc_x_full + 15 + col * (dc_w + dc_gap)
    dy = row1_y if row == 0 else row2_y
    fill = "#E8F8F5" if implemented else "#FFF9E6"
    border = C_ADAPTIVE if implemented else "#F39C12"
    status_mark = "●" if implemented else "○"
    parts.append(rrect(dx, dy, dc_w, dc_h, fill, border, sw=1.5, rx=8))
    parts.append(text(dx + dc_w//2, dy + 16, f"{status_mark} {name}", size=12, fill=C_TEXT, weight="bold"))
    parts.append(text(dx + dc_w//2, dy + 32, domain, size=10, fill=border, weight="bold"))
    parts.append(text(dx + dc_w//2, dy + 46, tools1, size=10, fill=C_SUBTEXT))
    parts.append(text(dx + dc_w//2, dy + 58, tools2, size=9, fill=C_SUBTEXT))

# Legend for implemented vs planned
parts.append(text(bc_x_full + bc_w_full - 10, bc_y + bc_h_full - 10,
    "● Implemented   ○ Planned (domain TOML registered)", size=10, fill=C_SUBTEXT, anchor="end"))

# ── Formalisation Agent (B-Cell enhancer, below domain cells) ─────────────────

fa_y = bc_y + bc_h_full + 8
fa_w, fa_h = 520, 44
fa_x = CX - fa_w//2
parts.append(rrect(fa_x, fa_y, fa_w, fa_h, "#FFF9E6", "#F39C12", sw=1.5, rx=8))
parts.append(text(fa_x + fa_w//2, fa_y + 17, "Formalisation Agent (B-Cell Enhancer)", size=12, fill="#F39C12", weight="bold"))
parts.append(text(fa_x + fa_w//2, fa_y + 33, "Extracts preconditions → Z3 constraints · Prevents false rejection from context erasure", size=10, fill=C_SUBTEXT))
# Connect to B-Cell complex
parts.append(line(fa_x + fa_w//2, fa_y, CX, bc_y + bc_h_full, stroke="#F39C12", sw=1.5, dash="4,3"))

# Down arrows from B-Cell complex to Stage 3
for dx_off in [-200, 0, 200]:
    parts.append(arrow_down(CX + dx_off, fa_y + fa_h, fa_y + fa_h + 18, stroke="#95A5A6"))

# ── Stage 3a: Helper T Cell ──────────────────────────────────────────────────

ht_y = fa_y + fa_h + 22
ht_w, ht_h = 540, 62
ht_x = CX - ht_w//2
parts.append(cell_box(ht_x, ht_y, ht_w, ht_h,
    "Helper T Cell (HT) — Verdict Synthesis",
    "Confidence-weighted aggregation across all cell types",
    "Asymmetric thresholds: Rejection ≥ 0.6 · Confirmation ≥ 0.4 · Else UNCERTAIN → escalate to HIL",
    "#E8F8F5", C_COORD))
parts.append(group_label(ht_x - 80, ht_y + 20, "STAGE 3a", C_COORD))

# Down arrow
parts.append(arrow_down(CX, ht_y + ht_h, ht_y + ht_h + 22, stroke="#95A5A6"))

# ── Stage 3b: Regulatory T Cell ──────────────────────────────────────────────

rt_y = ht_y + ht_h + 25
rt_w, rt_h = 540, 62
rt_x = CX - rt_w//2
parts.append(cell_box(rt_x, rt_y, rt_w, rt_h,
    "Regulatory T Cell (RT) — Autoimmune Prevention",
    "Monitors rejection rate · Prevents immune system attacking its own valid findings",
    "If rejection > 50% OR all findings from one model rejected → autoimmune override (all pass)",
    "#E8F8F5", C_COORD))
parts.append(group_label(rt_x - 80, rt_y + 20, "STAGE 3b", C_COORD))

# ═══════════════════════════════════════════════════════════════════════════════
# ENDOCRINE SYSTEM (right side, adjacent to immune)
# ═══════════════════════════════════════════════════════════════════════════════

ey = rt_y + rt_h + 50
ew, eh = 480, 120
ex = CX - ew - 30

parts.append(rrect(ex, ey, ew, eh, "#FFF5EB", C_ENDOCRINE, sw=2, rx=14))
parts.append(text(ex + ew//2, ey + 22, "Endocrine System — Fix Evaluation", size=15, fill=C_ENDOCRINE, weight="bold"))
parts.append(text(ex + ew//2, ey + 42, "Whole-body health monitor", size=12, fill=C_SUBTEXT))
parts.append(text(ex + ew//2, ey + 62, "Sandbox isolation · Pre/post diff · Ruff · Mypy · Bandit · Pytest", size=11, fill="#A0522D"))
parts.append(text(ex + ew//2, ey + 80, "Verdicts: SAFE · HARMFUL · NEUTRAL · UNEVALUABLE", size=11, fill=C_SUBTEXT))
parts.append(text(ex + ew//2, ey + 98, "SEARCH/REPLACE application · Target file resolution · Net issue delta", size=10, fill=C_SUBTEXT))

# Arrow from immune → endocrine
parts.append(arrow(CX - 40, iy + ih, ex + ew//2, ey, stroke=C_ENDOCRINE))

# ═══════════════════════════════════════════════════════════════════════════════
# S_k PIPELINE (Metabolism — right of endocrine)
# ═══════════════════════════════════════════════════════════════════════════════

sk_x = CX + 30
sk_w = ew
sk_y = ey
sk_h = eh

parts.append(rrect(sk_x, sk_y, sk_w, sk_h, "#F5EEF8", C_SK, sw=2, rx=14))
parts.append(text(sk_x + sk_w//2, sk_y + 22, "S_k Pipeline — Solution Reliability", size=15, fill=C_SK, weight="bold"))
parts.append(text(sk_x + sk_w//2, sk_y + 42, "Metabolism: energy extraction from fixes", size=12, fill=C_SUBTEXT))
parts.append(text(sk_x + sk_w//2, sk_y + 62, "S_k = A × E   (Admissibility × Effect Evidence)", size=12, fill=C_SK, weight="bold"))
parts.append(text(sk_x + sk_w//2, sk_y + 80, "Tristate: ADMISSIBLE · REJECTED · ESCALATE", size=11, fill=C_SUBTEXT))
parts.append(text(sk_x + sk_w//2, sk_y + 98, "Hard gates (AST, compile) · Effect gates (ruff, mypy, bandit, test) · S* threshold · R_k loop", size=10, fill=C_SUBTEXT))

# Arrow from immune → S_k
parts.append(arrow(CX + 40, iy + ih, sk_x + sk_w//2, sk_y, stroke=C_SK))

# ═══════════════════════════════════════════════════════════════════════════════
# CIRCULATORY SYSTEM (Finding Registry)
# ═══════════════════════════════════════════════════════════════════════════════

cy_r = ey + eh + 30
cw_r, ch_r = 700, 80
cx_r = CX - cw_r//2

parts.append(rrect(cx_r, cy_r, cw_r, ch_r, "#FDEDEC", C_CIRC, sw=2, rx=14))
parts.append(text(CX, cy_r + 22, "Finding Registry — Circulatory System", size=15, fill=C_CIRC, weight="bold"))
parts.append(text(CX, cy_r + 42, "Carries findings with full provenance between all body systems", size=12, fill=C_SUBTEXT))
parts.append(text(CX, cy_r + 60, "OPEN → CONFIRMED → CLOSED  ·  CONTESTED → ESCALATED → HIL", size=12, fill=C_CIRC))
parts.append(text(CX, cy_r + 74, "Source model · Round · Verdicts · Severity · Proposed fix · S_k result · Immune verdict", size=10, fill=C_SUBTEXT))

# Arrows from endocrine + S_k → registry
parts.append(arrow(ex + ew//2, ey + eh, CX - 100, cy_r, stroke=C_ENDOCRINE))
parts.append(arrow(sk_x + sk_w//2, sk_y + sk_h, CX + 100, cy_r, stroke=C_SK))

# ═══════════════════════════════════════════════════════════════════════════════
# CONVERGENCE GATE (Homeostasis)
# ═══════════════════════════════════════════════════════════════════════════════

cg_y = cy_r + ch_r + 30
cg_w, cg_h = 700, 90
cg_x = CX - cg_w//2

parts.append(rrect(cg_x, cg_y, cg_w, cg_h, "#EBF5FB", C_CONVERGENCE, sw=2, rx=14))
parts.append(text(CX, cg_y + 22, "Convergence Gate — Homeostasis", size=15, fill=C_CONVERGENCE, weight="bold"))
parts.append(text(CX, cg_y + 42, "System reaches equilibrium when discovery is exhausted and no contested findings remain", size=12, fill=C_SUBTEXT))
parts.append(text(CX, cg_y + 62, "ρ (novelty depletion) · γ (discovery exhaustion) · open_ch (unresolved critical/high) · contested = 0", size=11, fill=C_CONVERGENCE))
parts.append(text(CX, cg_y + 80, "2 consecutive gate passes required · Burst mode: per-phase convergence then integration", size=10, fill=C_SUBTEXT))

# Arrow from registry → convergence
parts.append(arrow_down(CX, cy_r + ch_r, cg_y, stroke=C_CIRC))

# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK LOOP (brain ← convergence)
# ═══════════════════════════════════════════════════════════════════════════════

# Right-side feedback loop: convergence → brain (next round dispatch)
fb_x = W - 35
parts.append(f'<path d="M {CX + cg_w//2} {cg_y + cg_h//2} '
             f'Q {fb_x} {cg_y + cg_h//2} {fb_x} {(cg_y + by + bh)//2} '
             f'Q {fb_x} {by + bh//2} {CX + bw//2 + 5} {by + bh//2}" '
             f'fill="none" stroke="{C_BRAIN}" stroke-width="2" '
             f'stroke-dasharray="6,4" marker-end="url(#arrowhead)"/>')
parts.append(text(fb_x - 6, (cg_y + iy)//2, "Next", size=10, fill=C_BRAIN, anchor="end"))
parts.append(text(fb_x - 6, (cg_y + iy)//2 + 14, "Round", size=10, fill=C_BRAIN, anchor="end"))

# Left-side label: HIL escalation
hil_x = 32
parts.append(f'<path d="M {ht_x} {ht_y + ht_h//2} '
             f'Q {hil_x} {ht_y + ht_h//2} {hil_x} {ht_y - 20}" '
             f'fill="none" stroke="{C_CIRC}" stroke-width="1.5" '
             f'stroke-dasharray="4,3" marker-end="url(#arrowhead)"/>')
parts.append(text(hil_x + 4, ht_y - 26, "HIL Escalation", size=10, fill=C_CIRC, anchor="start"))
parts.append(text(hil_x + 4, ht_y - 14, "(Human-in-Loop)", size=9, fill=C_SUBTEXT, anchor="start"))

# ═══════════════════════════════════════════════════════════════════════════════
# LEGEND
# ═══════════════════════════════════════════════════════════════════════════════

ly = H - 48
parts.append(line(40, ly - 16, W - 40, ly - 16, stroke="#E0E0E0", sw=1))
legend_items = [
    (C_BRAIN, "CNS / Brain"),
    (C_NEURON, "Neurons / Models"),
    (C_INNATE, "Innate Immune"),
    (C_ADAPTIVE, "Adaptive Immune"),
    (C_COORD, "Immune Coordination"),
    (C_ENDOCRINE, "Endocrine"),
    (C_SK, "Metabolism / S_k"),
    (C_CIRC, "Circulatory / Registry"),
    (C_CONVERGENCE, "Homeostasis"),
]
lx = 60
for colour, label in legend_items:
    parts.append(f'<rect x="{lx}" y="{ly - 6}" width="12" height="12" rx="3" fill="{colour}"/>')
    parts.append(text(lx + 18, ly + 5, label, size=10, fill=C_TEXT, anchor="start"))
    lx += len(label) * 7 + 38

parts.append("</svg>")

# ── Write output ──────────────────────────────────────────────────────────────

svg = "\n".join(parts)
out_path = Path(__file__).resolve().parent.parent / "docs" / "CDSFL_Topology.svg"
out_path.write_text(svg, encoding="utf-8")
print(f"Written: {out_path} ({len(svg):,} bytes)")
