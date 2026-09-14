---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---
# Pra-Pemrosesan Data Kewilayahan Kecamatan Jogoroto dan Ekstraksi 68 Fitur TSFEL

## 1. Preprocessing: Penanganan Outliers dan Interpolasi Data

Pada tahap ini, data yang sudah terkumpul diolah agar siap digunakan sebagai masukan pada model machine learning atau deep learning. Fokus utama pada tahap ini adalah menangani nilai yang menyimpang (*outliers*) dan mengisi nilai kosong (*missing values*) agar deret waktu menjadi konsisten secara temporal.

### Deteksi Outlier dengan Metode IQR

Metode Interquartile Range (IQR) digunakan untuk mendeteksi nilai pencilan pada kolom target, yaitu `NO2`. Nilai yang berada di luar batas bawah dan batas atas IQR akan diperlakukan sebagai outlier dan selanjutnya diubah menjadi `NaN` sebelum dilakukan interpolasi.

```{code-cell}
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Muat data hasil preprocessing awal
# Sesuaikan path sesuai lokasi file Anda

df = pd.read_csv("../file/NO2_Jogoroto_final.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# Hitung IQR
Q1 = df['NO2'].quantile(0.25)
Q3 = df['NO2'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Deteksi outlier
outliers_iqr = df[(df['NO2'] < lower_bound) | (df['NO2'] > upper_bound)]

print("Jumlah Outlier (IQR):", len(outliers_iqr))
print(outliers_iqr[['date', 'NO2']].head())
```

### Visualisasi Outlier

Berikut adalah visualisasi data NO2 beserta titik-titik outlier yang berhasil dideteksi.

![Outlier](../img/outlier.png)

```{code-cell}
plt.figure(figsize=(15, 5))
plt.plot(df['date'], df['NO2'], label='NO2', linewidth=1)

plt.scatter(outliers_iqr['date'], outliers_iqr['NO2'],
            color='red', marker='o', label='Outliers')

plt.axhline(upper_bound, color='orange', linestyle='dashed', label='Upper Bound (IQR)')
plt.axhline(lower_bound, color='blue', linestyle='dashed', label='Lower Bound (IQR)')

plt.title('Deteksi Outlier Data NO2 (Metode IQR)')
plt.xlabel('Tanggal')
plt.ylabel('Kadar NO2')
plt.legend()
plt.tight_layout()
plt.xticks(
    ticks=[df['date'].iloc[0], df['date'].iloc[-1]],
    labels=[df['date'].iloc[0].strftime('%Y-%m-%d'),
            df['date'].iloc[-1].strftime('%Y-%m-%d')]
)
plt.show()
```

### Penanganan Outlier dan Interpolasi Data

Setelah outlier ditemukan, nilai tersebut diubah menjadi `NaN`. Kemudian dilakukan interpolasi linier untuk mengisi data yang hilang. Untuk bagian awal dan akhir rangkaian yang tidak dapat diinterpolasi, digunakan teknik `bfill()` dan `ffill()` agar seluruh data tetap utuh.

```python
# Tandai outlier menjadi NaN
# df['NO2_cleaned'] = df['NO2'].mask((df['NO2'] < lower_bound) | (df['NO2'] > upper_bound))

# Lakukan interpolasi linier pada NaN yang sudah dibuat
# df['NO2_filled'] = df['NO2_cleaned'].interpolate(method='linear')
# df['NO2_filled'] = df['NO2_filled'].bfill().ffill()

# Simpan data yang sudah dibersihkan ke file baru
# df_no2_jogoroto = pd.DataFrame({
#     "date": df['date'],
#     "NO2": df['NO2_filled']
# })
# df_no2_jogoroto.to_csv("../file/NO2_Jogoroto_filled.csv", index=False)
```

### Hasil Setelah Cleaning dan Interpolasi

Setelah proses penanganan outlier dan imputasi selesai, data menjadi lebih stabil dan siap digunakan untuk ekstraksi fitur.

Berikut adalah contoh visualisasi data sebelum dan sesudah proses cleaning serta hasil imputasi:

![Before](../img/before.png)

![After](../img/after.png)

