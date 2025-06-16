import random
import json
import os
import sys

def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        # Chemin pour l'exécutable PyInstaller
        return os.path.join(sys._MEIPASS, "json", filename)
    # Chemin pour l'exécution en tant que script
    return os.path.join(os.path.dirname(__file__), "json", filename)

CONVERSIONS_CONFIG_PATH = get_resource_path('conversions_config.json')
try:
    with open(CONVERSIONS_CONFIG_PATH, 'r', encoding='utf-8') as f:
        CONVERSION_DATA_LOADED = json.load(f)
except FileNotFoundError:
    print(f"ERREUR: Le fichier de configuration des conversions '{CONVERSIONS_CONFIG_PATH}' est introuvable.")
    CONVERSION_DATA_LOADED = {"level_order": [], "conversions": {}}
except json.JSONDecodeError:
    print(f"ERREUR: Le fichier de configuration des conversions '{CONVERSIONS_CONFIG_PATH}' contient un JSON invalide.")
    # import traceback; traceback.print_exc() # Décommenter pour voir la pile d'appels de l'erreur JSON
    CONVERSION_DATA_LOADED = {"level_order": [], "conversions": {}}

# Exposer CONVERSION_DATA_LOADED pour import potentiel par d'autres modules si nécessaire
CONVERSION_DATA = CONVERSION_DATA_LOADED

# Génère des exercices de conversion aléatoires
# types_selectionnés : liste de types (ex : ['longueur', 'masse'])
# n : nombre d'exercices à générer
# sens : liste de sens de conversion possibles (ex : ['direct', 'inverse'])
# current_level : le niveau scolaire actuel pour filtrer les conversions
# Retourne une liste de chaînes (exercices)
def generate_conversion_exercises(types_selectionnes, n, senses, current_level=None):
    print(f"generate_conversion_exercises called. current_level: {current_level}, types_selectionnes: {types_selectionnes}, n: {n}, senses: {senses}")
    exercises = []
    config_level_order = CONVERSION_DATA.get("level_order", [])
    all_conversions_map = CONVERSION_DATA.get("conversions", {})

    if not types_selectionnes or not senses: # Si aucun type ou sens n'est sélectionné, on ne peut rien faire
        print("Aucun type de conversion ou sens sélectionné. Retourne une liste vide.")
        return exercises

    for _ in range(n):
        type_conv = random.choice(types_selectionnes)

        available_couples_for_type = []
        levels_to_consider = []

        if current_level and current_level in config_level_order:
            # Prend tous les niveaux jusqu'au niveau actuel inclus
            levels_to_consider = config_level_order[:config_level_order.index(current_level) + 1]
            print(f"Levels to consider for level '{current_level}': {levels_to_consider}")
        else: # Aucun niveau sélectionné ou niveau invalide, on prend tout par défaut
            levels_to_consider = config_level_order
            print(f"No valid level specified ('{current_level}'). Considering all levels: {levels_to_consider}")
        
        # Collect conversions from allowed levels for the selected type
        for lvl in levels_to_consider:
            conversions_for_level_type = all_conversions_map.get(type_conv, {}).get(lvl, [])
            if conversions_for_level_type:
                # print(f"  Adding {len(conversions_for_level_type)} conversions from level '{lvl}' for type '{type_conv}'")
                available_couples_for_type.extend(conversions_for_level_type)

        if not available_couples_for_type: # Pas de conversions pour ce type et ce(s) niveau(x)
            # print(f"No conversions available for type '{type_conv}' in levels {levels_to_consider}")
            continue

        unit_from, unit_to, factor = random.choice(available_couples_for_type)
        sens = random.choice(senses)

        if sens == 'direct':
            value = random.randint(1, 100)
            exercises.append(f"{value} {unit_from} = ____________ {unit_to}")
        else: # sens == 'inverse'
            # Pour l'inverse, on génère une valeur dans l'unité d'arrivée qui soit un multiple du facteur
            # pour éviter des résultats non entiers si on ne veut que des entiers.
            # Ici, on va générer une valeur de départ simple et la multiplier par le facteur.
            multiple = random.randint(1, 10) # Un petit multiple pour garder les nombres gérables
            value_in_unit_to = multiple * factor
            exercises.append(f"{value_in_unit_to} {unit_to} = ____________ {unit_from}")
    
    # print(f"Generated {len(exercises)} conversion exercises.")
    return exercises

