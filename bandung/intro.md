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

# Polutan di Kecamatan Bandung - Kabupaten Jombang

Pada studi kasus ini, kita akan membahas secara komprehensif mengenai analisis
data deret waktu (time series) untuk konsentrasi polutan udara di wilayah Kecamatan Bandung, Kabupaten Jombang. Fokus utama analisis ini adalah pada tiga jenis gas polutan utama, yaitu:

- Karbon Monoksida (CO)
- Sulfur Dioksida (SO₂)
- Nitrogen Dioksida (NO₂)

Proyek ini bertujuan untuk mengidentifikasi pola, melakukan eksplorasi data mentah,
dan memahami dinamika kualitas udara di wilayah ini dengan pendekatan sains data.

Berikut adalah alur tahapan analisis yang dilakukan dalam studi kasus ini:

1. [Business Understanding](bisnis.md) membahas latar belakang permasalahan, tujuan analisis, serta manfaat dari pemantauan kualitas udara di Kecamatan Bandung.
2. [Data Understanding](undestanding.md) meliputi pengumpulan data deret waktu untuk ketiga polutan serta eksplorasi awal untuk menemukan pola, missing value, dan outlier.
3. [Data Preprocessing dan Ekstraksi Fitur](../data_prepocessing/intro.md) menjelaskan pembersihan data, penanganan outlier, dan ekstraksi fitur time series.
4. [K-Means Clustering](../data_understanding/matrix.md) menyajikan eksperimen pengelompokan pola polutan menggunakan pendekatan clustering.

Setiap tahapan dirancang agar hasil analisis dapat dipahami secara bertahap, mulai dari konteks bisnis, pemahaman data, hingga interpretasi pola dan klaster yang muncul.

## Mengapa Kecamatan Bandung?

Kecamatan Bandung berada di wilayah Kabupaten Jombang yang memiliki dinamika aktivitas manusia cukup tinggi, seperti transportasi, pergerakan masyarakat, serta aktivitas ekonomi yang berpotensi memengaruhi kualitas udara. Oleh karena itu, pemantauan konsentrasi polutan menjadi penting untuk mengetahui kondisi lingkungan secara objektif.

## Tujuan Proyek

Proyek ini bertujuan untuk:

- Memahami pola temporal konsentrasi CO, SO₂, dan NO₂ di Kecamatan Bandung.
- Mengetahui munculnya anomali atau outlier pada data pengamatan.
- Menyediakan dasar analisis yang lebih kuat bagi pengambilan keputusan lingkungan dan kebijakan daerah.

## Fokus Analisis

Analisis dilakukan dengan memanfaatkan data satelit Sentinel-5P yang diolah menjadi data time series harian, lalu dibandingkan antara ketiga jenis polutan. Dengan pendekatan ini, kita dapat melihat apakah ada pola yang konsisten, tren musiman, atau peristiwa tertentu yang memengaruhi kualitas udara di wilayah tersebut.
