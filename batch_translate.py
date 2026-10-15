"""
Batch translation de toutes les cartes Satisfactory TTS via Gemini Nano Banana 2.1.
1. Extrait chaque carte des spritesheets
2. Envoie à Gemini pour traduction FR
3. Réassemble les spritesheets traduites
"""
import json
import os
import time
import sys
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
GLOSSAIRE DE TRADUCTION (à respecter strictement) :
- tile → case
- player tile → case du joueur
- adjacent tile → case adjacente
- creature → créature
- remove creature → retirez la créature
- biomass → biomasse
- gain +X biomass → gagnez +X biomasse
- lose X action → perdez X action
- movement action → action de déplacement
- build action → action de construction
- workshop action → action de workshop (garder "workshop")
- belt → convoyeur
- miner → foreuse
- constructor → constructeur
- assembler → assembleur
- manufacturer → fabricant
- depot → dépôt
- power → énergie
- power management → gestion d'énergie
- production phase → phase de production
- upgrade → amélioration
- build range → portée de construction
- movement range → portée de déplacement
- tool slot → emplacement d'outil
- extractor → extracteur
- milestone → milestone (garder en anglais)
- blueprint → blueprint (garder en anglais)
- overclock → overclock (garder en anglais)
- HUB → HUB (garder en anglais)
- MAM → MAM (garder en anglais)
- A.W.E.S.O.M.E. Sink → A.W.E.S.O.M.E. Sink (garder en anglais)
- Power Shard → Power Shard (garder en anglais)
- collect → collecter
- exploration → exploration
- biome → biome
"""

PROMPT = f"""Tu es un outil de traduction visuelle de cartes de jeu de société.

Voici une carte du jeu de société Satisfactory (adaptation plateau du jeu vidéo).

