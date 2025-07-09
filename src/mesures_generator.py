import random
import os
import json
import sys
from utils.resource_path import project_file_path


def get_resource_path(filename):
    # Utility to get resource path, useful if CONVERSION_DATA is in a JSON file
    if hasattr(sys, '_MEIPASS'):
        # For PyInstaller, assumes 'json' folder is at the same level as the executable
        return os.path.join(sys._MEIPASS, "json", filename)
    # For script execution, assumes 'json' folder is in the same directory as this script
    return os.path.join(os.path.dirname(__file__), "json", filename)


CONVERSION_DATA = {}
try:
    with open(project_file_path('json/conversions_config.json'), 'r', encoding='utf-8') as f:
        CONVERSION_DATA = json.load(f)
except FileNotFoundError:
    print("ERREUR: Fichier conversions_config.json introuvable. " "Les exercices de conversion ne seront pas disponibles.")
except json.JSONDecodeError as e:
    print(f"ERREUR: Erreur de décodage JSON dans 'conversions_config.json': {e}. " "Les exercices de conversion ne seront pas disponibles.")
except Exception as e:
    print(f"ERREUR: Impossible de charger les données de conversion: {e}. " "Les exercices de conversion ne seront pas disponibles.")

# --- NEW ---
MEASUREMENT_PROBLEMS_DATA = {}
try:
    with open(project_file_path('json/problemes_mesures.json'), 'r', encoding='utf-8') as f:
        MEASUREMENT_PROBLEMS_DATA = json.load(f)
except Exception as e:
    print(f"ERREUR: Impossible de charger les problèmes de mesures depuis 'problemes_mesures.json': {e}")
# --- END NEW ---



def generate_conversion_exercises(types_selectionnes, n, senses, current_level, level_order=None):
    """
    Génère des exercices de conversion.
    types_selectionnes: Liste des types de conversion (ex: ["longueur", "masse"]).
    n: Nombre d'exercices à générer.
    senses: Liste des sens de conversion (ex: ["direct", "inverse"]).
    current_level: Niveau scolaire actuel (ex: "CP", "CE1").
    level_order: Liste ordonnée des niveaux pour la collecte incrémentale des exercices.
    """
    exercices = []
    if not types_selectionnes or not senses or not CONVERSION_DATA or n == 0 or not current_level:
        return exercices

    # Détermine les niveaux à vérifier pour les conversions, de manière incrémentale.
    levels_to_check = []
    if level_order:
        try:
            target_index = level_order.index(current_level)
            levels_to_check = level_order[:target_index + 1]
        except ValueError:
            # Si le niveau actuel n'est pas dans la liste, on l'utilise seul.
            levels_to_check = [current_level]
    else:
        # Fallback si level_order n'est pas fourni.
        levels_to_check = [current_level]
    possible_conversions = []
    # Pour éviter les doublons si une conversion est définie dans plusieurs niveaux (ex: m->cm en CP et CE1)
    unique_conv_tracker = set()

    for type_conv in types_selectionnes:
        if type_conv in CONVERSION_DATA.get("conversions", {}): # Accède à la clé "conversions" du JSON
            for level in levels_to_check:
                level_config = CONVERSION_DATA["conversions"][type_conv].get(level) # Accès correct au type et au niveau
                if level_config:
                    for conv_details in level_config: # level_config est déjà la liste des conversions
                        if "direct" in senses and "from" in conv_details and "to" in conv_details:
                            conv_key = (type_conv, conv_details["from"], conv_details["to"], "direct")
                            if conv_key not in unique_conv_tracker:
                                possible_conversions.append({"from_unit": conv_details["from"], "to_unit": conv_details["to"],"multiplier": conv_details["multiplier"], "range": conv_details["range_from"],})
                                unique_conv_tracker.add(conv_key) 
                        if "inverse" in senses and conv_details["multiplier"] != 0:
                            conv_key = (type_conv, conv_details["to"], conv_details["from"], "inverse")
                            if conv_key not in unique_conv_tracker:
                                possible_conversions.append({"from_unit": conv_details["to"], "to_unit": conv_details["from"],"multiplier": 1 / conv_details["multiplier"], "range": [round(v * conv_details["multiplier"]) for v in conv_details["range_from"]],})
                                unique_conv_tracker.add(conv_key) 

    if not possible_conversions:
        return exercices

    for _ in range(n):
        chosen_conv = random.choice(possible_conversions)

        val_from = random.randint(
            chosen_conv["range"][0], chosen_conv["range"][1]) # noqa: E501
        exercices.append(
            f"{val_from} {chosen_conv['from_unit']} = ____________ {chosen_conv['to_unit']}")

    return exercices

