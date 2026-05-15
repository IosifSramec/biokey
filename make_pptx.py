from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

BG    = RGBColor(0x0d, 0x1a, 0x0d)
SURF  = RGBColor(0x14, 0x2a, 0x14)
SURF2 = RGBColor(0x1a, 0x35, 0x1a)
ACC   = RGBColor(0x4a, 0x9a, 0x4a)
ACC2  = RGBColor(0x2d, 0x7a, 0x2d)
LIGHT = RGBColor(0xe8, 0xf5, 0xe0)
MUTED = RGBColor(0x6a, 0xaa, 0x6a)
RED   = RGBColor(0xb9, 0x1c, 0x1c)
YELLOW= RGBColor(0xd4, 0xc5, 0x00)
WHITE = RGBColor(0xff, 0xff, 0xff)

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


def step_box(s, label, desc, x, y, w=3.9, h=0.85,
             fill=SURF, border=ACC, lsize=10, dsize=13):
    bx(s, x, y, w, h, fill=fill, border=border)
    t(s, label, x+0.1, y+0.08, w-0.2, 0.3, size=lsize, color=MUTED, bold=True)
    t(s, desc,  x+0.1, y+0.38, w-0.2, 0.45, size=dsize, color=LIGHT)


def arr(s, x, y, vertical=True, color=MUTED):
    char = '↓' if vertical else '→'
    t(s, char, x, y, 1, 0.35, size=16, color=color, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
hline(s, 6.85)

t(s, '// BIOKEY SYSTEM v2.0', 0.7, 0.7, 12, 0.5, size=13, color=MUTED)
t(s, 'Your heartbeat is the key —\nat any stress level.', 0.7, 1.3, 11.5, 2.6,
  size=52, bold=True, color=LIGHT)
t(s, 'Stress-Invariant Biometric Authentication  ·  AES-256-GCM',
  0.7, 4.1, 11.5, 0.6, size=20, color=ACC)
hline(s, 4.95, SURF2, 0.06)
t(s, 'HackTM 2026   //   Defence Track   //   Product Innovation Track',
  0.7, 5.15, 12, 0.45, size=14, color=MUTED)
t(s, 'Iosif Sramec   //   UPT AC',
  0.7, 5.65, 12, 0.45, size=14, color=MUTED)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — PROBLEM
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
t(s, '// 01  PROBLEM', 0.7, 0.62, 12, 0.4, size=12, color=MUTED)
t(s, 'Authentication breaks\nwhen it matters most.', 0.7, 1.05, 11, 1.7,
  size=40, bold=True, color=LIGHT)

cards = [
    ('PASSWORDS',          'Forgotten under stress.\nCoerced under threat.'),
    ('SMART CARDS',        'Lost in the field.\nStolen with the operator.'),
    ('FINGERPRINTS',       'Fail with gloves.\nFail when injured.'),
    ('BIOMETRICS AT REST', 'ECG at 160 bpm ≠ ECG at 70 bpm.\nSystem denies its own operator.'),
]
for i, (title, desc) in enumerate(cards):
    cx = 0.5 + i * 3.15
    bx(s, cx, 3.0, 3.0, 2.0, fill=SURF, border=RED, bw=Pt(1.5))
    t(s, title, cx+0.15, 3.1,  2.75, 0.4, size=11, bold=True, color=RED)
    t(s, desc,  cx+0.15, 3.6,  2.75, 1.2, size=14, color=MUTED)

t(s, '→  In the critical moment, the system locks out the right person.',
  0.7, 5.3, 12, 0.5, size=17, bold=True, color=YELLOW)
hline(s, 6.85)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — INSIGHT
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
t(s, '// 02  INSIGHT', 0.7, 0.62, 12, 0.4, size=12, color=MUTED)

t(s, '"ECG is unique and always present.\nThe problem is that nobody enrolled\nthe operator under stress."',
  0.8, 1.2, 11.5, 3.2, size=38, bold=True, color=ACC, italic=True)

bx(s, 0.5, 4.5, 5.8, 1.9, fill=SURF)
t(s, 'THE PROBLEM', 0.7, 4.62, 5.4, 0.35, size=11, bold=True, color=RED)
t(s, 'Soldier at rest: HR ~70 bpm\nUnder combat stress: 140–160 bpm\nECG morphology shifts → single template fails',
  0.7, 5.05, 5.4, 1.2, size=14, color=MUTED)

bx(s, 7.0, 4.5, 5.8, 1.9, fill=SURF, border=ACC, bw=Pt(2))
t(s, 'THE SOLUTION', 7.2, 4.62, 5.4, 0.35, size=11, bold=True, color=ACC)
t(s, 'Enroll the operator at ALL stress levels.\nSystem recognizes at 60 bpm and 160 bpm.\nNo manual state input required.',
  7.2, 5.05, 5.4, 1.2, size=14, color=LIGHT)

hline(s, 6.85)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — SOLUTION
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
t(s, '// 03  SOLUTION', 0.7, 0.62, 12, 0.4, size=12, color=MUTED)
t(s, 'Multi-Template Stress Enrollment', 0.7, 1.05, 12, 0.65, size=36, bold=True, color=LIGHT)
t(s, 'Like a treadmill stress test at the cardiologist — capture biometric signature across the full physiological spectrum.',
  0.7, 1.8, 12, 0.5, size=15, color=MUTED)

levels = [
    ('REST',      '60–90 bpm',   0.55),
    ('LIGHT',     '90–110 bpm',  3.0),
    ('MODERATE',  '110–130 bpm', 5.45),
    ('HEAVY',     '130–160 bpm', 7.9),
    ('COGNITIVE', '80–100 bpm',  10.35),
]
for name, hr, cx in levels:
    bx(s, cx, 2.55, 2.35, 2.8, fill=SURF2, border=ACC)
    t(s, name, cx+0.1, 2.68, 2.15, 0.4, size=11, bold=True, color=ACC)
    t(s, hr,   cx+0.1, 3.15, 2.15, 0.5, size=20, bold=True, color=LIGHT, align=PP_ALIGN.CENTER)
    t(s, '14 HRV\nfeatures', cx+0.1, 3.75, 2.15, 0.7, size=13, color=MUTED, align=PP_ALIGN.CENTER)
    t(s, 'ECG + RESP', cx+0.1, 4.55, 2.15, 0.4, size=11, color=MUTED, align=PP_ALIGN.CENTER)

bx(s, 0.5, 5.6, 12.3, 0.85, fill=SURF, border=ACC2)
t(s, '→  At authentication: live ECG + PIN → nearest template matched automatically → AES-256 key unwrapped',
  0.7, 5.75, 12, 0.5, size=15, bold=True, color=LIGHT)
hline(s, 6.85)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — ARCHITECTURE (redesigned)
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
t(s, '// 04  CRYPTOGRAPHIC ARCHITECTURE', 0.7, 0.62, 12, 0.4, size=12, color=MUTED)
t(s, 'From ECG to AES-256 Key', 0.7, 1.0, 12, 0.55, size=30, bold=True, color=LIGHT)

# ── ENROLLMENT (left) ──────────────────────────────────────────────────────
EX = 0.4
bx(s, EX, 1.75, 5.9, 4.95, fill=RGBColor(0x10,0x20,0x10), border=MUTED, bw=Pt(0.8))
t(s, 'ENROLLMENT', EX+0.15, 1.82, 5.6, 0.35, size=11, bold=True, color=MUTED)

# input row
bx(s, EX+0.15, 2.2,  2.6, 0.65, fill=SURF2, border=ACC, bw=Pt(1.5))
t(s, 'ECG + RESP',  EX+0.25, 2.3, 2.4, 0.45, size=14, bold=True, color=LIGHT, align=PP_ALIGN.CENTER)
bx(s, EX+3.0,  2.2,  2.6, 0.65, fill=SURF2, border=ACC, bw=Pt(1.5))
t(s, 'PIN',         EX+3.1,  2.3, 2.4, 0.45, size=14, bold=True, color=LIGHT, align=PP_ALIGN.CENTER)

t(s, '↓', EX+1.25, 2.9, 1.0, 0.35, size=16, color=MUTED, align=PP_ALIGN.CENTER)
t(s, '↓', EX+4.1,  2.9, 1.0, 0.35, size=16, color=MUTED, align=PP_ALIGN.CENTER)

bx(s, EX+0.15, 3.28, 2.6, 0.65, fill=SURF)
t(s, 'Feature Extraction', EX+0.25, 3.35, 2.4, 0.5, size=13, color=LIGHT, align=PP_ALIGN.CENTER)
bx(s, EX+3.0,  3.28, 2.6, 0.65, fill=SURF)
t(s, 'SHA-256  →  salt', EX+3.1, 3.35, 2.4, 0.5, size=13, color=LIGHT, align=PP_ALIGN.CENTER)

t(s, '↓  +  ↓', EX+1.8, 3.97, 2.0, 0.35, size=16, color=MUTED, align=PP_ALIGN.CENTER)

bx(s, EX+0.15, 4.35, 5.45, 0.65, fill=SURF, border=ACC, bw=Pt(1.5))
t(s, 'HKDF( SHA-256(features),  salt=SHA-256(PIN) )  →  wrapping_key',
  EX+0.25, 4.43, 5.25, 0.5, size=12, color=ACC, bold=True, align=PP_ALIGN.CENTER)

t(s, '↓', EX+2.8, 5.03, 1.0, 0.35, size=16, color=MUTED, align=PP_ALIGN.CENTER)

bx(s, EX+0.15, 5.4, 5.45, 0.65, fill=SURF)
t(s, 'AES-256-GCM.encrypt( aes_key )   [aes_key = os.urandom(32)]',
  EX+0.25, 5.48, 5.25, 0.5, size=12, color=LIGHT, align=PP_ALIGN.CENTER)

# ── AUTHENTICATION (right) ─────────────────────────────────────────────────
AX = 7.1
bx(s, AX, 1.75, 5.9, 4.95, fill=RGBColor(0x10,0x20,0x10), border=MUTED, bw=Pt(0.8))
t(s, 'AUTHENTICATION', AX+0.15, 1.82, 5.6, 0.35, size=11, bold=True, color=MUTED)

bx(s, AX+0.15, 2.2, 2.6, 0.65, fill=SURF2, border=ACC, bw=Pt(1.5))
t(s, 'Live ECG', AX+0.25, 2.3, 2.4, 0.45, size=14, bold=True, color=LIGHT, align=PP_ALIGN.CENTER)
bx(s, AX+3.0,  2.2, 2.6, 0.65, fill=SURF2, border=ACC, bw=Pt(1.5))
t(s, 'PIN', AX+3.1, 2.3, 2.4, 0.45, size=14, bold=True, color=LIGHT, align=PP_ALIGN.CENTER)

t(s, '↓', AX+1.25, 2.9, 1.0, 0.35, size=16, color=MUTED, align=PP_ALIGN.CENTER)

bx(s, AX+0.15, 3.28, 2.6, 0.65, fill=SURF)
t(s, 'Feature Extraction', AX+0.25, 3.35, 2.4, 0.5, size=13, color=LIGHT, align=PP_ALIGN.CENTER)

t(s, '↓', AX+1.25, 3.97, 1.0, 0.35, size=16, color=MUTED, align=PP_ALIGN.CENTER)

bx(s, AX+0.15, 4.35, 5.45, 0.65, fill=SURF)
t(s, 'Similarity( live, template_i ) × 5  →  best > 0.85 ?',
  AX+0.25, 4.43, 5.25, 0.5, size=13, color=LIGHT, align=PP_ALIGN.CENTER)

t(s, '↓ YES', AX+1.0, 5.03, 1.5, 0.35, size=13, color=MUTED)
t(s, 'NO →', AX+3.5, 5.03, 1.5, 0.35, size=13, color=RED)

bx(s, AX+0.15, 5.4, 3.1, 0.65, fill=SURF, border=ACC, bw=Pt(1.5))
t(s, 'HKDF + AES-GCM decrypt\n→  aes_key  →  GRANTED',
  AX+0.25, 5.43, 2.9, 0.6, size=11, color=ACC, bold=True, align=PP_ALIGN.CENTER)

bx(s, AX+3.5, 5.4, 2.1, 0.65, fill=RGBColor(0x30,0x10,0x10), border=RED)
t(s, 'ACCESS\nDENIED', AX+3.6, 5.43, 1.9, 0.6, size=12, color=RED, bold=True, align=PP_ALIGN.CENTER)

hline(s, 6.85)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — SECURITY PROPERTIES
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
t(s, '// 05  SECURITY PROPERTIES', 0.7, 0.62, 12, 0.4, size=12, color=MUTED)
t(s, 'What the attacker needs — and why they fail.',
  0.7, 1.05, 12, 0.6, size=32, bold=True, color=LIGHT)

props = [
    ('CAPTURED HARDWARE',       'Terrain DB is AES-256-GCM ciphertext.\nWithout ECG — permanently inaccessible.'),
    ('WRONG OPERATOR',          'Similarity < 0.85 → wrong wrapping key\n→ AES-GCM tag mismatch → denied.'),
    ('CORRECT ECG, WRONG PIN',  'Similarity passes.\nPIN salt missing → cryptographic failure.'),
    ('STRESS STATE MISMATCH',   '5 templates cover the full spectrum.\nNearest match selected automatically.'),
    ('KEY NEVER STORED',        'aes_key exists only in RAM.\nDerived fresh each authentication.'),
    ('BRUTE FORCE',             'AES-256: 2^256 keyspace.\nComputationally infeasible.'),
]
for i, (title, desc) in enumerate(props):
    col = i % 3
    row = i // 3
    cx = 0.5 + col * 4.25
    cy = 2.1 + row * 2.15
    bx(s, cx, cy, 4.0, 2.0, fill=SURF)
    t(s, title, cx+0.15, cy+0.12, 3.75, 0.4, size=11, bold=True, color=ACC)
    t(s, desc,  cx+0.15, cy+0.62, 3.75, 1.2, size=14, color=MUTED)

bx(s, 0.4, 6.28, 12.5, 0.44, fill=RGBColor(0x10,0x20,0x10), border=MUTED, bw=Pt(0.6))
t(s, '// PRODUCTION NOTE', 0.58, 6.34, 2.3, 0.32, size=9, bold=True, color=MUTED)
t(s, 'In production: biometric profile stored in TPM/HSM on-device. Key derivation inside secure enclave — profile never exposed in memory. Current implementation demonstrates the cryptographic layer (HKDF + AES-256-GCM), identical regardless of storage backend.',
  3.0, 6.34, 10.0, 0.34, size=9, color=MUTED, italic=True)
hline(s, 6.85)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — DEFENSE IN DEPTH
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
t(s, '// 06  ALTERNATIVE ARCHITECTURE', 0.7, 0.62, 12, 0.4, size=12, color=MUTED)
t(s, 'System Extensions.',
  0.7, 1.05, 12, 0.55, size=30, bold=True, color=LIGHT)

layers = [
    ('LAYER 1', 'Biometric — ECG + Respiration',
     'Stress-invariant multi-template enrollment. Unique cardiac signature across all physiological states.'),
    ('LAYER 2', 'PIN — Second Factor',
     'HKDF salt derived from SHA-256(PIN). Correct biometrics + wrong PIN = cryptographic failure.'),
    ('LAYER 3', 'Random Seed — Independent AES Key',
     'aes_key = os.urandom(32) — not derived from biometrics. Full biometric compromise cannot reconstruct the key.'),
    ('LAYER 4', 'Two-Man Rule',
     'Two operators must authenticate simultaneously. Neither can unlock the system alone. NATO nuclear standard.'),
    ('LAYER 5', 'Dead Man\'s Switch',
     'Key expires if operator does not re-authenticate every N minutes. Capture or incapacitation = automatic revocation.'),
]

for i, (tag, title, desc) in enumerate(layers):
    cy = 1.82 + i * 0.96
    bx(s, 0.4, cy, 12.5, 0.82, fill=SURF, border=MUTED, bw=Pt(0.8))
    t(s, tag,   0.55, cy+0.06, 1.1,  0.3, size=9,  bold=True, color=MUTED)
    t(s, title, 1.75, cy+0.06, 10.9, 0.3, size=13, bold=True, color=LIGHT)
    t(s, desc,  1.75, cy+0.40, 10.9, 0.35, size=11, color=MUTED)

hline(s, 6.85)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — NOVELTY + ACADEMIC VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
t(s, '// 07  ACADEMIC FOUNDATION + NOVELTY', 0.7, 0.62, 12, 0.4, size=12, color=MUTED)
t(s, 'Grounded in research — filling the gap.',
  0.7, 1.05, 12, 0.55, size=30, bold=True, color=LIGHT)

# Left — academic validation
bx(s, 0.4, 1.8, 6.0, 4.9, fill=RGBColor(0x10,0x20,0x10), border=MUTED, bw=Pt(0.8))
t(s, 'LITERATURE CONFIRMS OUR FOUNDATION', 0.6, 1.9, 5.8, 0.35, size=10, bold=True, color=MUTED)

papers = [
    ('ECG is person-distinctive',
     'Biel et al. — "ECG Analysis: A New Approach in\nHuman Identification" — IEEE Trans. 2001',
     '→ validates that ECG uniquely identifies individuals'),
    ('ECG → crypto key is feasible',
     'Venkatasubramanian et al. — "EKG-based Key\nAgreement in Body Sensor Networks" — IEEE 2008',
     '→ confirms 49.99% Hamming distance between persons'),
    ('Physiological signals for security',
     'Poon et al. — "A Novel Biometrics Method to\nSecure Wireless Body Area Sensor Networks" — 2006',
     '→ proves IPI-based keys are random, time-variant,\n   person-distinctive'),
]
for i, (title, cite, implication) in enumerate(papers):
    cy = 2.35 + i * 1.5
    bx(s, 0.55, cy, 5.7, 1.35, fill=SURF)
    t(s, title,       0.7,  cy+0.08, 5.4, 0.35, size=11, bold=True, color=LIGHT)
    t(s, cite,        0.7,  cy+0.45, 5.4, 0.5,  size=10, color=MUTED, italic=True)
    t(s, implication, 0.7,  cy+0.9,  5.4, 0.4,  size=10, color=ACC)

# Right — gap + BioKey contribution
bx(s, 7.0, 1.8, 5.9, 4.9, fill=RGBColor(0x10,0x20,0x10), border=ACC, bw=Pt(1.5))
t(s, 'THE GAP WE FILL', 7.2, 1.9, 5.6, 0.35, size=10, bold=True, color=ACC)

gaps = [
    ('All existing schemes:', 'Single enrollment at rest.\nFail under physiological stress.', RED),
    ('None address:', 'Operator authentication at\nvariable stress levels.', RED),
    ('BioKey contribution:', '5-template stress-invariant enrollment.\nHKDF + PIN second factor.\nAES-256-GCM — NATO standard.', ACC),
]
for i, (label_txt, desc, col) in enumerate(gaps):
    cy = 2.35 + i * 1.5
    bx(s, 7.15, cy, 5.6, 1.35, fill=SURF, border=col, bw=Pt(1.2))
    t(s, label_txt, 7.3, cy+0.08, 5.3, 0.35, size=11, bold=True, color=col)
    t(s, desc,      7.3, cy+0.48, 5.3, 0.75, size=13, color=LIGHT if col==ACC else MUTED)

hline(s, 6.85)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — APPLICATIONS
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
t(s, '// 08  APPLICATIONS', 0.7, 0.62, 12, 0.4, size=12, color=MUTED)
t(s, 'Any role where the right person\nmust be at the controls — right now.',
  0.7, 1.05, 11, 1.4, size=34, bold=True, color=LIGHT)

bx(s, 0.5, 2.7, 6.0, 3.7, fill=SURF)
t(s, 'MILITARY / DEFENCE', 0.7, 2.82, 5.7, 0.4, size=12, bold=True, color=RED)
for i, item in enumerate(['Drone operator authentication',
                          'Pilot / co-pilot verification',
                          'Nuclear launch authority (two-man rule)',
                          'Forward operating base access control']):
    t(s, f'→  {item}', 0.7, 3.35+i*0.55, 5.7, 0.5, size=15, color=LIGHT)

bx(s, 7.0, 2.7, 5.9, 3.7, fill=SURF, border=ACC, bw=Pt(1.5))
t(s, 'CIVIL / INDUSTRIAL', 7.2, 2.82, 5.6, 0.4, size=12, bold=True, color=ACC)
for i, item in enumerate(['Surgeon — operating room access control',
                          'Air traffic controller verification',
                          'Nuclear plant operator authentication',
                          'Critical infrastructure access control']):
    t(s, f'→  {item}', 7.2, 3.35+i*0.55, 5.6, 0.5, size=15, color=LIGHT)

t(s, 'Same platform. Same cryptographic guarantees. Different operator profiles.',
  0.7, 6.55, 12, 0.35, size=13, italic=True, color=MUTED)
hline(s, 6.85)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — CLOSING
# ══════════════════════════════════════════════════════════════════════════════
s = slide()
hline(s, 0.5)
hline(s, 6.85)

t(s, '"Your heartbeat is the key —\nat any stress level."',
  0.8, 1.3, 12, 3.0, size=46, bold=True, color=LIGHT,
  align=PP_ALIGN.CENTER, italic=True)

t(s, 'AES-256-GCM   ·   HKDF-SHA256   ·   Multi-Template HRV   ·   PIN Second Factor',
  0.7, 4.6, 12, 0.5, size=15, color=ACC, align=PP_ALIGN.CENTER)

hline(s, 5.35, SURF2, 0.05)

t(s, 'github.com/IosifSramec/biokey',
  0.7, 5.55, 12, 0.45, size=15, color=MUTED, align=PP_ALIGN.CENTER)
t(s, 'HackTM 2026', 0.7, 6.1, 12, 0.4, size=13, color=MUTED, align=PP_ALIGN.CENTER)

# ── Save ──────────────────────────────────────────────────────────────────────
prs.save('BioKey_Presentation.pptx')
print("Saved: BioKey_Presentation.pptx  (9 slides)")
