import os
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Config
# -----------------------------
from pathlib import Path

ROOT_DIR = Path("/home/pace-ubuntu/datasets/leica/EAST/pycolmap/5_output_test_24_horizontal_yaw_strict_match/images")
# ROOT_DIR = Path("/home/pace-ubuntu/datasets/leica/EAST/pycolmap/output_original/images")

OUTPUT_PATH = ROOT_DIR / "collage.png"  # use the / operator to join paths

IMAGES_PER_DIR = 5
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")

# Resize all images to same size for clean grid
CELL_WIDTH = 256
CELL_HEIGHT = 256
TEXT_HEIGHT = 20  # extra space for file names

# Font for text
try:
    FONT = ImageFont.truetype("arial.ttf", 16)
except:
    FONT = ImageFont.load_default()

# -----------------------------
# Collect images
# -----------------------------
rows = []
labels = []

subdirs = sorted([
    d for d in os.listdir(ROOT_DIR)
    if os.path.isdir(os.path.join(ROOT_DIR, d))
])

import re

def natural_sort_key(s):
    # Extract number at the end of the string
    m = re.search(r'(\d+)$', s)
    return int(m.group(1)) if m else float('inf')

subdirs = sorted(subdirs, key=natural_sort_key)


for subdir in subdirs:
    subdir_path = os.path.join(ROOT_DIR, subdir)

    images = sorted([
        f for f in os.listdir(subdir_path)
        if f.lower().endswith(IMAGE_EXTS)
    ])[:IMAGES_PER_DIR]

    images = sorted(images, key=natural_sort_key)

    if len(images) < IMAGES_PER_DIR:
        print(f"Skipping {subdir}: not enough images")
        continue

    row_images = []
    row_labels = []
    for img_name in images:
        img_path = os.path.join(subdir_path, img_name)
        img = Image.open(img_path).convert("RGB")
        img = img.resize((CELL_WIDTH, CELL_HEIGHT), Image.BILINEAR)
        row_images.append(img)
        row_labels.append(img_name)

    rows.append(row_images)
    labels.append((subdir, row_labels))

# -----------------------------
# Create collage
# -----------------------------
num_rows = len(rows)
num_cols = IMAGES_PER_DIR

collage_width = num_cols * CELL_WIDTH
collage_height = num_rows * (CELL_HEIGHT + TEXT_HEIGHT*2)  # extra for text

collage = Image.new("RGB", (collage_width, collage_height), (0, 0, 0))
draw = ImageDraw.Draw(collage)

for r, row in enumerate(rows):
    subdir_name, file_names = labels[r]

    for c, img in enumerate(row):
        x = c * CELL_WIDTH
        y = r * (CELL_HEIGHT + TEXT_HEIGHT*2)

        # Paste image
        collage.paste(img, (x, y))

        # Draw file name below image
        draw.text((x + 5, y + CELL_HEIGHT), file_names[c], fill=(255, 255, 255), font=FONT)

    # Draw subdirectory name at the start of row (first column)
    draw.text((5, r * (CELL_HEIGHT + TEXT_HEIGHT*2) - TEXT_HEIGHT//2), subdir_name, fill=(255, 255, 0), font=FONT)

collage.save(OUTPUT_PATH)
print(f"Saved collage to {OUTPUT_PATH}")
