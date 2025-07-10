import random
import json
import os
import sys
from utils.resource_path import project_file_path


def get_resource_path(filename):
    # Duplicated from problemes_maths_generator.py, consider centralizing later
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "json", filename)
    return os.path.join(os.path.dirname(__file__), "json", filename)


PROBLEMS_DATA = {}
try:
    with open(project_file_path('json/problemes_maths.json'), 'r', encoding='utf-8') as f:
        PROBLEMS_DATA = json.load(f)
except Exception as e:
    print(f"ERREUR: Impossible de charger les problèmes mathématiques depuis 'problemes_maths.json': {e}")


def _get_variable_value(var_config, current_vars, var_name_for_debug="<inconnue>"):
    """ Calcule la valeur d'une variable en tenant compte des dépendances. """
    if not isinstance(var_config, (list, tuple)):
        err_msg = f"Configuration de variable invalide pour '{var_name_for_debug}'. Attendu une liste/tuple, reçu: {var_config} (type: {type(var_config)})"
        print(f"ERREUR critique dans _get_variable_value: {err_msg}")
        raise TypeError(err_msg)

    if len(var_config) != 2:
        err_msg = f"Configuration de variable invalide pour '{var_name_for_debug}'. Attendu 2 éléments, reçu: {var_config} (longueur: {len(var_config)})"
        print(f"ERREUR critique dans _get_variable_value: {err_msg}")
        raise ValueError(err_msg)

    min_val, max_val_config = var_config
    max_val = max_val_config
    if isinstance(max_val_config, str):  # Gère les dépendances comme "X-1"
        try:
            # Tente d'évaluer l'expression. 'current_vars' fournit le contexte.
            max_val = eval(max_val_config, {}, current_vars)
        except Exception as e_eval:
            print(f"Avertissement: Impossible d'évaluer la dépendance '{max_val_config}' " f"pour la variable '{var_name_for_debug}'. Contexte: {current_vars}. " f"Erreur: {e_eval}. Utilisation de la valeur min ({min_val}).")
            max_val = min_val  # Fallback

    if min_val > max_val:
        max_val = min_val

    return random.randint(min_val, max_val)


# Pour éviter les boucles infinies si une condition est difficile à satisfaire
MAX_RETRIES_PER_PROBLEM = 10


def generate_story_math_problems(selected_problem_types, num_problems, target_level):
    """
    Génère des problèmes mathématiques (petits problèmes).
    selected_problem_types: Liste des types de problèmes choisis (ex: ["addition_simple", "soustraction_simple"]).
    num_problems: Nombre total de problèmes à générer.
    target_level: Niveau scolaire actuel (CP, CE1, etc.) pour filtrer les problèmes.
    """
    generated_exercises = []
    if not PROBLEMS_DATA or not selected_problem_types or num_problems == 0:
        return generated_exercises

    # print(f"DEBUG calculs_generator: target_level = {target_level}, selected_problem_types = {selected_problem_types}")

    candidate_problem_templates = []
    for problem_type_key in selected_problem_types:
        if problem_type_key in PROBLEMS_DATA:
            for template in PROBLEMS_DATA[problem_type_key]:
                problem_levels = template.get("levels", [])
                # If target_level is None (no level selected), or no specific levels are defined for the problem,
                # or the target_level matches one of the problem's levels.
                if target_level is None or not problem_levels or target_level in problem_levels:
                    candidate_problem_templates.append(template)

    # print(f"DEBUG calculs_generator: Found {len(candidate_problem_templates)} candidate problem templates.")

    if not candidate_problem_templates:
        return generated_exercises

    # --- MODIFICATION : Assurer des problèmes uniques par jour ---
    # S'assurer de ne pas demander plus de problèmes qu'il n'y a de modèles uniques.
    if len(candidate_problem_templates) < num_problems:
        print(f"Avertissement: Le nombre de problèmes mathématiques demandés ({num_problems}) est supérieur au nombre de modèles uniques disponibles ({len(candidate_problem_templates)}). Le nombre de problèmes sera limité.")
        num_problems = len(candidate_problem_templates)

    # Sélectionner un échantillon de modèles uniques pour éviter les doublons.
    selected_templates = random.sample(candidate_problem_templates, num_problems)

    for template in selected_templates:
        problem_successfully_generated_for_iteration = False
        for _retry_attempt in range(MAX_RETRIES_PER_PROBLEM):
            # Le modèle est déjà choisi, on génère juste les variables
            enonce_template = template["enonce"]
            variables_config = template["variables"]
            condition_str = template.get("condition")

            instance_variables = {}
            sorted_var_keys = list(variables_config.keys())

            for var_name in sorted_var_keys:
                if var_name == "condition":
                    continue
                instance_variables[var_name] = _get_variable_value(variables_config[var_name], instance_variables, var_name)

            condition_met = True
            if condition_str:
                python_condition_str = condition_str.replace("===", "==")
                try:
                    if not eval(python_condition_str, {}, instance_variables):
                        condition_met = False
                except Exception as e:
                    print(f"Avertissement: Erreur lors de l'évaluation de la condition " f"'{python_condition_str}' pour le modèle '{enonce_template}': {e}. " "Tentative suivante.")
                    condition_met = False

            if condition_met:
                formatted_enonce = enonce_template.format(**instance_variables)
                generated_exercises.append({"type": "math_problem", "content": formatted_enonce})
                problem_successfully_generated_for_iteration = True
                break # Sortir de la boucle de tentatives

        if not problem_successfully_generated_for_iteration:
            print(f"Avertissement: Impossible de générer un problème satisfaisant les conditions " f"après {MAX_RETRIES_PER_PROBLEM} tentatives pour le modèle '{template['enonce']}'.")
    return generated_exercises