# --- NEW ---
def _get_variable_value(var_config, current_vars, var_name_for_debug="<inconnue>"):
    """ Calcule la valeur d'une variable en tenant compte des dépendances. """
    if not isinstance(var_config, (list, tuple)) or len(var_config) != 2:
        raise TypeError(f"Config de variable invalide pour '{var_name_for_debug}': {var_config}")

    min_val, max_val_config = var_config
    max_val = max_val_config
    if isinstance(max_val_config, str):
        try:
            max_val = eval(max_val_config, {}, current_vars)
        except Exception as e:
            print(f"Avertissement: eval a échoué pour '{max_val_config}': {e}. Utilisation de min_val.")
            max_val = min_val

    # Ensure min_val and max_val are integers before passing to random.randint
    # This prevents ValueError: non-integer stop for randrange() if they become floats.
    min_val_int = int(min_val)
    max_val_int = int(max_val)
    return random.randint(min(min_val_int, max_val_int), max(min_val_int, max_val_int))

MAX_RETRIES_PER_PROBLEM = 10

def generate_measurement_story_problems(selected_problem_types, num_problems, target_level):
    """
    Génère des problèmes de mesures.
    selected_problem_types: Liste des types de problèmes choisis (ex: ["longueur", "masse"]).
    num_problems: Nombre total de problèmes à générer.
    target_level: Niveau scolaire actuel (CP, CE1, etc.) pour filtrer les problèmes.
    """
    generated_exercises = []
    if not MEASUREMENT_PROBLEMS_DATA or not selected_problem_types or num_problems == 0:
        return generated_exercises

    candidate_problem_templates = []
    for problem_type_key in selected_problem_types:
        if problem_type_key in MEASUREMENT_PROBLEMS_DATA:
            for template in MEASUREMENT_PROBLEMS_DATA[problem_type_key]:
                problem_levels = template.get("levels", [])
                if target_level is None or not problem_levels or target_level in problem_levels:
                    candidate_problem_templates.append(template)

    if not candidate_problem_templates:
        return generated_exercises

    problems_generated_count = 0
    while problems_generated_count < num_problems:
        if not candidate_problem_templates:
            break

        problem_successfully_generated = False
        for _ in range(MAX_RETRIES_PER_PROBLEM):
            template = random.choice(candidate_problem_templates)
            enonce_template = template["enonce"]
            variables_config = template["variables"]
            condition_str = template.get("condition")

            instance_variables = {}
            for var_name in variables_config.keys():
                instance_variables[var_name] = _get_variable_value(variables_config[var_name], instance_variables, var_name)

            condition_met = True
            if condition_str:
                try:
                    if not eval(condition_str, {}, instance_variables):
                        condition_met = False
                except Exception as e:
                    print(f"Avertissement: Erreur d'évaluation de condition '{condition_str}': {e}")
                    condition_met = False

            if condition_met:
                formatted_enonce = enonce_template.format(**instance_variables)
                generated_exercises.append({"type": "measurement_problem", "content": formatted_enonce})
                problems_generated_count += 1
                problem_successfully_generated = True
                break
        
        if not problem_successfully_generated:
            problems_generated_count += 1 # Avoid infinite loop if no problem can be generated

    return generated_exercises
# --- END NEW ---