Tu dois régénérer EXACTEMENT la même image avec ces modifications :
- Le texte descriptif en bas de la carte (sous les icônes d'action) doit être traduit en FRANÇAIS
- Le NOM de l'item/carte en haut doit RESTER EN ANGLAIS
- Les icônes, couleurs, mise en page, bordures, illustrations, tier (I, II, III) doivent rester IDENTIQUES
- La police, la taille du texte et le style doivent être conservés exactement
- Les dimensions de l'image doivent être EXACTEMENT les mêmes que l'original

{GLOSSARY}

Génère l'image traduite, identique pixel-perfect sauf le texte descriptif traduit en français."""


DECKS = {
    "18": {"file": "deck18-face.jpg", "cols": 1, "rows": 1},
    "19": {"file": "deck19-face.jpg", "cols": 1, "rows": 1},
    "20": {"file": "deck20-face.jpg", "cols": 1, "rows": 1},
    "21": {"file": "deck21-biome-face.jpg", "cols": 5, "rows": 4},
    "36": {"file": "deck36-face.jpg", "cols": 7, "rows": 6},
    "38": {"file": "deck38-face.jpg", "cols": 5, "rows": 4},
    "39": {"file": "deck39-face.jpg", "cols": 1, "rows": 1},
}


def translate_card_image(image_path, output_path):
    """Envoie une carte à Gemini et récupère la version FR."""
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    ext = image_path.lower().split(".")[-1]
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-nano-banana-2.1",
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text=PROMPT),
                            types.Part(
                                inline_data=types.Blob(mime_type=mime, data=image_bytes)
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

            print(f"  [WARN] Pas d'image dans la réponse, tentative {attempt+1}")
        except Exception as e:
            print(f"  [ERR] {e}, tentative {attempt+1}")
            time.sleep(5)

    return False


def extract_cards(deck_id, deck_info):
    """Extrait les cartes individuelles d'une spritesheet."""
    src = f"{PROJ}/images-original/{deck_info['file']}"
    if not os.path.exists(src):
        print(f"  [SKIP] {src} non trouvé")
        return []

    img = Image.open(src)
    w, h = img.size
    cols, rows = deck_info['cols'], deck_info['rows']
    card_w = w // cols
    card_h = h // rows

    cards_dir = f"{PROJ}/cards-extracted"
    os.makedirs(cards_dir, exist_ok=True)

    cards = []
    for row in range(rows):
        for col in range(cols):
            card = img.crop((col * card_w, row * card_h, (col + 1) * card_w, (row + 1) * card_h))

            # Vérifier que la carte n'est pas vide (tout noir ou tout blanc)
            extrema = card.getextrema()
            if all(e[0] == e[1] for e in extrema[:3]):
                continue  # carte vide

            card_path = f"{cards_dir}/deck{deck_id}_r{row}_c{col}.png"
            card.save(card_path, quality=95)
            cards.append({
                "deck_id": deck_id,
                "row": row,
                "col": col,
                "path": card_path,
                "card_w": card_w,
                "card_h": card_h,
            })

    return cards


def reassemble_spritesheet(deck_id, deck_info, translated_cards):
    """Réassemble les cartes traduites en spritesheet."""
    src = f"{PROJ}/images-original/{deck_info['file']}"
    original = Image.open(src)
    w, h = original.size
    cols, rows = deck_info['cols'], deck_info['rows']
    card_w = w // cols
    card_h = h // rows

    # Partir de l'original (pour garder les slots vides)
    sheet = original.copy()

    for card_info in translated_cards:
        tr_path = card_info["translated_path"]
        if not os.path.exists(tr_path):
            continue
        tr_card = Image.open(tr_path)
        # Resize si Gemini a changé les dimensions
        if tr_card.size != (card_w, card_h):
            tr_card = tr_card.resize((card_w, card_h), Image.LANCZOS)
        col, row = card_info["col"], card_info["row"]
        sheet.paste(tr_card, (col * card_w, row * card_h))

    out_name = deck_info['file'].replace('.', '-fr.')
    out_path = f"{PROJ}/images-translated/{out_name}"
    sheet.save(out_path, quality=95)
    print(f"  Spritesheet: {out_path}")
    return out_path


def main():
    os.makedirs(f"{PROJ}/cards-extracted", exist_ok=True)
    os.makedirs(f"{PROJ}/cards-translated", exist_ok=True)
    os.makedirs(f"{PROJ}/images-translated", exist_ok=True)

    # Charger la progression existante
    progress_file = f"{PROJ}/translation-progress.json"
    if os.path.exists(progress_file):
        with open(progress_file) as f:
            progress = json.load(f)
    else:
        progress = {}

    total_cards = 0
    all_cards = {}

    # Phase 1: Extraire toutes les cartes
    print("=== Phase 1: Extraction des cartes ===")
    for deck_id, deck_info in DECKS.items():
        print(f"Deck {deck_id} ({deck_info['file']}, {deck_info['cols']}x{deck_info['rows']})...")
        cards = extract_cards(deck_id, deck_info)
        all_cards[deck_id] = cards
        total_cards += len(cards)
        print(f"  {len(cards)} cartes extraites")

    print(f"\nTotal: {total_cards} cartes à traduire")

    # Phase 2: Traduire chaque carte
    print("\n=== Phase 2: Traduction via Gemini ===")
    done = 0
    failed = 0

    for deck_id, cards in all_cards.items():
        print(f"\nDeck {deck_id}:")
        for card_info in cards:
            card_key = f"deck{deck_id}_r{card_info['row']}_c{card_info['col']}"
            tr_path = f"{PROJ}/cards-translated/{card_key}.png"
            card_info["translated_path"] = tr_path

            # Skip si déjà traduit
            if card_key in progress and progress[card_key] == "done":
                if os.path.exists(tr_path):
                    done += 1
                    continue

            done += 1
            print(f"  [{done}/{total_cards}] {card_key}...", end=" ", flush=True)

            ok = translate_card_image(card_info["path"], tr_path)
            if ok:
                progress[card_key] = "done"
                print("OK")
            else:
                progress[card_key] = "failed"
                failed += 1
                print("FAILED")

            # Sauvegarder la progression
            with open(progress_file, "w") as f:
                json.dump(progress, f, indent=2)

            # Rate limit
            time.sleep(1)

    print(f"\nTraduction terminée: {done - failed} OK, {failed} échouées")

    # Phase 3: Réassembler les spritesheets
    print("\n=== Phase 3: Réassemblage des spritesheets ===")
    for deck_id, deck_info in DECKS.items():
        if deck_id in all_cards:
            reassemble_spritesheet(deck_id, deck_info, all_cards[deck_id])

    print("\nTerminé !")


if __name__ == "__main__":
    main()
