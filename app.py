"""DEPLOYMENT: aplikasi Streamlit klasifikasi tutupan lahan Jawa Timur (Sentinel-2)."""
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import streamlit as st

from src.config import (CLASS_NAMES, DEFAULT_TIF, MODEL_PATH, MODEL_DIR, FEATURES)
from src.data_loader import read_raster, raster_summary, band_statistics, load_csv
from src.preprocessing import build_features, to_matrix, rgb_preview
from src.modeling import load_model, predict_map
from src.evaluation import compute_area
from src.postprocessing import fix_sea_as_lake, majority_filter
from src.visualization import (plot_class_map, plot_area_bar, plot_spectral, plot_tiles)

st.set_page_config(page_title="LULC Jawa Timur - Sentinel-2", layout="wide")
st.title("Klasifikasi & Luas Tutupan Lahan Jawa Timur")
st.caption("Sentinel-2 (CDSE openEO) | Random Forest | alur CRISP-DM")


# ------------------------------------------------------------------ cache
@st.cache_resource(show_spinner=False)
def get_model():
    return load_model(MODEL_PATH)


@st.cache_data(show_spinner=False)
def analyze(raster_bytes: bytes | None):
    """Baca raster -> fitur -> prediksi -> luas. Di-cache per file."""
    r = read_raster(io.BytesIO(raster_bytes)) if raster_bytes else read_raster(DEFAULT_TIF)
    feat, mask = build_features(r.array, r.band_names, r.nodata)
    X, valid = to_matrix(feat, mask)
    cmap = predict_map(get_model(), X, valid, r.shape_hw)
    return {
        "class_map": cmap, "bounds": r.bounds,
        "transform": r.transform, "geographic": r.is_geographic,
        "summary": raster_summary(r), "bandstats": band_statistics(r),
        "rgb": rgb_preview(np.where(r.array == r.nodata, 0, r.array), r.band_names)
               if r.nodata is not None else rgb_preview(r.array, r.band_names),
    }


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Citra yang dianalisis")
    src = st.radio("Sumber", ["Bawaan: jatim_250m.tif", "Unggah GeoTIFF sendiri"])
    upload = None
    if src.startswith("Unggah"):
        upload = st.file_uploader(
            "GeoTIFF 5 band: B02, B03, B04, B08, B11", type=["tif", "tiff"])
        st.caption("Nama band diambil dari metadata file. Skala reflektansi DN 0-10000.")
    st.divider()
    st.header("Pasca-proses (opsional)")
    opt_sea = st.checkbox("Danau yang tersambung ke laut -> Laut", value=True,
                          help="Laut dangkal/keruh sering terbaca Danau. Heuristik, bukan hasil model.")
    opt_maj = st.checkbox("Haluskan bintik (filter modus 3x3)", value=False,
                          help="Mengurangi salt-and-pepper, tetapi mengubah luas kelas.")
    st.divider()
    st.markdown("**Kelas:** " + ", ".join(CLASS_NAMES.values()))

model_ready = MODEL_PATH.exists()
if not model_ready:
    st.error("Model belum ada. Jalankan: `python scripts/train.py --data data/raw/dataset.csv`")

result, err = None, None
if model_ready and (src.startswith("Bawaan") or upload is not None):
    try:
        with st.spinner("Memproses citra dan memprediksi kelas..."):
            result = analyze(upload.getvalue() if upload else None)
    except Exception as e:
        err = str(e)
        st.error(f"Gagal memproses citra: {err}")

if result:
    cm_final = result["class_map"]
    if opt_sea:
        cm_final = fix_sea_as_lake(cm_final)
    if opt_maj:
        cm_final = majority_filter(cm_final, n_classes=len(CLASS_NAMES))
    result["final_map"] = cm_final
    result["area"] = compute_area(cm_final, result["transform"], result["geographic"])

tabs = st.tabs(["1. Business Understanding", "2. Data Understanding",
                "3. Data Preparation", "4. Modeling", "5. Evaluation",
                "6. Hasil & Luas"])