def generate_sort_exercises(params, days):
    """ Génère des exercices de rangement de nombres pour plusieurs jours. """
    sort_count = params.get('sort_count', 0)
    sort_digits = params.get('sort_digits', 0)
    sort_n_numbers = params.get('sort_n_numbers', 0)
    sort_type_croissant_param = params.get('sort_type_croissant', True)
    sort_type_decroissant_param = params.get('sort_type_decroissant', False)
    all_sort_exercises = []

    if sort_count > 0 and sort_digits > 0 and sort_n_numbers > 0 and (sort_type_croissant_param or sort_type_decroissant_param):

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
                if sort_digits == 1:
                    max_val = 9
                elif sort_digits > 1:
                    min_val = 10**(sort_digits-1)
                    max_val = 10**sort_digits - 1
                else:
                    max_val = 0

                # Générer une liste de tous les nombres possibles dans la plage
                possible_numbers_range = list(range(min_val, max_val + 1))

                # S'assurer qu'il y a assez de nombres uniques disponibles
                if len(possible_numbers_range) < sort_n_numbers:
                    print(f"Avertissement: Pas assez de nombres uniques dans la plage [{min_val}, {max_val}] pour générer {sort_n_numbers} nombres. Le nombre d'éléments sera réduit.")
                    sort_n_numbers = len(possible_numbers_range)

                # Sélectionner des nombres uniques aléatoirement
                numbers = random.sample(possible_numbers_range, sort_n_numbers)
                daily_sort_ex.append({'numbers': numbers, 'type': actual_sort_type_for_day})
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
        if digits == 1:
            max_n = 9
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


def generate_compare_numbers_exercises(params, days):
    """ Génère des exercices de comparaison de nombres pour plusieurs jours. """
    compare_count = params.get('count', 0)
    compare_digits = params.get('digits', 0)
    all_compare_exercises = []

    if compare_count > 0 and compare_digits > 0:
        min_val = 0
        if compare_digits == 1:
            max_val = 9
        elif compare_digits > 1:
            # Pour éviter 0 si digits=1
            min_val = 10**(compare_digits - 1) if compare_digits > 1 else 0
            max_val = 10**compare_digits - 1
        else:  # digits == 0 or invalid
            max_val = 9  # fallback
            min_val = 0
        if min_val > max_val:
            min_val = max_val  # Sanity check

        for _ in range(days):
            daily_compare_ex = []
            for _ in range(compare_count):
                num1 = random.randint(min_val, max_val)
                num2 = random.randint(min_val, max_val)
                # S'assurer que les nombres sont différents pour rendre l'exercice pertinent
                while num1 == num2:
                    num2 = random.randint(min_val, max_val)
                daily_compare_ex.append({'num1': num1, 'num2': num2})
            all_compare_exercises.append(daily_compare_ex)
    else:
        for _ in range(days):
            all_compare_exercises.append([])

    return all_compare_exercises


# Une suite doit avoir au moins 3 éléments pour être valide.
MIN_VALID_SEQUENCE_LENGTH = 3
# Max tentatives pour générer une suite valide par slot d'exercice.
MAX_GENERATION_ATTEMPTS_PER_EXERCISE = 10


