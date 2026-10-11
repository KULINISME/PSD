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
# 1. Business Understanding

## Latar Belakang

Pengelolaan ruang wilayah dan pemeliharaan lingkungan hidup memerlukan data yang akurat, terkini, dan dapat diakses secara cepat. Dalam praktiknya, pemerintah pusat maupun daerah memiliki tanggung jawab untuk menyusun dan mengawasi perencanaan tata ruang, termasuk Rencana Tata Ruang Wilayah (RTRW) dan Rencana Detail Tata Ruang (RDTR). Proses pemutakhiran data tutupan lahan serta penggunaan lahan menjadi faktor penting dalam mendukung keputusan strategis, terutama dalam konteks ketahanan pangan, pengendalian urbanisasi, serta perlindungan ekosistem pesisir dan hutan.

Kendala utama yang sering dihadapi adalah keterlambatan pemutakhiran data karena proses survei lapangan secara manual masih memerlukan waktu yang lama dan biaya yang relatif tinggi. Kondisi ini berdampak pada lambatnya deteksi perubahan lahan, misalnya konversi lahan sawah menjadi kawasan permukiman, alih fungsi kawasan mangrove, atau perubahan tutupan hutan yang tidak sesuai dengan perencanaan tata ruang. Dalam situasi seperti ini, data yang tidak mutakhir dapat menghambat pengambilan keputusan dan meningkatkan risiko pelanggaran zonasi.

Di sisi lain, perkembangan teknologi penginderaan jauh dan data citra satelit beresolusi menengah hingga tinggi, seperti Sentinel-2A, membuka peluang besar untuk mengembangkan sistem pemantauan lahan secara otomatis. Data satelit yang tersedia dalam volume besar dan pembaruan berkala dapat dimanfaatkan untuk menganalisis perubahan tutupan lahan secara berkelanjutan. Namun, kapasitas manusia untuk memproses data dalam jumlah besar secara manual terbatas. Oleh karena itu, diperlukan pendekatan berbasis Machine Learning yang dapat mengotomatisasi proses klasifikasi lahan serta mengubah data raw geospasial menjadi informasi yang siap dipakai untuk pengambilan keputusan publik.

Berdasarkan pertimbangan tersebut, proyek ini dirancang sebagai upaya untuk membangun suatu pipeline analisis data geospasial yang mampu mengklasifikasikan tutupan lahan secara otomatis dan terukur. Fokus utama proyek ini adalah pada penggunaan data citra satelit untuk mengidentifikasi enam kelas utama lahan, yaitu sawah, bangunan, mangrove, hutan, laut, dan danau. Dengan demikian, proyek ini tidak hanya menjadi studi teknis analisis citra, tetapi juga merupakan solusi kebijakan yang selaras dengan kebutuhan pemerintah dalam mendukung tata ruang yang presisi dan berkelanjutan.

## Tujuan Bisnis

Proyek ini bertujuan untuk menjembatani kebutuhan analisis kebijakan publik dengan solusi rekayasa data dan perangkat lunak melalui penerapan pendekatan Machine Learning pada data penginderaan jauh. Tujuan bisnisnya dapat dibagi menjadi dua dimensi utama, yaitu dimensi kebijakan dan dimensi teknis.

### Dimensi Kebijakan Publik

Tujuan utama dari sisi kebijakan adalah menyediakan dasar data yang aktual dan andal bagi pemerintah dalam pengambilan keputusan terkait tata ruang dan pengelolaan lingkungan. Dengan keberadaan peta tutupan lahan yang terus diperbarui, pemerintah dapat memantau perkembangan lahan secara lebih cepat dan akurat. Informasi ini sangat penting untuk mendukung pengawasan ketahanan pangan, pemetaan ekspansi kawasan terbangun, perlindungan ekosistem mangrove dan hutan, serta pengelolaan sumber daya air.

Secara operasional, hasil klasifikasi lahan dapat digunakan untuk mempercepat proses audit tata ruang dari yang semula memerlukan waktu berbulan-bulan menjadi lebih cepat, bahkan dalam hitungan jam. Dengan demikian, keputusan yang menyangkut pengendalian alih fungsi lahan dapat diambil berdasarkan bukti data yang lebih mutakhir dan konsisten.

