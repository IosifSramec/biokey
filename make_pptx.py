from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

BG    = RGBColor(0x0d, 0x1a, 0x0d)
SURF  = RGBColor(0x14, 0x2a, 0x14)
SURF2 = RGBColor(0x1a, 0x35, 0x1a)
ACC   = RGBColor(0x4a, 0x9a, 0x4a)
LIGHT = RGBColor(0xe8, 0xf5, 0xe0)
MUTED = RGBColor(0x6a, 0xaa, 0x6a)
RED   = RGBColor(0xb9, 0x1c, 0x1c)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H
blank = prs.slide_layouts[6]


def slide():
    s = prs.slides.add_slide(blank)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    return s


def t(s, text, x, y, w, h, size=20, bold=False, color=LIGHT,
      align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = 'Courier New'


def bx(s, x, y, w, h, fill=SURF, border=ACC, bw=Pt(1.2)):
    sh = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = border
    sh.line.width = bw
    return sh


def hline(s, y, color=ACC, thickness=0.04):
    sh = s.shapes.add_shape(1, Inches(0), Inches(y), W, Inches(thickness))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
hline(s, 6.85)

t(s, '// BIOKEY', 0.7, 0.7, 12, 0.5, size=13, color=MUTED)
t(s, 'Your heartbeat is the key —\nat any stress level.', 0.7, 1.3, 11.5, 2.8,
  size=54, bold=True, color=LIGHT)
t(s, 'Stress-Invariant Biometric Authentication  ·  AES-256-GCM',
  0.7, 4.2, 11.5, 0.6, size=19, color=ACC)
hline(s, 5.0, SURF2, 0.06)
t(s, 'HackTM 2026   //   Defence Track',
  0.7, 5.2, 12, 0.45, size=14, color=MUTED)
t(s, 'Jigmond Alexandru   ·   Milotin Rareș   ·   Sramec Iosif   ·   Stan Cristian     //     UPT AC',
  0.7, 5.7, 12, 0.45, size=12, color=MUTED)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — PROBLEM & CAUSE
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
t(s, '// 01  PROBLEM & CAUSE', 0.7, 0.62, 12, 0.4, size=12, color=MUTED)
t(s, 'Authentication fails\nwhen it matters most.', 0.7, 1.05, 12, 1.6,
  size=42, bold=True, color=LIGHT)

t(s, 'The human body changes under stress. Authentication systems don\'t.',
  0.7, 2.8, 12, 0.5, size=17, italic=True, color=MUTED)

cards = [
    ('STRESS CHANGES THE BODY',
     'HR: 70 bpm → 160 bpm\nECG enrolled at rest fails in the field.\nThe system denies its own operator.'),
    ('CAPTURED HARDWARE',
     'No cryptographic binding to the operator.\nSeized device = immediate data access.'),
    ('COERCION',
     'Passwords and cards can be taken by force.\nThe operator cannot protect them.'),
]
for i, (title, desc) in enumerate(cards):
    cx = 0.4 + i * 4.3
    bx(s, cx, 3.45, 4.0, 2.9, fill=SURF, border=RED, bw=Pt(1.5))
    t(s, title, cx+0.18, 3.57, 3.7, 0.45, size=11, bold=True, color=RED)
    t(s, desc,  cx+0.18, 4.15, 3.7, 2.0,  size=14, color=MUTED)

hline(s, 6.85)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — WHAT EXISTS vs WHAT WE HAVE
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
t(s, '// 02  EXISTING SOLUTIONS vs BIOKEY', 0.7, 0.62, 12, 0.4, size=12, color=MUTED)
t(s, 'Everything leaves a gap.\nWe close it.', 0.7, 1.05, 12, 1.5,
  size=40, bold=True, color=LIGHT)

# Left — what exists
bx(s, 0.4, 2.75, 5.9, 3.65, fill=SURF, border=RED, bw=Pt(1.5))
t(s, 'WHAT EXISTS', 0.6, 2.87, 5.6, 0.4, size=11, bold=True, color=RED)
for i, line in enumerate([
    '✕  Passwords — coerced or forgotten',
    '✕  Smart cards — lost or stolen',
    '✕  Single biometric template — fails under stress',
    '✕  Hardware encryption — key tied to device, not operator',
]):
    t(s, line, 0.6, 3.45+i*0.68, 5.6, 0.6, size=14, color=MUTED)

# Right — BioKey
bx(s, 7.0, 2.75, 5.9, 3.65, fill=SURF, border=ACC, bw=Pt(2))
t(s, 'BIOKEY', 7.2, 2.87, 5.6, 0.4, size=11, bold=True, color=ACC)
for i, line in enumerate([
    '✓  5 templates — covers all stress levels',
    '✓  Key derived from biometrics — not stored',
    '✓  PIN second factor — biometrics alone not enough',
    '✓  Captured hardware = only ciphertext',
]):
    t(s, line, 7.2, 3.45+i*0.68, 5.6, 0.6, size=14, color=LIGHT)

hline(s, 6.85)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — CLOSING
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
hline(s, 6.85)

t(s, '"We are the key\nto your heartbeat."',
  0.7, 1.0, 12, 3.4, size=56, bold=True, color=LIGHT,
  align=PP_ALIGN.CENTER, italic=True)

hline(s, 4.75, SURF2, 0.05)

t(s, 'AES-256-GCM   ·   HKDF-SHA256   ·   Multi-Template HRV   ·   PIN Second Factor',
  0.7, 4.95, 12, 0.5, size=15, color=ACC, align=PP_ALIGN.CENTER)
t(s, 'github.com/IosifSramec/biokey',
  0.7, 5.6, 12, 0.45, size=14, color=MUTED, align=PP_ALIGN.CENTER)
t(s, 'HackTM 2026   //   Defence Track',
  0.7, 6.1, 12, 0.4, size=13, color=MUTED, align=PP_ALIGN.CENTER)


# ── Save ──────────────────────────────────────────────────────────────────────
prs.save('BioKey_Presentation.pptx')
print("Saved: BioKey_Presentation.pptx  (4 slides)")
