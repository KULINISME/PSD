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
# Data Preprocessing

Bayangkan Anda adalah seorang koki yang ingin memasak hidangan istimewa. Sebelum mulai memasak, Anda tidak mungkin langsung melempar sayuran yang baru dibeli dari pasar—beserta tanah, akar, dan plastiknya—ke dalam panci, bukan? 

Anda pasti akan mencuci sayuran tersebut, mengupas kulitnya, memotong bagian yang layu, dan menakar bumbu dengan pas.

Dalam dunia Sains Data (*Data Science*), **Data Preprocessing** adalah proses "mencuci dan memotong bahan" tersebut. Ini adalah tahap persiapan awal di mana kita membersihkan, merapikan, dan menyaring data mentah agar siap "dimasak" (diolah) oleh komputer atau algoritma kecerdasan buatan.

## Mengapa Ini Sangat Penting?

Ada aturan emas di dunia data: **"Garbage In, Garbage Out" (Sampah yang masuk, sampah pula yang keluar)**. 

Jika kita memberikan data yang berantakan, kotor, atau salah kepada komputer, maka hasil analisis atau prediksi yang dikeluarkan komputer juga akan melenceng dan tidak bisa dipercaya. Sebaliknya, data yang rapi akan menghasilkan sistem yang cerdas dan akurat.

## 3 Langkah Utama dalam Data Preprocessing (Dalam Bahasa Sehari-hari)

### 1. Membersihkan Data (*Data Cleaning*)
Data di dunia nyata sering kali berantakan. Kadang ada informasi yang hilang, salah ketik, atau sama sekali tidak masuk akal.
* **Contoh Kasus Transaksi E-commerce:** Misalnya kita sedang menganalisis ribuan data pesanan (*detail_pesanan*) pembeli. Tiba-tiba ada pelanggan yang umurnya tertulis "250 tahun" (tidak masuk akal), atau kolom jumlah barang kosong. Pada tahap ini, kita harus memperbaiki data yang salah tersebut, membuangnya, atau mengisi kekosongannya agar perhitungan sistem tidak kacau.

### 2. Menyeragamkan Format (*Data Transformation*)
Komputer butuh keseragaman agar tidak kebingungan saat membaca pola.
* **Contoh Kasus Mesin Pencari Artikel:** Jika kita sedang membangun sistem mesin pencari untuk artikel akademik, komputer bisa menganggap kata "Teknologi", "TEKNOLOGI", dan "teknologi" sebagai tiga hal yang berbeda. Di tahap ini, kita mengubah semua teks menjadi huruf kecil dan membuang tanda baca yang mengganggu, sehingga sistem pencarian bisa berjalan jauh lebih pintar dan cepat.

### 3. Memilah yang Penting Saja (*Data Reduction / Feature Selection*)
Tidak semua data yang kita miliki itu berguna. Membawa terlalu banyak data yang tidak relevan hanya akan membuat komputer bekerja terlalu berat dan lambat.
* **Contoh:** Jika kita ingin membuat sistem yang memprediksi apakah seseorang akan membeli buku pemrograman atau tidak, kita mungkin butuh data riwayat pencarian dan usia mereka. Tapi, kita **tidak butuh** data golongan darah atau warna baju favorit mereka. Data yang tidak ada hubungannya ini kita singkirkan saja.