def generate_logical_sequences_exercises(params, days, current_level):
    """ Génère des exercices de suites logiques pour plusieurs jours. """
    sequences_count = params.get('count', 0)
    # sequence_length est le nombre total d'éléments souhaités dans la suite. Min 3.
    sequence_length = max(MIN_VALID_SEQUENCE_LENGTH, params.get('length', 5))
    selected_types = params.get('types', [])
    all_sequences_exercises = []

    # Adapter la complexité en fonction du niveau (longueur de la suite, valeur du pas)
    # num_blanks = 1      # Nombre de trous dans la suite (currently fixed to 1)

    if sequences_count > 0 and selected_types:
        for _ in range(days):
            daily_sequences_ex = []
            # Pour chaque slot d'exercice demandé pour la journée
            for _ in range(sequences_count):
                generated_valid_sequence_for_slot = False
                for _attempt in range(MAX_GENERATION_ATTEMPTS_PER_EXERCISE):
                    if not selected_types:
                        break  # Aucun type sélectionné
                    chosen_type = random.choice(selected_types)

                    step, start_value = 0, 0
                    sequence = [] # Initialize sequence for each attempt
                    # Déterminer step et start_value en fonction du type
                    if chosen_type == 'arithmetic_plus':
                        step = random.randint(1, 20) # Nouveau range pour le pas
                        start_value = random.randint(1, 100) # Nouveau range pour la valeur de départ
                        current_val = start_value
                        for _ in range(sequence_length):
                            sequence.append(current_val)
                            current_val += step
                    elif chosen_type == 'arithmetic_multiply':
                        step = random.randint(2, 10) # Pas de changement demandé
                        start_value = random.randint(1, 100)
                    elif chosen_type == 'arithmetic_divide':
                        step = random.randint(2, 5)  # Diviseur
                        # Générer la suite "à l'envers" en partant d'un petit nombre
                        # et en multipliant, puis inverser la suite.
                        # Le plus petit nombre de la suite
                        last_term = random.randint(1, 10)

                        temp_sequence_for_division = [last_term]
                        current_val_for_multi = last_term
                        possible_to_generate = True
                        for _ in range(sequence_length - 1):
                            try:
                                next_val = current_val_for_multi * step
                                if next_val > 10**12:  # Limite très haute pour éviter des nombres ingérables
                                    possible_to_generate = False
                                    break
                                temp_sequence_for_division.append(next_val)
                                current_val_for_multi = next_val
                            except OverflowError:
                                possible_to_generate = False
                                break
                        if not possible_to_generate or len(temp_sequence_for_division) != sequence_length:
                            continue  # Impossible de générer, essayer une autre tentative
                        # Inverser pour obtenir la suite de division
                        sequence = list(reversed(temp_sequence_for_division))

                    elif chosen_type == 'arithmetic_minus':
                        step = random.randint(1, 20) # Nouveau range pour le pas
                        # La plus petite valeur de la suite
                        final_value = random.randint(1, 100) # Nouveau range pour la valeur finale
                        temp_sequence_for_plus = [final_value]
                        current_val_for_plus = final_value
                        for _ in range(sequence_length - 1):
                            current_val_for_plus += step
                            temp_sequence_for_plus.append(current_val_for_plus)
                        sequence = list(reversed(temp_sequence_for_plus)) # Inverser pour obtenir la suite soustractive

                    # Pour les suites multiplicatives, la génération est similaire à avant
                    if chosen_type == 'arithmetic_multiply':
                        current_val = start_value
                        for _ in range(sequence_length):
                            # Vérifier avant multiplication pour éviter OverflowError
                            if current_val > (10**12) / step:
                                sequence = [] # Invalider la séquence
                                break
                            sequence.append(current_val)
                            current_val *= step
                            if current_val > 10**12: # Vérifier après multiplication
                                sequence = [] # Invalider la séquence
                                break

                    # La suite doit avoir exactement la longueur demandée
                    if len(sequence) == sequence_length:
                        # Blank pas aux extrémités
                        blank_pos = random.randint(1, len(sequence) - 2)
                        daily_sequences_ex.append({
                            'type': chosen_type,
                            'sequence_displayed': [val if idx != blank_pos else "____" for idx, val in enumerate(sequence)],
                            'full_sequence': sequence,
                            'blank_position': blank_pos,
                            'step': step
                        })
                        generated_valid_sequence_for_slot = True
                        break  # Sortir de la boucle d'essais, passer au prochain slot d'exercice
                if not generated_valid_sequence_for_slot:  # Check if a sequence was generated for the slot
                    pass  # Optionnellement, enregistrer ou gérer le cas où aucune séquence n'a pu être générée
            # This was potentially mis-indented or logic error
            all_sequences_exercises.append(daily_sequences_ex)
    else:
        for _ in range(days):
            all_sequences_exercises.append([])

    return all_sequences_exercises
