"""
Build final French translation of Satisfactory TTS mod.
1. Translate all Nicknames and Descriptions
2. Replace FaceURL for translated spritesheets
3. Translate Lua broadcast message
4. Output final JSON ready for TTS
"""
import json
import copy
import os
import re

PROJ = "C:/Users/hiind/projects/satisfactory-tts-fr"

# =============================================================================
# NICKNAME TRANSLATIONS
# Rule: keep game-specific proper nouns in English, translate generic terms
# =============================================================================
NICKNAME_TR = {
    # --- Keep in English ---
    "A.W.E.S.O.M.E. Sink": "A.W.E.S.O.M.E. Sink",
    "HUB Upgrade": "Amélioration HUB",
    "MAM Upgrade": "Amélioration MAM",
    "Power Shard": "Power Shard",
    "Overclock": "Overclock",
    "Bean": "Bean",
    "Hog": "Hog",
    "Spitter": "Spitter",

    # --- Translated ---
    "Action Token": "Jeton d'action",
    "Additional Belts": "Convoyeurs supplémentaires",
    "Additional Build Range": "Portée de construction supplémentaire",
    "Additional Movement Range": "Portée de déplacement supplémentaire",
    "Additional Tool Slot": "Emplacement d'outil supplémentaire",
    "Assembler": "Assembleur",
    "Belt Movement Phase": "Phase de déplacement des convoyeurs",
    "Belts": "Convoyeurs",
    "Biomass": "Biomasse",
    "Biome Cards": "Cartes biome",
    "Biome Deck Zone": "Zone du deck biome",
    "Blue Extractor": "Extracteur bleu",
    "Blueprint T1 Zone": "Zone blueprint T1",
    "Blueprint T2 Zone": "Zone blueprint T2",
    "Blueprint T3 Zone": "Zone blueprint T3",
    "Build Action": "Action de construction",
    "Build Bonus": "Bonus de construction",
    "Build on dotted line spaces": "Construire sur les cases en pointillés",
    "Buildings": "Bâtiments",
    "Constructor": "Constructeur",
    "Copper": "Cuivre",
    "Creature Bag": "Sac de créatures",
    "Depot": "Dépôt",
    "Double Workshop Action": "Double action workshop",
    "Exploration Tiles (Beige)": "Cases d'exploration (Beige)",
    "Exploration Tiles (Green)": "Cases d'exploration (Vert)",
    "Extractor Improvements": "Améliorations d'extracteur",
    "Extractor Phase": "Phase d'extraction",
    "First Player Token": "Jeton de premier joueur",
    "Game End": "Fin de partie",
    "HUB Markers": "Marqueurs HUB",
    "Improved Power Plants": "Centrales améliorées",
    "Increase Belt MK": "Augmenter le MK des convoyeurs",
    "Increase Miner MK": "Augmenter le MK des foreuses",
    "Increase Power": "Augmenter l'énergie",
    "Iron": "Fer",
    "Lime": "Calcaire",
    "Manufacturer": "Fabricant",
    "Maximum Production Bonus": "Bonus de production maximum",
    "Milestone Deck Zone": "Zone du deck milestone",
    "Milestone T1 Zone": "Zone milestone T1",
    "Milestone T2 Zone": "Zone milestone T2",
    "Milestone T3 Zone": "Zone milestone T3",
    "Miner": "Foreuse",
    "Movement Action": "Action de déplacement",
    "Power Management": "Gestion d'énergie",
    "Production Phase": "Phase de production",
    "Red Extractor": "Extracteur rouge",
    "Refiner Improvements": "Améliorations de raffineur",
    "Refresh Blueprint Card Row": "Rafraîchir la rangée de cartes blueprint",
    "Reserve Blueprint Card": "Réserver une carte blueprint",
    "Setup Button": "Bouton de mise en place",
    "Upgrade Phase": "Phase d'amélioration",
    "Workshop action": "Action workshop",
    "Yellow Extractor": "Extracteur jaune",
}

