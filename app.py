import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io, base64, os, glob
from scipy.optimize import curve_fit

st.set_page_config(layout="wide", page_title="TP — Learning Curve Dashboard", page_icon="📊")

# ═══ TP BRAND ═══
TP = dict(blue='#3047b0', light_blue='#0087FF', turquoise='#00AF9B', green_light='#84c98b',
    green_flash='#00D769', yellow='#F5D200', dark_slate='#4B4C6A', slate='#848dad',
    muted_violet='#706398', dark_gray='#414141', gray='#676767', light_gray='#cccccc',
    pastel_gray='#e6e6e5', pastel_sand='#ece9e7', sand='#d4d2ca', pastel_violet='#e2dfe8',
    pastel_slate='#c2c7cd', purple='#780096', violet='#8042CF', dark_indigo='#3e2666',
    indigo='#4d3293', burgundy='#5f365e', carmine='#ab2c37', dark_coral='#e04c5c',
    black='#000000', white='#FFFFFF')

KPI_DIRECTIONS = {"AHT": "Decreasing", "CSAT Agent": "Increasing", "CSAT Service": "Increasing",
                   "CES": "Increasing", "FCR": "Increasing",
                   "EUC": "Increasing", "BC": "Increasing", "CC": "Increasing", "CSAT": "Increasing"}

def load_logo(fn):
    for p in glob.glob(f'/mnt/user-data/uploads/*{fn}') + [fn]:
        if os.path.exists(p): 
            with open(p,'rb') as f: return base64.b64encode(f.read()).decode()
    try:
        sp = os.path.join(os.path.dirname(os.path.abspath(__file__)), fn)
        if os.path.exists(sp):
            with open(sp,'rb') as f: return base64.b64encode(f.read()).decode()
    except: pass
    return None

logo_w = load_logo('GMT_Logo_TP_RGB_Feb_2025_white.png')
logo_img = f'<img style="height:36px;width:auto;filter:brightness(1.1)" src="data:image/png;base64,{logo_w}">' if logo_w else ''

