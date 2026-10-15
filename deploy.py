"""
Deploy the French Satisfactory TTS mod.
- Rebuilds the final JSON with all translations and URLs
- Copies to TTS Saves folder
- Shows instructions for sharing
"""
import json
import os
import shutil

PROJ = "C:/Users/hiind/projects/satisfactory-tts-fr"
TTS_SAVES = os.path.expanduser("~/Documents/My Games/Tabletop Simulator/Saves")


def main():
    print("=== Deploy Satisfactory TTS FR ===\n")

    # 1. Rebuild the JSON
    print("1. Construction du JSON final...")
    os.system(f'python "{PROJ}/build_fr_mod.py"')

    # 2. Update rulebook PDF URL if available
    fr_json_path = f"{PROJ}/satisfactory-tts-fr.json"
    rulebook_path = f"{PROJ}/rulebook-fr.pdf"

    if os.path.exists(rulebook_path):
        print("\n2. Mise a jour de l'URL du rulebook...")
        with open(fr_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Replace PDF URL with GitHub hosted version
        rulebook_url = "https://raw.githubusercontent.com/caillef/satisfactory-tts-fr/main/rulebook-fr.pdf"
        original_url = "https://steamusercontent-a.akamaihd.net/ugc/17176852519472159796/148939F571DB3F706A516EF8F65889ED88E7B54E/"

        json_str = json.dumps(data, ensure_ascii=False)
        if original_url in json_str:
            json_str = json_str.replace(original_url, rulebook_url)
            data = json.loads(json_str)
            with open(fr_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  URL du rulebook mise a jour: {rulebook_url}")
        else:
            print("  URL du rulebook deja mise a jour ou non trouvee")
    else:
        print("\n2. Rulebook FR non trouve, PDF non mis a jour")

    # 3. Copy to TTS Saves
    print(f"\n3. Copie vers TTS Saves...")
    if os.path.exists(TTS_SAVES):
        dest = os.path.join(TTS_SAVES, "Satisfactory FR.json")
        shutil.copy2(fr_json_path, dest)
        print(f"  Copie: {dest}")
    else:
        print(f"  [!] Dossier TTS non trouve: {TTS_SAVES}")
        print(f"  Copie manuelle: {fr_json_path}")

    # 4. Summary
    print("\n=== Resume ===")
    print(f"  JSON final: {fr_json_path}")
    print(f"  Taille: {os.path.getsize(fr_json_path) / 1024:.0f} KB")
    print()
    print("Pour jouer:")
    print("  1. Ouvre TTS")
    print("  2. Games > Save & Load")
    print("  3. Charge 'Satisfactory FR'")
    print()
    print("Pour partager avec tes potes:")
    print("  - Envoie-leur le fichier satisfactory-tts-fr.json")
    print("  - Ils le mettent dans: Documents/My Games/Tabletop Simulator/Saves/")
    print("  - Quand tu host, les images se chargent automatiquement depuis GitHub")


if __name__ == "__main__":
    main()
