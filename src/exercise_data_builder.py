import random
from mesures_generator import generate_sort_exercises, generate_daily_encadrement_exercises # Ajout des imports

class InvalidFieldError(Exception):
    def __init__(self, field_name, value):
        super().__init__(f"Champ '{field_name}' invalide : '{value}' n'est pas un nombre valide.")
        self.field_name = field_name
        self.value = value

class ExerciseDataBuilder:
    @staticmethod
    def build(params):
        # print(f"ExerciseDataBuilder.build: Received params. params.get('current_level_for_conversions') is {params.get('current_level_for_conversions')}") # Debug print
        try:
            days = params['days']
            relier_count = params.get('relier_count', 0)
            operations = []
            params_list = []
            # Addition
            if params.get('addition_count', 0) > 0 and params.get('addition_digits', 0) > 0:
                count = params['addition_count']
                digits = params['addition_digits']
                decimals = params.get('addition_decimals', 0)
                params_list.append({
                    'operation': 'addition',
                    'count': count,
                    'digits': digits,
                    'with_decimals': decimals > 0,
                    'decimals': decimals
                })
                operations.append('addition')
            # Soustraction
            if params.get('subtraction_count', 0) > 0 and params.get('subtraction_digits', 0) > 0:
                count = params['subtraction_count']
                digits = params['subtraction_digits']
                decimals = params.get('subtraction_decimals', 0)
                allow_negative = params.get('subtraction_negative', False)
                params_list.append({
                    'operation': 'soustraction',
                    'count': count,
                    'digits': digits,
                    'with_decimals': decimals > 0,
                    'decimals': decimals,
                    'allow_negative': allow_negative
                })
                operations.append('soustraction')
            # Multiplication
            if params.get('multiplication_count', 0) > 0 and params.get('multiplication_digits', 0) > 0:
                count = params['multiplication_count']
                digits = params['multiplication_digits']
                decimals = params.get('multiplication_decimals', 0)
                params_list.append({
                    'operation': 'multiplication',
                    'count': count,
                    'digits': digits,
                    'with_decimals': decimals > 0,
                    'decimals': decimals
                })
                operations.append('multiplication')
            # Division
            if params.get('division_count', 0) > 0 and params.get('division_digits', 0) > 0:
                count = params['division_count']
                digits = params['division_digits']
                division_reste = params.get('division_reste', False)
                division_decimals = params.get('division_decimals', 0)
                division_quotient_decimal = division_decimals > 0
                params_list.append({
                    'operation': 'division',
                    'count': count,
                    'digits': digits,
                    'division_reste': division_reste,
                    'division_quotient_decimal': division_quotient_decimal,
                    'division_decimals': division_decimals
                })
                operations.append('division')

            # Conjugaison
            groupes_choisis = params.get('conjugation_groups', [])
            include_usuels = params.get('conjugation_usual', False)
            TENSES = params.get('TENSES', [])
            temps_choisis = params.get('conjugation_tenses', [])
            jours = days
            verbes_par_jour = params.get('verbs_per_day', 0)
            VERBS = params.get('VERBS', {})
            verbes_possibles = []
            for g in groupes_choisis:
                verbes_possibles += VERBS.get(g, [])
            if include_usuels and "usuels" in VERBS:
                verbes_possibles += VERBS["usuels"]
            
            # S'assurer qu'il y a des verbes et des temps avant de continuer
            if not verbes_possibles or not temps_choisis:
                verbes_par_jour = 0 # Force à 0 si pas de verbes ou pas de temps

            if verbes_par_jour > 0 and len(verbes_possibles) < verbes_par_jour * jours:
                print("Avertissement : Pas assez de verbes uniques pour couvrir tous les jours sans doublon. Les verbes seront répétés.")
                # Permettre la répétition si nécessaire
                extended_verbes_possibles = []
                while len(extended_verbes_possibles) < verbes_par_jour * jours:
                    random.shuffle(verbes_possibles) # Mélanger pour varier la répétition
                    extended_verbes_possibles.extend(verbes_possibles)
                verbes_possibles = extended_verbes_possibles[:verbes_par_jour * jours]


            index = 0
            conjugations = []
            if verbes_par_jour > 0: # Seulement si on doit générer des conjugaisons
                for _ in range(jours):
                    daily_conjugations = []
                    for _ in range(verbes_par_jour):
                        if index < len(verbes_possibles): # Vérifier si on a encore des verbes
                            verbe = verbes_possibles[index]
                            index += 1
                            temps = random.choice(temps_choisis)
                            daily_conjugations.append({"verb": verbe, "tense": temps})
                        else: # Plus de verbes disponibles (ne devrait pas arriver avec la logique d'extension)
                            break 
                    conjugations.append(daily_conjugations)
            else: # Pas de conjugaisons à générer
                 for _ in range(jours):
                    conjugations.append([])


            # Construction des listes attendues par generate_workbook_pdf
            operations_list = []
            counts = []
            max_digits = []
            for param in params_list:
                operations_list.append(param['operation'])
                counts.append(param['count'])
                max_digits.append(param['digits'])

            # Grammaire
            grammar_sentence_count = params.get('grammar_sentence_count', 0)
            grammar_types = params.get('grammar_types', [])
            grammar_transformations = params.get('grammar_transformations', [])
            get_random_phrases = params.get('get_random_phrases')
            get_random_transformation = params.get('get_random_transformation')
            grammar_exercises = []
            for _ in range(jours):
                phrases_choisies = get_random_phrases(grammar_types, grammar_sentence_count)
                daily_grammar = []
                if phrases_choisies and grammar_transformations: # S'assurer qu'il y a des phrases ET des transformations possibles
                    for phrase in phrases_choisies:
                        transformation = get_random_transformation(grammar_transformations)
                        if transformation: # S'assurer qu'une transformation a été choisie
                            daily_grammar.append({
                                'phrase': phrase,
                                'transformation': transformation
                            })
                grammar_exercises.append(daily_grammar)

            # Conversion
            generate_conversion_exercises = params.get('generate_conversion_exercises')
            geo_ex_count = params.get('geo_ex_count', 0)
            geo_types = params.get('geo_types', [])
            geo_senses = params.get('geo_senses', [])
            all_geo_exercises = [] # Sera une liste de listes (une par jour)
            if geo_types and geo_ex_count > 0 and geo_senses and generate_conversion_exercises:
                for _ in range(days): # Générer pour chaque jour
                    # Passer le niveau actuel à la fonction de génération
                    # print(f"ExerciseDataBuilder: Calling generate_conversion_exercises with current_level={params.get('current_level_for_conversions')}") # Debug print
                    daily_geo_ex = generate_conversion_exercises(
                        types_selectionnes=geo_types,
                        n=geo_ex_count,
                        senses=geo_senses,
                        current_level=params.get('current_level_for_conversions'))
                    all_geo_exercises.append(daily_geo_ex)
            else: # S'il n'y a pas d'exercices de conversion, s'assurer que la structure est cohérente
                for _ in range(days):
                    all_geo_exercises.append([])

            # Anglais
            english_types = params.get('english_types', [])
            PHRASES_SIMPLES = params.get('PHRASES_SIMPLES', [])
            PHRASES_COMPLEXES = params.get('PHRASES_COMPLEXES', [])
            MOTS_A_RELIER = params.get('MOTS_A_RELIER', [])
            english_ex_count = params.get('english_ex_count', 0) # Nombre de phrases à compléter
            # relier_count est le nombre de jeux à relier, déjà dans params
            # n_mots_reliés est le nombre de mots par jeu, déjà dans params
            
            english_exercises_data = [] # Renommé pour éviter conflit avec le paramètre 'english_exercises' de EduForge
            
            # Récupérer les paramètres pour la fonction de génération anglaise
            generate_english_full_exercises_func = params.get('generate_english_full_exercises_func')
            n_complete_param = params.get('english_complete_count', 0)
            n_relier_param = params.get('english_relier_count', 0) # Nombre de jeux
            n_mots_relies_param = params.get('relier_count', 0) # Nombre de mots par jeu
            # print(f"DEBUG Builder: Thèmes reçus: {params.get('selected_english_themes')}") # DEBUG
            selected_english_themes = params.get('selected_english_themes', [])
            
            if generate_english_full_exercises_func:
                for _ in range(jours):
                    daily_english_ex = generate_english_full_exercises_func(
                        types=english_types, # ['simple', 'complexe']
                        n_complete=n_complete_param,
                        n_relier=n_relier_param,
                        n_mots_reliés=n_mots_relies_param,
                        selected_themes=selected_english_themes
                    )
                    english_exercises_data.append(daily_english_ex)
            else:
                for _ in range(jours):
                    english_exercises_data.append([])


            # Orthographe
            import os, json
            orthographe_ex_count = params.get('orthographe_ex_count', 0)
            orthographe_homophones = params.get('orthographe_homophones', [])
            # Charger les phrases depuis le JSON
            homophones_path = os.path.join(os.path.dirname(__file__), 'json', 'homophones.json')
            with open(homophones_path, encoding='utf-8') as f:
                homophones_data = json.load(f)
            orthographe_exercises = []
            for day_idx in range(jours):
                daily_orthographe = []
                for _ in range(orthographe_ex_count):
                    if orthographe_homophones:
                        homophone = random.choice(orthographe_homophones)
                        # Normaliser la clé pour correspondre au JSON (enlever les espaces autour du slash)
                        homophone_key = homophone.replace(' / ', '/').replace(' ', '') if homophone.count('/') == 1 else homophone
                        if homophone_key not in homophones_data:
                            homophone_key = homophone.replace(' / ', '/').replace(' ', '')
                        phrases = homophones_data.get(homophone_key, [])
                        if phrases:
                            phrase = random.choice(phrases)
                            daily_orthographe.append({'type': 'homophone', 'homophone': homophone, 'content': phrase})
                orthographe_exercises.append(daily_orthographe)
            
            # Enumérer un nombre
            enumerate_count = params.get('enumerate_count', 0)
            enumerate_digits = params.get('enumerate_digits', 0)
            all_enumerate_exercises = [] # Sera une liste de listes (une par jour)
            if enumerate_count > 0 and enumerate_digits > 0:
                for _ in range(days): # Générer pour chaque jour
                    daily_enum_ex = []
                    for _ in range(enumerate_count):
                        n = random.randint(0, 10**enumerate_digits-1)
                        daily_enum_ex.append(n)
                    all_enumerate_exercises.append(daily_enum_ex)
            else:
                for _ in range(days):
                    all_enumerate_exercises.append([])

            # Ranger les nombres (utilise la nouvelle fonction de mesures_generator)
            all_sort_exercises = generate_sort_exercises(params, jours)

            # Encadrement de nombre
            encadrement_build_params = params.get('encadrement_params', {'count': 0, 'digits': 0, 'types': []})
            all_encadrement_exercises_list = []
            if encadrement_build_params['count'] > 0 and encadrement_build_params['digits'] > 0 and encadrement_build_params['types']:
                for _ in range(jours):
                    daily_ex = generate_daily_encadrement_exercises(
                        encadrement_build_params['count'],
                        encadrement_build_params['digits'],
                        encadrement_build_params['types']
                    )
                    all_encadrement_exercises_list.append(daily_ex)
            else:
                for _ in range(jours):
                    all_encadrement_exercises_list.append([])

            # Petits Problèmes Mathématiques
            generate_math_problems_func = params.get('generate_math_problems_func')
            math_problems_count = params.get('math_problems_count', 0)
            selected_math_problem_types = params.get('selected_math_problem_types', [])
            current_level_for_problems = params.get('current_level_for_problems')
            all_math_problems = [] # Sera une liste de listes (une par jour)

            if generate_math_problems_func and math_problems_count > 0 and selected_math_problem_types:
                for _ in range(jours):
                    daily_math_problems = generate_math_problems_func(
                        selected_problem_types=selected_math_problem_types,
                        num_problems=math_problems_count,
                        target_level=current_level_for_problems
                    )
                    all_math_problems.append(daily_math_problems)
            else:
                for _ in range(jours):
                    all_math_problems.append([])

            return {
                'days': days,
                'operations': operations_list,
                'counts': counts,
                'max_digits': max_digits,
                'conjugations': conjugations,
                'params_list': params_list,
                'grammar_exercises': grammar_exercises,
                'geo_exercises': all_geo_exercises, 
                'english_exercises': english_exercises_data, # Utiliser les données générées ici
                'orthographe_exercises': orthographe_exercises,
                'enumerate_exercises': all_enumerate_exercises,
                'sort_exercises': all_sort_exercises, 
                'encadrement_exercises_list': all_encadrement_exercises_list, # Modifié pour la nouvelle structure
                'math_problems': all_math_problems
            }
        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
            return None # Retourner None en cas d'erreur de validation
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite dans ExerciseDataBuilder.build : {type(e).__name__} : {e}")
            traceback.print_exc()
            return None # Retourner None en cas d'autre erreur
