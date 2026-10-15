"""
Traduction du rulebook PDF via Gemini Nano Banana 2.1.
1. Convertit chaque page en image
2. Envoie a Gemini pour traduction FR
3. Reassemble en PDF
"""
import json
import os
import time
import sys
import fitz  # PyMuPDF
from PIL import Image
from google import genai
from google.genai import types

PROJ = "C:/Users/hiind/projects/satisfactory-tts-fr"

# --- Config ---
with open(f"{PROJ}/.env", "rb") as f:
    env_text = f.read().decode("utf-16").strip()
for line in env_text.splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

GLOSSARY = """
GLOSSAIRE DE TRADUCTION (a respecter strictement) :
- tile -> case
- player tile -> case du joueur
- adjacent tile -> case adjacente
- creature -> creature
- biomass -> biomasse
- belt -> convoyeur
- miner -> foreuse
- constructor -> constructeur
- assembler -> assembleur
- manufacturer -> fabricant
- depot -> depot
- power -> energie
- power management -> gestion d'energie
- production phase -> phase de production
- upgrade -> amelioration
- build range -> portee de construction
- movement range -> portee de deplacement
- tool slot -> emplacement d'outil
- extractor -> extracteur
- milestone -> milestone (garder en anglais)
- blueprint -> blueprint (garder en anglais)
- overclock -> overclock (garder en anglais)
- HUB -> HUB (garder en anglais)
- MAM -> MAM (garder en anglais)
- A.W.E.S.O.M.E. Sink -> A.W.E.S.O.M.E. Sink (garder en anglais)
- Power Shard -> Power Shard (garder en anglais)
- workshop -> workshop (garder en anglais)
- FICSIT -> FICSIT (garder en anglais)
- Pioneer -> Pionnier
"""

PROMPT = f"""Tu es un outil de traduction visuelle de pages de regles de jeu de societe.

Voici une page du rulebook du jeu de societe Satisfactory (adaptation plateau du jeu video).

Tu dois regenerer EXACTEMENT la meme image avec ces modifications :
- TOUT le texte anglais doit etre traduit en FRANCAIS
- Les titres de sections doivent etre traduits
- Les icones, couleurs, mise en page, bordures, illustrations doivent rester IDENTIQUES
- La police, la taille du texte et le style doivent etre conserves exactement
- Les dimensions de l'image doivent etre EXACTEMENT les memes que l'original
- Les diagrammes et schemas doivent garder leur texte traduit en francais

{GLOSSARY}

Genere l'image traduite, identique pixel-perfect sauf le texte traduit en francais."""


def translate_page(image_path, output_path):
    """Envoie une page a Gemini et recupere la version FR."""
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-nano-banana-2.1",
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text=PROMPT),
                            types.Part(
                                inline_data=types.Blob(mime_type="image/png", data=image_bytes)
                            ),
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_modalities=["image", "text"],
                ),
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    with open(output_path, "wb") as f:
                        f.write(part.inline_data.data)
                    return True

            print(f"  [WARN] Pas d'image, tentative {attempt+1}")
        except Exception as e:
            print(f"  [ERR] {e}, tentative {attempt+1}")
            time.sleep(5)

    return False


def main():
    pages_dir = f"{PROJ}/rulebook-pages"
    pages_tr_dir = f"{PROJ}/rulebook-pages-translated"
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(pages_tr_dir, exist_ok=True)

    # Progress tracking
    progress_file = f"{PROJ}/rulebook-progress.json"
    if os.path.exists(progress_file):
        with open(progress_file) as f:
            progress = json.load(f)
    else:
        progress = {}

    # Phase 1: Extract pages
    print("=== Phase 1: Extraction des pages du PDF ===")
    doc = fitz.open(f"{PROJ}/rulebook-original.pdf")
    total_pages = len(doc)
    print(f"  {total_pages} pages")

    for i in range(total_pages):
        page_path = f"{pages_dir}/page_{i:03d}.png"
        if not os.path.exists(page_path):
            page = doc[i]
            pix = page.get_pixmap(dpi=200)
            pix.save(page_path)
    doc.close()
    print("  Pages extraites")

    # Phase 2: Translate each page
    print(f"\n=== Phase 2: Traduction via Gemini ({total_pages} pages) ===")
    done = 0
    failed = 0

    for i in range(total_pages):
        page_key = f"page_{i:03d}"
        src_path = f"{pages_dir}/{page_key}.png"
        tr_path = f"{pages_tr_dir}/{page_key}.png"

        # Skip if already done
        if page_key in progress and progress[page_key] == "done" and os.path.exists(tr_path):
            done += 1
            continue

        done += 1
        print(f"  [{done}/{total_pages}] {page_key}...", end=" ", flush=True)

        ok = translate_page(src_path, tr_path)
        if ok:
            progress[page_key] = "done"
            print("OK")
        else:
            progress[page_key] = "failed"
            failed += 1
            print("FAILED")

        # Save progress
        with open(progress_file, "w") as f:
            json.dump(progress, f, indent=2)

        # Rate limit
        time.sleep(1)

    print(f"\nTraduction: {done - failed} OK, {failed} echouees")

    # Phase 3: Reassemble PDF
    print("\n=== Phase 3: Reassemblage du PDF ===")
    output_pdf = f"{PROJ}/rulebook-fr.pdf"

    # Use PIL to create PDF from images
    images = []
    for i in range(total_pages):
        tr_path = f"{pages_tr_dir}/page_{i:03d}.png"
        if os.path.exists(tr_path):
            img = Image.open(tr_path).convert("RGB")
            images.append(img)
        else:
            # Use original page if translation failed
            src_path = f"{pages_dir}/page_{i:03d}.png"
            img = Image.open(src_path).convert("RGB")
            images.append(img)

    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:], resolution=200)
        print(f"  PDF: {output_pdf}")
        print(f"  Taille: {os.path.getsize(output_pdf) / 1024 / 1024:.1f} MB")

    print("\nTermine !")


if __name__ == "__main__":
    main()