def generate_arithmetic_problems(operation, params):
    """ Génère des problèmes arithmétiques simples (addition, soustraction, etc.). """
    problems = []
    count = params.get('count', 5)
    num_operands = params.get('num_operands', 2)
    digits = params.get('digits', 2)
    decimals = params.get('decimals', 0)
    with_decimals = decimals > 0
    allow_negative = params.get('allow_negative', False)
    division_reste = params.get('division_reste', False)
    # This was from pdf_generator, but seems it should be based on division_decimals
    division_quotient_decimal = params.get('division_quotient_decimal', False)
    division_decimals = params.get('division_decimals', 0)

    if num_operands < 2:  # S'assurer qu'il y a au moins 2 opérandes
        num_operands = 2

    for _ in range(count):
        operands = []
        # Génération standard des opérandes (non nuls)
        for i_op_gen in range(num_operands):
            min_op_val = 0.1 * (10**(-decimals)) if with_decimals else 1  # Eviter 0

            if with_decimals:
                # Max value: 10^digits - epsilon, or 9.99... if digits=0
                max_val_raw = (10**digits - (0.1**(decimals+2))) if digits > 0 else (10 - (0.1**(decimals+2)))
                op_val_raw = random.uniform(min_op_val, max_val_raw)
                op = round(op_val_raw, decimals)
                if op == 0:
                    op = min_op_val  # S'assurer qu'il n'est pas 0.0 après arrondi
            else:
                # Max value: 10^digits - 1, or 9 if digits=0
                max_val_int = (10**digits - 1) if digits > 0 else 9
                op = random.randint(min_op_val, max_val_int if max_val_int >= min_op_val else min_op_val)
                if op == 0:
                    op = 1  # S'assurer qu'il n'est pas 0
            operands.append(op)

        if operation == "addition":
            # Pour l'addition, tous les opérandes sont ajoutés
            problem_str = " + ".join(map(str, operands))
            problems.append(f"{problem_str} = ")

        elif operation == "soustraction":
            if allow_negative:
                # La génération standard des opérandes est utilisée si les négatifs sont autorisés
                # (operands a déjà été rempli au début de la boucle)
                problem_str = " - ".join(map(str, operands))
            else:
                # Assurer un résultat positif ou nul
                subtractors = []
                # Générer les N-1 opérandes à soustraire
                for _ in range(num_operands - 1):
                    min_op_val = 0.1 * (10**(-decimals)) if with_decimals else 1
                    if with_decimals:
                        max_val_raw = (10**digits - (0.1**(decimals+2))) if digits > 0 else (10 - (0.1**(decimals+2)))
                        op_val_raw = random.uniform(min_op_val, max_val_raw)
                        op = round(op_val_raw, decimals)
                        if op == 0:
                            op = min_op_val
                    else:
                        max_val_int = (10**digits - 1) if digits > 0 else 9
                        op = random.randint(min_op_val, max_val_int if max_val_int >= min_op_val else min_op_val)
                        if op == 0:
                            op = 1
                    subtractors.append(op)

                sum_of_subtractors = sum(subtractors)

                # Générer le premier opérande (minuend)
                minuend_min_val = sum_of_subtractors

                # Définir une plage pour la partie "résultat" de l'opération
                if with_decimals:
                    result_range_max = (
                        10**digits - (0.1**(decimals+2))) if digits > 0 else (10 - (0.1**(decimals+2)))
                    minuend_val = round(random.uniform(
                        minuend_min_val, minuend_min_val + result_range_max), decimals)
                    if minuend_val < minuend_min_val:  # Assurer après arrondi
                        minuend_val = minuend_min_val
                else:
                    result_range_max = (10**digits - 1) if digits > 0 else 9
                    # Assurer que result_range_max est au moins 0 pour éviter randint error
                    if result_range_max < 0:
                        result_range_max = 0
                    minuend_val = random.randint(int(minuend_min_val), int(
                        minuend_min_val + result_range_max))

                final_operands = [minuend_val] + subtractors
                problem_str = " - ".join(map(str, final_operands))
            problems.append(f"{problem_str} = ")

        elif operation == "multiplication":
            # Pour la multiplication, tous les opérandes sont multipliés
            problem_str = " × ".join(map(str, operands))
            problems.append(f"{problem_str} = ")

        elif operation == "division":
            # La division reste à 2 opérandes (dividende et diviseur) pour l'instant
            # car la division multiple (a / b / c) est moins courante et plus ambiguë.
            # On utilise les deux premiers opérandes générés.
            if len(operands) < 2:  # S'assurer qu'on a au moins deux opérandes pour la division
                if with_decimals:
                    operands.append(
                        round(random.uniform(0, 10**digits-1), decimals))
                else:
                    operands.append(random.randint(0, 10**digits-1))

            # dividend_base = operands[0]  # Sera ajusté

            min_divisor = 1  # Divisor can be 1
            # Max divisor should be based on digits, ensuring it's not 0 if digits is 0 or 1
            # if digits is 0, max_divisor is 9 (single digit)
            max_divisor = (10**digits - 1) if digits > 0 else 9
            if max_divisor == 0:
                max_divisor = 1  # Ensure max_divisor is at least 1

            divisor = operands[1] if min_divisor <= operands[1] <= max_divisor else random.randint(min_divisor, max_divisor)  # noqa: E501
            if divisor == 0:
                divisor = 1  # Avoid division by zero explicitly

            if division_quotient_decimal and division_decimals > 0:  # Corrected from pdf_generator
                # For decimal quotients, ensure dividend allows for it.
                # This part needs careful implementation if we want specific decimal places in quotient.
                # For now, let's make dividend a product that might result in decimals.
                quotient_val = round(random.uniform(1, 10), division_decimals)  # Desired quotient  # noqa: E501
                dividend = round(divisor * quotient_val,division_decimals + 2)  # Ensure precision
                # Ensure dividend is not smaller than divisor if we want non-zero integer part
                if dividend < divisor and digits > 0:
                    dividend = divisor  # simple adjustment
                problems.append(f"{dividend} ÷ {divisor} = ")
            elif not division_reste:  # Exact division
                # Quotient can also have 'digits'
                quotient = random.randint(1, 10**(digits if digits > 0 else 1))
                dividend = divisor * quotient  # Ensure quotient is not 0
                problems.append(f"{dividend} ÷ {divisor} = ")
            else:  # Division with remainder
                quotient = random.randint(1, 10**(digits if digits > 0 else 1))
                # Remainder must be less than divisor. If divisor is 1, remainder is 0.
                reste = random.randint(0, divisor - 1) if divisor > 1 else 0
                dividend = divisor * quotient + reste  # Ensure quotient is not 0
                problems.append(f"{dividend} ÷ {divisor} = ")
    return problems


