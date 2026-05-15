import sys
import os
import json
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import neurokit2 as nk

sys.path.insert(0, '.')
from src.biometric import load_subject, extract_stress_templates, extract_biometric_vector, STRESS_LEVELS, get_ecg_segment_for_level
from src.keyderivation import enroll_multi, authenticate_multi, save_profile, load_profile, biometric_similarity
from src.crypto import encrypt_database, decrypt_database

PROFILE_PATH = 'models/operator_profile.json'
TERRAIN_DB   = b'{"terrain": "Sector-7-Alpha", "coordinates": [[45.2, 21.3], [45.3, 21.4]], "classification": "NATO-SECRET", "elevation_map": "DEM-2024-RO"}'

OPERATORS = {
    'Operator Alpha':   {'bidmc': 'data/bidmc/bidmc05', 'stdb': 'data/stdb/300'},
    'Operator Bravo':   {'bidmc': 'data/bidmc/bidmc02', 'stdb': 'data/stdb/301'},
    'Operator Charlie': {'bidmc': 'data/bidmc/bidmc07', 'stdb': 'data/stdb/302'},
    'Operator Delta':   {'bidmc': 'data/bidmc/bidmc08', 'stdb': 'data/stdb/303'},
    'Operator Echo':    {'bidmc': 'data/bidmc/bidmc09', 'stdb': 'data/stdb/304'},
}

STRESS_HR     = {'rest':'60-90','light':'90-110','moderate':'110-130','heavy':'130-160','cognitive':'80-100'}
STRESS_COLORS = {'rest':'#1a5c1a','light':'#2d7a2d','moderate':'#4a9a4a','heavy':'#1a4a1a','cognitive':'#3a6a3a'}

BG   = '#e8f5e0'
SURF = '#d4edcc'
ACC  = '#1a5c1a'
MUTED = 'rgba(26,92,26,0.5)'
GRID  = 'rgba(26,92,26,0.1)'
ERR   = '#b91c1c'

DRONE_STATES = {
    'idle':       {'led':ACC,      'label':'STANDBY',         'gps':'ACTIVE',  'color':ACC},
    'enrolled':   {'led':'#2d7a2d','label':'OPERATOR LOCKED', 'gps':'ACTIVE',  'color':'#2d7a2d'},
    'granted':    {'led':'#166016','label':'ACCESS GRANTED',  'gps':'ACTIVE',  'color':'#166016'},
    'denied':     {'led':ERR,      'label':'ACCESS DENIED',   'gps':'ACTIVE',  'color':ERR},
    'attack':     {'led':ERR,      'label':'ATTACK BLOCKED',  'gps':'SPOOFED', 'color':ERR},
    'processing': {'led':'#4a9a4a','label':'PROCESSING...',   'gps':'ACTIVE',  'color':'#4a9a4a'},
}