# =============================================================================
# DESCRIPTION TRANSLATIONS
# =============================================================================
DESCRIPTION_TR = {
    "After placing a miner, you may place one belt connected to the miner.":
        "Après avoir placé une foreuse, vous pouvez placer un convoyeur connecté à la foreuse.",

    "After placing belts, you may move two spaces.":
        "Après avoir placé des convoyeurs, vous pouvez vous déplacer de deux cases.",

    "Allows the player to carry one additional tool blueprint card.":
        "Permet au joueur de porter une carte blueprint d'outil supplémentaire.",

    "Allows the player to choose two workshop actions when chosing the 'workshop action'":
        "Permet au joueur de choisir deux actions workshop lors du choix de l'action workshop.",

    "Allows the player to place buildings on dotted line spaces.":
        "Permet au joueur de construire sur les cases en pointillés.",

    "Allows the player to place buildings one additional tile away.":
        "Permet au joueur de construire une case plus loin.",

    "Allows the player to reserve a blueprint card. \n\nTake a card from the blueprint card row and place it near your playerboard, only you can build this card.":
        "Permet au joueur de réserver une carte blueprint.\n\nPrenez une carte de la rangée de cartes blueprint et placez-la près de votre plateau joueur. Vous seul pouvez construire cette carte.",

    "Choose a belt segment and move all resources to the right a number of segments equal to your belt MK. \n\nIf resources are moved to the next machine they are refined if that machine is built and powered on.":
        "Choisissez un segment de convoyeur et déplacez toutes les ressources vers la droite d'un nombre de segments égal à votre MK de convoyeur.\n\nSi les ressources atteignent la machine suivante, elles sont raffinées si cette machine est construite et alimentée.",

    "Choose a belt segment. \nMove all resources on that belt segment to the left a number of spaces based on your belt MK speed.":
        "Choisissez un segment de convoyeur.\nDéplacez toutes les ressources de ce segment vers la gauche d'un nombre de cases selon votre vitesse MK de convoyeur.",

    "Choose a building from the build board or a blueprint card to build. If it's a structure place it 0-1 spaces away from your character.\n\nYou cannot build on dotted lined spaces unless you have the [Traverse] upgrade.":
        "Choisissez un bâtiment du plateau de construction ou une carte blueprint à construire. S'il s'agit d'une structure, placez-la à 0-1 cases de votre personnage.\n\nVous ne pouvez pas construire sur les cases en pointillés sans l'amélioration [Traverse].",

    "Choose a built miner and increase it's MK by one.":
        "Choisissez une foreuse construite et augmentez son MK de un.",

    "Choose an extractor and perform an extraction.":
        "Choisissez un extracteur et effectuez une extraction.",

    "Choose three times:\n> Refine a resource.\nor\n> Choose a miner and perform and extraction.":
        "Choisissez trois fois :\n> Raffiner une ressource.\nou\n> Choisir une foreuse et effectuer une extraction.",

    "During the 'Extractor' Production Phase the left most slot of the miner belt will be filled by blue resources based on the MK of the extractor. \n\nMK can be increased by building additional miners on blue resource nodes.":
        "Pendant la phase de production « Extracteur », l'emplacement le plus à gauche du convoyeur de la foreuse sera rempli de ressources bleues selon le MK de l'extracteur.\n\nLe MK peut être augmenté en construisant des foreuses supplémentaires sur les nœuds de ressources bleues.",

    "During the 'Extractor' Production Phase the left most slot of the miner belt will be filled by red resources based on the MK of the extractor. \n\nMK can be increased by building additional miners on red resource nodes.":
        "Pendant la phase de production « Extracteur », l'emplacement le plus à gauche du convoyeur de la foreuse sera rempli de ressources rouges selon le MK de l'extracteur.\n\nLe MK peut être augmenté en construisant des foreuses supplémentaires sur les nœuds de ressources rouges.",

    "During the 'Extractor' Production Phase the left most slot of the miner belt will be filled by yellow resources based on the MK of the extractor. \n\nMK can be increased by building additional miners on yellow resource nodes.":
        "Pendant la phase de production « Extracteur », l'emplacement le plus à gauche du convoyeur de la foreuse sera rempli de ressources jaunes selon le MK de l'extracteur.\n\nLe MK peut être augmenté en construisant des foreuses supplémentaires sur les nœuds de ressources jaunes.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TI blue HUB Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration HUB TI bleue.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TI red HUB Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration HUB TI rouge.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TI yellow HUB Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration HUB TI jaune.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TII blue HUB Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration HUB TII bleue.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TII blue MAM Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration MAM TII bleue.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TII red HUB Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration HUB TII rouge.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TII red MAM Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration MAM TII rouge.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TII yellow HUB Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration HUB TII jaune.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TII yellow MAM Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration MAM TII jaune.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TIII blue HUB Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration HUB TIII bleue.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TIII blue MAM Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration MAM TIII bleue.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TIII red HUB Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration HUB TIII rouge.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TIII red MAM Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration MAM TIII rouge.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TIII yellow HUB Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration HUB TIII jaune.",

    "During the final Production Phase step, if a resource is on this space, you may remove it and place it on a TIII yellow MAM Upgrade.":
        "Lors de la dernière étape de la phase de production, si une ressource est sur cette case, vous pouvez la retirer et la placer sur une amélioration MAM TIII jaune.",

    "During the 'Power Management' of the Production Phase, the player must pay 1 biomass per depot.\n\nIf they fail to do so - they must power down one of their miners for each depot not paid for.":
        "Pendant la « Gestion d'énergie » de la phase de production, le joueur doit payer 1 biomasse par dépôt.\n\nS'il ne peut pas, il doit éteindre une de ses foreuses pour chaque dépôt non payé.",

    "During the production phase go down the list to activate each part of your factory.":
        "Pendant la phase de production, suivez la liste pour activer chaque partie de votre usine.",

    "Each MK increase how many segments the resources move during belt movement actions. \n\nFrom left to right, with the right most resources moving first.\n\nSee HUB upgrades for belt MK increases.":
        "Chaque MK augmente le nombre de segments que les ressources parcourent lors des actions de déplacement de convoyeur.\n\nDe gauche à droite, les ressources les plus à droite se déplaçant en premier.\n\nVoir les améliorations HUB pour augmenter le MK des convoyeurs.",

    "Each player must lose two power and you gain two power per player.":
        "Chaque joueur doit perdre deux points d'énergie et vous gagnez deux points d'énergie par joueur.",

    "Gain one FICIST point upon building a Manufacturer":
        "Gagnez un point FICSIT en construisant un fabricant.",

    "Grants two additional movement range when performing a 'Movement' Action":
        "Accorde deux cases de portée de déplacement supplémentaires lors d'une action de déplacement.",

    "If a constructor is built and powered, when a TI resources crosses this space, it will be refined into a TII resource.":
        "Si un constructeur est construit et alimenté, quand une ressource TI traverse cette case, elle sera raffinée en ressource TII.",

    "If a manufacturer is built and powered, when all three types of TIII resources crosses this threshold, they will be refined into a single TIV resource.":
        "Si un fabricant est construit et alimenté, quand les trois types de ressources TIII traversent ce seuil, elles seront raffinées en une seule ressource TIV.",

    "If all right most slots on each machine are full, gain a FICIST point.":
        "Si tous les emplacements les plus à droite de chaque machine sont pleins, gagnez un point FICSIT.",

    "If an assembler is built and powered, when two TII resources crosses this space, it will be refined into a single TIII resource.":
        "Si un assembleur est construit et alimenté, quand deux ressources TII traversent cette case, elles seront raffinées en une seule ressource TIII.",

    "If any resources are on spaces on the belts with these icons, you may take the resources off the belts and place them on upgrades in the MAM or HUB based on the icon the resource is on, and place that resource on the matching resource and tier icon.":
        "Si des ressources se trouvent sur des cases des convoyeurs avec ces icônes, vous pouvez retirer les ressources des convoyeurs et les placer sur les améliorations du MAM ou du HUB selon l'icône sur laquelle se trouve la ressource, en la plaçant sur l'icône de ressource et de tier correspondant.",

    "If the power cube is on a space with an icon, trigger that effect. \n\nIf the power cube is in a negative space, you must pay that much power in biomass, for each point unable to be spent you must shut off one of your machines. \n\nShutting off machines will disable it's belt movement and extraction if miner, or refinement if other machine.\n":
        "Si le cube d'énergie est sur une case avec une icône, déclenchez cet effet.\n\nSi le cube d'énergie est sur une case négative, vous devez payer autant d'énergie en biomasse. Pour chaque point non payé, vous devez éteindre une de vos machines.\n\nÉteindre une machine désactive son déplacement de convoyeur et son extraction si c'est une foreuse, ou son raffinage si c'est une autre machine.",

    "If you have a miner on blue resources and it is powered, place as many yellow cubes on the left most spaces as your extractor MK.\n\nSlots already filled do not get extra resources.":
        "Si vous avez une foreuse sur des ressources bleues et qu'elle est alimentée, placez autant de cubes jaunes sur les emplacements les plus à gauche que votre MK d'extracteur.\n\nLes emplacements déjà remplis ne reçoivent pas de ressources supplémentaires.",

    "If you have a miner on red resources and it is powered, place as many yellow cubes on the left most spaces as your extractor MK.\n\nSlots already filled do not get extra resources.":
        "Si vous avez une foreuse sur des ressources rouges et qu'elle est alimentée, placez autant de cubes jaunes sur les emplacements les plus à gauche que votre MK d'extracteur.\n\nLes emplacements déjà remplis ne reçoivent pas de ressources supplémentaires.",

    "If you have a miner on yellow resources and it is powered, place as many yellow cubes on the left most spaces as your extractor MK.\n\nSlots already filled do not get extra resources.":
        "Si vous avez une foreuse sur des ressources jaunes et qu'elle est alimentée, placez autant de cubes jaunes sur les emplacements les plus à gauche que votre MK d'extracteur.\n\nLes emplacements déjà remplis ne reçoivent pas de ressources supplémentaires.",

    "Increase your belt MK by one.":
        "Augmentez votre MK de convoyeur de un.",

    "Move a single resource from one Tier to the next Tier.\n\nThe destination building does not need to be built or powered.":
        "Déplacez une seule ressource d'un tier au tier suivant.\n\nLe bâtiment de destination n'a pas besoin d'être construit ou alimenté.",

    "Move all resources from left to right starting with the right most resources as many spaces as your belt MK. \n\nMachines that are not built or turned off do not move. \n\nIf a resource crosses a treshold into the next machine you may choose to refine the resource.":
        "Déplacez toutes les ressources de gauche à droite en commençant par les ressources les plus à droite, d'autant de cases que votre MK de convoyeur.\n\nLes machines non construites ou éteintes ne déplacent pas.\n\nSi une ressource franchit un seuil vers la machine suivante, vous pouvez choisir de raffiner la ressource.",

    "Move your character 1-2 spaces. \n\nYou cannot move or end your movement through dotted lines if you do not have the [Traverse] upgrade":
        "Déplacez votre personnage de 1-2 cases.\n\nVous ne pouvez pas vous déplacer ou terminer votre mouvement à travers les lignes pointillées sans l'amélioration [Traverse].",

    "Move your power cube to the right one space.":
        "Déplacez votre cube d'énergie d'une case vers la droite.",

    "Once the space elevator indicator (black cube) reaches this space, the game is over. \n\nCalculate end game score.\nThe player with the most FICIST points wins the game !":
        "Quand l'indicateur de l'ascenseur spatial (cube noir) atteint cette case, la partie est terminée.\n\nCalculez le score final.\nLe joueur avec le plus de points FICSIT remporte la partie !",

    "Overlock: For each power shard the player has, they may choose one of the power rewards in this box, irregardless if they have enough power or not.":
        "Overclock : Pour chaque Power Shard que le joueur possède, il peut choisir une des récompenses d'énergie dans cette case, qu'il ait assez d'énergie ou non.",

    "Perform any of the overclock power bonuses on the previous spaces. You may do this twice.":
        "Effectuez n'importe lequel des bonus d'énergie overclock des cases précédentes. Vous pouvez le faire deux fois.",

    "Pick either, belt movement, or refinement. \n\nHover over these for more information.":
        "Choisissez entre le déplacement de convoyeur ou le raffinage.\n\nSurvol pour plus d'informations.",

    "Place 4 biomass on an empty space adjacent to one of your buildings.":
        "Placez 4 biomasses sur une case vide adjacente à l'un de vos bâtiments.",

    "Place one creature on the map adjacent to a building.":
        "Placez une créature sur la carte adjacente à un bâtiment.",

    "Place purple cubes (power shard) on these spaces. \n\nThese are found by exploring. \nFor each power shard on your player board, during the 'Power Management' portion of the 'Production Phase', the player may trigger an 'Overlock' bonus - see the power bar tooltips for more information.\n":
        "Placez des cubes violets (Power Shard) sur ces emplacements.\n\nIls se trouvent en explorant.\nPour chaque Power Shard sur votre plateau joueur, pendant la « Gestion d'énergie » de la « Phase de production », le joueur peut déclencher un bonus overclock — voir les infobulles de la barre d'énergie pour plus d'informations.",

    "Players cannot build in any adjacent tile to the creature until it is removed.":
        "Les joueurs ne peuvent pas construire sur les cases adjacentes à la créature tant qu'elle n'est pas retirée.",

    "Players ending their movement action in any adjacent tile to the creature lose 1 Action":
        "Les joueurs terminant leur action de déplacement sur une case adjacente à la créature perdent 1 action.",

    "Players ending their movement action on the creature's tile lose 1 Action":
        "Les joueurs terminant leur action de déplacement sur la case de la créature perdent 1 action.",

    "Players ending their movement action on the creature\u2019s tile lose 1 Action":
        "Les joueurs terminant leur action de déplacement sur la case de la créature perdent 1 action.",

    "Refine one resource from one tier to the next tier. The corresponding machines do not need to be built.":
        "Raffinez une ressource d'un tier au tier suivant. Les machines correspondantes n'ont pas besoin d'être construites.",

    "Remove all cards from a single blueprint card row and replace them with new cards.":
        "Retirez toutes les cartes d'une rangée de cartes blueprint et remplacez-les par de nouvelles cartes.",

    "Spend 4 power (reduce their power grid by 4) and gain one FICSIT Point.":
        "Dépensez 4 points d'énergie (réduisez votre grille d'énergie de 4) et gagnez un point FICSIT.",

    "TI blue resources are obtained from miners placed on TI blue resource nodes.":
        "Les ressources bleues TI sont obtenues grâce aux foreuses placées sur les nœuds de ressources bleues TI.",

    "TI red resources are obtained from miners placed on TI red resource nodes.":
        "Les ressources rouges TI sont obtenues grâce aux foreuses placées sur les nœuds de ressources rouges TI.",

    "TI yellow resources are obtained from miners placed on TI yellow resource nodes.":
        "Les ressources jaunes TI sont obtenues grâce aux foreuses placées sur les nœuds de ressources jaunes TI.",

    "When building a power plant increase the power generated by an additional two points.":
        "Lors de la construction d'une centrale, augmentez l'énergie générée de deux points supplémentaires.",

    "When extracting resources you may choose which belt portion to place the extracted resources on.":
        "Lors de l'extraction de ressources, vous pouvez choisir sur quelle portion de convoyeur placer les ressources extraites.",

    "When reaching this space, move the the space elevator indicator (black cube) up one space.":
        "En atteignant cette case, avancez l'indicateur de l'ascenseur spatial (cube noir) d'une case.",

    "When refining resources you may choose which belt portion to place refined resources on.":
        "Lors du raffinage de ressources, vous pouvez choisir sur quelle portion de convoyeur placer les ressources raffinées.",

    "When two TIV resources move onto this space you may remove them to gain one FICIST point.":
        "Quand deux ressources TIV arrivent sur cette case, vous pouvez les retirer pour gagner un point FICSIT.",

    "You may exchange any two resources for any single resource.":
        "Vous pouvez échanger deux ressources quelconques contre une seule ressource.",

    "You may not build on this space.":
        "Vous ne pouvez pas construire sur cette case.",

    "You may not build on this space.\n\nPoison / Radioactive - If you move onto the space lose one action.":
        "Vous ne pouvez pas construire sur cette case.\n\nPoison / Radioactif — Si vous vous déplacez sur cette case, perdez une action.",

    "You may not move onto or through this space without a [Traverse] upgrade.\n\nYou may not build on the space without the approriate MAM upgrade.":
        "Vous ne pouvez pas vous déplacer sur ou à travers cette case sans l'amélioration [Traverse].\n\nVous ne pouvez pas construire sur cette case sans l'amélioration MAM appropriée.",

    "You may place one additional belt when building belts and miners.":
        "Vous pouvez placer un convoyeur supplémentaire lors de la construction de convoyeurs et de foreuses.",

    "You may refine one TI resources into a TIII resource.":
        "Vous pouvez raffiner une ressource TI en ressource TIII.",

    "You may take a free 'build' action, you must still pay the costs of the chosen building or blueprint card.":
        "Vous pouvez effectuer une action de construction gratuite. Vous devez quand même payer le coût du bâtiment ou de la carte blueprint choisi.",
}