![Imput](../img/imput.png)

```{code-cell}
# Contoh penerapan lengkap

df = pd.read_csv("../file/NO2_Jogoroto_final.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

Q1 = df['NO2'].quantile(0.25)
Q3 = df['NO2'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Ubah outlier menjadi NaN
cleaned = df['NO2'].mask((df['NO2'] < lower_bound) | (df['NO2'] > upper_bound))

# Interpolasi linier + backfill/forward fill untuk data di ujung
filled = cleaned.interpolate(method='linear').bfill().ffill()

# Simpan hasil
result = pd.DataFrame({
    'date': df['date'],
    'NO2': filled
})

result.to_csv('../file/NO2_Jogoroto_filled.csv', index=False)

print('Data berhasil dibersihkan dan disimpan ke ../file/NO2_Jogoroto_filled.csv')
```

---

## 2. Ekstraksi 68 Fitur dengan TSFEL

Data deret waktu yang sudah bersih lalu diproses menggunakan library `tsfel` untuk menghasilkan fitur-fitur representatif. Pada tahap ini, saya mengekstraksi sebanyak 68 fitur dari deret waktu `NO2`, yang kemudian dapat dijadikan input untuk analisis lanjutan seperti klasifikasi, prediksi, atau pemodelan machine learning.

# 68 Fitur TSFEL (Time Series Feature Extraction Library)

TSFEL mengelompokkan fiturnya ke dalam 4 domain: **Statistik** (21 fitur), **Temporal** (15 fitur), **Spektral** (26 fitur), dan **Fraktal** (6 fitur) — total **68 fitur**. Domain fraktal secara default tidak diaktifkan pada konfigurasi bawaan TSFEL, namun tetap tersedia di library.

Notasi umum:
- $x = [x_1, x_2, \dots, x_N]$ = sinyal/jendela data dengan $N$ titik
- $\mu$ = rata-rata sinyal, $\sigma$ = standar deviasi sinyal
- $f_s$ = frekuensi sampling, $t_i$ = waktu sampel ke-$i$ ($t_i = i/f_s$)
- $X(f)$ = magnitudo spektrum hasil FFT pada frekuensi $f$

---

## 1. Domain Statistik (21 fitur)

Fitur statistik meringkas sinyal menggunakan statistik deskriptif (tidak bergantung pada urutan data).

