"""Dasbor Klasifikasi Spasial Tutupan Lahan Jawa Timur (Sentinel-2).

Semua angka dibaca dari berkas hasil `scripts/train.py` dan `scripts/build_assets.py`
(models/evaluasi.json, data/processed/*.csv, maps/*.html) - tidak ada angka yang
ditulis manual di kode ini.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="Klasifikasi Tutupan Lahan Jawa Timur", page_icon="🗺️",
                   layout="wide", initial_sidebar_state="expanded")

# ============================================================== tema
DARK_LABEL, LIGHT_LABEL = "Dark Mode (Espresso)", "Light Mode (Coklat-Putih)"
is_dark = st.session_state.get("theme_mode", LIGHT_LABEL) == DARK_LABEL

if is_dark:
    T = dict(BG="#1A1412", SURFACE="#251D19", SIDEBAR="#1F1814", BORDER="#3E3029",
             SUBTLE="#322721", TEXT="#F5EBE1", MUTED="#C7B3A3", PRIMARY="#A1887F",
             HOVER="#BCAAA4", BADGE="#352721", BADGE_TXT="#EFEBE9", SHADOW="rgba(0,0,0,.35)")
else:
    T = dict(BG="#FDFBF9", SURFACE="#FFFFFF", SIDEBAR="#F8F4EE", BORDER="#EADCCF",
             SUBTLE="#F3EBE1", TEXT="#3D2B1F", MUTED="#795548", PRIMARY="#6D4C41",
             HOVER="#4E342E", BADGE="#F3EBE1", BADGE_TXT="#5D4037", SHADOW="rgba(61,43,31,.06)")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, .stApp, [data-testid="stAppViewContainer"] {
  background:@BG@ !important; color:@TEXT@ !important;
  font-family:"Plus Jakarta Sans",-apple-system,"Segoe UI",Roboto,sans-serif !important; }
[data-testid="stHeader"] { background:transparent !important; }
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
  background:@SIDEBAR@ !important; border-right:1px solid @BORDER@ !important; }
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3, [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] span,
div[role="radiogroup"] label p, [data-testid="stCaptionContainer"] { color:@TEXT@ !important; }
.card { background:@SURFACE@; border:1px solid @BORDER@; border-radius:1.1rem;
  padding:1.2rem 1.3rem; box-shadow:0 4px 14px @SHADOW@; margin-bottom:1rem; }
.card-head { display:flex; align-items:center; justify-content:space-between; gap:.6rem; flex-wrap:wrap;
  padding-bottom:.7rem; border-bottom:1px solid @SUBTLE@; margin-bottom:.7rem; }
.card-title { font-size:1.02rem; font-weight:700; color:@TEXT@; display:flex; align-items:center; gap:.5rem; margin:0; }
.card-text { font-size:.83rem; color:@MUTED@; line-height:1.55; }
.badge { background:@BADGE@; color:@BADGE_TXT@; font-size:.74rem; font-weight:700; padding:.28rem .7rem;
  border-radius:9999px; display:inline-flex; align-items:center; gap:.4rem; border:1px solid @BORDER@; }
.metric { background:@SURFACE@; border:1px solid @BORDER@; border-radius:1.1rem; padding:1.15rem 1.25rem;
  box-shadow:0 3px 10px @SHADOW@; height:100%; }
.metric-top { display:flex; align-items:center; justify-content:space-between; }
.metric-label { font-size:.7rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color:@MUTED@; }
.metric-row { display:flex; align-items:baseline; gap:.6rem; margin-top:.7rem; flex-wrap:wrap; }
.metric-num { font-size:2rem; font-weight:800; color:@TEXT@; line-height:1; }
.metric-sub { font-size:.74rem; color:@MUTED@; margin-top:.45rem; line-height:1.4; }
.banner { background:@BADGE@; border:1px solid @BORDER@; border-radius:.85rem; padding:.9rem 1.1rem;
  font-size:.84rem; color:@TEXT@; line-height:1.55; margin-bottom:1rem; }
.stDownloadButton button, .stButton button { background:@PRIMARY@ !important; color:#fff !important;
  border:none !important; border-radius:.65rem !important; font-weight:600 !important; }
.stDownloadButton button:hover, .stButton button:hover { background:@HOVER@ !important; }
div[data-baseweb="tab-list"] { background:@SURFACE@ !important; border:1px solid @BORDER@ !important;
  border-radius:.75rem !important; padding:.3rem !important; gap:.35rem !important; }
button[data-baseweb="tab"] { border-radius:.55rem !important; color:@MUTED@ !important; font-weight:600 !important; }
button[data-baseweb="tab"][aria-selected="true"] { background:@BADGE@ !important; color:@TEXT@ !important; }
[data-testid="stExpander"] { background:@SURFACE@; border:1px solid @BORDER@ !important; border-radius:.85rem; }
[data-testid="stExpander"] summary p { color:@TEXT@ !important; font-weight:700; }
</style>
"""
for k, v in T.items():
    CSS = CSS.replace(f"@{k}@", v)
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================== ikon (Heroicons, MIT)
def icon(d, size=20, color=None):
    color = color or T["PRIMARY"]
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'style="width:{size}px;height:{size}px;min-width:{size}px;display:inline-block;vertical-align:middle">'
            f'<path d="{d}"/></svg>')