# Original FaceURLs for the 7 translated decks -> will be replaced
# Maps original URL prefix to deck ID
DECK_FACE_URLS = {
    "18": "https://steamusercontent-a.akamaihd.net/ugc/10633318762055327419/85DB27E4ACB2DC4F30B7C0F5D358FD6AB24A2D1B/",
    "19": "https://steamusercontent-a.akamaihd.net/ugc/11449472078591682700/0F5A4BBBFABEA43019AA0E1B882FCB8682BCAA5F/",
    "20": "https://steamusercontent-a.akamaihd.net/ugc/9419809450847062810/D325EAAA8F3840AFDB819E9192657C35A14896F1/",
    "21": "https://steamusercontent-a.akamaihd.net/ugc/11257853964554378906/4485CECAFE30E7F37E97F307D116B4459094D3A2/",
    "36": "https://steamusercontent-a.akamaihd.net/ugc/12317926724997449471/222A935761B472C4DAFFF16F5933FC5BB30A61FA/",
    "38": "https://steamusercontent-a.akamaihd.net/ugc/12827630344160901045/0380D309C6F9B4E64D677EC81B65CC9F90A17BE3/",
    "39": "https://steamusercontent-a.akamaihd.net/ugc/16519910720659503270/A645A70D77247AF5342070514E2F00B28BD7D88C/",
}