| # | Nama Fitur | Rumus | Deskripsi |
|---|---|---|---|
| 1 | `abs_energy` (Absolute Energy) | $E = \sum_{i=1}^{N} x_i^2$ | Jumlah kuadrat seluruh nilai sinyal; menunjukkan total energi mentah sinyal. |
| 2 | `average_power` (Average Power) | $P = \dfrac{\sum x_i^2}{T}$, $T$ = durasi sinyal (detik) | Energi sinyal dibagi durasi waktu total; daya rata-rata sinyal. |
| 3 | `calc_max` (Maximum) | $\max(x)$ | Nilai maksimum sinyal dalam jendela. |
| 4 | `calc_mean` (Mean) | $\mu = \dfrac{1}{N}\sum_{i=1}^{N} x_i$ | Rata-rata aritmetika nilai sinyal. |
| 5 | `calc_median` (Median) | $\mathrm{median}(x)$ | Nilai tengah sinyal setelah diurutkan. |
| 6 | `calc_min` (Minimum) | $\min(x)$ | Nilai minimum sinyal dalam jendela. |
| 7 | `calc_std` (Standard Deviation) | $\sigma = \sqrt{\dfrac{1}{N}\sum_{i=1}^{N} (x_i-\mu)^2}$ | Ukuran sebaran nilai sinyal di sekitar rata-rata. |
| 8 | `calc_var` (Variance) | $\sigma^2 = \dfrac{1}{N}\sum_{i=1}^{N} (x_i-\mu)^2$ | Kuadrat dari standar deviasi; ukuran variabilitas sinyal. |
| 9 | `ecdf` (Empirical CDF) | $F(x) = \dfrac{1}{N}\,\#\{x_i \le x\}$ | Nilai fungsi distribusi kumulatif empiris sinyal pada sejumlah titik sepanjang sumbu waktu. |
| 10 | `ecdf_percentile` | $x_p$ sehingga $F(x_p) = p$ | Nilai sinyal pada persentil tertentu dari ECDF (default $p = 0{,}2$ dan $0{,}8$). |
| 11 | `ecdf_percentile_count` | $\#\{x_i \le x_p\}$ | Jumlah kumulatif sampel yang berada di bawah nilai persentil tertentu. |
| 12 | `ecdf_slope` | $m = \dfrac{p_{end}-p_{init}}{x(p_{end})-x(p_{init})}$ | Kemiringan ECDF antara dua persentil (default $0{,}5$ dan $0{,}75$). |
| 13 | `entropy` (Shannon Entropy) | $H = -\dfrac{\sum_i p_i \log_2 p_i}{\log_2 N}$ | Entropi Shannon ternormalisasi dari distribusi probabilitas nilai sinyal; ukuran keacakan/ketidakpastian. |
| 14 | `hist_mode` (Histogram Mode) | titik tengah bin histogram dengan frekuensi tertinggi | Nilai yang paling sering muncul berdasarkan histogram sinyal (default 10 bin). |
| 15 | `interq_range` (IQR) | $\mathrm{IQR} = Q_3 - Q_1$ | Selisih antara kuartil ke-3 dan kuartil ke-1; ukuran sebaran yang tahan outlier. |
| 16 | `kurtosis` | $\kappa = \dfrac{E[(x-\mu)^4]}{\sigma^4} - 3$ | Mengukur "keruncingan" (tailedness) distribusi sinyal dibanding distribusi normal. |
| 17 | `mean_abs_deviation` | $\mathrm{MAD}_{mean} = \dfrac{1}{N}\sum_i \lvert x_i-\mu\rvert$ | Rata-rata deviasi absolut nilai sinyal terhadap rata-ratanya. |
| 18 | `median_abs_deviation` | $\mathrm{MAD}_{med} = \mathrm{median}(\lvert x_i-\mathrm{median}(x)\rvert)$ | Median dari deviasi absolut terhadap median; ukuran sebaran yang robust terhadap outlier. |
| 19 | `pk_pk_distance` (Peak to Peak) | $PP = \max(x) - \min(x)$ | Selisih antara nilai maksimum dan minimum sinyal (rentang amplitudo). |
| 20 | `rms` (Root Mean Square) | $\mathrm{RMS} = \sqrt{\dfrac{1}{N}\sum_{i=1}^{N} x_i^2}$ | Akar dari rata-rata kuadrat sinyal; representasi magnitudo energetik sinyal (contoh: RMS $\approx 2{,}607$ pada slide 8). |
| 21 | `skewness` | $\gamma = \dfrac{E[(x-\mu)^3]}{\sigma^3}$ | Mengukur asimetri (kemiringan) distribusi nilai sinyal terhadap rata-ratanya. |

---

## 2. Domain Temporal (15 fitur)

Fitur temporal menganalisis dinamika dan perubahan nilai sinyal seiring waktu (sensitif terhadap urutan data).