I_GLOBE = "M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-.778.099-1.533.284-2.253"
I_LAYERS = "M6.429 9.75 2.25 12l4.179 2.25m0-4.5 5.571 3 5.571-3m-11.142 0L2.25 7.5 12 2.25l9.75 5.25-4.179 2.25m0 0L21 12l-4.179 2.25m0 0 4.179 2.25L12 21.75 2.25 16.5l4.179-2.25m11.142 0-5.571 3-5.571-3"
I_CHECK = "M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
I_WARN = "M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
I_BAR = "M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z"
I_MAP = "M9 6.75V15m6-6v8.25m.503 3.046 4.84-2.42A1.125 1.125 0 0 0 21 16.883V5.86a1.125 1.125 0 0 0-.623-1.006l-4.82-2.41a1.125 1.125 0 0 0-.96.002l-5.195 2.597a1.125 1.125 0 0 1-.96 0L3.623 2.633A1.125 1.125 0 0 0 3 3.639v11.023a1.125 1.125 0 0 0 .623 1.006l4.82 2.41a1.125 1.125 0 0 0 .96-.002l5.195-2.597a1.125 1.125 0 0 1 .96 0l-.062-.033Z"

# ============================================================== pemuat berkas
SEARCH = ["", "maps", "data/processed", "models", "data", "assets"]

def cari_file(name):
    for base in (APP_DIR, Path.cwd()):
        for sub in SEARCH:
            p = base / sub / name
            if p.is_file():
                return p
    return None

@st.cache_data(show_spinner=False)
def baca_csv(path):
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def baca_teks(path):
    return Path(path).read_text(encoding="utf-8")

def muat_csv(name):
    p = cari_file(name)
    return baca_csv(str(p)) if p else None

p_ev = cari_file("evaluasi.json")
EV = json.loads(p_ev.read_text()) if p_ev else None
if EV is not None and "models" not in EV:
    st.error("`evaluasi.json` berasal dari versi lama (Random Forest) dan tidak cocok dengan app.py ini. "
             "Ganti dengan `assets/evaluasi.json` dari paket terbaru (dashboard_lulc.zip).")
    st.stop()
df_poly = muat_csv("prediksi_poligon.csv")
df_luas = muat_csv("luas_kelas.csv")

