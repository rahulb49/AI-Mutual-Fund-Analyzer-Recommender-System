from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / 'architecture.png'
W, H = 1200, 800
img = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype('arial.ttf', 14)
except Exception:
    font = ImageFont.load_default()

# Helper to draw a labeled box
def box(x, y, w, h, text, fill='#EFEFEF'):
    d.rectangle([x, y, x+w, y+h], fill=fill, outline='black')
    # center text
    lines = text.split('\n')
    ty = y + 8
    for line in lines:
        try:
            bbox = d.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except Exception:
            tw, th = font.getsize(line)
        d.text((x + (w-tw)/2, ty), line, fill='black', font=font)
        ty += th + 2

# Draw components
box(40, 40, 200, 60, 'AMFI NAV\n(NAVAll.txt)')
box(300, 40, 200, 60, 'Ingestion')
box(560, 40, 220, 60, 'Data Cleaning')
box(840, 40, 260, 60, 'Feature Engineering')
box(560, 160, 220, 60, 'Data Store / CSVs')
box(300, 300, 220, 60, 'FastAPI Backend')
box(840, 300, 260, 60, 'Streamlit Dashboard')
box(560, 420, 220, 60, 'ML: Clustering /\nRanking / Recommendation')

# Airflow group
d.rectangle([260, 20, 930, 520], outline='blue', width=2)
d.text((265,22), 'Airflow', fill='blue', font=font)

# Arrows
def arrow(x1,y1,x2,y2):
    d.line([x1,y1,x2,y2], fill='black', width=2)
    # arrowhead
    ax = x2; ay = y2
    import math
    angle = math.atan2(y2-y1, x2-x1)
    l = 10
    pa1 = (ax - l*math.cos(angle - 0.4), ay - l*math.sin(angle - 0.4))
    pa2 = (ax - l*math.cos(angle + 0.4), ay - l*math.sin(angle + 0.4))
    d.polygon([ (ax,ay), pa1, pa2 ], fill='black')

arrow(240,70,300,70) # AMFI -> Ingestion
arrow(500,70,560,70) # Ingestion -> Cleaning
arrow(780,70,840,70) # Cleaning -> Feature Eng
arrow(960,100,960,160) # Feature Eng -> Data Store
arrow(670,220,420,300) # Data Store -> FastAPI
arrow(820,220,940,300) # Feature Eng -> Dashboard
arrow(670,220,670,420) # Feature Eng -> ML
arrow(770,450,940,330) # ML -> Dashboard

# Save
img.save(OUT)
print(f'Wrote {OUT}')