st.set_page_config(page_title='BioKey', layout='wide')
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap');
* {{ font-family: 'Share Tech Mono', monospace !important; }}
.stApp {{ background-color: {BG}; color: {ACC}; }}
.block-container {{ padding: 0 320px 4rem 2rem; max-width: 100%; }}
.nav-bar {{ position:sticky;top:0;z-index:999;background:{SURF}ee;backdrop-filter:blur(8px);border-bottom:1px solid {ACC}33;padding:0.6rem 0;display:flex;align-items:center;justify-content:space-between;margin-bottom:0; }}
.nav-brand {{ color:{ACC};font-size:1rem;letter-spacing:0.15em;font-family:'Orbitron',monospace !important;font-weight:900; }}
.nav-links {{ display:flex;gap:2rem; }}
.nav-links a {{ color:{ACC}77;text-decoration:none;font-size:0.72rem;letter-spacing:0.1em;transition:color 0.2s; }}
.nav-links a:hover {{ color:{ACC}; }}
.section-sm {{ padding:1.4rem 0 1rem 0;border-bottom:1px solid {ACC}22; }}
.drone-panel {{
    position:fixed; right:0; top:0; width:300px; height:100vh;
    background:{SURF}; border-left:1px solid {ACC}33;
    display:flex; flex-direction:column; align-items:center;
    justify-content:center; gap:1.2rem; z-index:100; padding:2rem 1.5rem;
    overflow-y:auto;
}}
.sec-label {{ color:{ACC}66;font-size:0.65rem;letter-spacing:0.25em;margin-bottom:0.3rem; }}
.sec-title {{ color:{ACC};font-size:1.35rem;letter-spacing:0.06em;margin-bottom:0.25rem;font-family:'Orbitron',monospace !important;font-weight:700; }}
.sec-desc {{ color:{ACC}88;font-size:0.75rem;max-width:560px;line-height:1.6;margin-bottom:0.8rem; }}
.card {{ background:{SURF};border:1px solid {ACC}33;border-radius:4px;padding:0.7rem; }}
.card-label {{ color:{ACC}66;font-size:0.62rem;letter-spacing:0.15em;margin-bottom:0.2rem; }}
.card-value {{ color:{ACC};font-size:0.9rem;font-family:'Orbitron',monospace !important;font-weight:700; }}
.result-ok  {{ background:#c8e6c0;border:1px solid {ACC};border-radius:4px;padding:1rem; }}
.result-err {{ background:#fce8e8;border:1px solid {ERR};border-radius:4px;padding:1rem; }}
div[data-testid="metric-container"] {{ background:{SURF};border:1px solid {ACC}22;border-radius:4px;padding:0.5rem; }}
div[data-testid="metric-container"] label {{ color:{ACC}66 !important;font-size:0.68rem !important; }}
div[data-testid="metric-container"] div[data-testid="metric-value"] {{ color:{ACC} !important;font-size:1rem !important; }}
.stButton>button {{ background:{SURF};border:1px solid {ACC};color:{ACC};border-radius:2px;font-family:'Share Tech Mono',monospace;font-size:0.78rem;padding:0.6rem 1rem;width:100%;letter-spacing:0.08em;transition:all 0.2s; }}
.stButton>button:hover {{ background:{ACC}22;box-shadow:0 0 8px {ACC}44; }}
.stButton>button[kind="primary"] {{ background:{ACC};color:{BG}; }}
.stButton>button[kind="primary"]:hover {{ background:#2d7a2d; }}
button[data-testid="baseButton-secondary"] {{ border-color:{ERR}88 !important;color:{ERR} !important; }}
.stSelectbox>div>div {{ background:{SURF} !important;border-color:{ACC}44 !important;color:{ACC} !important; }}
.stSelectbox label,.stSlider label,.stCheckbox label,.stMultiSelect label {{ color:{ACC}66 !important;font-size:0.72rem !important; }}
hr {{ border-color:{ACC}22 !important; }}
h1,h2,h3 {{ color:{ACC} !important; }}
</style>
<div class="nav-bar">
  <span class="nav-brand">BIOKEY SYSTEM v2.0</span>
  <div class="nav-links">
    <a href="#overview">Overview</a>
    <a href="#signals">Signals</a>
    <a href="#enrollment">Enrollment</a>
    <a href="#authentication">Authentication</a>
    <a href="#attack">Attack</a>
  </div>
</div>
""", unsafe_allow_html=True)


def make_drone(state='idle', size=24):
    ds = DRONE_STATES.get(state, DRONE_STATES['idle'])
    led = ds['led']
    anim = 'animation:blink 0.8s infinite;' if state in ('processing','attack') else ''
    G = [[4,3,3,3,0,0,0,0,0,3,3,3,4],[3,3,3,0,0,0,0,0,0,0,3,3,3],[3,3,0,0,0,2,2,2,0,0,0,3,3],
         [3,0,0,0,2,1,1,1,2,0,0,0,3],[0,0,0,2,1,1,1,1,1,2,0,0,0],[0,0,2,1,1,1,5,1,1,1,2,0,0],
         [0,0,2,1,1,5,5,5,1,1,2,0,0],[0,0,2,1,1,1,5,1,1,1,2,0,0],[0,0,0,2,1,1,1,1,1,2,0,0,0],
         [3,0,0,0,2,1,1,1,2,0,0,0,3],[3,3,0,0,0,2,2,2,0,0,0,3,3],[3,3,3,0,0,0,0,0,0,0,3,3,3],
         [4,3,3,3,0,0,0,0,0,3,3,3,4]]
    C = {0:BG,1:'#2d4a2d',2:'#3a5a3a',3:'#4a6a4a',4:led,5:'#1a2a1a'}
    W = 13 * size
    rows = ''.join('<tr>'+''.join(f'<td style="width:{size}px;height:{size}px;min-width:{size}px;min-height:{size}px;background:{C[c]};padding:0;border:none;{"box-shadow:0 0 4px "+led+";" if c==4 else ""}"></td>' for c in row)+'</tr>' for row in G)
    return f'<style>@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}</style><div style="{anim}display:inline-block;width:{W}px;height:{W}px;flex-shrink:0;"><table style="border-collapse:collapse;border-spacing:0;width:{W}px;height:{W}px;table-layout:fixed;">{rows}</table></div>'


def plot_ecg(ecg, fs, seconds=10, color=ACC):
    samples = min(seconds*fs, len(ecg))
    t = np.linspace(0, seconds, samples)
    seg = ecg[:samples] - np.mean(ecg[:samples])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=seg, line=dict(color=color, width=1.5), fill='tozeroy', fillcolor='rgba(26,92,26,0.06)'))
    fig.update_layout(paper_bgcolor=SURF, plot_bgcolor=SURF, font=dict(color=MUTED, family='Share Tech Mono'),
        height=120, showlegend=False, margin=dict(l=30,r=10,t=6,b=20),
        xaxis=dict(gridcolor=GRID,title='sec',tickfont=dict(size=9)),
        yaxis=dict(gridcolor=GRID,tickfont=dict(size=9)))
    return fig


def plot_similarity(sims, threshold=0.85):
    levels, scores = list(sims.keys()), list(sims.values())
    fig = go.Figure()
    fig.add_trace(go.Bar(x=levels, y=scores, marker_color=[ACC if s>=threshold else ERR for s in scores],
        text=[f'{s:.3f}' for s in scores], textposition='outside', textfont=dict(color=ACC,size=11,family='Share Tech Mono')))
    fig.add_hline(y=threshold, line_dash='dash', line_color='#4a9a4a',
        annotation_text=f'threshold {threshold}', annotation_font=dict(color='#4a9a4a',family='Share Tech Mono',size=10))
    fig.update_layout(paper_bgcolor=SURF, plot_bgcolor=SURF, font=dict(color=MUTED,family='Share Tech Mono'),
        height=200, margin=dict(l=30,r=10,t=16,b=35),
        yaxis=dict(range=[0,1.15],gridcolor=GRID), xaxis=dict(gridcolor=GRID))
    return fig


for k,v in [('drone_state','idle'),('auth_result',None),('similarities',None),('enrolled_op',None),('decrypted_db',None),('encrypted',None)]:
    if k not in st.session_state: st.session_state[k] = v

profile_exists = os.path.exists(PROFILE_PATH)

# ── FIXED DRONE PANEL (right side) ───────────────────────────────────────────
ds = DRONE_STATES[st.session_state.drone_state]
enrolled_label = st.session_state.enrolled_op or 'NONE'
db_state = 'UNLOCKED' if st.session_state.drone_state == 'granted' else 'LOCKED'
db_color = ACC if st.session_state.drone_state == 'granted' else ERR
gps_color = ERR if ds['gps'] == 'SPOOFED' else ACC

result_html = ''
if st.session_state.auth_result:
    r = st.session_state.auth_result
    col = ACC if r['success'] else ERR
    cls = 'result-ok' if r['success'] else 'result-err'
    result_html = f'<div class="{cls}" style="width:100%;font-size:0.7rem;margin-top:0.3rem;"><b style="color:{col}">{r["label"]}</b><br><span style="color:{col}99;font-size:0.66rem;">{r["detail"]}</span></div>'

st.markdown(f"""
<div class="drone-panel">
  <div style="color:{ACC}66;font-size:0.6rem;letter-spacing:0.2em;align-self:flex-start;">// DRONE STATUS</div>
  {make_drone(st.session_state.drone_state, size=24)}
  <div style="width:100%;display:flex;flex-direction:column;gap:0.4rem;">
    <div class="card" style="padding:0.5rem;">
      <div class="card-label">STATUS</div>
      <div class="card-value" style="color:{ds['color']};font-size:0.82rem;">{ds['label']}</div>
    </div>
    <div class="card" style="padding:0.5rem;">
      <div class="card-label">GPS</div>
      <div class="card-value" style="color:{gps_color};font-size:0.82rem;">{ds['gps']}</div>
    </div>
    <div class="card" style="padding:0.5rem;">
      <div class="card-label">ENROLLED OPERATOR</div>
      <div class="card-value" style="font-size:0.82rem;">{enrolled_label}</div>
    </div>
    <div class="card" style="padding:0.5rem;">
      <div class="card-label">TERRAIN DATABASE</div>
      <div class="card-value" style="color:{db_color};font-size:0.82rem;">{db_state}</div>
    </div>
  </div>
  {result_html}
</div>
""", unsafe_allow_html=True)

# ── SECTION 1: OVERVIEW ──────────────────────────────────────────────────────
st.markdown('<div id="overview"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="section-sm">
<div class="sec-label">// SECTION 01</div>
<div class="sec-title">System Architecture</div>
<div class="sec-desc">End-to-end workflow — from raw ECG signal to AES-256-GCM encrypted terrain database.</div>

<style>
.blk {{
  border:1px solid {ACC}44; border-radius:4px; padding:0.45rem 0.8rem;
  font-size:0.72rem; text-align:center; background:{SURF};
  font-family:'Share Tech Mono',monospace;
}}
.blk-in  {{ border-color:{ACC}; background:{ACC}18; font-weight:700; }}
.blk-ok  {{ border-color:{ACC}; background:{ACC}22; color:{ACC}; }}
.blk-err {{ border-color:{ERR}; background:#fce8e8;  color:{ERR}; }}
.blk-out {{ border-color:{ACC}99; background:{ACC}12; }}
.blk-sub {{ font-size:0.63rem; color:{ACC}66; margin-top:0.15rem; }}
.arr {{ text-align:center; color:{ACC}44; font-size:1rem; line-height:1.4; }}
.col-title {{ font-size:0.65rem; letter-spacing:0.2em; color:{ACC}66; margin-bottom:0.6rem; }}
.branch {{ display:flex; gap:0.5rem; align-items:stretch; }}
.branch-line {{ width:1px; background:{ACC}33; align-self:stretch; }}
</style>

<div style="display:grid;grid-template-columns:1fr 1px 1fr;gap:1.5rem;margin-top:1rem;">

<!-- ═══ ENROLLMENT ═══ -->
<div>
  <div class="col-title">// ENROLLMENT</div>

  <div style="display:flex;gap:0.5rem;">
    <div class="blk blk-in" style="flex:2;">ECG + RESP<div class="blk-sub">raw signal — 5 stress levels</div></div>
    <div class="blk blk-in" style="flex:1;">PIN<div class="blk-sub">operator secret</div></div>
  </div>
  <div style="display:flex;">
    <div class="arr" style="flex:2;">↓</div>
    <div class="arr" style="flex:1;">↓</div>
  </div>
  <div style="display:flex;gap:0.5rem;">
    <div class="blk" style="flex:2;">Feature Extraction<div class="blk-sub">14 features × 5 templates</div></div>
    <div class="blk" style="flex:1;">SHA-256<div class="blk-sub">→ salt (32B)</div></div>
  </div>
  <div style="display:flex;">
    <div class="arr" style="flex:2;">↓</div>
    <div class="arr" style="flex:1;">↓</div>
  </div>
  <div style="display:flex;gap:0.5rem;">
    <div class="blk" style="flex:2;">Scale + Quantize → SHA-256<div class="blk-sub">→ seed (32B)</div></div>
    <div style="flex:1;display:flex;align-items:center;justify-content:center;color:{ACC}44;font-size:1.2rem;">↘</div>
  </div>
  <div class="arr">↓</div>
  <div class="blk">HKDF — SHA-256<div class="blk-sub">HKDF( seed, salt ) → wrapping_key (32B)</div></div>
  <div class="arr">↓</div>
  <div style="display:flex;gap:0.5rem;align-items:center;">
    <div class="blk" style="flex:2;">AES-256-GCM Encrypt<div class="blk-sub">wrapping_key.encrypt( aes_key )</div></div>
    <div style="flex:1;font-size:0.68rem;color:{ACC}66;text-align:center;">← aes_key<br>os.urandom(32)<br>generated once</div>
  </div>
  <div class="arr">↓</div>
  <div class="blk blk-out">Profile JSON<div class="blk-sub">wrapped_key × 5 &nbsp;|&nbsp; templates × 5</div></div>
  <div class="arr">↓</div>
  <div class="blk blk-out">AES-256-GCM Encrypt<div class="blk-sub">aes_key.encrypt( terrain_db ) → stored</div></div>
</div>

<!-- divider -->
<div style="background:{ACC}22;"></div>

<!-- ═══ AUTHENTICATION ═══ -->
<div>
  <div class="col-title">// AUTHENTICATION</div>

  <div style="display:flex;gap:0.5rem;">
    <div class="blk blk-in" style="flex:2;">Live ECG<div class="blk-sub">current measurement</div></div>
    <div class="blk blk-in" style="flex:1;">PIN<div class="blk-sub">operator input</div></div>
  </div>
  <div class="arr">↓</div>
  <div class="blk">Feature Extraction<div class="blk-sub">14 features from live signal</div></div>
  <div class="arr">↓</div>
  <div class="blk">Biometric Similarity × 5<div class="blk-sub">( cosine + proximity ) / 2 vs each template</div></div>
  <div class="arr">↓</div>
  <div class="blk" style="border-color:{ACC}88;">best_sim &gt; 0.85 ?<div class="blk-sub">nearest-neighbor threshold check</div></div>
  <div style="display:flex;gap:0.5rem;">
    <div style="flex:1;">
      <div class="arr">↓ NO</div>
      <div class="blk blk-err">ACCESS DENIED<div class="blk-sub">biometric mismatch</div></div>
    </div>
    <div style="flex:1;">
      <div class="arr">↓ YES</div>
      <div class="blk">Stored Template<div class="blk-sub">best match → seed derivation</div></div>
      <div class="arr">↓</div>
      <div class="blk">Scale + Quantize → SHA-256<div class="blk-sub">seed + SHA-256(PIN) = salt</div></div>
      <div class="arr">↓</div>
      <div class="blk">HKDF → wrapping_key<div class="blk-sub">deterministic from template + PIN</div></div>
      <div class="arr">↓</div>
      <div class="blk">AES-256-GCM Decrypt<div class="blk-sub">wrapping_key.decrypt( wrapped_key )</div></div>
      <div style="display:flex;gap:0.4rem;">
        <div style="flex:1;">
          <div class="arr" style="font-size:0.7rem;">↓ tag fail</div>
          <div class="blk blk-err" style="font-size:0.66rem;">PIN WRONG<div class="blk-sub">GCM auth tag mismatch</div></div>
        </div>
        <div style="flex:1;">
          <div class="arr" style="font-size:0.7rem;">↓ ok</div>
          <div class="blk">aes_key (32B)<div class="blk-sub">unwrapped</div></div>
          <div class="arr">↓</div>
          <div class="blk blk-ok">ACCESS GRANTED<div class="blk-sub">terrain DB decrypted</div></div>
        </div>
      </div>
    </div>
  </div>
</div>

</div>
</div>
""", unsafe_allow_html=True)

# ── SECTION 2: SIGNALS ───────────────────────────────────────────────────────
st.markdown('<div id="signals"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-sm">', unsafe_allow_html=True)
st.markdown('<div class="sec-label">// SECTION 02</div><div class="sec-title" style="font-size:1.3rem;">Biometric Signals</div><div class="sec-desc">Preview ECG and respiration signals for each operator at rest.</div>', unsafe_allow_html=True)

op_sel = st.selectbox('Select operator', list(OPERATORS.keys()), key='sig_op')
ecg, resp, fs = load_subject(OPERATORS[op_sel]['bidmc'])
ecg_c = ecg - np.mean(ecg)

c1, c2 = st.columns(2, gap='medium')
with c1:
    st.markdown('<div class="card-label">ECG — LEAD II</div>', unsafe_allow_html=True)
    st.plotly_chart(plot_ecg(ecg_c, fs), use_container_width=True, config={'displayModeBar':False})
with c2:
    if resp is not None:
        st.markdown('<div class="card-label">RESPIRATION</div>', unsafe_allow_html=True)
        st.plotly_chart(plot_ecg(resp, fs, color='#2d7a2d'), use_container_width=True, config={'displayModeBar':False})

ecg_clean = nk.ecg_clean(ecg_c[:60*fs], sampling_rate=fs)
_, info = nk.ecg_peaks(ecg_clean, sampling_rate=fs)
rr = np.diff(info['ECG_R_Peaks']) / fs * 1000
hr = int(60000/np.mean(rr)) if len(rr)>0 else 0
rmssd = np.sqrt(np.mean(np.diff(rr)**2)) if len(rr)>1 else 0
m1,m2,m3,m4 = st.columns(4)
with m1: st.metric('Heart Rate', f'{hr} bpm')
with m2: st.metric('RR Mean', f'{np.mean(rr):.0f} ms')
with m3: st.metric('RMSSD', f'{rmssd:.1f} ms')
with m4: st.metric('pNN50', f'{np.sum(np.abs(np.diff(rr))>50)/len(rr)*100:.1f}%')
st.markdown('</div>', unsafe_allow_html=True)

# ── SECTION 3: ENROLLMENT ────────────────────────────────────────────────────
st.markdown('<div id="enrollment"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-sm">', unsafe_allow_html=True)
st.markdown('<div class="sec-label">// SECTION 03</div><div class="sec-title" style="font-size:1.3rem;">Stress Test Enrollment</div><div class="sec-desc">Select an operator and stress levels. Each level generates a separate biometric template wrapping the same AES-256 key.</div>', unsafe_allow_html=True)

e1, e2 = st.columns([1,2], gap='large')
with e1:
    enroll_op = st.selectbox('Operator to enroll', list(OPERATORS.keys()), key='enroll_op')
    enroll_pin = st.text_input('Operator PIN', type='password', key='enroll_pin', placeholder='min 4 characters')
    enroll_btn = st.button('ENROLL OPERATOR', type='primary', use_container_width=True)
with e2:
    st.markdown('<div class="card-label">SELECT STRESS LEVELS</div>', unsafe_allow_html=True)
    cols5 = st.columns(5)
    selected_levels = []
    for i, level in enumerate(STRESS_LEVELS):
        with cols5[i]:
            if st.checkbox(level.upper(), value=True, key=f'lvl_{level}'):
                selected_levels.append(level)
            st.markdown(f'<div style="color:{STRESS_COLORS[level]}99;font-size:0.62rem;text-align:center;">{STRESS_HR[level]} bpm</div>', unsafe_allow_html=True)

if enroll_btn:
    if not selected_levels:
        st.warning('Select at least one stress level.')
    elif len(enroll_pin) < 4:
        st.warning('PIN must be at least 4 characters.')
    else:
        with st.spinner('Running stress test protocol...'):
            paths = OPERATORS[enroll_op]
            all_t = extract_stress_templates(paths['stdb'], paths['bidmc'])
            templates = {k:v for k,v in all_t.items() if k in selected_levels}
            profile, aes_key = enroll_multi(templates, pin=enroll_pin)
            os.makedirs('models', exist_ok=True)
            save_profile(profile, PROFILE_PATH)
            enc = encrypt_database(aes_key, TERRAIN_DB)
            st.session_state['encrypted'] = enc
            st.session_state.enrolled_op  = enroll_op
            st.session_state.drone_state  = 'enrolled'
            st.session_state.auth_result  = {'success':True,'label':'ENROLLMENT COMPLETE','detail':f'{enroll_op} // {len(templates)} templates'}
            st.session_state.similarities = None
        st.rerun()

if profile_exists:
    p = load_profile(PROFILE_PATH)
    st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-label">ENROLLED TEMPLATES</div>', unsafe_allow_html=True)
    tcols = st.columns(len(p['templates']))
    for i,(level,feat) in enumerate(p['templates'].items()):
        feat = np.array(feat)
        hr_t = int(60000/feat[0]) if feat[0]>0 else 0
        with tcols[i]:
            st.markdown(f'<div class="card" style="text-align:center;border-color:{STRESS_COLORS.get(level,ACC)}66"><div class="card-label">{level.upper()}</div><div class="card-value">~{hr_t} bpm</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── SECTION 4: AUTHENTICATION ────────────────────────────────────────────────
st.markdown('<div id="authentication"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-sm">', unsafe_allow_html=True)
st.markdown('<div class="sec-label">// SECTION 04</div><div class="sec-title" style="font-size:1.3rem;">Authentication</div><div class="sec-desc">Select who is authenticating and at what stress level. The system finds the nearest enrolled template and unlocks the AES key if similarity exceeds the threshold.</div>', unsafe_allow_html=True)

a1, a2, a3 = st.columns([1.2, 1, 1], gap='medium')
with a1: auth_op = st.selectbox('Authenticating as', list(OPERATORS.keys())+['Random injection'], key='auth_op')
with a2: auth_stress = st.selectbox('Stress state', STRESS_LEVELS, key='auth_stress')
with a3: auth_pin = st.text_input('PIN', type='password', key='auth_pin', placeholder='operator PIN')

b1, b2 = st.columns([3, 1], gap='medium')
with b1: noise = st.slider('Signal noise', 0.0, 3.0, 0.5, 0.1, key='noise')
with b2:
    st.markdown('<div style="height:1.8rem;"></div>', unsafe_allow_html=True)
    auth_btn = st.button('AUTHENTICATE', type='primary', use_container_width=True)

if auth_op != 'Random injection':
    paths = OPERATORS[auth_op]
    ecg_prev, fs_prev = get_ecg_segment_for_level(auth_stress, paths['bidmc'], paths['stdb'])
    ecg_cp = nk.ecg_clean(ecg_prev, sampling_rate=fs_prev)
    _, ip = nk.ecg_peaks(ecg_cp, sampling_rate=fs_prev)
    rr_p = np.diff(ip['ECG_R_Peaks']) / fs_prev * 1000
    hr_p = int(60000/np.mean(rr_p)) if len(rr_p)>0 else 0
    st.markdown(f'<div class="card-label">ECG PREVIEW — {auth_op.upper()} // {auth_stress.upper()} // HR ~{hr_p} bpm</div>', unsafe_allow_html=True)
    st.plotly_chart(plot_ecg(ecg_prev, fs_prev), use_container_width=True, config={'displayModeBar':False})

if auth_btn:
    if not profile_exists:
        st.warning('Enroll an operator first.')
    else:
        profile_loaded = load_profile(PROFILE_PATH)
        if auth_op == 'Random injection':
            features = np.random.normal(500, 150, 14)
        else:
            paths = OPERATORS[auth_op]
            if auth_stress == 'rest':
                features = extract_biometric_vector(paths['bidmc'])
            else:
                all_t = extract_stress_templates(paths['stdb'], paths['bidmc'])
                features = all_t.get(auth_stress, extract_biometric_vector(paths['bidmc']))
        features = features + np.random.normal(0, noise, features.shape)
        sims = {level: biometric_similarity(features, np.array(profile_loaded['templates'][level])) for level in profile_loaded['templates']}
        st.session_state.similarities = sims
        try:
            aes_key, matched, _ = authenticate_multi(features, profile_loaded, pin=auth_pin)
            if not st.session_state['encrypted']:
                st.session_state['encrypted'] = encrypt_database(aes_key, TERRAIN_DB)
            decrypted = decrypt_database(aes_key, st.session_state['encrypted'])
            st.session_state['decrypted_db'] = decrypted.decode()
            st.session_state.drone_state = 'granted'
            st.session_state.auth_result = {'success':True,'label':'ACCESS GRANTED','detail':f'matched: {matched.upper()} // score: {max(sims.values()):.4f}'}
        except ValueError as e:
            st.session_state.drone_state = 'denied'
            detail = str(e)
            st.session_state.auth_result = {'success':False,'label':'ACCESS DENIED','detail':detail}
            st.session_state['decrypted_db'] = None
        st.rerun()

if st.session_state.similarities:
    st.plotly_chart(plot_similarity(st.session_state.similarities), use_container_width=True, config={'displayModeBar':False})

if st.session_state.drone_state == 'granted' and st.session_state.get('decrypted_db'):
    st.markdown('<div class="result-ok">', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{ACC};font-size:0.78rem;margin-bottom:0.5rem;">TERRAIN DATABASE DECRYPTED</div>', unsafe_allow_html=True)
    st.json(json.loads(st.session_state['decrypted_db']))
    st.markdown('</div>', unsafe_allow_html=True)
elif st.session_state.drone_state == 'denied':
    st.markdown(f'<div class="result-err"><span style="color:{ERR};font-size:0.78rem;">ACCESS DENIED — terrain database remains encrypted</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── SECTION 5: ATTACK ────────────────────────────────────────────────────────
st.markdown('<div id="attack"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-sm">', unsafe_allow_html=True)
st.markdown('<div class="sec-label">// SECTION 05</div><div class="sec-title" style="font-size:1.3rem;">Attack Simulation</div><div class="sec-desc">Simulate unauthorized access attempts. The system blocks all access and the terrain database remains encrypted.</div>', unsafe_allow_html=True)

atk1, atk2 = st.columns([2,1], gap='large')
with atk1:
    attack_type = st.selectbox('Attack type', [
        'Different operator (biometric mismatch)',
        'Correct biometrics, wrong PIN',
        'Random biometric injection',
    ], key='atk_type')
    descs = {
        'Different': 'Attacker uses valid ECG from a different operator. Features are real but do not match the enrolled template.',
        'PIN': 'Attacker has the correct biometrics (e.g. captured operator) but does not know the PIN. Biometric similarity passes — key unwrap fails.',
        'Random': 'Attacker injects random biometric values attempting to brute-force the threshold. Computationally infeasible.',
    }
    key = 'PIN' if 'PIN' in attack_type else ('Random' if 'Random' in attack_type else 'Different')
    desc = descs[key]
    st.markdown(f'<div class="card" style="margin-top:0.5rem;font-size:0.75rem;line-height:1.8;"><div class="card-label">DESCRIPTION</div>{desc}</div>', unsafe_allow_html=True)
with atk2:
    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)
    attack_btn = st.button('SIMULATE ATTACK', type='secondary', use_container_width=True)

if attack_btn:
    if not profile_exists:
        st.warning('Enroll an operator first.')
    else:
        profile_loaded = load_profile(PROFILE_PATH)
        if 'Different' in attack_type:
            attacker = [k for k in OPERATORS if k != st.session_state.enrolled_op]
            attacker = attacker[0] if attacker else list(OPERATORS.keys())[1]
            fake = extract_biometric_vector(OPERATORS[attacker]['bidmc'])
            attack_pin = None
            detail = f'signal from {attacker}'
        elif 'PIN' in attack_type:
            enrolled_paths = OPERATORS.get(st.session_state.enrolled_op, list(OPERATORS.values())[0])
            fake = extract_biometric_vector(enrolled_paths['bidmc'])
            attack_pin = 'wrongpin999'
            detail = 'correct biometrics, wrong PIN'
        else:
            fake = np.random.normal(500, 150, 14)
            attack_pin = None
            detail = 'random biometric injection'
        sims = {level: biometric_similarity(fake, np.array(profile_loaded['templates'][level])) for level in profile_loaded['templates']}
        st.session_state.similarities = sims
        try:
            authenticate_multi(fake, profile_loaded, pin=attack_pin)
            st.session_state.auth_result = {'success':False,'label':'ATTACK SUCCEEDED','detail':'WARNING — review threshold'}
        except ValueError as e:
            st.session_state.auth_result = {'success':False,'label':'ATTACK BLOCKED','detail':f'{detail} // {str(e)}'}
        st.session_state.drone_state = 'attack'
        st.session_state['decrypted_db'] = None
        st.rerun()

st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-top:1.5rem;">
  <div class="card"><div class="card-label">BRUTE FORCE RESISTANCE</div><div class="card-value">2^896 combinations</div></div>
  <div class="card"><div class="card-label">KEY ENTROPY</div><div class="card-value">256 bit (AES-256-GCM)</div></div>
  <div class="card"><div class="card-label">BIOMETRIC ENTROPY</div><div class="card-value">~0.98 / 1.0</div></div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