# ============================================================== sidebar
CLASSES = [("Sawah", "#FFD92F", "Lahan pertanian"), ("Bangunan", "#E41A1C", "Kawasan terbangun"),
           ("Hutan", "#2E7D32", "Vegetasi rapat"), ("Danau", "#4FC3F7", "Air pedalaman / waduk"),
           ("Laut", "#0D47A1", "Perairan terbuka"), ("Mangrove", "#8E44AD", "Hutan bakau pesisir")]

with st.sidebar:
    st.markdown('<div class="metric-label">Tema tampilan</div>', unsafe_allow_html=True)
    st.radio("Tema", [LIGHT_LABEL, DARK_LABEL], key="theme_mode", label_visibility="collapsed")
    st.markdown(f'<hr style="border:none;border-top:1px solid {T["BORDER"]};margin:.8rem 0">', unsafe_allow_html=True)

    if EV:
        mkey = st.selectbox("Model (Peta 2, 3, kartu, luas)", list(EV["models"]),
                            format_func=lambda k: EV["models"][k]["nama"])
        model_name = EV["models"][mkey]["nama"]
    else:
        mkey, model_name = "knn", "KNN"
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:1rem">{icon(I_GLOBE, 26)}
<div><div style="font-size:1.1rem;font-weight:800;color:{T['TEXT']}">LULC Jawa Timur</div>
<div style="font-size:.75rem;color:{T['MUTED']};font-weight:600">Sentinel-2 &bull; {model_name}</div></div></div>
<div class="card" style="font-size:.8rem;line-height:1.7;padding:.8rem 1rem">
<b>Sensor:</b> Sentinel-2 MSI (CDSE openEO)<br><b>Band:</b> B02, B03, B04, B08, B11<br>
<b>Indeks:</b> NDVI, NDWI, MNDWI, NDBI<br><b>Raster peta:</b> ~250 m<br><b>Data latih:</b> piksel 10 m</div>
""", unsafe_allow_html=True)

    legend = "".join(
        f'<div style="display:flex;align-items:center;gap:.55rem;font-size:.82rem;line-height:1.85">'
        f'<span style="width:12px;height:12px;border-radius:50%;background:{c};border:1px solid #D7C4B7;display:inline-block"></span>'
        f'<b>{n}</b><span style="color:{T["MUTED"]};font-size:.74rem">({d})</span></div>' for n, c, d in CLASSES)
    st.markdown(f'<div class="metric-label" style="margin-bottom:.5rem">6 kelas tutupan lahan</div>'
                f'<div class="card" style="padding:.7rem 1rem">{legend}</div>', unsafe_allow_html=True)

    layout = st.radio("Tata letak 3 peta", ["Tab navigasi (1 peta per tab)", "Berurutan vertikal",
                                            "Peta 1 & 2 bersisian"])
    tinggi = st.slider("Tinggi frame peta (px)", 450, 900, 620, 25)

# ============================================================== header
st.markdown(f"""
<div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:1rem;margin-bottom:1.2rem">
<div><div style="display:flex;align-items:center;gap:.65rem">{icon(I_GLOBE, 32)}
<h1 style="font-size:1.9rem;font-weight:800;letter-spacing:-.02em;color:{T['TEXT']};margin:0">Klasifikasi Spasial Tutupan Lahan Jawa Timur</h1></div>
<p style="font-size:.9rem;color:{T['MUTED']};margin:.4rem 0 0;max-width:52rem;line-height:1.55">
Pemetaan 6 kelas tutupan lahan dari citra Sentinel-2 dengan {model_name}, beserta evaluasi model dan estimasi luas tiap kelas.</p></div>
<div class="badge" style="padding:.45rem .95rem">Sentinel-2 &bull; {model_name}</div></div>
""", unsafe_allow_html=True)

if EV is None or df_poly is None:
    st.error("Berkas hasil belum ada. Jalankan `python scripts/train.py` lalu "
             "`python scripts/build_assets.py` (lihat README).")
    st.stop()

# ============================================================== kartu metrik
M = EV["models"][mkey]
n_poly, n_ok = EV["n_poligon"], M["n_poligon_benar"]
n_salah = n_poly - n_ok
ppc = EV["poligon_per_kelas"]
kartu = [
    ("Akurasi (CV per poligon)", I_CHECK, T["PRIMARY"], f"{M['akurasi_piksel']*100:.1f}%", "Piksel uji",
     f"Poligon: {n_ok/n_poly*100:.1f}% ({n_ok}/{n_poly}) &bull; Kappa {M['kappa']:.2f}"),
    ("Piksel ekstraksi", I_BAR, T["PRIMARY"], f"{EV['n_piksel_total']/1000:.0f}K", "Sentinel-2",
     "5 band + 4 indeks spektral (NDVI, NDWI, MNDWI, NDBI)"),
    ("Poligon ground truth", I_LAYERS, T["PRIMARY"], f"{n_poly}", f"{min(ppc.values())}-{max(ppc.values())} / kelas",
     "Jumlah poligon per kelas tidak sama (Hutan paling sedikit)"),
    ("Poligon salah prediksi", I_WARN, "#D97706", f"{n_salah}", f"{n_salah/n_poly*100:.1f}%",
     "Garis merah putus-putus pada Peta 2"),
]
for col, (lab, ic, icol, num, badge, sub) in zip(st.columns(4), kartu):
    with col:
        st.markdown(f"""<div class="metric"><div class="metric-top"><span class="metric-label">{lab}</span>
