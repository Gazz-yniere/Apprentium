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
    print("ERREUR: Fichier conversions_config.json introuvable. "
          "Les exercices de conversion ne seront pas disponibles.")
except json.JSONDecodeError as e:
    print(f"ERREUR: Erreur de décodage JSON dans 'conversions_config.json': {e}. "
          "Les exercices de conversion ne seront pas disponibles.")
except Exception as e:
    print(f"ERREUR: Impossible de charger les données de conversion: {e}. "
          "Les exercices de conversion ne seront pas disponibles.")


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
                    if "inverse" in senses and conv_details["multiplier"] != 0:
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

        val_from = random.randint(
            chosen_conv["range"][0], chosen_conv["range"][1])
        exercices.append(
            f"{val_from} {chosen_conv['from_unit']} = ......... {chosen_conv['to_unit']}")

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
                actual_sort_type_for_day = random.choice(
                    ['croissant', 'decroissant'])
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

                numbers = [random.randint(min_val, max_val)
                           for _ in range(sort_n_numbers)]
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
                    # Déterminer step et start_value en fonction du type
                    if chosen_type in ['arithmetic_plus', 'arithmetic_minus']:
                        step = random.randint(1, 9)
                        start_value = random.randint(1, 50)
                        if chosen_type == 'arithmetic_minus' and sequence_length > 4:
                            start_value = random.randint(
                                step * (sequence_length // 2) + 5, 60 + step * (sequence_length // 2))
                    elif chosen_type == 'arithmetic_multiply':
                        step = random.randint(2, 10)
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
                        temp_sequence_for_division.reverse()
                        sequence = temp_sequence_for_division
                        # Le premier terme de la suite de division
                        start_value = sequence[0]
                        # current_val sera initialisé à start_value plus bas

                    if chosen_type != 'arithmetic_divide':  # Pour les autres types, initialiser comme avant
                        sequence = [start_value]
                    current_val = start_value

                    # Essayer de construire jusqu'à la longueur désirée
                    for i in range(1, sequence_length):
                        prev_val = current_val
                        if chosen_type == 'arithmetic_plus':
                            current_val += step
                        elif chosen_type == 'arithmetic_minus':
                            if current_val == 0:
                                break
                            current_val -= step
                            if current_val < 0:
                                current_val = 0
                        elif chosen_type == 'arithmetic_multiply':
                            # Suppression de la limite de 10000
                            # Vérifier avant multiplication
                            if prev_val > (10**12) / step:
                                break
                            current_val *= step
                            if current_val > 10**12:
                                break  # Limite très haute pour éviter des nombres gigantesques
                        elif chosen_type == 'arithmetic_divide':
                            if step == 0:
                                break
                            if current_val < step or current_val % step != 0:
                                break
                            current_val //= step
                            if current_val == 0 and prev_val > 0:  # Éviter de finir sur 0
                                if len(sequence) > 1:
                                    sequence.pop()  # Retirer le 0
                                break
                            if current_val < 1 and prev_val > 0:  # Si on obtient une fraction < 1
                                break

                        # Pour la division, la séquence est déjà construite.
                        # Pour les autres, on ajoute le terme.
                        if chosen_type != 'arithmetic_divide':
                            sequence.append(current_val)

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