# ------------------------------------------------------------ 1. Business
with tabs[0]:
    st.subheader("Business Understanding")
    st.markdown("""
**Tujuan bisnis:** mengetahui sebaran dan luas tutupan lahan Jawa Timur secara cepat
dari citra satelit, tanpa survei lapangan menyeluruh.

**Tujuan analitik:** mengklasifikasikan setiap piksel Sentinel-2 ke 6 kelas
(Sawah, Bangunan, Hutan, Danau, Laut, Mangrove), lalu menghitung luas tiap kelas.

**Kriteria sukses:** akurasi pada data uji yang *terpisah per poligon* serta
luas per kelas yang masuk akal; hasil dibaca bersama keterbatasan di tab Evaluation.
""")
    st.table(pd.DataFrame({"id": list(CLASS_NAMES), "kelas": list(CLASS_NAMES.values())}))

# --------------------------------------------------------- 2. Data Understanding
with tabs[1]:
    st.subheader("Data Understanding")
    st.markdown("#### Data latih (poligon sampel)")
    ringkasan = load_csv("ringkasan_kelas.csv")
    sample = load_csv("dataset_sample.csv")
    c1, c2 = st.columns(2)
    if ringkasan is not None:
        with c1:
            st.dataframe(ringkasan.rename(columns={"label_teks": "kelas"}),
                         hide_index=True)
            st.caption(f"Total {ringkasan['piksel'].sum():,} piksel dari "
                       f"{ringkasan['poligon'].sum()} poligon. Kelas tidak seimbang "
                       "(Laut jauh lebih banyak dari Sawah), jadi pelatihan memakai "
                       "pembobotan kelas dan subsampel per kelas.")
        with c2:
            st.bar_chart(ringkasan.set_index("label_teks")["piksel"])
    if sample is not None:
        st.markdown("**Tanda tangan spektral** (rata-rata tiap kelas)")
        st.pyplot(plot_spectral(sample))

    st.markdown("#### Rencana tile & pengambilan data (openEO / CDSE)")
    tiles, jobs = load_csv("rencana_tile.csv"), load_csv("daftar_job.csv")
    if tiles is not None:
        st.pyplot(plot_tiles(tiles, sample))
        st.caption(f"{len(tiles)} tile; titik biru = contoh piksel latih.")
    if jobs is not None:
        num = lambda c: pd.to_numeric(jobs[c].astype(str).str.extract(r"([\d.]+)")[0], errors="coerce")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Job selesai", f"{(jobs['status'] == 'finished').sum()} / {len(jobs)}")
        m2.metric("Total biaya (credits)", f"{jobs['costs'].sum():,}")
        m3.metric("Total durasi", f"{num('duration').sum() / 60:,.0f} menit")
        m4.metric("Total input", f"{num('input_pixel').sum():,.0f} MP")

    st.markdown("#### Citra yang akan diklasifikasi")
    if result:
        a, b = st.columns([1, 1])
        with a:
            st.json(result["summary"])
            st.dataframe(result["bandstats"], hide_index=True)
        with b:
            st.image(result["rgb"], caption="Komposit warna alami (B04-B03-B02)")
    else:
        st.info("Pilih citra di sidebar.")

# --------------------------------------------------------- 3. Data Preparation
with tabs[2]:
    st.subheader("Data Preparation")
    st.markdown(f"""
1. **Baca raster** dan metadata (nama band, CRS, NoData = -32768).
2. **Masker NoData**: piksel NoData tidak diprediksi dan tidak dihitung luasnya.
3. **Reflektansi negatif** dipotong ke 0.
4. **Indeks spektral** (identik dengan kolom pada `dataset.csv`):
   - NDVI = (B08 - B04) / (B08 + B04)
   - NDWI = (B03 - B08) / (B03 + B08)
   - MNDWI = (B03 - B11) / (B03 + B11)
   - NDBI = (B11 - B08) / (B11 + B08)
5. **9 fitur** model: {", ".join(FEATURES)}.
6. **Data latih:** subsampel seimbang per kelas; pemisahan latih/uji per **poligon** agar
   piksel bertetangga dari poligon yang sama tidak bocor ke data uji.
""")

