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
# 3. Modelling Klasifikasi

Tahap modelling merupakan proses membangun model klasifikasi yang dapat mempelajari pola dari data pelatihan dan kemudian menggunakannya untuk memprediksi kelas tutupan lahan pada data uji. Dalam proyek ini, setiap piksel dianggap sebagai sampel data, sedangkan fitur seperti nilai reflektansi band dan indeks spektral (`B02`, `B03`, `B04`, `B08`, `B11`, `NDVI`, `NDWI`, `MNDWI`, `NDBI`) dijadikan variabel input untuk membedakan kelas seperti sawah, bangunan, hutan, danau, laut, serta mangrove.

Model yang digunakan pada tahap ini adalah Naive Bayes dan K-Nearest Neighbors (KNN). Naive Bayes bekerja berdasarkan probabilitas kelas dengan asumsi bahwa antar fitur tidak saling bergantung secara penuh, sehingga cocok digunakan pada data numerik yang memiliki karakteristik distribusi tertentu. Sementara itu, KNN bekerja dengan cara mencari tetangga terdekat pada ruang fitur; kelas suatu sampel ditentukan berdasarkan kelas yang paling dominan dari sejumlah tetangga terdekat.

Sebelum pelatihan, data dibagi menjadi data latih dan data uji menggunakan `train_test_split` agar model dinilai pada data yang belum pernah dilihat sebelumnya. Selanjutnya, fitur dinormalisasi menggunakan `StandardScaler` supaya skala antar fitur seragam dan tidak memengaruhi hasil klasifikasi. Setelah model dilatih, evaluasi dilakukan dengan akurasi dan `classification_report` untuk melihat sejauh mana model mampu mengenali setiap kelas secara keseluruhan dan per kelas.

```{code-cell}

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('../hasil_s2_piksel/dataset.csv')
fitur = ['B02', 'B03', 'B04', 'B08', 'B11', 'NDVI', 'NDWI', 'MNDWI', 'NDBI']
df_bersih = df.dropna(subset=fitur + ['label_teks']).copy()

X = df_bersih[fitur]
y = df_bersih['label_teks']
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

```{code-cell}
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report

nb_model = GaussianNB()
nb_model.fit(X_train_scaled, y_train)
y_pred_nb = nb_model.predict(X_test_scaled)

print("=== HASIL EVALUASI NAIVE BAYES ===")
print(f"Akurasi Keseluruhan : {accuracy_score(y_test, y_pred_nb) * 100:.2f}%\n")
print(classification_report(y_test, y_pred_nb))
```

```{code-cell}
from sklearn.neighbors import KNeighborsClassifier

knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X_train_scaled, y_train)
y_pred_knn = knn_model.predict(X_test_scaled)

print("=== HASIL EVALUASI KNN ===")
print(f"Akurasi Keseluruhan : {accuracy_score(y_test, y_pred_knn) * 100:.2f}%\n")
print(classification_report(y_test, y_pred_knn))
```
