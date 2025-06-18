import random
import json
import os
import sys

def get_resource_path(filename):
    # Duplicated from problemes_maths_generator.py, consider centralizing later
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "json", filename)
    return os.path.join(os.path.dirname(__file__), "json", filename)

PROBLEMS_DATA = {}
try:
    with open(get_resource_path('problemes_maths.json'), 'r', encoding='utf-8') as f:
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
    if isinstance(max_val_config, str): # Gère les dépendances comme "X-1"
        try:
            # Tente d'évaluer l'expression. 'current_vars' fournit le contexte.
            max_val = eval(max_val_config, {}, current_vars)
        except Exception as e_eval:
            print(f"Avertissement: Impossible d'évaluer la dépendance '{max_val_config}' pour la variable '{var_name_for_debug}'. Contexte: {current_vars}. Erreur: {e_eval}. Utilisation de la valeur min ({min_val}).")
            max_val = min_val # Fallback
    
    if min_val > max_val:
        max_val = min_val 

    return random.randint(min_val, max_val)

MAX_RETRIES_PER_PROBLEM = 10 # Pour éviter les boucles infinies si une condition est difficile à satisfaire

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

    candidate_problem_templates = []
    for problem_type_key in selected_problem_types:
        if problem_type_key in PROBLEMS_DATA:
            for template in PROBLEMS_DATA[problem_type_key]:
                if target_level in template.get("levels", []):
                    candidate_problem_templates.append(template)
    
    if not candidate_problem_templates:
        return generated_exercises

    problems_generated_count = 0
    while problems_generated_count < num_problems:
        if not candidate_problem_templates:
            break 

        problem_successfully_generated_for_iteration = False
        for _retry_attempt in range(MAX_RETRIES_PER_PROBLEM):
            template = random.choice(candidate_problem_templates)
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
                    print(f"Avertissement: Erreur lors de l'évaluation de la condition '{python_condition_str}' pour le modèle '{enonce_template}': {e}. Tentative suivante.")
                    condition_met = False 
            
            if condition_met:
                formatted_enonce = enonce_template.format(**instance_variables)
                generated_exercises.append({"type": "math_problem", "content": formatted_enonce})
                problems_generated_count += 1
                problem_successfully_generated_for_iteration = True
                break 

        if not problem_successfully_generated_for_iteration:
            print(f"Avertissement: Impossible de générer un problème satisfaisant les conditions après {MAX_RETRIES_PER_PROBLEM} tentatives pour un modèle. Passage au problème suivant si possible.")
    return generated_exercises

def generate_arithmetic_problems(operation, params):
    """ Génère des problèmes arithmétiques simples (addition, soustraction, etc.). """
    problems = []
    count = params.get('count', 5)
    digits = params.get('digits', 2)
    decimals = params.get('decimals', 0)
    with_decimals = decimals > 0
    allow_negative = params.get('allow_negative', False)
    division_reste = params.get('division_reste', False)
    division_quotient_decimal = params.get('division_quotient_decimal', False) # This was from pdf_generator, but seems it should be based on division_decimals
    division_decimals = params.get('division_decimals', 0)

    for _ in range(count):
        if operation == "addition":
            if with_decimals:
                a = round(random.uniform(0, 10**digits-1), decimals)
                b = round(random.uniform(0, 10**digits-1), decimals)
            else:
                a = random.randint(0, 10**digits-1)
                b = random.randint(0, 10**digits-1)
            problems.append(f"{a} + {b} = ")
        elif operation == "soustraction":
            if with_decimals:
                a = round(random.uniform(0, 10**digits-1), decimals)
                b = round(random.uniform(0, 10**digits-1), decimals)
            else:
                a = random.randint(0, 10**digits-1)
                b = random.randint(0, 10**digits-1)
            if not allow_negative and a < b:
                a, b = b, a
            problems.append(f"{a} - {b} = ")
        elif operation == "multiplication":
            if with_decimals:
                a = round(random.uniform(0, 10**digits-1), decimals)
                b = round(random.uniform(0, 10**digits-1), decimals)
            else:
                a = random.randint(0, 10**digits-1)
                b = random.randint(0, 10**digits-1)
            problems.append(f"{a} × {b} = ")
        elif operation == "division":
            min_divisor = 1 # Divisor can be 1
            # Max divisor should be based on digits, ensuring it's not 0 if digits is 0 or 1
            max_divisor = (10**digits -1) if digits > 0 else 9 # if digits is 0, max_divisor is 9 (single digit)
            if max_divisor == 0 : max_divisor = 1 # Ensure max_divisor is at least 1
            
            divisor = random.randint(min_divisor, max_divisor)
            if divisor == 0: divisor = 1 # Avoid division by zero explicitly

            if division_quotient_decimal and division_decimals > 0: # Corrected from pdf_generator
                # For decimal quotients, ensure dividend allows for it.
                # This part needs careful implementation if we want specific decimal places in quotient.
                # For now, let's make dividend a product that might result in decimals.
                quotient_val = round(random.uniform(1, 10), division_decimals) # Desired quotient
                dividend = round(divisor * quotient_val, division_decimals + 2) # Ensure precision
                # Ensure dividend is not smaller than divisor if we want non-zero integer part
                if dividend < divisor and digits > 0 : dividend = divisor # simple adjustment
                problems.append(f"{dividend} ÷ {divisor} = ")
            elif not division_reste: # Exact division
                quotient = random.randint(1, 10**(digits if digits > 0 else 1)) # Quotient can also have 'digits'
                dividend = divisor * quotient
                problems.append(f"{dividend} ÷ {divisor} = ")
            else: # Division with remainder
                quotient = random.randint(1, 10**(digits if digits > 0 else 1))
                # Remainder must be less than divisor. If divisor is 1, remainder is 0.
                reste = random.randint(0, divisor - 1) if divisor > 1 else 0
                dividend = divisor * quotient + reste
                problems.append(f"{dividend} ÷ {divisor} = ")
    return problems

if __name__ == '__main__':
    # Test story problems
    test_problems_cp = generate_story_math_problems(["addition_simple", "soustraction_simple"], 2, "CP")
    print("Problèmes CP (Story):", test_problems_cp)
    test_problems_ce1_mult = generate_story_math_problems(["multiplication_simple"], 1, "CE1")
    print("Problèmes CE1 Mult (Story):", test_problems_ce1_mult)
    
    # Test arithmetic problems
    print("\nProblèmes Arithmétiques:")
    add_params = {'count': 2, 'digits': 2, 'decimals': 0}
    print("Addition:", generate_arithmetic_problems("addition", add_params))
    
    sub_params = {'count': 2, 'digits': 2, 'decimals': 1, 'allow_negative': True}
    print("Soustraction:", generate_arithmetic_problems("soustraction", sub_params))

    mult_params = {'count': 1, 'digits': 1, 'decimals': 0}
    print("Multiplication:", generate_arithmetic_problems("multiplication", mult_params))

    div_params_exact = {'count': 2, 'digits': 2, 'division_reste': False}
    print("Division (exacte):", generate_arithmetic_problems("division", div_params_exact))

    div_params_reste = {'count': 2, 'digits': 1, 'division_reste': True} # digits 1 for divisor
    print("Division (avec reste):", generate_arithmetic_problems("division", div_params_reste))

    # Test for division_quotient_decimal (from pdf_generator logic)
    div_params_decimal_q = {'count':1, 'digits':1, 'division_decimals':1, 'division_quotient_decimal': True} 
    print("Division (quotient decimal):", generate_arithmetic_problems("division", div_params_decimal_q))