<span style="background:{T['BADGE']};border-radius:50%;padding:.35rem;display:inline-flex">{icon(ic, 18, icol)}</span></div>
<div class="metric-row"><span class="metric-num">{num}</span><span class="badge">{badge}</span></div>
<div class="metric-sub">{sub}</div></div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="banner" style="margin-top:1rem">
<b>Cara membaca akurasi.</b> Data dibagi <b>per poligon</b>: piksel dari satu poligon tidak pernah muncul sekaligus di data
latih dan data uji. Jika dibagi acak per piksel, akurasi tampak <b>{M['akurasi_split_acak']*100:.1f}%</b>, tetapi angka itu terlalu
optimis karena piksel bertetangga sangat mirip.</div>""", unsafe_allow_html=True)

# ============================================================== peta
MAPS = [
    ("peta_1_ground_truth.html", "Peta 1: Poligon Sampel Ground Truth", I_LAYERS, f"{n_poly} poligon",
     "Poligon sampel dengan warna sesuai label asli. Nyalakan/matikan tiap kelas dan ganti basemap pada kontrol di kanan atas."),
    (f"peta_2_prediksi_{mkey}.html", f"Peta 2: Prediksi {model_name} per Poligon", I_MAP, "Evaluasi model",
     "Warna menunjukkan kelas prediksi. <b style='color:#DC2626'>Garis putus-putus merah</b> menandai poligon yang salah prediksi. "
     "Prediksi tiap poligon dibuat oleh model yang tidak pernah melihat poligon itu."),
    (f"peta_3_regional_{mkey}.html", "Peta 3: Prediksi Regional Jawa Timur (Raster ~250 m)", I_GLOBE, "Raster citra",
     "Prediksi piksel-per-piksel pada citra Sentinel-2 Jawa Timur. Tiap kelas adalah layer terpisah. "
     "Danau yang tersambung ke laut sudah dikoreksi menjadi Laut."),
]

def render_map(i):
    fname, title, ic, badge, desc = MAPS[i]
    st.markdown(f"""<div class="card" style="margin-bottom:.6rem"><div class="card-head">
