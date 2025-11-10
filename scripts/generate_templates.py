"""
generate_templates.py
Compute mean landmark vector (21 x 3 => 63 values) per class from landmarks.csv
and save each as numpy .npy in ../outputs/text_to_sign/templates/
Also writes mapping.json with sorted class list.
"""

import os
import numpy as np
import pandas as pd
import json

BASE = "/Users/srishtisindgi/samvaad_project"
CSV = os.path.join(BASE, "outputs", "landmarks.csv")
OUT_DIR = os.path.join(BASE, "outputs", "text_to_sign", "templates")
MAPPING = os.path.join(BASE, "outputs", "text_to_sign", "mapping.json")

os.makedirs(OUT_DIR, exist_ok=True)

# Read CSV
df = pd.read_csv(CSV)

# Each row: label,x0,y0,z0,...,x20,y20,z20
labels = df['label'].unique()
labels_sorted = sorted(labels, key=lambda s: (len(s), s))  # simple stable sort

# compute mean vector per label
for lbl in labels_sorted:
    subset = df[df['label'] == lbl].drop(columns=['label']).values
    mean_vec = np.mean(subset, axis=0)  # shape (63,)
    out_path = os.path.join(OUT_DIR, f"{lbl}.npy")
    np.save(out_path, mean_vec.astype(np.float32))
    print(f"Saved template for {lbl} -> {out_path}")

# save mapping
with open(MAPPING, "w") as f:
    json.dump({"classes": labels_sorted}, f, indent=2)
print(f"\nSaved mapping: {MAPPING}")
print("Template generation complete.")
