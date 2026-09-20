import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

base = "c:/Users/NEC VH-3/Documents/MyPSD"
img_dir = os.path.join(base, "img")
os.makedirs(img_dir, exist_ok=True)

rng = np.random.default_rng(7)

# PCA reduction illustration: 15 features reduced into principal components
variance = np.array([0.21, 0.18, 0.15, 0.12, 0.10, 0.08, 0.06, 0.04, 0.03, 0.02, 0.01, 0.008, 0.006, 0.004, 0.003])
labels = [f"PC{i+1}" for i in range(15)]
fig, ax = plt.subplots(figsize=(10, 5), dpi=180)
ax.bar(labels, variance, color="#6c8ebf", edgecolor="black", linewidth=0.5)
ax.set_title("PCA: Reduksi 15 Fitur Menjadi Komponen Utama", fontsize=12)
ax.set_ylabel("Explained variance")
ax.set_xlabel("Komponen utama")
ax.set_ylim(0, 0.25)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
fig.savefig(os.path.join(img_dir, "pca_bandung.png"), bbox_inches="tight")
plt.close(fig)

# KMeans after PCA: 3 clusters
centers = np.array([
    [2.8, 3.2],
    [-2.0, 2.0],
    [0.5, -2.8],
])
all_pts = []
all_labels = []
for i, c in enumerate(centers):
    pts = rng.normal(loc=c, scale=1.0, size=(35, 2))
    all_pts.append(pts)
    all_labels.extend([i] * len(pts))
all_pts = np.vstack(all_pts)
all_labels = np.array(all_labels)

fig, ax = plt.subplots(figsize=(10, 5), dpi=180)
for i in range(3):
    mask = all_labels == i
    ax.scatter(all_pts[mask, 0], all_pts[mask, 1], s=35, alpha=0.82, label=f"Cluster {i + 1}")
ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
ax.axvline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
ax.set_title("K-Means pada PCA (15 Fitur -> 3 Cluster)", fontsize=12)
ax.set_xlabel("PC 1")
ax.set_ylabel("PC 2")
ax.legend(frameon=False)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
plt.tight_layout()
fig.savefig(os.path.join(img_dir, "kmeans_pca_bandung.png"), bbox_inches="tight")
plt.close(fig)

print("Generated:")
print(os.path.join(img_dir, "pca_bandung.png"))
print(os.path.join(img_dir, "kmeans_pca_bandung.png"))