| # | Nama Fitur | Rumus | Deskripsi |
|---|---|---|---|
| 22 | `auc` (Area Under the Curve) | $\mathrm{AUC} = \sum_{i} \tfrac{1}{2}(t_{i+1}-t_i)\,\lvert x_i+x_{i+1}\rvert$ | Luas area di bawah kurva sinyal dihitung dengan aturan trapesium. |
| 23 | `autocorr` (Autocorrelation) | lag pertama saat $\mathrm{ACF}(\text{lag}) < 1/e\;(\approx 0{,}3679)$ | Lag waktu pertama di mana fungsi autokorelasi sinyal turun di bawah $1/e$; menunjukkan skala waktu ketergantungan diri sinyal. |
| 24 | `calc_centroid` (Temporal Centroid) | $C = \dfrac{\sum_i t_i\,x_i^2}{\sum_i x_i^2}$ | "Pusat massa" sinyal pada sumbu waktu, dibobotkan oleh energi (kuadrat amplitudo) di setiap titik. |
| 25 | `distance` (Signal Distance) | $D = \sum_i \sqrt{1+(x_{i+1}-x_i)^2}$ | Total jarak tempuh sinyal, dihitung dari hipotenusa antar titik data berurutan. |
| 26 | `lempel_ziv` (LZ Complexity) | indeks LZ dari sinyal biner (threshold default = $\mu$), dinormalisasi thd panjang sinyal | Indeks kompleksitas Lempel-Ziv; mengukur tingkat keberagaman pola/kompleksitas sinyal. |
| 27 | `mean_abs_diff` | $\mathrm{MAD} = \dfrac{1}{N-1}\sum_i \lvert x_{i+1}-x_i\rvert$ | Rata-rata perubahan absolut antar sampel berurutan (contoh: MAD $=4{,}5$ pada slide 12). |
| 28 | `mean_diff` | $\dfrac{1}{N-1}\sum_i (x_{i+1}-x_i)$ | Rata-rata selisih (bertanda) antar sampel berurutan; menunjukkan tren naik/turun rata-rata. |
| 29 | `median_abs_diff` | $\mathrm{median}(\lvert x_{i+1}-x_i\rvert)$ | Median dari perubahan absolut antar sampel berurutan. |
| 30 | `median_diff` | $\mathrm{median}(x_{i+1}-x_i)$ | Median dari selisih (bertanda) antar sampel berurutan. |
| 31 | `negative_turning` | $\#\{i : \text{pola naik}\to\text{turun}\}$ | Jumlah titik balik negatif (puncak lokal yang berubah arah menurun) pada sinyal. |
| 32 | `neighbourhood_peaks` | $\#\{i : x_i > x_{i\pm 1},\dots,x_{i\pm n}\}$ | Jumlah puncak (peak) yang terdeteksi dalam suatu lingkungan bertetangga sepanjang sinyal. |
| 33 | `positive_turning` | $\#\{i : \text{pola turun}\to\text{naik}\}$ | Jumlah titik balik positif (lembah lokal yang berubah arah naik) pada sinyal. |
| 34 | `slope` | $m$ dari regresi linear $x(t) = m\,t+b$ | Kemiringan garis linear yang paling sesuai (least squares) terhadap data sinyal. |
| 35 | `sum_abs_diff` | $\sum_i \lvert x_{i+1}-x_i\rvert$ | Jumlah total perubahan absolut antar sampel berurutan sepanjang sinyal. |
| 36 | `zero_cross` (ZCR) | $\#\{i : \mathrm{sign}(x_{i+1}) \neq \mathrm{sign}(x_i)\}$ | Jumlah transisi sinyal dari positif ke negatif atau sebaliknya (contoh: ZCR $=4$ pada slide 10). |

---

## 3. Domain Spektral (26 fitur)

Fitur spektral menganalisis komposisi frekuensi sinyal, umumnya setelah transformasi Fourier (FFT). $X(f)$ menyatakan magnitudo spektrum pada frekuensi $f$.