# ═══ CSS — FIXED SIDEBAR INPUT COLORS ═══
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
.stApp{{background:#f4f5f9;font-family:'Inter',-apple-system,sans-serif}}

/* === SIDEBAR === */
[data-testid="stSidebar"]{{background:linear-gradient(175deg,{TP['dark_slate']} 0%,{TP['blue']} 50%,{TP['dark_indigo']} 100%)}}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown {{color:#fff!important}}
[data-testid="stSidebar"] label {{
    font-weight:600!important;font-size:11px!important;letter-spacing:.6px;text-transform:uppercase;opacity:.85
}}
/* Sidebar inputs — white bg so text is readable */
[data-testid="stSidebar"] .stSelectbox > div > div {{
    background:rgba(255,255,255,.95)!important;border:1px solid rgba(255,255,255,.3)!important;
    color:{TP['dark_slate']}!important;border-radius:6px!important
}}
[data-testid="stSidebar"] .stSelectbox > div > div * {{color:{TP['dark_slate']}!important}}
[data-testid="stSidebar"] .stMultiSelect > div > div {{
    background:rgba(255,255,255,.95)!important;border:1px solid rgba(255,255,255,.3)!important;
    color:{TP['dark_slate']}!important;border-radius:6px!important
}}
[data-testid="stSidebar"] .stMultiSelect > div > div * {{color:{TP['dark_slate']}!important}}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
    background:{TP['dark_coral']}!important;color:#fff!important
}}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span {{color:#fff!important}}
[data-testid="stSidebar"] .stNumberInput > div > div > input {{
    background:rgba(255,255,255,.95)!important;border:1px solid rgba(255,255,255,.3)!important;
    color:{TP['dark_slate']}!important;border-radius:6px!important
}}
[data-testid="stSidebar"] .stSlider p {{color:#fff!important}}
[data-testid="stSidebar"] hr {{border-color:rgba(255,255,255,.12)!important}}
[data-testid="stSidebar"] .stRadio label {{text-transform:none!important;color:#fff!important}}
[data-testid="stSidebar"] .stRadio span {{color:#fff!important}}

/* === HEADER === */
.tp-hdr{{background:linear-gradient(135deg,{TP['blue']} 0%,{TP['dark_indigo']} 100%);color:#fff;padding:16px 28px;
    border-radius:12px;display:flex;align-items:center;justify-content:space-between;
    box-shadow:0 6px 30px rgba(48,71,176,.28);margin-bottom:0;position:relative;overflow:hidden}}
.tp-hdr::before{{content:'';position:absolute;top:0;right:0;width:200px;height:100%;
    background:linear-gradient(135deg,transparent 0%,rgba(0,175,155,.15) 100%);pointer-events:none}}
.tp-hdr .ts{{display:flex;align-items:center;gap:16px}}
.tp-hdr h1{{font-size:18px;font-weight:700;letter-spacing:.4px;margin:0;color:#fff}}
.tp-hdr .sub{{font-size:10px;opacity:.7;letter-spacing:1.2px;text-transform:uppercase;margin-top:2px}}
.tp-hdr .badge{{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);padding:5px 14px;
    border-radius:18px;font-size:12px;font-weight:600}}
.tp-hdr .dir{{background:{TP['turquoise']};padding:3px 10px;border-radius:10px;font-size:10px;font-weight:700;margin-left:6px}}

.al{{height:3px;background:linear-gradient(90deg,{TP['turquoise']},{TP['light_blue']},{TP['violet']});border-radius:2px;margin-bottom:18px}}

/* === KPI CARDS === */
.kc{{background:linear-gradient(135deg,#fff 0%,#fafbff 100%);border:1px solid {TP['pastel_gray']};border-radius:12px;
    padding:18px 14px;text-align:center;border-top:4px solid {TP['blue']};
    box-shadow:0 2px 12px rgba(75,76,106,.06);min-height:108px;
    display:flex;flex-direction:column;justify-content:center;transition:all .2s ease}}
.kc:hover{{transform:translateY(-3px);box-shadow:0 8px 28px rgba(75,76,106,.12)}}
.kc .v{{font-size:23px;font-weight:800;color:{TP['dark_slate']};line-height:1.2;letter-spacing:-.3px}}
.kc .l{{font-size:9px;color:{TP['gray']};margin-top:6px;font-weight:600;letter-spacing:.5px;text-transform:uppercase}}
.kc.tq{{border-top-color:{TP['turquoise']}}}.kc.gn{{border-top-color:{TP['green_flash']}}}
.kc.vi{{border-top-color:{TP['violet']}}}.kc.ig{{border-top-color:{TP['indigo']}}}.kc.co{{border-top-color:{TP['dark_coral']}}}

/* === SECTION HEADERS === */
.sh{{display:flex;align-items:center;gap:10px;margin:10px 0 8px;padding-bottom:6px;
    border-bottom:3px solid transparent;border-image:linear-gradient(90deg,{TP['turquoise']},{TP['blue']}) 1}}
.sh .i{{font-size:17px}}.sh h3{{font-size:13px;font-weight:700;color:{TP['dark_slate']};letter-spacing:.4px;text-transform:uppercase;margin:0}}

/* === PILLS === */
.ir{{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 14px}}
.ip{{background:{TP['pastel_violet']};color:{TP['dark_slate']};padding:3px 10px;border-radius:12px;font-size:10px;font-weight:500}}
.ip.hi{{background:{TP['blue']};color:#fff}}

/* === TABS === */
.stTabs [data-baseweb="tab-list"]{{gap:0;background:#fff;border-radius:8px;padding:3px;box-shadow:0 1px 4px rgba(0,0,0,.05)}}
.stTabs [data-baseweb="tab"]{{border-radius:6px;font-weight:600;font-size:12px;padding:7px 16px;color:{TP['gray']}}}
.stTabs [aria-selected="true"]{{background:{TP['blue']}!important;color:#fff!important}}

/* === TABLES === */
.stDataFrame thead tr th{{background:{TP['dark_slate']}!important;color:#fff!important;font-weight:600!important;
    font-size:10px!important;text-transform:uppercase;letter-spacing:.5px;padding:8px 12px!important}}
.stDataFrame tbody tr:nth-child(even){{background-color:{TP['pastel_violet']}!important}}
.stDataFrame tbody tr:hover{{background-color:rgba(48,71,176,.06)!important}}
.stDataFrame tbody td{{font-size:12px!important;padding:6px 12px!important;border-bottom:1px solid {TP['pastel_gray']}!important}}

/* === BUTTONS === */
.stDownloadButton>button{{background:{TP['blue']}!important;color:#fff!important;border:none!important;border-radius:8px!important;font-weight:600!important}}
.stDownloadButton>button:hover{{background:{TP['dark_indigo']}!important}}
hr{{border-color:{TP['pastel_gray']}!important}}

/* === METRIC DELTA COLORS (direction-aware, handled via CSS override) === */
[data-testid="stMetricValue"]{{font-size:20px;font-weight:700;color:{TP['dark_slate']}}}

/* === MISC === */
#MainMenu{{visibility:hidden}}footer{{visibility:hidden}}
/* Hide slider number input sub-labels */
[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] {{display:none!important}}
[data-testid="stSidebar"] [data-baseweb="slider"] + div {{display:none!important}}
.sb-logo{{text-align:center;padding:10px 0 4px}}.sb-logo img{{height:44px;width:auto}}
.sb-brand{{text-align:center;font-size:9px;letter-spacing:2px;text-transform:uppercase;opacity:.55;margin-bottom:8px;color:#fff!important}}

/* === GLOSSARY === */
.g-card{{background:linear-gradient(135deg,#fff 0%,#fafbff 100%);border:1px solid {TP['pastel_gray']};border-radius:12px;
    padding:20px 22px;margin-bottom:12px;border-left:5px solid {TP['blue']};
    box-shadow:0 2px 8px rgba(75,76,106,.04);transition:all .2s ease}}
.g-card:hover{{box-shadow:0 4px 16px rgba(75,76,106,.08);transform:translateX(2px)}}
.g-card h4{{color:{TP['blue']};font-size:14px;margin:0 0 8px;font-weight:700;letter-spacing:.2px}}
.g-card p{{color:{TP['dark_gray']};font-size:12.5px;margin:0;line-height:1.7}}
.g-section{{color:{TP['blue']};font-size:17px;font-weight:700;border-bottom:3px solid {TP['turquoise']};
    padding-bottom:6px;margin:24px 0 14px;letter-spacing:.3px}}
</style>""", unsafe_allow_html=True)

# ═══ HELPERS ═══
def kc_html(v, l, c=None, cls=""):
    s = f'color:{c};' if c else ''
    return f'<div class="kc {cls}"><div class="v" style="{s}">{v}</div><div class="l">{l}</div></div>'

def sh_html(i, t):
    return f'<div class="sh"><span class="i">{i}</span><h3>{t}</h3></div>'

def pills_html(items):
    return '<div class="ir">' + ''.join(f'<span class="ip{" hi" if h else ""}">{t}</span>' for t, h in items) + '</div>'

def fkpi(v, kn):
    if pd.isna(v): return "N/A"
    if kn == "AHT":
        return f"{v:.1f}s"
    elif v <= 1.0:
        return f"{v*100:.1f}%"
    else:
        return f"{v:.1f}"

def get_dir(kn):
    return KPI_DIRECTIONS.get(kn, "Increasing")

def gran_label(val, gr):
    """Format target/stabilization with granularity-aware label."""
    if val is None: return "N/A"
    if gr == "Day": return f"Gün {val}"
    elif gr == "Week": return f"Hafta {val}"
    else: return f"Ay {val}"

def target_label(val, gr, d1_pred, target, direction):
    """Always show the actual period when target is reached."""
    if val is None: return "Ulaşılamadı"
    return gran_label(val, gr)

PF = 'Inter,Segoe UI,sans-serif'
CL = dict(plot_bgcolor='#fff', paper_bgcolor='#fff',
    font=dict(family=PF, color=TP['dark_gray'], size=11), hovermode='x unified',
    legend=dict(orientation='h', yanchor='top', y=-.15, xanchor='center', x=.5,
                font=dict(size=10), bgcolor='rgba(255,255,255,.8)'),
    margin=dict(l=60, r=30, t=50, b=80))

def base_ly(t="", h=500, x="", y=""):
    la = dict(**CL)
    la['title'] = dict(text=t, font=dict(size=13, color=TP['dark_slate'], family=PF), x=.01)
    la['height'] = h
    la['xaxis'] = dict(title=dict(text=x, font=dict(size=11)), gridcolor='#f0f0f5', gridwidth=1,
                       zeroline=False, linecolor=TP['pastel_gray'])
    la['yaxis'] = dict(title=dict(text=y, font=dict(size=11)), gridcolor='#f0f0f5', gridwidth=1,
                       zeroline=False, linecolor=TP['pastel_gray'])
    return la

MC = {'Linear': TP['dark_coral'], 'Logarithmic': TP['light_blue'], 'Power': TP['turquoise'], 'Exponential': TP['violet'], 'Asymptotic': TP['green_flash']}
MO = ['Linear', 'Logarithmic', 'Power', 'Exponential', 'Asymptotic']

# ═══ BOUNDED KPI RANGE DETECTION ═══
def is_bounded_kpi(kpi_name):
    """Detect if KPI is bounded between 0-1 (quality/ratio metrics)."""
    return kpi_name in ["EUC", "BC", "CC", "CSAT", "FCR", "CSAT Agent", "CSAT Service", "CES"]

def clamp_predictions(pred, kpi_name):
    """Clamp predictions to valid KPI range."""
    pred = np.where(np.isfinite(pred), pred, np.nan)
    if is_bounded_kpi(kpi_name):
        pred = np.clip(pred, 0.0, 1.0)
    return pred

# ═══ DATA LOADING ═══
@st.cache_data(ttl=3600)
def load_data(f):
    df = pd.read_excel(f)
    df = df.dropna(subset=['KPI_Value'])
    if 'Interaction_Count' not in df.columns:
        df['Interaction_Count'] = 1
    df['Wave'] = df['Wave'].astype(str)
    m = df.groupby('Full_Name')['working_day_index2'].transform('min')
    df['Relative_Day'] = df['working_day_index2'] - m + 1
    df['Week'] = ((df['working_day_index2'] - m) // 5) + 1
    df['Month'] = ((df['working_day_index2'] - m) // 22) + 1
    def tb(r):
        if r <= 7: return "Week 1"
        elif r <= 14: return "Week 2"
        elif r <= 30: return "Month 1"
        elif r <= 60: return "Month 2"
        elif r <= 90: return "Month 3"
        elif r <= 180: return "Month 4-6"
        elif r <= 365: return "Month 7-12"
        else: return "Year 2+"
    df['Tenure_Bucket'] = df['Relative_Day'].apply(tb)
    return df

# ═══ REGRESSION ENGINE (with bounded Asymptotic model) ═══
def fit_models(x, y, kpi_name=""):
    R = {}
    x = np.array(x, dtype=float); y = np.array(y, dtype=float)
    mk = np.isfinite(x) & np.isfinite(y) & (x > 0); x, y = x[mk], y[mk]
    if len(x) < 3: return R
    bounded = is_bounded_kpi(kpi_name)

    # Linear
    try:
        a, b = np.polyfit(x, y, 1); p = a * x + b
        if bounded: p = np.clip(p, 0, 1)
        r2 = 1 - np.sum((y - p)**2) / np.sum((y - np.mean(y))**2)
        def lin_fn(d, a=a, b=b, bd=bounded):
            r = a*d + b
            return np.clip(r, 0, 1) if bd else r
        R['Linear'] = {'a': a, 'b': b, 'r2': r2, 'pred_fn': lin_fn,
                       'formula': f"KPI = {a:.6g} × Day + {b:.6g}"}
    except: pass

    # Logarithmic
    try:
        a, b = np.polyfit(np.log(x), y, 1); p = a * np.log(x) + b
        if bounded: p = np.clip(p, 0, 1)
        r2 = 1 - np.sum((y - p)**2) / np.sum((y - np.mean(y))**2)
        def log_fn(d, a=a, b=b, bd=bounded):
            r = a*np.log(d) + b
            return np.clip(r, 0, 1) if bd else r
        R['Logarithmic'] = {'a': a, 'b': b, 'r2': r2, 'pred_fn': log_fn,
                            'formula': f"KPI = {a:.6g} × ln(Day) + {b:.6g}"}
    except: pass

    # Power
    try:
        mp = y > 0
        if mp.sum() >= 3:
            bc, la = np.polyfit(np.log(x[mp]), np.log(y[mp]), 1); ac = np.exp(la)
            p = ac * x**bc; v = np.isfinite(p)
            if bounded: p = np.clip(p, 0, 1)
            r2 = 1 - np.sum((y[v] - p[v])**2) / np.sum((y[v] - np.mean(y[v]))**2)
            def pow_fn(d, a=ac, b=bc, bd=bounded):
                r = a * d**b
                return np.clip(r, 0, 1) if bd else r
            R['Power'] = {'a': ac, 'b': bc, 'r2': r2, 'pred_fn': pow_fn,
                          'formula': f"KPI = {ac:.6g} × Day^{bc:.6g}"}
    except: pass

    # Exponential
    try:
        me = y > 0
        if me.sum() >= 3:
            bc, la = np.polyfit(x[me], np.log(y[me]), 1); ac = np.exp(la)
            p = ac * np.exp(bc * x); v = np.isfinite(p) & (p < 1e10)
            if bounded: p[v] = np.clip(p[v], 0, 1)
            if v.sum() > 0:
                r2 = 1 - np.sum((y[v] - p[v])**2) / np.sum((y[v] - np.mean(y[v]))**2)
                def exp_fn(d, a=ac, b=bc, bd=bounded):
                    r = a * np.exp(b*d)
                    return np.clip(r, 0, 1) if bd else r
                R['Exponential'] = {'a': ac, 'b': bc, 'r2': r2, 'pred_fn': exp_fn,
                                    'formula': f"KPI = {ac:.6g} × e^({bc:.6g}×Day)"}
    except: pass

    # Asymptotic (Saturating Growth): y = L - b * exp(-c * x)
    # Naturally bounded — approaches L as x → ∞, never exceeds it
    # Best for quality metrics that plateau near a ceiling
    if len(x) >= 5:
        try:
            y_max = max(np.percentile(y, 95), 0.5)
            y_min = max(np.percentile(y, 5), 0.01)

            def asymp_model(x, L, b, c):
                return L - b * np.exp(-c * x)

            if bounded:
                bounds_lo = [y_max * 0.8, 0.001, 1e-6]
                bounds_hi = [1.0, y_max, 1.0]
            else:
                bounds_lo = [y_min, -np.inf, 1e-6]
                bounds_hi = [y_max * 3, np.inf, 1.0]

            p0 = [min(y_max * 1.05, 1.0) if bounded else y_max * 1.1,
                  max(y_max - y_min, 0.01), 0.01]
            popt, _ = curve_fit(asymp_model, x, y, p0=p0, bounds=(bounds_lo, bounds_hi), maxfev=5000)
            L_fit, b_fit, c_fit = popt
            pred_a = asymp_model(x, L_fit, b_fit, c_fit)
            if bounded: pred_a = np.clip(pred_a, 0, 1)
            r2_a = 1 - np.sum((y - pred_a)**2) / np.sum((y - np.mean(y))**2)

            def asymp_fn(d, L=L_fit, b=b_fit, c=c_fit, bd=bounded):
                r = L - b * np.exp(-c * d)
                return np.clip(r, 0, 1) if bd else r

            R['Asymptotic'] = {'a': L_fit, 'b': b_fit, 'r2': r2_a, 'pred_fn': asymp_fn,
                               'formula': f"KPI = {L_fit:.4f} − {b_fit:.4f} × e^(−{c_fit:.6f}×Day)",
                               'ceiling': L_fit}
        except: pass

    return R

def get_best(R):
    if not R: return None, None
    b = max(R, key=lambda k: R[k]['r2']); return b, R[b]

def find_target_period(fn, tgt, direction, max_val=500):
    """Find the period (day/week/month) when target is reached."""
    try:
        d = np.arange(1, max_val + 1); p = fn(d)
        h = np.where(p <= tgt)[0] if direction == "Decreasing" else np.where(p >= tgt)[0]
        if len(h) > 0: return int(d[h[0]])
    except: pass
    return None

def find_stab_period(fn, max_val=500):
    """Find the period when performance stabilizes (<1% change)."""
    try:
        d = np.arange(2, max_val + 1); p = fn(d); pr = fn(d - 1)
        c = np.abs(p - pr) / np.abs(np.where(pr == 0, 1, pr))
        h = np.where(c < 0.01)[0]
        if len(h) > 0: return int(d[h[0]])
    except: pass
    return None

# ═══ LOAD DATA ═══
with st.sidebar:
    if logo_w:
        st.markdown(f'<div class="sb-logo"><img src="data:image/png;base64,{logo_w}"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-brand">Learning Curve Analytics</div>', unsafe_allow_html=True)
    else:
        st.title("📊 TP Analytics")

try:
    # Auto-detect Excel file in the same directory
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.'
    xlsx_files = glob.glob(os.path.join(script_dir, '*.xlsx'))
    if not xlsx_files:
        xlsx_files = glob.glob('*.xlsx')
    if xlsx_files:
        data_file = xlsx_files[0]
        df = load_data(data_file)
    else:
        st.error("⚠️ Dizinde .xlsx dosyası bulunamadı.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Veri yüklenemedi: {e}")
    st.stop()

# ═══ SIDEBAR FILTERS (Min N removed) ═══
with st.sidebar:
    st.divider()
    kpi_list = sorted(df['KPI_Name'].unique())
    default_kpi_idx = 0
    for preferred in ["EUC", "CSAT", "AHT", "FCR"]:
        if preferred in kpi_list:
            default_kpi_idx = kpi_list.index(preferred)
            break
    sel_kpi = st.selectbox("📌 KPI", kpi_list, index=default_kpi_idx)

    st.markdown('<p style="color:#fff!important;font-size:14px;font-weight:700;margin:8px 0 4px;">🔬 Model Seçimi</p>', unsafe_allow_html=True)
    sel_models = st.multiselect("Modeller", MO, default=MO, label_visibility="collapsed")
    model_mode = st.radio("Birincil Trend", ["Otomatik (En İyi R²)", "Manuel Seçim"], horizontal=True, label_visibility="collapsed")
    primary_choice = st.selectbox("Model", sel_models if sel_models else MO, label_visibility="collapsed") if model_mode == "Manuel Seçim" else None

    st.divider()
    sel_clients = st.multiselect("🏢 Client", sorted(df['Client'].unique()), default=[])
    sel_lobs = st.multiselect("📂 LOB", sorted(df['LOB'].unique()), default=[])
    sel_waves = st.multiselect("🎓 Wave", sorted(df['Wave'].unique()), default=[])
    sel_agents = st.multiselect("👤 Agent", sorted(df['Full_Name'].unique()), default=[])

    st.divider()
    tenure_filter = st.radio("📊 Kıdem Filtresi", ["Tümü", "0–90 Gün", "90+ Gün"], horizontal=True)

    st.divider()
    max_rd = int(df['Relative_Day'].max())
    day_range = st.slider("📅 Gün Aralığı", 1, max_rd, (1, max_rd))

    default_targets = {"AHT": 420.0, "CSAT Agent": 0.80, "CSAT Service": 0.80, "CES": 0.75, "FCR": 0.80,
                       "EUC": 0.90, "BC": 0.90, "CC": 0.95, "CSAT": 0.80}
    target_default = default_targets.get(sel_kpi, float(df[df['KPI_Name'] == sel_kpi]['KPI_Value'].median()))
    target_val = st.number_input("🎯 Hedef KPI", value=target_default, format="%.2f")

    granularity = st.radio("⏱️ Granülarite", ["Day", "Week", "Month"], horizontal=True)

# ═══ FILTER DATA ═══
fdf = df[df['KPI_Name'] == sel_kpi].copy()
if sel_clients: fdf = fdf[fdf['Client'].isin(sel_clients)]
if sel_lobs: fdf = fdf[fdf['LOB'].isin(sel_lobs)]
if sel_waves: fdf = fdf[fdf['Wave'].isin(sel_waves)]
if sel_agents: fdf = fdf[fdf['Full_Name'].isin(sel_agents)]
fdf = fdf[(fdf['Relative_Day'] >= day_range[0]) & (fdf['Relative_Day'] <= day_range[1])]

# Apply tenure filter
if tenure_filter == "0–90 Gün":
    fdf = fdf[fdf['Relative_Day'] <= 90]
elif tenure_filter == "90+ Gün":
    fdf = fdf[fdf['Relative_Day'] > 90]

if fdf.empty:
    st.warning("⚠️ Filtrelerle eşleşen veri yok. Lütfen filtreleri ayarlayın.")
    st.stop()

# ═══ AGGREGATION (Min N = 1, no filter) ═══
gran_col = {'Day': 'Relative_Day', 'Week': 'Week', 'Month': 'Month'}[granularity]
agg = fdf.groupby(gran_col).agg(
    Avg_KPI=('KPI_Value', 'mean'), Median_KPI=('KPI_Value', 'median'),
    Std_Dev=('KPI_Value', 'std'), Min_KPI=('KPI_Value', 'min'), Max_KPI=('KPI_Value', 'max'),
    P25=('KPI_Value', lambda x: np.nanpercentile(x, 25)),
    P75=('KPI_Value', lambda x: np.nanpercentile(x, 75)),
    N_Agents=('Full_Name', 'nunique'),
    Total_Int=('Interaction_Count', 'sum'),
).reset_index().sort_values(gran_col)

if agg.empty:
    st.warning("⚠️ Veri bulunamadı.")
    st.stop()

# ═══ KPI DIRECTION ═══
kpi_dir = get_dir(sel_kpi)

# ═══ REGRESSION ═══
x_data = agg[gran_col].values
y_data = agg['Avg_KPI'].values
all_models = fit_models(x_data, y_data, sel_kpi)
models = {k: v for k, v in all_models.items() if k in sel_models}
auto_best_name, auto_best_model = get_best(models)

if model_mode == "Manuel Seçim" and primary_choice in models:
    best_name, best_mod = primary_choice, models[primary_choice]
else:
    best_name, best_mod = auto_best_name, auto_best_model

# Smooth predictions
x_smooth = np.linspace(max(x_data.min(), 1), x_data.max(), 300)
model_preds = {}
for mn, mi in models.items():
    try:
        p = mi['pred_fn'](x_smooth)
        model_preds[mn] = np.where(np.isfinite(p), p, np.nan)
    except:
        model_preds[mn] = np.full_like(x_smooth, np.nan)

# Confidence band
if best_mod:
    best_pred_data = best_mod['pred_fn'](x_data)
    residuals = y_data - best_pred_data
    sigma = np.nanstd(residuals)
    best_smooth = model_preds.get(best_name, np.full_like(x_smooth, np.nan))
    upper_band = best_smooth + sigma
    lower_band = best_smooth - sigma
else:
    residuals = np.zeros_like(y_data); sigma = 0
    upper_band = lower_band = best_smooth = np.full_like(x_smooth, np.nan)

# Target & Stabilization — computed on GRANULARITY axis (not always days)
target_period = find_target_period(best_mod['pred_fn'], target_val, kpi_dir, int(x_data.max() * 2)) if best_mod else None
stab_period = find_stab_period(best_mod['pred_fn'], int(x_data.max() * 2)) if best_mod else None

# Day 1 predicted
day1_pred = best_mod['pred_fn'](1) if best_mod else np.nan
current_level = agg['Avg_KPI'].tail(30).mean()

# First 7 / Day 90
first7 = fdf[fdf['Relative_Day'] <= 7]['KPI_Value'].mean()
day90 = fdf[(fdf['Relative_Day'] >= 85) & (fdf['Relative_Day'] <= 95)]['KPI_Value'].mean()

if not pd.isna(first7) and first7 != 0 and not pd.isna(day90):
    improvement = ((first7 - day90) / first7 * 100) if kpi_dir == "Decreasing" else ((day90 - first7) / first7 * 100)
else:
    improvement = np.nan

x_label = {"Day": "Çalışma Günü", "Week": "Hafta", "Month": "Ay"}[granularity]
y_label = sel_kpi + (" (saniye)" if sel_kpi == "AHT" else " (oran)")

# ═══ TABS ═══
t1, t2, t3, t4, t5 = st.tabs(["📊 Ana Dashboard", "👤 Agent Analizi", "🏢 Wave Karşılaştırma", "📈 Glide Path", "📖 Glossary"])

# ═══════════════════════════════════════════
# TAB 1: MAIN DASHBOARD
# ═══════════════════════════════════════════
with t1:
    dir_arrow = "↘" if kpi_dir == "Decreasing" else "↗"
    st.markdown(f'''<div class="tp-hdr"><div class="ts">{logo_img}<div>
        <h1>LEARNING CURVE PERFORMANS DASHBOARD</h1>
        <div class="sub">Yeni İşe Alım Performans Analitiği · Regresyon Analizi</div></div></div>
        <div style="display:flex;align-items:center;gap:8px">
        <span class="badge">{sel_kpi}</span><span class="dir">{dir_arrow} {kpi_dir}</span></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="al"></div>', unsafe_allow_html=True)

    st.markdown(pills_html([
        (f"Agent: {fdf['Full_Name'].nunique()}", False),
        (f"Wave: {fdf['Wave'].nunique()}", False),
        (f"Veri: {len(agg)} nokta", False),
        (f"Hedef: {fkpi(target_val, sel_kpi)}", True),
        (f"En İyi: {best_name}" if best_name else "—", True),
    ]), unsafe_allow_html=True)

    # KPI Cards — granularity-aware labels
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(kc_html(fkpi(day1_pred, sel_kpi), "Başlangıç (Day 1)", cls="tq"), unsafe_allow_html=True)
    with c2:
        st.markdown(kc_html(fkpi(current_level, sel_kpi), "Güncel Performans"), unsafe_allow_html=True)
    with c3:
        tgt_label = target_label(target_period, granularity, day1_pred, target_val, kpi_dir)
        tgt_color = TP['green_flash'] if target_period else TP['dark_coral']
        st.markdown(kc_html(tgt_label, "Hedefe Ne Zaman?", tgt_color, "gn"), unsafe_allow_html=True)
    with c4:
        r2_str = f"{best_mod['r2']:.4f}" if best_mod else "N/A"
        st.markdown(kc_html(r2_str, f"En İyi R² ({best_name or '—'})", cls="vi"), unsafe_allow_html=True)
    with c5:
        imp_str = f"{improvement:+.1f}%" if not pd.isna(improvement) else "N/A"
        imp_col = TP['green_flash'] if not pd.isna(improvement) and improvement > 0 else TP['dark_coral']
        st.markdown(kc_html(imp_str, "İyileşme (7g→90g)", imp_col, "ig"), unsafe_allow_html=True)
    with c6:
        stab_label = gran_label(stab_period, granularity)
        st.markdown(kc_html(stab_label, "Stabilizasyon", cls="co"), unsafe_allow_html=True)

    st.markdown("")

    # Main Chart — Full Width
    st.markdown(sh_html("📈", "Tüm Modeller Karşılaştırma"), unsafe_allow_html=True)
    fig = go.Figure()
    if best_mod:
        fig.add_trace(go.Scatter(
            x=np.concatenate([x_smooth, x_smooth[::-1]]),
            y=np.concatenate([upper_band, lower_band[::-1]]),
            fill='toself', fillcolor='rgba(132,141,173,.1)',
            line=dict(color='rgba(0,0,0,0)'), showlegend=True, name='±1σ Güven Bandı', hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=agg[gran_col], y=agg['Avg_KPI'], mode='markers',
        marker=dict(color=TP['dark_slate'], size=6, opacity=.45), name='Gerçek Ort.',
        customdata=agg['N_Agents'],
        hovertemplate=f'{x_label}: %{{x}}<br>Ort: %{{y:.2f}}<br>N=%{{customdata}}<extra></extra>'))
    for mn_ in MO:
        if mn_ not in model_preds: continue
        is_best = (mn_ == best_name)
        fig.add_trace(go.Scatter(x=x_smooth, y=model_preds[mn_], mode='lines',
            line=dict(color=MC[mn_], width=3.5 if is_best else 1.5, dash=None if is_best else 'dot'),
            opacity=1.0 if is_best else .55,
            name=f"{'★ ' if is_best else ''}{mn_} (R²={models[mn_]['r2']:.4f})"))

    # Forecast extension — extrapolate best model 50% beyond data with clamping
    if best_mod:
        x_max = x_data.max()
        x_forecast = np.linspace(x_max, x_max * 1.5, 100)
        y_forecast = best_mod['pred_fn'](x_forecast)
        y_forecast = clamp_predictions(y_forecast, sel_kpi)
        fig.add_trace(go.Scatter(x=x_forecast, y=y_forecast, mode='lines',
            line=dict(color=MC.get(best_name, TP['blue']), width=2.5, dash='dashdot'),
            opacity=0.6, name=f'📊 Tahmin ({best_name})'))
        # Forecast confidence band (clamped)
        fc_upper = clamp_predictions(y_forecast + sigma * 1.2, sel_kpi)
        fc_lower = clamp_predictions(y_forecast - sigma * 1.2, sel_kpi)
        fig.add_trace(go.Scatter(
            x=np.concatenate([x_forecast, x_forecast[::-1]]),
            y=np.concatenate([fc_upper, fc_lower[::-1]]),
            fill='toself', fillcolor='rgba(132,141,173,.06)',
            line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))

    fig.add_hline(y=target_val, line_dash="dash", line_color=TP['dark_gray'], line_width=1.5,
        annotation_text=f"Hedef: {fkpi(target_val, sel_kpi)}", annotation_position="top right",
        annotation_font=dict(size=10))
    if target_period and best_mod:
        fig.add_vline(x=target_period, line_dash="dot", line_color=TP['green_flash'], line_width=1,
            annotation_text=gran_label(target_period, granularity),
            annotation_font=dict(size=9, color=TP['green_flash']))
    title = f"<b>{sel_kpi} Öğrenme Eğrisi & Tahmin</b> — En İyi: {best_name} (R²={best_mod['r2']:.4f})" if best_mod else f"<b>{sel_kpi} Öğrenme Eğrisi</b>"
    fig.update_layout(**base_ly(title, 560, x_label, y_label))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Bottom analysis row
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(sh_html("📉", "Residual Analizi"), unsafe_allow_html=True)
        if best_mod:
            fig_r = go.Figure()
            res_colors = [TP['blue'] if r >= 0 else TP['dark_coral'] for r in residuals]
            fig_r.add_trace(go.Scatter(x=x_data, y=residuals, mode='markers',
                marker=dict(color=res_colors, size=5, opacity=.6), name='Residual'))
            fig_r.add_hline(y=0, line_color=TP['dark_gray'])
            fig_r.add_hline(y=sigma, line_dash="dot", line_color=TP['light_gray'])
            fig_r.add_hline(y=-sigma, line_dash="dot", line_color=TP['light_gray'])
            fig_r.update_layout(**base_ly("", 360, x_label, "Residual"))
            st.plotly_chart(fig_r, use_container_width=True)

    with b2:
        st.markdown(sh_html("🏆", "Model R² Karşılaştırma"), unsafe_allow_html=True)
        if models:
            m_names = [m for m in MO if m in models]
            m_r2s = [models[m]['r2'] for m in m_names]
            bar_cols = [TP['blue'] if m == best_name else TP['pastel_slate'] for m in m_names]
            fig_r2 = go.Figure(go.Bar(y=m_names, x=m_r2s, orientation='h',
                marker=dict(color=bar_cols),
                text=[f"<b>{r:.4f}</b>" if m == best_name else f"{r:.4f}" for r, m in zip(m_r2s, m_names)],
                textposition='inside', textfont=dict(color='white', size=12)))
            fig_r2.update_layout(**base_ly("", 360, "R²", ""))
            fig_r2.update_layout(xaxis=dict(range=[0, max(m_r2s) * 1.15] if m_r2s else [0, 1]))
            st.plotly_chart(fig_r2, use_container_width=True)

    with b3:
        st.markdown(sh_html("📋", "Model Detayları"), unsafe_allow_html=True)
        if models:
            rows = []
            for mn_ in MO:
                if mn_ not in models: continue
                mi = models[mn_]
                rows.append({'Model': mn_, 'Formül': mi['formula'],
                    'a': f"{mi['a']:.6g}", 'b': f"{mi['b']:.6g}", 'R²': f"{mi['r2']:.4f}",
                    'Durum': '⭐ EN İYİ' if mn_ == best_name else '—'})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=360)

# ═══════════════════════════════════════════
# TAB 2: AGENT ANALYSIS
# ═══════════════════════════════════════════
with t2:
    st.markdown(f'''<div class="tp-hdr"><div class="ts">{logo_img}<div>
        <h1>AGENT PERFORMANS ANALİZİ</h1>
        <div class="sub">Bireysel Öğrenme Eğrisi vs Genel Trend</div></div></div>
        <span class="badge">{sel_kpi} · {kpi_dir}</span></div>''', unsafe_allow_html=True)
    st.markdown('<div class="al"></div>', unsafe_allow_html=True)

    agent_list = sorted(fdf['Full_Name'].unique())
    if not agent_list:
        st.warning("Filtrelenen veride agent bulunamadı.")
    else:
        sel_agent = st.selectbox("Agent Seçin", agent_list)
        adf = fdf[fdf['Full_Name'] == sel_agent].sort_values('Relative_Day')

        agent_wave = adf['Wave'].iloc[0] if len(adf) > 0 else "N/A"
        agent_days = int(adf['Relative_Day'].max()) if len(adf) > 0 else 0
        agent_avg = adf['KPI_Value'].mean()

        # vs trend calculation
        if best_mod and len(adf) > 0:
            atv = best_mod['pred_fn'](adf['Relative_Day'].values.astype(float))
            vm = np.isfinite(atv)
            trend_avg = np.nanmean(atv[vm]) if vm.sum() > 0 else agent_avg
            vs_trend = ((agent_avg - trend_avg) / abs(trend_avg) * 100) if trend_avg != 0 else 0
        else:
            vs_trend = 0

        # Direction-aware "is better"
        is_better = (kpi_dir == "Decreasing" and vs_trend < 0) or (kpi_dir == "Increasing" and vs_trend > 0)
        vs_color = TP['green_flash'] if is_better else TP['dark_coral']
        vs_label = "İyi" if is_better else "Kötü"

        a1, a2, a3, a4, a5 = st.columns(5)
        with a1: st.markdown(kc_html(sel_agent, "Agent Adı", cls="tq"), unsafe_allow_html=True)
        with a2: st.markdown(kc_html(agent_wave, "Wave", cls="vi"), unsafe_allow_html=True)
        with a3: st.markdown(kc_html(f"{agent_days} gün", "Kıdem"), unsafe_allow_html=True)
        with a4: st.markdown(kc_html(fkpi(agent_avg, sel_kpi), "Agent Ort. KPI", cls="ig"), unsafe_allow_html=True)
        with a5: st.markdown(kc_html(f"{vs_trend:+.1f}% ({vs_label})", "vs Trend", vs_color,
                    "gn" if is_better else "co"), unsafe_allow_html=True)

        st.markdown("")
        st.markdown(sh_html("📈", f"{sel_agent} — Bireysel vs Trend"), unsafe_allow_html=True)
        fig_ag = go.Figure()
        if best_mod:
            xr = np.linspace(1, max(adf['Relative_Day'].max(), x_data.max()), 200)
            tl = best_mod['pred_fn'](xr)
            fig_ag.add_trace(go.Scatter(
                x=np.concatenate([xr, xr[::-1]]),
                y=np.concatenate([tl + sigma, (tl - sigma)[::-1]]),
                fill='toself', fillcolor='rgba(132,141,173,.08)',
                line=dict(color='rgba(0,0,0,0)'), name='±1σ Band', hoverinfo='skip'))
            fig_ag.add_trace(go.Scatter(x=xr, y=tl, mode='lines',
                line=dict(color=TP['blue'], width=2.5), name=f'Genel Trend ({best_name})'))
        fig_ag.add_trace(go.Scatter(x=adf['Relative_Day'], y=adf['KPI_Value'], mode='markers',
            marker=dict(color=TP['violet'], size=7, line=dict(width=1, color='white')), name=sel_agent))
        fig_ag.add_hline(y=target_val, line_dash="dash", line_color=TP['dark_gray'], annotation_text="Hedef")
        fig_ag.update_layout(**base_ly("", 480, "Çalışma Günü", y_label))
        st.plotly_chart(fig_ag, use_container_width=True)

        # Detail table + Progression
        col_tbl, col_prog = st.columns([3, 2])
        with col_tbl:
            st.markdown(sh_html("📋", "Günlük Performans Detayı"), unsafe_allow_html=True)
            if best_mod and len(adf) > 0:
                tbl = adf[['Relative_Day', 'KPI_Value']].copy()
                if 'Interaction_Count' in adf.columns and adf['Interaction_Count'].notna().any():
                    tbl['Etkileşim'] = adf['Interaction_Count'].values
                tbl['Trend'] = best_mod['pred_fn'](tbl['Relative_Day'].values.astype(float))
                tbl['Fark'] = tbl['KPI_Value'] - tbl['Trend']
                tbl['Fark%'] = np.where(tbl['Trend'] != 0, tbl['Fark'] / np.abs(tbl['Trend']) * 100, 0)
                tbl['Durum'] = tbl['Fark'].apply(
                    lambda d: '🟢' if (d <= 0 if kpi_dir == "Decreasing" else d >= 0) else '🔴')
                st.dataframe(tbl.round(2), use_container_width=True, hide_index=True, height=400)

        with col_prog:
            st.markdown(sh_html("📊", "Kıdem İlerlemesi"), unsafe_allow_html=True)
            af7 = adf[adf['Relative_Day'] <= 7]['KPI_Value'].mean()
            al7 = adf.tail(7)['KPI_Value'].mean()

            # ★ FIX: Direction-aware delta color for st.metric
            if not pd.isna(al7) and not pd.isna(af7):
                delta_val = al7 - af7
                # For Decreasing KPI: increase is BAD → invert so st.metric shows red
                if kpi_dir == "Decreasing":
                    delta_display = f"{delta_val:+.1f}"
                    # st.metric shows green for positive, red for negative
                    # For AHT: increase = bad, so we invert: show negative delta for increase
                    delta_inverted = -delta_val
                    delta_str = f"{delta_inverted:+.1f}"
                else:
                    delta_str = f"{delta_val:+.1f}"
            else:
                delta_str = "0"

            m1, m2 = st.columns(2)
            with m1: st.metric("İlk 7 Gün", fkpi(af7, sel_kpi))
            with m2: st.metric("Son 7 Gün", fkpi(al7, sel_kpi), delta=delta_str)

            # Tenure bucket chart
            tb_order = ["Week 1", "Week 2", "Month 1", "Month 2", "Month 3", "Month 4-6", "Month 7-12", "Year 2+"]
            ta = adf.groupby('Tenure_Bucket')['KPI_Value'].mean().reset_index()
            ta['Tenure_Bucket'] = pd.Categorical(ta['Tenure_Bucket'], categories=tb_order, ordered=True)
            ta = ta.sort_values('Tenure_Bucket')
            ot = fdf.groupby('Tenure_Bucket')['KPI_Value'].mean().reset_index()
            ot['Tenure_Bucket'] = pd.Categorical(ot['Tenure_Bucket'], categories=tb_order, ordered=True)
            ot = ot.sort_values('Tenure_Bucket')

            fig_tb = go.Figure()
            fig_tb.add_trace(go.Bar(x=ta['Tenure_Bucket'].astype(str), y=ta['KPI_Value'],
                marker=dict(color=TP['violet'], opacity=.7), name='Agent'))
            fig_tb.add_trace(go.Scatter(x=ot['Tenure_Bucket'].astype(str), y=ot['KPI_Value'],
                mode='lines+markers', line=dict(color=TP['dark_coral'], width=2), name='Genel'))
            fig_tb.update_layout(**base_ly("", 300, "", y_label))
            st.plotly_chart(fig_tb, use_container_width=True)

# ═══════════════════════════════════════════
# TAB 3: WAVE COMPARISON
# ═══════════════════════════════════════════
with t3:
    st.markdown(f'''<div class="tp-hdr"><div class="ts">{logo_img}<div>
        <h1>WAVE & LOB KARŞILAŞTIRMA</h1>
        <div class="sub">Kohort Benchmarking · Verimlilik Analizi</div></div></div>
        <span class="badge">{sel_kpi} · {fdf["Wave"].nunique()} Wave</span></div>''', unsafe_allow_html=True)
    st.markdown('<div class="al"></div>', unsafe_allow_html=True)

    st.markdown(sh_html("📋", "Wave Özet Tablosu"), unsafe_allow_html=True)
    wave_summaries = []
    for wave in sorted(fdf['Wave'].unique()):
        wdf = fdf[fdf['Wave'] == wave]
        w_agents = wdf['Full_Name'].nunique()
        w_start = wdf['Action_Date'].min()
        d1 = wdf[wdf['Relative_Day'] <= 7]['KPI_Value'].mean()
        d30 = wdf[(wdf['Relative_Day'] >= 27) & (wdf['Relative_Day'] <= 33)]['KPI_Value'].mean()
        d60 = wdf[(wdf['Relative_Day'] >= 57) & (wdf['Relative_Day'] <= 63)]['KPI_Value'].mean()
        d90_ = wdf[(wdf['Relative_Day'] >= 87) & (wdf['Relative_Day'] <= 93)]['KPI_Value'].mean()

        if not pd.isna(d1) and d1 != 0 and not pd.isna(d90_):
            imp = ((d1 - d90_) / d1 * 100) if kpi_dir == "Decreasing" else ((d90_ - d1) / d1 * 100)
        else: imp = np.nan

        wag = wdf.groupby('Relative_Day').agg(A=('KPI_Value', 'mean'), N=('Full_Name', 'nunique')).reset_index()
        wag = wag[wag['N'] >= 2]
        wm = fit_models(wag['Relative_Day'].values, wag['A'].values, sel_kpi)
        wbn, wb = get_best(wm)

        wave_summaries.append({
            'Wave': wave, 'Agent': w_agents,
            'Başlangıç': w_start.strftime('%Y-%m-%d') if pd.notna(w_start) else 'N/A',
            'Gün 1-7': round(d1, 2) if not pd.isna(d1) else None,
            'Gün 30': round(d30, 2) if not pd.isna(d30) else None,
            'Gün 60': round(d60, 2) if not pd.isna(d60) else None,
            'Gün 90': round(d90_, 2) if not pd.isna(d90_) else None,
            'İyileşme%': round(imp, 1) if not pd.isna(imp) else None,
            'R²': round(wb['r2'], 4) if wb else None,
            'Stab.': find_stab_period(wb['pred_fn']) if wb else None,
        })

    ws_df = pd.DataFrame(wave_summaries)
    st.dataframe(ws_df, use_container_width=True, hide_index=True)
    st.divider()

    col_ov, col_ef = st.columns(2)
    with col_ov:
        st.markdown(sh_html("📈", "Wave Öğrenme Eğrileri"), unsafe_allow_html=True)
        top_w = ws_df.sort_values('Agent', ascending=False).head(10)['Wave'].tolist()
        scw = st.multiselect("Wave Seçin", fdf['Wave'].unique(), default=top_w[:5], key='wc')
        if scw:
            wp = [TP['blue'], TP['dark_coral'], TP['turquoise'], TP['violet'], TP['indigo'],
                  TP['light_blue'], TP['muted_violet'], TP['burgundy'], TP['green_flash'], TP['dark_slate']]
            fw = go.Figure()
            for i, w in enumerate(scw[:10]):
                wd = fdf[fdf['Wave'] == w].groupby('Relative_Day')['KPI_Value'].mean().reset_index().sort_values('Relative_Day')
                wd['S'] = wd['KPI_Value'].rolling(5, min_periods=1, center=True).mean() if len(wd) > 5 else wd['KPI_Value']
                fw.add_trace(go.Scatter(x=wd['Relative_Day'], y=wd['S'], mode='lines',
                    line=dict(color=wp[i % len(wp)], width=2.5), name=w))
            fw.add_hline(y=target_val, line_dash="dash", line_color=TP['dark_gray'])
            fw.update_layout(**base_ly("", 450, "Çalışma Günü", y_label))
            st.plotly_chart(fw, use_container_width=True)

    with col_ef:
        st.markdown(sh_html("🎯", "Wave Verimlilik"), unsafe_allow_html=True)
        edf = ws_df.dropna(subset=['Stab.', 'Gün 90']).copy()
        if not edf.empty:
            cs = 'RdYlGn' if kpi_dir == "Increasing" else 'RdYlGn_r'
            fe = go.Figure(go.Scatter(
                x=edf['Stab.'], y=edf['Gün 90'], mode='markers+text',
                marker=dict(size=edf['Agent'].clip(3, 30)*2.5+8, color=edf['İyileşme%'],
                    colorscale=cs, showscale=True, line=dict(width=1, color='white'),
                    colorbar=dict(title='İyileşme%', thickness=12)),
                text=edf['Wave'], textposition='top center', textfont=dict(size=8)))
            fe.add_hline(y=edf['Gün 90'].median(), line_dash="dot", line_color=TP['light_gray'])
            fe.add_vline(x=edf['Stab.'].median(), line_dash="dot", line_color=TP['light_gray'])
            fe.update_layout(**base_ly("", 450, "Stabilizasyon Günü", "Gün 90 Ort."))
            st.plotly_chart(fe, use_container_width=True)
        else:
            st.info("Yeterli veri yok.")

    st.divider()
    st.markdown(sh_html("🗺️", "Wave × Kıdem Isı Haritası"), unsafe_allow_html=True)
    tb_order = ["Week 1", "Week 2", "Month 1", "Month 2", "Month 3", "Month 4-6", "Month 7-12", "Year 2+"]
    hm = fdf.groupby(['Wave', 'Tenure_Bucket'])['KPI_Value'].mean().reset_index()
    hp = hm.pivot_table(index='Wave', columns='Tenure_Bucket', values='KPI_Value')
    hp = hp.reindex(columns=[c for c in tb_order if c in hp.columns])
    if not hp.empty:
        cs = 'RdYlGn_r' if kpi_dir == "Decreasing" else 'RdYlGn'
        fig_hm = go.Figure(go.Heatmap(
            z=hp.values, x=hp.columns.tolist(), y=hp.index.tolist(), colorscale=cs,
            text=np.where(np.isnan(hp.values), '', np.round(hp.values, 1).astype(str)),
            texttemplate='%{text}', textfont=dict(size=9), colorbar=dict(thickness=10)))
        fig_hm.update_layout(**base_ly("", max(300, len(hp)*20+120), "", ""))
        fig_hm.update_layout(yaxis=dict(dtick=1, tickfont=dict(size=9)))
        st.plotly_chart(fig_hm, use_container_width=True)

# ═══════════════════════════════════════════
# TAB 4: GLIDE PATH & FORECAST
# ═══════════════════════════════════════════
with t4:
    st.markdown(f'''<div class="tp-hdr"><div class="ts">{logo_img}<div>
        <h1>GLIDE PATH, TAHMİN & İLERLEME</h1>
        <div class="sub">Gelecek Projeksiyon · Agent Tahminleri · Kilometre Taşları</div></div></div>
        <span class="badge">{sel_kpi}</span></div>''', unsafe_allow_html=True)
    st.markdown('<div class="al"></div>', unsafe_allow_html=True)

    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.markdown(kc_html(fkpi(first7, sel_kpi), "Başlangıç (Gün 1-7)", cls="co"), unsafe_allow_html=True)
    with g2:
        st.markdown(kc_html(fkpi(day90, sel_kpi), "Gün 90", cls="tq"), unsafe_allow_html=True)
    with g3:
        imp_s = f"{improvement:+.1f}%" if not pd.isna(improvement) else "N/A"
        imp_c = TP['green_flash'] if not pd.isna(improvement) and improvement > 0 else TP['dark_coral']
        st.markdown(kc_html(imp_s, "Toplam İyileşme", imp_c, "gn"), unsafe_allow_html=True)
    with g4:
        st.markdown(kc_html(fkpi(current_level, sel_kpi), "Güncel (Son 30g)", cls="vi"), unsafe_allow_html=True)

    st.divider()

    # ── FORECAST CHART: Future projection ──
    st.markdown(sh_html("🔮", "Geleceğe Yönelik Tahmin (Forecast)"), unsafe_allow_html=True)
    if best_mod:
        x_max = x_data.max()
        forecast_extend = st.slider("Tahmin uzatma oranı (%)", 20, 100, 50, 10, key='forecast_pct')
        x_fc = np.linspace(1, x_max * (1 + forecast_extend / 100), 400)
        x_hist = x_fc[x_fc <= x_max]
        x_future = x_fc[x_fc > x_max]

        fig_fc = go.Figure()

        # Historical confidence band (clamped)
        y_hist = best_mod['pred_fn'](x_hist)
        hist_upper = clamp_predictions(y_hist + sigma, sel_kpi)
        hist_lower = clamp_predictions(y_hist - sigma, sel_kpi)
        fig_fc.add_trace(go.Scatter(
            x=np.concatenate([x_hist, x_hist[::-1]]),
            y=np.concatenate([hist_upper, hist_lower[::-1]]),
            fill='toself', fillcolor='rgba(48,71,176,.08)',
            line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))

        # Historical data points
        fig_fc.add_trace(go.Scatter(x=agg[gran_col], y=agg['Avg_KPI'], mode='markers',
            marker=dict(color=TP['dark_slate'], size=5, opacity=.4), name='Gerçek Veri'))

        # Historical trend (clamped)
        y_hist_clamped = clamp_predictions(y_hist, sel_kpi)
        fig_fc.add_trace(go.Scatter(x=x_hist, y=y_hist_clamped, mode='lines',
            line=dict(color=TP['blue'], width=3), name=f'Trend ({best_name})'))

        # FORECAST zone (clamped)
        y_future = clamp_predictions(best_mod['pred_fn'](x_future), sel_kpi)

        # Forecast confidence band (wider — 1.5σ, clamped)
        fc_upper = clamp_predictions(y_future + sigma * 1.5, sel_kpi)
        fc_lower = clamp_predictions(y_future - sigma * 1.5, sel_kpi)
        fig_fc.add_trace(go.Scatter(
            x=np.concatenate([x_future, x_future[::-1]]),
            y=np.concatenate([fc_upper, fc_lower[::-1]]),
            fill='toself', fillcolor='rgba(0,175,155,.08)',
            line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))

        # Forecast line
        fig_fc.add_trace(go.Scatter(x=x_future, y=y_future, mode='lines',
            line=dict(color=TP['turquoise'], width=3, dash='dash'), name='📊 Tahmin (Forecast)'))

        # Divider line between historical and forecast
        fig_fc.add_vline(x=x_max, line_dash="dot", line_color=TP['gray'], line_width=1,
            annotation_text="← Gerçek | Tahmin →", annotation_position="top",
            annotation_font=dict(size=9, color=TP['gray']))

        # Target
        fig_fc.add_hline(y=target_val, line_dash="dash", line_color=TP['dark_gray'], line_width=1.5,
            annotation_text=f"Hedef: {fkpi(target_val, sel_kpi)}", annotation_font=dict(size=10))

        # Find where forecast hits target
        fc_target = find_target_period(best_mod['pred_fn'], target_val, kpi_dir, int(x_max * (1 + forecast_extend / 100)))
        if fc_target and fc_target > x_max:
            fig_fc.add_vline(x=fc_target, line_dash="dot", line_color=TP['green_flash'], line_width=1.5,
                annotation_text=f"Tahmini Hedef: {gran_label(fc_target, granularity)}",
                annotation_font=dict(size=10, color=TP['green_flash']))

        fig_fc.update_layout(**base_ly(
            f"<b>{sel_kpi} — Gerçek Veri & Gelecek Tahmin</b>", 500, x_label, y_label))
        st.plotly_chart(fig_fc, use_container_width=True)
    else:
        st.info("Tahmin için yeterli model verisi yok.")

    st.divider()

    # ── AGENT-LEVEL FORECAST TABLE ──
    st.markdown(sh_html("🎯", "Agent Bazlı Hedef Tahmini"), unsafe_allow_html=True)
    if best_mod:
        agent_forecasts = []
        for agent in sorted(fdf['Full_Name'].unique()):
            adf_fc = fdf[fdf['Full_Name'] == agent]
            a_wave = adf_fc['Wave'].iloc[0] if len(adf_fc) > 0 else "N/A"
            a_days = int(adf_fc['Relative_Day'].max()) if len(adf_fc) > 0 else 0
            a_avg = adf_fc['KPI_Value'].mean()
            a_last = adf_fc.tail(5)['KPI_Value'].mean()

            # Fit individual model for this agent
            a_agg = adf_fc.groupby('Relative_Day')['KPI_Value'].mean().reset_index()
            if len(a_agg) >= 5:
                a_models = fit_models(a_agg['Relative_Day'].values, a_agg['KPI_Value'].values, sel_kpi)
                a_bn, a_bm = get_best(a_models)
                if a_bm:
                    a_target_day = find_target_period(a_bm['pred_fn'], target_val, kpi_dir, 1000)
                    a_r2 = a_bm['r2']
                else:
                    a_target_day = None; a_r2 = None
            else:
                a_target_day = None; a_r2 = None; a_bn = None

            # Status
            if a_target_day and a_target_day <= a_days:
                status = "✅ Ulaştı"
            elif a_target_day:
                status = f"📊 Tahmini: Gün {a_target_day}"
            else:
                status = "⏳ Belirsiz"

            # Current vs Target gap
            if kpi_dir == "Decreasing":
                gap = a_last - target_val if not pd.isna(a_last) else np.nan
                at_target = not pd.isna(a_last) and a_last <= target_val
            else:
                gap = target_val - a_last if not pd.isna(a_last) else np.nan
                at_target = not pd.isna(a_last) and a_last >= target_val

            agent_forecasts.append({
                'Agent': agent,
                'Wave': a_wave,
                'Kıdem (Gün)': a_days,
                f'Ort. {sel_kpi}': round(a_avg, 2) if not pd.isna(a_avg) else None,
                f'Son 5g {sel_kpi}': round(a_last, 2) if not pd.isna(a_last) else None,
                'Hedefe Fark': round(abs(gap), 2) if not pd.isna(gap) else None,
                'Tahmini Hedef Günü': a_target_day if a_target_day else "—",
                'R²': round(a_r2, 4) if a_r2 else None,
                'Durum': "✅ Hedefte" if at_target else status,
            })

        fc_df = pd.DataFrame(agent_forecasts)
        st.dataframe(fc_df, use_container_width=True, hide_index=True, height=450)

        # Summary stats
        at_target_count = sum(1 for r in agent_forecasts if "✅" in r['Durum'])
        forecast_count = sum(1 for r in agent_forecasts if "📊" in r['Durum'])
        uncertain_count = sum(1 for r in agent_forecasts if "⏳" in r['Durum'])

        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1: st.markdown(kc_html(f"{len(agent_forecasts)}", "Toplam Agent", cls="tq"), unsafe_allow_html=True)
        with sc2: st.markdown(kc_html(f"{at_target_count}", "Hedefte ✅", TP['green_flash'], "gn"), unsafe_allow_html=True)
        with sc3: st.markdown(kc_html(f"{forecast_count}", "Tahminli 📊", TP['light_blue'], "vi"), unsafe_allow_html=True)
        with sc4: st.markdown(kc_html(f"{uncertain_count}", "Belirsiz ⏳", TP['dark_coral'], "co"), unsafe_allow_html=True)
    else:
        st.info("Tahmin için yeterli model yok.")

    st.divider()

    # ── PROGRESSION TABLE ──
    st.markdown(sh_html("📋", "İlerleme Kontrol Noktaları"), unsafe_allow_html=True)

    periods = [("Hafta 1", 1, 5), ("Hafta 2", 6, 10), ("Hafta 3", 11, 15), ("Hafta 4", 16, 22),
               ("Ay 1", 1, 22), ("Ay 2", 23, 44), ("Ay 3", 45, 66), ("Ay 4-6", 67, 132)]
    prog_rows = []
    for pname, ds, de in periods:
        pd_ = fdf[(fdf['Relative_Day'] >= ds) & (fdf['Relative_Day'] <= de)]
        actual = pd_['KPI_Value'].mean() if len(pd_) > 0 else np.nan
        n_ag = pd_['Full_Name'].nunique() if len(pd_) > 0 else 0

        if best_mod:
            try: exp_kpi = float(best_mod['pred_fn']((ds + de) / 2))
            except: exp_kpi = np.nan
            exp_range = f"{exp_kpi - sigma:.1f} – {exp_kpi + sigma:.1f}" if not pd.isna(exp_kpi) else "N/A"
        else:
            exp_kpi = np.nan; exp_range = "N/A"

        gap = actual - target_val if not pd.isna(actual) else np.nan

        if pd.isna(actual) or n_ag == 0: status = "—"
        elif (kpi_dir == "Decreasing" and actual <= target_val) or (kpi_dir == "Increasing" and actual >= target_val):
            status = "✅ Hedefte"
        elif best_mod and not pd.isna(exp_kpi) and abs(actual - exp_kpi) <= sigma:
            status = "⚠️ Band İçi"
        else: status = "❌ Sapma"

        prog_rows.append({'Dönem': pname, 'Günler': f"{ds}–{de}",
            'Beklenen': round(exp_kpi, 2) if not pd.isna(exp_kpi) else None,
            'Aralık (±1σ)': exp_range, 'Gerçek': round(actual, 2) if not pd.isna(actual) else None,
            'N': n_ag, 'Fark': round(gap, 2) if not pd.isna(gap) else None, 'Durum': status})

    st.dataframe(pd.DataFrame(prog_rows), use_container_width=True, hide_index=True)
    st.divider()

    col_t, col_c = st.columns(2)
    with col_t:
        st.markdown(sh_html("📈", "Haftalık Trend"), unsafe_allow_html=True)
        wa = fdf.groupby('Week').agg(A=('KPI_Value', 'mean'), N=('Full_Name', 'nunique')).reset_index()
        wa = wa.sort_values('Week')
        if len(wa) > 0:
            fig_wt = go.Figure()
            if best_mod:
                wd = (wa['Week'] * 5 - 2).values.astype(float)
                wt = best_mod['pred_fn'](wd)
                fig_wt.add_trace(go.Scatter(
                    x=np.concatenate([wa['Week'].values, wa['Week'].values[::-1]]),
                    y=np.concatenate([wt + sigma, (wt - sigma)[::-1]]),
                    fill='toself', fillcolor='rgba(0,135,255,.08)',
                    line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
            fig_wt.add_trace(go.Scatter(x=wa['Week'], y=wa['A'], mode='lines+markers',
                line=dict(color=TP['blue'], width=2.5), marker=dict(size=5), name='Haftalık Ort.'))
            fig_wt.add_hline(y=target_val, line_dash="dash", line_color=TP['dark_gray'], annotation_text="Hedef")
            fig_wt.update_layout(**base_ly("", 420, "Hafta", y_label))
            st.plotly_chart(fig_wt, use_container_width=True)

    with col_c:
        st.markdown(sh_html("🔄", "Kohort İlerlemesi"), unsafe_allow_html=True)
        sc_waves = st.multiselect("Wave", fdf['Wave'].unique(), default=list(fdf['Wave'].unique())[:3], key='cs')
        if sc_waves:
            cp = [TP['blue'], TP['dark_coral'], TP['turquoise'], TP['violet'], TP['indigo'], TP['light_blue'], TP['muted_violet']]
            fig_co = go.Figure()
            for i, w in enumerate(sc_waves[:7]):
                ww = fdf[fdf['Wave'] == w].groupby('Week')['KPI_Value'].mean().reset_index().sort_values('Week')
                fig_co.add_trace(go.Scatter(x=ww['Week'], y=ww['KPI_Value'], mode='lines+markers',
                    line=dict(color=cp[i % len(cp)], width=2), marker=dict(size=4), name=w))
            fig_co.add_hline(y=target_val, line_dash="dash", line_color=TP['dark_gray'])
            fig_co.update_layout(**base_ly("", 420, "Hafta", y_label))
            st.plotly_chart(fig_co, use_container_width=True)

    st.divider()
    st.markdown(sh_html("📥", "Dışa Aktarım"), unsafe_allow_html=True)
    dl1, dl2, _ = st.columns([1, 1, 2])

    @st.cache_data
    def gen_excel(_a, _m, _w, _f, _p):
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as wr:
            _a.to_excel(wr, sheet_name='Ortalamalar', index=False)
            if _m:
                pd.DataFrame([{'Model': m, 'a': i['a'], 'b': i['b'], 'R2': i['r2'], 'Formül': i['formula']}
                    for m, i in _m.items()]).to_excel(wr, sheet_name='Modeller', index=False)
            _w.to_excel(wr, sheet_name='Wave', index=False)
            _f.groupby('Full_Name').agg(Wave=('Wave', 'first'), Gün=('Relative_Day', 'max'),
                Ort_KPI=('KPI_Value', 'mean')).reset_index().to_excel(wr, sheet_name='Agentlar', index=False)
            pd.DataFrame(_p).to_excel(wr, sheet_name='İlerleme', index=False)
        return buf.getvalue()

    with dl1:
        try:
            st.download_button("📥 Tam Analiz (Excel)", gen_excel(agg, models, ws_df, fdf, prog_rows),
                "TP_Learning_Curve.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except: st.info("Dışa aktarım mevcut değil.")
    with dl2:
        st.download_button("📥 Ortalamalar (CSV)", agg.to_csv(index=False).encode(), "TP_Ortalamalar.csv", "text/csv")

# ═══════════════════════════════════════════
# TAB 5: GLOSSARY
# ═══════════════════════════════════════════
with t5:
    st.markdown(f'''<div class="tp-hdr"><div class="ts">{logo_img}<div>
        <h1>TERIMLER SÖZLÜĞÜ & KULLANIM KILAVUZU</h1>
        <div class="sub">Dashboard Referans Dokümanı</div></div></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="al"></div>', unsafe_allow_html=True)

    def gcard(t, d, bdr=TP['blue']):
        return f'<div class="g-card" style="border-left-color:{bdr}"><h4>{t}</h4><p>{d}</p></div>'

    st.markdown('<div class="g-section">📌 KPI Tanımları & Yönelim</div>', unsafe_allow_html=True)
    k1, k2 = st.columns(2)
    with k1:
        st.markdown(gcard("EUC — End User Communication",
            "Son Kullanıcı İletişim Kalitesi (0–1). Müşteri ile iletişim standartlarına uyum oranı. "
            "<b>Olumlu yönelim: ↗ Artması</b> — yüksek değer daha iyidir. Hedef: 0.90 (%90).",
            TP['turquoise']), unsafe_allow_html=True)
        st.markdown(gcard("BC — Business Compliance",
            "İş Uyumluluk Skoru (0–1). İş süreçlerine ve prosedürlere uyum oranı. "
            "<b>Olumlu yönelim: ↗ Artması</b> — yüksek değer daha iyidir. Hedef: 0.90 (%90).",
            TP['turquoise']), unsafe_allow_html=True)
        st.markdown(gcard("CC — Customer Critical",
            "Müşteri Kritik Skor (0–1). Müşteri açısından kritik süreçlerin doğru yönetilme oranı. "
            "<b>Olumlu yönelim: ↗ Artması</b> — yüksek değer daha iyidir. Hedef: 0.95 (%95).",
            TP['turquoise']), unsafe_allow_html=True)
        st.markdown(gcard("AHT — Average Handle Time",
            "Ortalama İşlem Süresi (saniye). Bir müşteri etkileşiminin ortalama süresi. "
            "<b>Olumlu yönelim: ↘ Azalması</b> — düşük değer daha iyidir.",
            TP['dark_coral']), unsafe_allow_html=True)
    with k2:
        st.markdown(gcard("CSAT — Customer Satisfaction",
            "Müşteri Memnuniyeti (0–1). Genel müşteri memnuniyet oranı. "
            "<b>Olumlu yönelim: ↗ Artması</b> — yüksek değer daha iyidir. Hedef: 0.80 (%80).",
            TP['turquoise']), unsafe_allow_html=True)
        st.markdown(gcard("FCR — First Contact Resolution",
            "İlk Temasta Çözüm oranı (0–1). Müşteri sorununun ilk aramada çözülme oranı. "
            "<b>Olumlu yönelim: ↗ Artması</b> — yüksek değer daha iyidir. Hedef: 0.80 (%80).",
            TP['turquoise']), unsafe_allow_html=True)
        st.markdown(gcard("CSAT Agent — Temsilci Memnuniyeti",
            "Müşterinin temsilciden memnuniyet oranı (0–1). "
            "<b>Olumlu yönelim: ↗ Artması</b> — yüksek değer daha iyidir.",
            TP['turquoise']), unsafe_allow_html=True)
        st.markdown(gcard("CSAT Service — Hizmet Memnuniyeti",
            "Müşterinin genel hizmet memnuniyeti oranı (0–1). "
            "<b>Olumlu yönelim: ↗ Artması</b> — yüksek değer daha iyidir.",
            TP['turquoise']), unsafe_allow_html=True)

    st.markdown('<div class="g-section">📊 Dashboard Terimleri</div>', unsafe_allow_html=True)
    g1_, g2_ = st.columns(2)
    with g1_:
        st.markdown(gcard("Learning Curve (Öğrenme Eğrisi)",
            "Yeni çalışanların deneyim arttıkça performanslarının nasıl geliştiğini gösteren istatistiksel eğri. "
            "Dashboard bu eğriyi 4 farklı regresyon modeliyle hesaplar."), unsafe_allow_html=True)
        st.markdown(gcard("Relative Day (Göreceli Gün)",
            "Her agent'ın kendi başlangıcından itibaren normalize edilmiş çalışma günü. "
            "Tüm agentlar Day 1'den başlar, böylece farklı tarihlerde başlayanlar karşılaştırılabilir."), unsafe_allow_html=True)
        st.markdown(gcard("Wave (Dalga/Kohort)",
            "Aynı dönemde eğitime başlayan agent grubu. Örn: TCO_73, BUHA_03. "
            "Her wave'in performansı ayrı ayrı izlenebilir ve karşılaştırılabilir."), unsafe_allow_html=True)
        st.markdown(gcard("Confidence Band (Güven Bandı)",
            "En iyi modelin ±1 standart sapma aralığı. Gerçek değerlerin yaklaşık %68'i bu band içinde kalır. "
            "Band dışı değerler olağandışı performansı gösterir."), unsafe_allow_html=True)
        st.markdown(gcard("Residual (Artık Değer)",
            "Gerçek değer − Model tahmini. Sıfıra yakın residualler iyi uyum gösterir. "
            "Sistematik sapmalar modelin verilere iyi uymadığına işaret eder."), unsafe_allow_html=True)
    with g2_:
        st.markdown(gcard("R² (Determinasyon Katsayısı)",
            "Modelin verileri ne kadar iyi açıkladığını gösteren ölçü (0–1). "
            "<br>• 0.00–0.30: Zayıf &nbsp; • 0.30–0.50: Orta &nbsp; • 0.50–0.70: İyi &nbsp; • 0.70–1.00: Mükemmel"), unsafe_allow_html=True)
        st.markdown(gcard("Target Day (Hedef Günü)",
            "Regresyon modelinin hedef KPI değerine ulaştığı dönem. Granülariteye göre gün, hafta veya ay olarak gösterilir. "
            "Eğrinin hedef çizgisiyle kesiştiği nokta."), unsafe_allow_html=True)
        st.markdown(gcard("Stabilization (Stabilizasyon)",
            "Performansın oturduğu dönem. <b>Hesaplama yöntemi:</b> En iyi regresyon modelinin tahmin eğrisi üzerinde, "
            "bir dönemden diğerine geçişteki değişim oranı <b>%1'in altına</b> düştüğü ilk nokta. "
            "Örneğin, EUC eğrisi Gün 50'de %92, Gün 51'de %92.3 ise değişim oranı %0.33 → stabilize sayılır. "
            "Granülariteye göre gün, hafta veya ay olarak gösterilir. "
            "Bu nokta, yeni çalışanın performansının artık belirgin şekilde değişmediğini ve operasyonel seviyeye ulaştığını ifade eder."), unsafe_allow_html=True)
        st.markdown(gcard("Glide Path (Performans Yolu)",
            "Yeni başlayanlardan beklenen ilerleme planı. Ramp-up döneminde hedeflerin takibi için kullanılır. "
            "Haftalık ve aylık kontrol noktaları ile izlenir."), unsafe_allow_html=True)
        st.markdown(gcard("Granülarite",
            "<b>Day:</b> Günlük detay — en hassas, küçük gruplarda gürültülü olabilir. "
            "<b>Week:</b> Haftalık — genel trend için ideal. "
            "<b>Month:</b> Aylık — uzun vadeli eğilimler, raporlama amaçlı."), unsafe_allow_html=True)

    st.markdown('<div class="g-section">🔬 Regresyon Modelleri</div>', unsafe_allow_html=True)
    r1_, r2_ = st.columns(2)
    with r1_:
        st.markdown(gcard("Linear (Doğrusal)",
            "KPI = a × Gün + b — Sabit hızda değişim. Kısa dönem analizlerde kullanışlı. <b>Renk: 🔴 Kırmızı</b>",
            TP['dark_coral']), unsafe_allow_html=True)
        st.markdown(gcard("Logarithmic (Logaritmik)",
            "KPI = a × ln(Gün) + b — Başlangıçta hızlı, sonra yavaşlayan değişim. "
            "Çoğu öğrenme eğrisi için en uygun model. <b>Renk: 🔵 Mavi</b>",
            TP['light_blue']), unsafe_allow_html=True)
    with r2_:
        st.markdown(gcard("Power (Üstel Kuvvet)",
            "KPI = a × Gün^b — Ölçeklenen değişim. Uzun vadeli trendlerde başarılı. <b>Renk: 🟢 Turkuaz</b>",
            TP['turquoise']), unsafe_allow_html=True)
        st.markdown(gcard("Exponential (Üstel)",
            "KPI = a × e^(b×Gün) — Hızlı ivmeli değişim. Uzun extrapolasyonda dikkatli olun. <b>Renk: 🟣 Mor</b>",
            TP['violet']), unsafe_allow_html=True)

    st.markdown('<div class="g-section">📈 Grafik Okuma Rehberi</div>', unsafe_allow_html=True)
    st.markdown(gcard("Ana Dashboard Grafiği",
        "<b>Gri noktalar:</b> Dönemlik ortalama KPI. <b>Renkli çizgiler:</b> 4 regresyon modeli (kalın = en iyi). "
        "<b>Gri gölge:</b> ±1σ güven bandı. <b>Siyah kesikli:</b> Hedef. <b>Yeşil dikey:</b> Hedefe ulaşma noktası.",
        TP['indigo']), unsafe_allow_html=True)
    st.markdown(gcard("Progression Durumları",
        "<b>✅ Hedefte:</b> Gerçek ortalama hedefe ulaşmış. "
        "<b>⚠️ Band İçi:</b> Güven bandı içinde ama hedefe ulaşmamış — normal ilerleme. "
        "<b>❌ Sapma:</b> Güven bandı dışında — müdahale gerekebilir.",
        TP['indigo']), unsafe_allow_html=True)
    st.markdown(gcard("Renk Kodları",
        "AHT: Koyu yeşil = düşük (iyi), kırmızı = yüksek (kötü). "
        "Kalite metrikleri (EUC, BC, CC, CSAT, FCR): Koyu yeşil = yüksek (iyi), kırmızı = düşük (kötü). "
        "Renk skalası KPI yönüne göre otomatik ayarlanır.",
        TP['indigo']), unsafe_allow_html=True)

    st.markdown('<div class="g-section">🔧 Filtre Kullanım İpuçları</div>', unsafe_allow_html=True)
    st.markdown(gcard("Wave Filtresi",
        "Belirli bir eğitim grubunu seçerek sadece o grubun performansını analiz edin. "
        "Eğitim etkinliğini değerlendirmek için çok değerlidir. Boş = tümü dahil.",
        TP['muted_violet']), unsafe_allow_html=True)
    st.markdown(gcard("Granülarite Seçimi",
        "<b>Day:</b> Detaylı analiz, az agent olduğunda gürültülü olabilir. "
        "<b>Week:</b> Genel trend için ideal, gürültüyü azaltır. "
        "<b>Month:</b> Uzun vadeli eğilimler, raporlama amaçlı.",
        TP['muted_violet']), unsafe_allow_html=True)
    st.markdown(gcard("Model Seçimi",
        "<b>Otomatik:</b> Sistem en yüksek R² değerini seçer — çoğu zaman en iyisidir. "
        "<b>Manuel:</b> Müşteri raporunda belirli bir model tipi isteniyorsa kullanın.",
        TP['muted_violet']), unsafe_allow_html=True)