def translate_text(obj):
    """Recursively translate Nickname and Description fields."""
    if isinstance(obj, dict):
        # Translate Nickname
        if "Nickname" in obj and obj["Nickname"]:
            original = obj["Nickname"]
            if original in NICKNAME_TR:
                obj["Nickname"] = NICKNAME_TR[original]

        # Translate Description
        if "Description" in obj and obj["Description"]:
            original = obj["Description"]
            if original in DESCRIPTION_TR:
                obj["Description"] = DESCRIPTION_TR[original]

        # Recurse into all values
        for key, val in obj.items():
            if key in ("LuaScript", "LuaScriptState", "XmlUI"):
                continue  # Handle Lua separately
            translate_text(val)

    elif isinstance(obj, list):
        for item in obj:
            translate_text(item)


def replace_face_urls(obj, url_map):
    """Recursively replace FaceURL entries for translated decks."""
    if isinstance(obj, dict):
        if "FaceURL" in obj:
            for deck_id, original_url in DECK_FACE_URLS.items():
                if obj["FaceURL"] == original_url and deck_id in url_map:
                    obj["FaceURL"] = url_map[deck_id]

        for val in obj.values():
            replace_face_urls(val, url_map)

    elif isinstance(obj, list):
        for item in obj:
            replace_face_urls(item, url_map)