| # | Nama Fitur | Rumus | Deskripsi |
|---|---|---|---|
| 37 | `fundamental_frequency` | $f_0 = \min\{f : X(f) \text{ puncak signifikan}, X(f) > 0{,}3\max X\}$ | Frekuensi dasar (fundamental) yang paling mewakili konten utama spektrum sinyal. |
| 38 | `human_range_energy` | $\dfrac{E_{0,6-2,5\,\text{Hz}}}{E_{total}}$ | Rasio energi sinyal pada rentang frekuensi gerak manusia (0,6–2,5 Hz) terhadap energi total spektrum. |
| 39 | `lpcc` (Linear Prediction Cepstral Coeff.) | koefisien cepstral dari koefisien LPC via rekursi cepstral | Koefisien yang menggambarkan karakteristik spektral sinyal berdasarkan model prediksi linear (umum pada pengolahan suara). |
| 40 | `max_frequency` | $f$ dengan $\mathrm{cumsum}(X(f)) = 0{,}95 \sum X(f)$ | Batas frekuensi atas di mana 95% energi spektrum sinyal sudah terkandung. |
| 41 | `max_power_spectrum` | $\max[\mathrm{PSD}(f)]$ (metode Welch) | Nilai puncak dari kerapatan spektrum daya (Power Spectral Density) sinyal. |
| 42 | `median_frequency` | $f$ dengan $\mathrm{cumsum}(X(f)) = 0{,}50 \sum X(f)$ | Frekuensi tengah (median) dari distribusi energi spektral sinyal. |
| 43 | `mfcc` (Mel-Freq. Cepstral Coeff.) | $\mathrm{DCT}\big(\log(\text{energi filterbank Mel})\big)$ | Koefisien cepstral berskala Mel yang merepresentasikan distribusi daya pada tiap pita frekuensi, umum untuk audio. |
| 44 | `power_bandwidth` | lebar pita frekuensi yang memuat 95% daya spektrum | Lebar pita (bandwidth) tempat sebagian besar (95%) daya sinyal terkonsentrasi. |
| 45 | `spectral_centroid` | $C = \dfrac{\sum_f f\,X(f)}{\sum_f X(f)}$ | "Pusat gravitasi" spektrum frekuensi; berkorelasi dengan persepsi kecerahan/brightness sinyal (contoh: Centroid $=1{,}25$ pada slide 24). |
| 46 | `spectral_decrease` | $\mathrm{SDec} = \dfrac{1}{\sum_{k=2}^{N} X(k)} \sum_{k=2}^{N} \dfrac{X(k)-X(1)}{k-1}$ | Menggambarkan seberapa cepat amplitudo spektrum menurun terhadap frekuensi. |
| 47 | `spectral_distance` | jarak antara $\mathrm{cumsum}(X(f))$ dan garis regresi liniernya | Jarak antara kumulatif spektrum FFT sinyal dan garis regresi liniernya; menunjukkan penyimpangan bentuk spektrum dari linier. |
| 48 | `spectral_entropy` | $H = -\dfrac{\sum_f p_f \log_2 p_f}{\log_2 N}$, $p_f = \dfrac{X(f)}{\sum X(f)}$ | Entropi Shannon dari spektrum daya sinyal; mengukur keacakan/kompleksitas kandungan frekuensi (contoh: $1{,}469$ bit pada slide 22). |
| 49 | `spectral_kurtosis` | $\kappa_{spec} = \dfrac{\sum_f (f-C)^4 X(f)}{\sum_f X(f)\cdot \mathrm{spread}^4}$ | Mengukur "keruncingan" distribusi spektrum di sekitar centroid-nya. |
| 50 | `spectral_positive_turning` | $\#\{f : \text{titik balik positif pada } \lvert X(f)\rvert\}$ | Jumlah titik balik naik pada sinyal magnitudo spektrum (FFT). |
| 51 | `spectral_roll_off` | $f$ dengan 95% magnitudo spektrum berada $\le f$ | Frekuensi ambang di mana 95% dari total magnitudo spektrum sudah terlingkupi. |
| 52 | `spectral_roll_on` | $f$ dengan 5% magnitudo spektrum berada $\le f$ | Frekuensi ambang bawah di mana baru 5% dari total magnitudo spektrum terlingkupi. |
| 53 | `spectral_skewness` | $\gamma_{spec} = \dfrac{\sum_f (f-C)^3 X(f)}{\sum_f X(f)\cdot \mathrm{spread}^3}$ | Mengukur asimetri distribusi spektrum di sekitar centroid-nya. |
| 54 | `spectral_slope` | $m$ dari regresi linear $X(f) = m f + b$ | Kemiringan garis linear terhadap amplitudo spektral sepanjang frekuensi. |
| 55 | `spectral_spread` | $\mathrm{spread} = \sqrt{\dfrac{\sum_f (f-C)^2 X(f)}{\sum_f X(f)}}$ | Standar deviasi/sebaran spektrum di sekitar centroid-nya; lebar "pita" tempat energi terkonsentrasi. |
| 56 | `spectral_variation` | $1 - \dfrac{\sum_f X_t(f)X_{t-1}(f)}{\sqrt{\sum_f X_t(f)^2}\sqrt{\sum_f X_{t-1}(f)^2}}$ | Jumlah variasi spektrum antar-waktu, dihitung dari korelasi silang ternormalisasi antara spektrum amplitudo yang berurutan. |
| 57 | `spectrogram_mean_coeff` | $\overline{\mathrm{PSD}}(f) = \dfrac{1}{T}\sum_t \mathrm{PSD}_t(f)$ | Rata-rata kerapatan spektrum daya untuk tiap bin frekuensi, dihitung dari spektrogram sinyal penuh. |
| 58 | `wavelet_abs_mean` | $\mathrm{mean}(\lvert \mathrm{CWT}_{scale}\rvert)$ | Nilai rata-rata absolut dari hasil Continuous Wavelet Transform (CWT) pada tiap skala wavelet. |
| 59 | `wavelet_energy` | $\sum (\mathrm{CWT}_{scale})^2$ | Energi hasil transformasi wavelet kontinu (CWT) pada tiap skala. |
| 60 | `wavelet_entropy` | entropi Shannon dari distribusi energi antar skala wavelet | Entropi dari distribusi energi CWT di seluruh skala wavelet; ukuran kompleksitas sinyal dalam domain waktu-skala. |
| 61 | `wavelet_std` | $\mathrm{std}(\mathrm{CWT}_{scale})$ | Standar deviasi dari hasil CWT pada tiap skala wavelet. |
| 62 | `wavelet_var` | $\mathrm{var}(\mathrm{CWT}_{scale})$ | Variansi dari hasil CWT pada tiap skala wavelet. |