<h2 class="card-title">{icon(ic, 22)}<span>{title}</span></h2><span class="badge">{badge}</span></div>
<div class="card-text">{desc}</div></div>""", unsafe_allow_html=True)
    p = cari_file(fname)
    if p:
        components.html(baca_teks(str(p)), height=tinggi, scrolling=False)
        st.caption("Peta memuat basemap dan pustaka Leaflet dari internet; butuh koneksi aktif.")
    else:
        st.error(f"File `{fname}` tidak ditemukan.")

if layout.startswith("Tab"):
    for tab, i in zip(st.tabs(["Peta 1: Ground Truth", "Peta 2: Prediksi Poligon", "Peta 3: Regional Jatim"]), range(3)):
        with tab:
            render_map(i)
elif layout.startswith("Berurutan"):
    for i in range(3):
        render_map(i)
else:
    c1, c2 = st.columns(2)
    with c1:
        render_map(0)
    with c2:
        render_map(1)
    render_map(2)

# ============================================================== luas
st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
st.markdown(f"""<div class="card" style="margin-bottom:.6rem"><div class="card-head">
<h2 class="card-title">{icon(I_LAYERS, 22)}<span>Estimasi Luas Tutupan Lahan</span></h2>
<span class="badge">Raster ~250 m</span></div>
<div class="card-text">Luas = jumlah piksel x luas piksel. Raster memakai derajat (EPSG:4326), jadi luas tiap piksel
dihitung menurut lintangnya, bukan konstan. Angka berikut hanya <b>estimasi</b>, bukan statistik resmi.</div></div>""",
            unsafe_allow_html=True)
if df_luas is not None:
    dl = df_luas[df_luas["model"] == model_name].drop(columns="model")
    cl, cr = st.columns([1.1, 1])
    with cl:
        show = dl.rename(columns={"kelas": "Kelas", "luas_km2_mentah": "Luas mentah (km²)",
                                       "luas_km2": "Luas final (km²)", "luas_ha": "Luas final (ha)", "persen": "%"})
        st.dataframe(show.round(1), hide_index=True)
        st.metric("Total area terklasifikasi", f"{dl['luas_km2'].sum():,.0f} km²")
        st.download_button("Unduh tabel luas (CSV)", df_luas.to_csv(index=False).encode(),
                           "luas_lulc_jatim.csv", "text/csv")
    with cr:
        st.bar_chart(dl.set_index("kelas")["luas_km2"], y_label="km²")
    st.caption(f"Model: {model_name}. “Mentah” = keluaran model; “final” = setelah Danau yang tersambung ke laut diubah menjadi Laut.")

# ============================================================== evaluasi
st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
st.markdown(f"""<div class="card" style="margin-bottom:.6rem"><div class="card-head">
<h2 class="card-title">{icon(I_BAR, 22)}<span>Evaluasi Kinerja Model</span></h2>
<span class="badge">{model_name} &bull; CV 5-lipatan per poligon</span></div></div>""", unsafe_allow_html=True)

ca, cb = st.columns(2)
with ca:
    p = cari_file(f"confusion_matrix_{mkey}.png")
    if p:
        st.image(str(p), caption="Confusion matrix (angka = jumlah piksel, persen = per baris aktual)")
with cb:
    p = cari_file(f"kinerja_kelas_{mkey}.png")
    if p:
        st.image(str(p), caption="Precision, recall, dan F1 per kelas")

st.markdown("**Perbandingan algoritma** (data dan lipatan validasi sama)")
cmp_df = pd.DataFrame(list(EV["models"].values()))[["nama", "akurasi_piksel", "kappa", "f1_macro", "akurasi_poligon"]].rename(columns={
    "nama": "Model", "akurasi_piksel": "Akurasi piksel", "kappa": "Kappa",
    "f1_macro": "F1 macro", "akurasi_poligon": "Akurasi poligon"})
st.dataframe(cmp_df, hide_index=True)

st.markdown("**Fitur yang digunakan model**")
st.dataframe(pd.DataFrame({
    "Fitur": ["B02, B03, B04", "B08 (NIR)", "B11 (SWIR1)", "NDVI", "NDWI", "MNDWI", "NDBI"],
    "Rumus / Nama": ["Biru, Hijau, Merah", "Near infrared", "Shortwave infrared",
                     "(B08-B04)/(B08+B04)", "(B03-B08)/(B03+B08)", "(B03-B11)/(B03+B11)", "(B11-B08)/(B11+B08)"],
    "Fungsi": ["Warna tampak", "Biomassa kanopi", "Lahan terbangun & kelembapan", "Vegetasi rapat",
               "Perairan terbuka", "Air pedalaman", "Kawasan terbangun"]}), hide_index=True)

with st.expander("Keterbatasan dan catatan metodologi"):
    st.markdown("""
