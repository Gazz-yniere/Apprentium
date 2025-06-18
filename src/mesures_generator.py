import random
import os
import json
import sys

def get_resource_path(filename):
    # Utility to get resource path, useful if CONVERSION_DATA is in a JSON file
    if hasattr(sys, '_MEIPASS'):
        # For PyInstaller, assumes 'json' folder is at the same level as the executable
        return os.path.join(sys._MEIPASS, "json", filename)
    # For script execution, assumes 'json' folder is in the same directory as this script
    return os.path.join(os.path.dirname(__file__), "json", filename)

CONVERSION_DATA = {}
try:
    # Assuming your conversion configuration is in 'conversions_config.json'
    # in the 'json' subdirectory relative to this script's location.
    with open(get_resource_path('conversions_config.json'), 'r', encoding='utf-8') as f:
        CONVERSION_DATA = json.load(f)
except FileNotFoundError:
    print(f"ERREUR: Fichier 'conversions_config.json' introuvable. Les exercices de conversion ne seront pas disponibles.")
except json.JSONDecodeError as e:
    print(f"ERREUR: Erreur de décodage JSON dans 'conversions_config.json': {e}. Les exercices de conversion ne seront pas disponibles.")
except Exception as e:
    print(f"ERREUR: Impossible de charger les données de conversion: {e}. Les exercices de conversion ne seront pas disponibles.")


def generate_conversion_exercises(types_selectionnes, n, senses, current_level):
    """
    Génère des exercices de conversion.
    types_selectionnes: Liste des types de conversion (ex: ["longueur", "masse"]).
    n: Nombre d'exercices à générer.
    senses: Liste des sens de conversion (ex: ["direct", "inverse"]).
    current_level: Niveau scolaire actuel (ex: "CP", "CE1").
    """
    exercices = []
    if not types_selectionnes or not senses or not CONVERSION_DATA or n == 0:
        return exercices

    possible_conversions = []
    for type_conv in types_selectionnes:
        if type_conv in CONVERSION_DATA:
            level_config = CONVERSION_DATA[type_conv].get(current_level)
            if level_config:
                for conv_details in level_config.get("conversions", []):
                    # conv_details = {"from": "m", "to": "cm", "multiplier": 100, "range_from": [1, 10]}
                    if "direct" in senses:
                        possible_conversions.append({
                            "type": type_conv,
                            "from_unit": conv_details["from"],
                            "to_unit": conv_details["to"],
                            "multiplier": conv_details["multiplier"],
                            "range": conv_details["range_from"],
                            "sense": "direct"
                        })
                    if "inverse" in senses and conv_details["multiplier"] != 0 :
                         possible_conversions.append({
                            "type": type_conv,
                            "from_unit": conv_details["to"], 
                            "to_unit": conv_details["from"],
                            "multiplier": 1 / conv_details["multiplier"], 
                            "range": [round(v * conv_details["multiplier"]) for v in conv_details["range_from"]],
                            "sense": "inverse"
                        })
    
    if not possible_conversions:
        return exercices

    for _ in range(n):
        chosen_conv = random.choice(possible_conversions)
        
        val_from = random.randint(chosen_conv["range"][0], chosen_conv["range"][1])
        exercices.append(f"{val_from} {chosen_conv['from_unit']} = ......... {chosen_conv['to_unit']}")
        
    return exercices

def generate_sort_exercises(params, days):
    """ Génère des exercices de rangement de nombres pour plusieurs jours. """
    sort_count = params.get('sort_count', 0)
    sort_digits = params.get('sort_digits', 0)
    sort_n_numbers = params.get('sort_n_numbers', 0)
    sort_type_croissant_param = params.get('sort_type_croissant', True)
    sort_type_decroissant_param = params.get('sort_type_decroissant', False)
    all_sort_exercises = []

    if sort_count > 0 and sort_digits > 0 and sort_n_numbers > 0 and \
       (sort_type_croissant_param or sort_type_decroissant_param):
        
        needs_daily_random_sort = sort_type_croissant_param and sort_type_decroissant_param
        
        for _ in range(days):
            daily_sort_ex = []
            actual_sort_type_for_day = 'croissant' 
            if needs_daily_random_sort:
                actual_sort_type_for_day = random.choice(['croissant', 'decroissant'])
            elif sort_type_decroissant_param:
                actual_sort_type_for_day = 'decroissant'
            
            for _ in range(sort_count):
                min_val = 0
                if sort_digits == 1: max_val = 9
                elif sort_digits > 1:
                    min_val = 10**(sort_digits-1)
                    max_val = 10**sort_digits - 1
                else: 
                    max_val = 0 
                
                numbers = [random.randint(min_val, max_val) for _ in range(sort_n_numbers)]
                daily_sort_ex.append({
                    'numbers': numbers,
                    'type': actual_sort_type_for_day
                })
            all_sort_exercises.append(daily_sort_ex)
    else: 
        for _ in range(days):
            all_sort_exercises.append([])
            
    return all_sort_exercises

def generate_daily_encadrement_exercises(count, digits, types):
    """ Génère des exercices d'encadrement pour un jour. """
    generated_lines = []
    if count > 0 and digits > 0 and types:
        min_n = 0
        if digits == 1: max_n = 9
        elif digits > 1:
            min_n = 10**(digits - 1)
            max_n = (10**digits - 1)
        else: 
            max_n = 0
        
        for _ in range(count):
            t = random.choice(types)
            if min_n > max_n: 
                n = min_n 
            else:
                n = random.randint(min_n, max_n)
            generated_lines.append({'number': n, 'type': t})
    return generated_lines