---

## 4. Domain Fraktal (6 fitur)

Fitur fraktal mengukur kompleksitas/self-similarity sinyal, biasanya diterapkan pada sinyal yang relatif panjang (domain ini nonaktif secara default di TSFEL).

| # | Nama Fitur | Rumus | Deskripsi |
|---|---|---|---|
| 63 | `dfa` (Detrended Fluctuation Analysis) | $F(n) \propto n^{\alpha}$ | Eksponen skala $\alpha$ dari analisis fluktuasi ter-detrend; mengukur korelasi jangka panjang dalam sinyal. |
| 64 | `higuchi_fractal_dimension` (HFD) | $L(k) \propto k^{-D}$ | Dimensi fraktal $D$ sinyal, dihitung dari kemiringan hubungan panjang kurva $L(k)$ terhadap skala $k$ (metode Higuchi). |
| 65 | `hurst_exponent` | $\dfrac{R}{S} \propto n^{H}$ | Eksponen Hurst $H$ dari analisis Rescaled Range (R/S); menunjukkan sifat persistensi/anti-persistensi deret waktu. |
| 66 | `maximum_fractal_length` (MFL) | $\mathrm{MFL} = \log\big(\overline{L(k_{min})}\big)$ | Panjang fraktal maksimum; rata-rata panjang kurva pada skala terkecil dari plot logaritmik penentu dimensi fraktal (metode Higuchi). |
| 67 | `mse` (Multiscale Entropy) | $\mathrm{MSE}_{area} = \dfrac{1}{K}\sum_{s=1}^{K} \mathrm{SampEn}(s)$ | Analisis entropi sinyal pada berbagai skala waktu (coarse-graining), menghasilkan luas area ternormalisasi di bawah kurva MSE. |
| 68 | `petrosian_fractal_dimension` (PFD) | $\mathrm{PFD} = \dfrac{\log_{10} N}{\log_{10} N + \log_{10}\!\left(\dfrac{N}{N+0{,}4\,N_\Delta}\right)}$ | Dimensi fraktal Petrosian, dihitung cepat dari jumlah perubahan arah turunan sinyal $N_\Delta$. |

---

### Sumber
Daftar dan klasifikasi domain fitur disusun berdasarkan dokumentasi resmi TSFEL 0.2.0 (tsfel.readthedocs.io) dan source code `tsfel/feature_extraction/features.py` (fraunhoferportugal/tsfel). Notasi rumus ditulis ulang dalam bentuk LaTeX standar, bukan salinan kode sumber.

### Langkah Ekstraksi Fitur