def translate_lua(script):
    """Translate user-visible strings in the Lua script."""
    return script.replace(
        "Tooltips are included. Hover your cursor over many elements for a few seconds to display a tooltip for that element.",
        "Des infobulles sont disponibles. Survolez les éléments du jeu quelques secondes pour afficher leur description."
    )


def count_translations(obj, stats=None):
    """Count how many fields were translated vs missed."""
    if stats is None:
        stats = {"nick_translated": 0, "nick_missed": [], "desc_translated": 0, "desc_missed": []}

    if isinstance(obj, dict):
        if "Nickname" in obj and obj["Nickname"]:
            original = obj.get("_original_nickname", obj["Nickname"])
            # We already translated, so check if it's in our dict
            # Actually let's count before translation
            pass

        for val in obj.values():
            count_translations(val, stats)
    elif isinstance(obj, list):
        for item in obj:
            count_translations(item, stats)

    return stats


def find_untranslated(obj, path=""):
    """Find any Nickname/Description not in our translation dicts."""
    missing = []
    if isinstance(obj, dict):
        if "Nickname" in obj and obj["Nickname"] and obj["Nickname"] not in NICKNAME_TR and obj["Nickname"] not in NICKNAME_TR.values():
            missing.append(("Nickname", obj["Nickname"], path))
        if "Description" in obj and obj["Description"] and obj["Description"] not in DESCRIPTION_TR and obj["Description"] not in DESCRIPTION_TR.values():
            missing.append(("Description", obj["Description"][:80], path))

        for key, val in obj.items():
            if key in ("LuaScript", "LuaScriptState", "XmlUI"):
                continue
            missing.extend(find_untranslated(val, f"{path}.{key}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            missing.extend(find_untranslated(item, f"{path}[{i}]"))
    return missing


def main():
    print("=== Construction du mod FR Satisfactory TTS ===\n")

    # 1. Load original JSON
    print("Chargement du JSON original...")
    with open(f"{PROJ}/satisfactory-tts-original.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Check for untranslated text first
    print("Vérification des textes manquants...")
    missing = find_untranslated(data)
    if missing:
        print(f"\n[!] {len(missing)} textes non traduits trouves:")
        for field_type, text, path in missing:
            print(f"  [{field_type}] {text}")
        print()
    else:
        print("  Tous les textes sont couverts !\n")

    # 3. Translate metadata
    data["SaveName"] = "Satisfactory - Preview [FR]"
    data["GameMode"] = "Satisfactory - Preview [FR]"
    # Replace "English" tag with "French"
    if "English" in data.get("Tags", []):
        data["Tags"] = [t if t != "English" else "French" for t in data["Tags"]]

    # 4. Translate Lua script
    print("Traduction du script Lua...")
    if "LuaScript" in data:
        data["LuaScript"] = translate_lua(data["LuaScript"])

    # 5. Translate all Nicknames and Descriptions
    print("Traduction des Nicknames et Descriptions...")
    translate_text(data)

    # 6. Handle image URLs
    # Check if we have a URL map file (created after uploading images)
    url_map_file = f"{PROJ}/translated-urls.json"
    if os.path.exists(url_map_file):
        print("Remplacement des URLs d'images traduites...")
        with open(url_map_file) as f:
            url_map = json.load(f)
        replace_face_urls(data, url_map)
        print(f"  {len(url_map)} URLs remplacées")
    else:
        print("\n[!] Fichier translated-urls.json non trouve.")
        print("  Les URLs d'images n'ont pas été remplacées.")
        print("  Pour les remplacer, créez translated-urls.json avec le format:")
        print('  {"18": "https://...", "19": "https://...", ...}\n')

    # 7. Save final JSON
    output_path = f"{PROJ}/satisfactory-tts-fr.json"
    print(f"Sauvegarde du JSON final: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nFichier sauvegardé: {os.path.getsize(output_path) / 1024:.0f} KB")
    print("\n=== Terminé ! ===")
    print("\nProchaines étapes:")
    print("1. Uploader les images traduites (images-translated/) quelque part")
    print("2. Créer translated-urls.json avec les nouvelles URLs")
    print("3. Relancer ce script pour mettre à jour les URLs")
    print("4. Copier satisfactory-tts-fr.json dans:")
    print("   Documents/My Games/Tabletop Simulator/Saves/")


if __name__ == "__main__":
    main()