if __name__ == '__main__':
    # Test story problems with no level
    test_problems_cp = generate_story_math_problems(["addition_simple", "soustraction_simple"], 2, "CP")
    print("Problèmes CP (Story):", test_problems_cp)
    test_problems_ce1_mult = generate_story_math_problems(["multiplication_simple"], 1, "CE1")
    print("Problèmes CE1 Mult (Story):", test_problems_ce1_mult)

    # Test arithmetic problems
    print("\nProblèmes Arithmétiques:")
    add_params = {'count': 2, 'digits': 1, 'decimals': 0, 'num_operands': 2}
    print("Addition:", generate_arithmetic_problems("addition", add_params))

    # digits=0 means single digit 1-9
    add_params_zero_digits = {'count': 1, 'digits': 0, 'decimals': 0, 'num_operands': 2}
    print("Addition (digits 0):", generate_arithmetic_problems("addition", add_params_zero_digits))

    sub_params = {'count': 2, 'digits': 2, 'decimals': 0, 'allow_negative': False, 'num_operands': 2}
    print("Soustraction:", generate_arithmetic_problems("soustraction", sub_params))
    sub_params_neg = {'count': 1, 'digits': 1, 'decimals': 0, 'allow_negative': True, 'num_operands': 2}
    print("Soustraction (neg ok):", generate_arithmetic_problems("soustraction", sub_params_neg))

    mult_params = {'count': 1, 'digits': 1, 'decimals': 0, 'num_operands': 4}
    print("Multiplication:", generate_arithmetic_problems("multiplication", mult_params))

    div_params_exact = {'count': 2, 'digits': 2, 'division_reste': False}
    print("Division (exacte):", generate_arithmetic_problems("division", div_params_exact))

    div_params_reste = {'count': 2, 'digits': 1, 'division_reste': True}  # digits 1 for divisor
    print("Division (avec reste):", generate_arithmetic_problems("division", div_params_reste))

    # Test for division_quotient_decimal (from pdf_generator logic)
    div_params_decimal_q = {'count': 1, 'digits': 1, 'division_decimals': 1, 'division_quotient_decimal': True}
    print("Division (quotient decimal):", generate_arithmetic_problems("division", div_params_decimal_q))