```code-cell
import pandas as pd
import numpy as np
import inspect
import tsfel.feature_extraction.features as tsfel_features

# Muat data hasil preprocessing

df = pd.read_csv('../file/NO2_Jogoroto_filled.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# Target kolom

target_pollutant = 'NO2'

df[target_pollutant] = pd.to_numeric(df[target_pollutant], errors='coerce')

# Tetap pastikan data bersih dan urut berdasarkan waktu

df_clean = df.set_index('date').interpolate(method='time').ffill().bfill()
fs = 1
signal_1d = df_clean[target_pollutant].astype(float).values

# 68 fitur TSFEL
FEATURE_LIST = """abs_energy auc autocorr average_power calc_centroid calc_max calc_mean
calc_median calc_min calc_std calc_var dfa distance ecdf ecdf_percentile ecdf_percentile_count
ecdf_slope entropy fundamental_frequency higuchi_fractal_dimension hist_mode human_range_energy
hurst_exponent interq_range kurtosis lempel_ziv lpcc max_frequency max_power_spectrum
maximum_fractal_length mean_abs_deviation mean_abs_diff mean_diff median_abs_deviation
median_abs_diff median_diff median_frequency mfcc mse negative_turning neighbourhood_peaks
petrosian_fractal_dimension pk_pk_distance positive_turning power_bandwidth rms skewness slope
spectral_centroid spectral_decrease spectral_distance spectral_entropy spectral_kurtosis
spectral_positive_turning spectral_roll_off spectral_roll_on spectral_skewness spectral_slope
spectral_spread spectral_variation spectrogram_mean_coeff sum_abs_diff wavelet_abs_mean
wavelet_energy wavelet_entropy wavelet_std wavelet_var zero_cross""".split()

print('Jumlah fitur yang diproses:', len(FEATURE_LIST))

# Fungsi bantu untuk merubah output TSFEL menjadi skalar

def to_scalar(result):
    if isinstance(result, dict) and 'values' in result:
        result = result['values']
    if isinstance(result, (list, tuple, np.ndarray)):
        arr = np.asarray(result, dtype=float)
        return float(np.nanmean(arr))
    return float(result)

# Fungsi ekstraksi satu fitur

def extract_one(fn_name, signal, fs):
    fn = getattr(tsfel_features, fn_name)
    params = inspect.signature(fn).parameters
    if 'fs' in params:
        result = fn(signal, fs)
    else:
        result = fn(signal)
    return to_scalar(result)

# Ekstraksi fitur
row = {}
for fn_name in FEATURE_LIST:
    row[fn_name] = extract_one(fn_name, signal_1d, fs)

extracted_features_final = pd.DataFrame([row])

print(f'Berhasil mengekstrak {extracted_features_final.shape[1]} fitur dari data {target_pollutant}')

# Simpan hasil ekstraksi
extracted_features_final.to_csv('../file/NO2_Jogoroto_TSFEL.csv', index=False)
```

### Hasil Ekstraksi Fitur

Data hasil ekstraksi dapat dilihat pada file CSV berikut:

- `../file/NO2_Jogoroto_TSFEL.csv`

File ini berisi 68 kolom fitur yang mewakili karakteristik statistik, temporal, dan spektral dari deret waktu NO2 di wilayah Jogoroto.

---


## 5. Penjelasan Singkat

Proses preprocessing dan ekstraksi fitur ini sangat penting karena data mentah sering kali mengandung noise, missing value, dan outlier yang dapat mengganggu kualitas analisis. Dengan menangani semua ketidakrataan tersebut terlebih dahulu, fitur yang dihasilkan akan lebih representatif dan stabil untuk dipakai pada tahap berikutnya, seperti pemodelan prediksi, klasifikasi, atau analisis pola spasial-temporal.

Pada konteks penelitian ini, penggunaan TSFEL memungkinkan ekstraksi fitur dari data NO2 wilayah Jogoroto secara otomatis dan konsisten. Total 68 fitur yang diperoleh mencakup karakteristik statistik, temporal, dan spektral sehingga dapat mendukung pengambilan keputusan berbasis data dengan lebih baik.