### Dimensi Pengembangan Perangkat Lunak

Dari sisi pengembangan perangkat lunak, proyek ini bertujuan untuk merancang sebuah pipeline pemrosesan data geospasial yang scalable, efisien, dan mudah diintegrasikan ke dalam sistem informasi pemerintah. Pipeline ini mencakup proses pengambilan data citra, preprocessing, eksplorasi fitur, pelatihan model, evaluasi performa, serta visualisasi hasil klasifikasi. Infrastruktur yang dibangun diharapkan menjadi fondasi bagi pengembangan aplikasi atau layanan berbasis API di masa depan.

Dalam konteks eksperimen teknis, proyek ini juga bertujuan untuk membandingkan performa dua algoritma klasifikasi yang umum digunakan, yaitu Naive Bayes dan K-Nearest Neighbors (KNN). Perbandingan tersebut tidak hanya menilai akurasi model, tetapi juga mempertimbangkan efisiensi komputasi, termasuk waktu pelatihan dan waktu inferensi. Tujuannya adalah memilih model yang mampu memberikan hasil klasifikasi yang handal tanpa membebani infrastruktur sistem secara berlebihan.

## Manfaat dan Dampak yang Diharapkan

Proyek ini diharapkan memberikan manfaat yang luas bagi berbagai pemangku kepentingan. Bagi pemerintah, hasil analisis dapat menjadi pendukung keputusan strategis dalam perencanaan dan pengawasan tata ruang. Bagi peneliti dan akademisi, data dan model yang dihasilkan dapat menjadi dasar untuk studi lanjutan mengenai dinamika perubahan lahan serta pola penggunaan lahan. Sementara itu, bagi para pengembang data dan sistem informasi geospasial, proyek ini menjadi contoh implementasi teknis yang menggabungkan analisis geospasial, Machine Learning, dan kebutuhan kebijakan publik dalam satu ekosistem yang terintegrasi.

Pada level yang lebih luas, proyek ini berkontribusi pada pembangunan sistem pengelolaan lingkungan yang berbasis data, yang secara langsung mendukung upaya penguatan tata kelola sumber daya alam, peningkatan akuntabilitas kebijakan publik, dan efisiensi operasional dalam pengawasan lahan.

## Kriteria Keberhasilan

### Keberhasilan Teknis

Keberhasilan teknis proyek diukur berdasarkan kemampuan model klasifikasi yang dipilih untuk mengklasifikasikan enam kelas tutupan lahan secara akurat dan konsisten. Model yang terpilih diharapkan mampu mencapai metrik evaluasi yang memenuhi ambang batas yang telah ditentukan, seperti akurasi, precision, recall, atau F1-score. Selain itu, pipeline analisis harus dapat berjalan secara otomatis, mulai dari ingest data citra hingga output klasifikasi, tanpa memerlukan intervensi manual yang berulang.

### Keberhasilan Bisnis dan Kebijakan

Keberhasilan bisnis diperlihatkan melalui kemampuan sistem untuk menghasilkan informasi yang dapat dimanfaatkan oleh pihak berwenang dalam proses pengawasan serta perencanaan wilayah. Dengan demikian, proyek ini diharapkan dapat menghasilkan prototipe visualisasi atau layanan berbasis API yang memungkinkan analis tata ruang untuk mengevaluasi perubahan lahan secara interaktif dan cepat. Dampak yang diharapkan adalah meningkatnya efisiensi kerja operasional, pengurangan waktu survei lapangan, dan peningkatan kualitas keputusan yang didasarkan pada data yang lebih mutakhir.

Secara keseluruhan, proyek ini merupakan upaya strategis untuk mengintegrasikan analisis data geospasial dengan kebutuhan manajerial dan kebijakan publik. Melalui pendekatan berbasis data dan teknologi, pengelolaan lahan dapat dilakukan secara lebih terukur, efisien, dan berkelanjutan.