- **Perbedaan resolusi.** Model dilatih dari piksel 10 m, tetapi Peta 3 memakai raster ~250 m. Satu piksel 250 m
  bisa memuat beberapa jenis tutupan, sehingga prediksi dapat bergeser dan tampak bintik-bintik.
- **Tidak ada validasi pada resolusi 250 m.** Akurasi di atas diukur pada poligon latih 10 m, bukan pada peta akhir.
- **Hanya 6 kelas.** Tegalan, kebun, semak, dan lahan terbuka tetap dipaksa masuk ke salah satu dari 6 kelas.
- **Sawah, Bangunan, Hutan paling sering tertukar** (lihat confusion matrix). Mangrove juga muncul sebagai bintik di daratan.
- **Naive Bayes** mengasumsikan fitur saling bebas, padahal band dan indeks spektral sangat berkorelasi.
  Hal ini kemungkinan menjelaskan akurasinya lebih rendah dari KNN dan Mangrove yang terlalu luas pada petanya.
- **Koreksi laut** adalah aturan keterhubungan (heuristik), bukan keluaran model; kolom "mentah" pada tabel luas menunjukkan angka sebelum koreksi.
- Kelas tidak seimbang dalam data asli (Laut jauh lebih banyak piksel daripada Sawah); pelatihan memakai bobot kelas.
""")

# ============================================================== tabel poligon
st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
st.markdown(f"""<div class="card" style="margin-bottom:.6rem"><div class="card-head">
<h2 class="card-title">{icon(I_LAYERS, 22)}<span>Eksplorasi Poligon &amp; Hasil Prediksi</span></h2>
<span class="badge">Filter interaktif</span></div></div>""", unsafe_allow_html=True)

cols = ["poligon_id", "kelas_asli", f"prediksi_{mkey}", f"benar_{mkey}", f"persen_piksel_benar_{mkey}",
        "n_piksel", "NDVI", "NDWI", "MNDWI", "NDBI", "lon", "lat"]
dview = df_poly[cols].rename(columns={f"prediksi_{mkey}": "kelas_prediksi", f"benar_{mkey}": "benar",
                                      f"persen_piksel_benar_{mkey}": "persen_piksel_benar"})
c1, c2 = st.columns([2, 1])
with c1:
    semua = sorted(dview["kelas_asli"].unique())
    pilih = st.multiselect("Kelas asli:", semua, default=semua)
with c2:
    status = st.radio("Status:", ["Semua", "Benar", "Salah"], horizontal=True)
d = dview[dview["kelas_asli"].isin(pilih)]
if status == "Benar":
    d = d[d["benar"]]
elif status == "Salah":
    d = d[~d["benar"]]
st.caption(f"Menampilkan {len(d)} dari {len(dview)} poligon ({model_name}).")
st.dataframe(d, hide_index=True, height=360)
st.download_button("Unduh hasil prediksi poligon (CSV)", d.to_csv(index=False).encode(),
                   "prediksi_poligon_jatim.csv", "text/csv")

st.markdown(f"""<div style="margin-top:3rem;padding-top:1.2rem;border-top:1px solid {T['BORDER']};text-align:center;
font-size:.8rem;color:{T['MUTED']}">Klasifikasi Spasial Tutupan Lahan Jawa Timur &bull; Sentinel-2 &bull; {model_name}</div>""",
            unsafe_allow_html=True)
