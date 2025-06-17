import random
import json
import os
import sys

def get_resource_path(filename):
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
    
    # S'assurer que min_val n'est pas supérieur à max_val après évaluation
    if min_val > max_val:
        # Ceci peut arriver légitimement si max_val est une expression comme "X-5" et X est petit.
        # print(f"Avertissement: min_val ({min_val}) > max_val ({max_val}) pour la variable '{var_name_for_debug}' (config: {var_config}). Ajustement de max_val à min_val.")
        max_val = min_val # Ajuster pour éviter l'erreur avec randint

    return random.randint(min_val, max_val)

MAX_RETRIES_PER_PROBLEM = 10 # Pour éviter les boucles infinies si une condition est difficile à satisfaire


def generate_math_problems(selected_problem_types, num_problems, target_level):
    """
    Génère des problèmes mathématiques.
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
        # print(f"Avertissement: Aucun modèle de problème trouvé pour les types {selected_problem_types} et le niveau {target_level}.")
        return generated_exercises

    problems_generated_count = 0
    while problems_generated_count < num_problems:
        if not candidate_problem_templates:
            break # Plus de modèles disponibles

        problem_successfully_generated_for_iteration = False
        for _retry_attempt in range(MAX_RETRIES_PER_PROBLEM):
            template = random.choice(candidate_problem_templates)
            enonce_template = template["enonce"]
            variables_config = template["variables"]
            condition_str = template.get("condition")

            instance_variables = {}
            sorted_var_keys = list(variables_config.keys()) 

            for var_name in sorted_var_keys:
                if var_name == "condition": # Ignorer si "condition" est trouvée erronément comme clé de variable
                    continue
                instance_variables[var_name] = _get_variable_value(variables_config[var_name], instance_variables, var_name)

            condition_met = True # Supposer que la condition est remplie s'il n'y en a pas
            if condition_str:
                python_condition_str = condition_str.replace("===", "==") # Adapter pour Python
                try:
                    if not eval(python_condition_str, {}, instance_variables):
                        condition_met = False # Condition non remplie
                except Exception as e:
                    print(f"Avertissement: Erreur lors de l'évaluation de la condition '{python_condition_str}' pour le modèle '{enonce_template}': {e}. Tentative suivante.")
                    condition_met = False # Erreur d'évaluation, considérer comme non remplie
            
            if condition_met:
                formatted_enonce = enonce_template.format(**instance_variables)
                generated_exercises.append({"type": "math_problem", "content": formatted_enonce})
                problems_generated_count += 1
                problem_successfully_generated_for_iteration = True
                break # Sortir de la boucle de tentatives

        if not problem_successfully_generated_for_iteration:
            print(f"Avertissement: Impossible de générer un problème satisfaisant les conditions après {MAX_RETRIES_PER_PROBLEM} tentatives pour un modèle. Passage au problème suivant si possible.")
            # Si on ne peut pas générer ce problème, on essaiera d'en générer un autre pour atteindre num_problems
            # Si num_problems est grand et les conditions difficiles, cela pourrait prendre du temps ou ne pas atteindre le compte.
    return generated_exercises

if __name__ == '__main__':
    # Test
    test_problems_cp = generate_math_problems(["addition_simple", "soustraction_simple"], 2, "CP")
    print("Problèmes CP:", test_problems_cp)
    test_problems_ce1_mult = generate_math_problems(["multiplication_simple"], 1, "CE1")
    print("Problèmes CE1 Mult:", test_problems_ce1_mult)
    test_problems_all_ce1 = generate_math_problems(["addition_simple", "soustraction_simple", "multiplication_simple"], 3, "CE1")
    print("Problèmes CE1 Tous:", test_problems_all_ce1)