# ------------------------------------------------------------------ 4. Modeling
with tabs[3]:
    st.subheader("Modeling")
    mpath = MODEL_DIR / "metrics.json"
    if mpath.exists():
        mt = json.load(open(mpath))
        st.markdown(f"**Random Forest**, {mt['n_pohon']} pohon, "
                    f"{mt['n_latih']:,} piksel latih dari {mt['n_poligon']} poligon, "
                    f"`class_weight=balanced_subsample`.")
        imp = pd.read_csv(MODEL_DIR / "kepentingan_fitur.csv", index_col=0)
        st.markdown("**Kepentingan fitur**")
        st.bar_chart(imp["importance"])
    else:
        st.info("Belum ada metrik. Jalankan scripts/train.py.")

# ---------------------------------------------------------------- 5. Evaluation
with tabs[4]:
    st.subheader("Evaluation")
    if mpath.exists():
        c1, c2, c3 = st.columns(3)
        c1.metric("Akurasi (CV per poligon)", f"{mt['akurasi_group_cv']*100:.1f}%")
        c2.metric("Kappa", f"{mt['kappa_group_cv']:.3f}")
        c3.metric("F1 macro", f"{mt['f1_macro_group_cv']:.3f}")
        st.warning(
            f"Jika data dibagi **acak per piksel**, akurasi tampak {mt['akurasi_split_acak']*100:.1f}%, "
            "tetapi angka itu terlalu optimis karena piksel dari poligon yang sama saling "
            "mirip. Angka yang jujur adalah CV per poligon di atas.")
        st.markdown("**Confusion matrix** (baris = aktual, kolom = prediksi)")
        st.dataframe(pd.read_csv(MODEL_DIR / "confusion_matrix.csv", index_col=0))
        st.markdown("**Precision / Recall / F1 per kelas**")
        st.dataframe(pd.read_csv(MODEL_DIR / "laporan_kelas.csv", index_col=0))
        st.markdown("""
**Keterbatasan yang perlu dicatat**
- Model dilatih dari piksel **10 m** dan diterapkan ke raster **~250 m**; piksel 250 m
  berisi campuran kelas sehingga prediksi bisa bergeser.
- Hanya 6 kelas. Penggunaan lahan lain (tegalan, kebun, semak, lahan terbuka) tetap
  dipaksa masuk ke salah satu dari 6 kelas ini.
- Luas adalah estimasi, bukan angka statistik resmi.
- Kelas **Sawah, Bangunan, Hutan** paling sering tertukar (F1 sekitar 0,6), dan
  **Mangrove** muncul sebagai bintik di daratan (salah deteksi). Luas ketiganya
  dan Mangrove sebaiknya dibaca sebagai perkiraan kasar.
- Laut dangkal/keruh terbaca Danau; opsi pasca-proses di sidebar memperbaikinya
  dengan aturan keterhubungan, dan itu heuristik yang belum divalidasi dengan data lapangan.
""")
    else:
        st.info("Belum ada metrik.")

# ------------------------------------------------------------------ 6. Hasil
with tabs[5]:
    st.subheader("Peta klasifikasi & luas")
    if result:
        st.pyplot(plot_class_map(result["final_map"], result["bounds"]))
        area = result["area"]
        left, right = st.columns([1, 1])
        with left:
            show = area.rename(columns={"kelas": "Kelas", "jumlah_piksel": "Piksel",
                                        "luas_ha": "Luas (ha)", "luas_km2": "Luas (km²)",
                                        "persen": "%"})[["Kelas", "Piksel", "Luas (ha)", "Luas (km²)", "%"]]
            st.dataframe(show, hide_index=True)
            st.metric("Total area terklasifikasi", f"{area['luas_km2'].sum():,.0f} km²")
            st.download_button("Unduh tabel luas (CSV)", area.to_csv(index=False).encode(),
                               "luas_lulc.csv", "text/csv")
        with right:
            st.pyplot(plot_area_bar(area))
        if result["summary"]["CRS"].upper().endswith("4326"):
            st.caption("CRS raster berupa derajat (EPSG:4326): luas dihitung per baris "
                       "menurut lintang (luas pita bola), bukan piksel dikali konstanta.")
    else:
        st.info("Pilih citra di sidebar.")
