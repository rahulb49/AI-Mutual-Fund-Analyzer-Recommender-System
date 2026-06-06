Presentation build instructions

1. Install dependencies

```bash
pip install python-pptx pillow
# Optional (diagram rendering):
# pip install cairosvg
# or install mermaid-cli to export mermaid diagrams as SVG/PNG
```

2. Generate PPTX

```bash
python presentation/build_presentation.py --output presentation/AI_Mutual_Fund_Presentation.pptx
```

3. (Optional) Convert PPTX to PDF using LibreOffice

```bash
soffice --headless --convert-to pdf presentation/AI_Mutual_Fund_Presentation.pptx --outdir presentation/
```

4. Diagrams

- Mermaid source files are in `presentation/diagrams/`. If you want image diagrams in the slides, render the `.mmd` files to PNG/SVG and place the PNG next to the `.mmd` with the same basename (e.g., `architecture.png`). The generator will include the PNG if present, otherwise it will insert the mermaid source as text.

5. Notes

- The script `presentation/build_presentation.py` uses `presentation/slide_content.md` as the slide source. Edit that file to tweak slide titles and bullet points before building.
- If you want me to render the diagrams to PNG and embed them, I can attempt to install `cairosvg` and `mermaid-cli` locally and generate the images (confirm if you'd like me to proceed).
