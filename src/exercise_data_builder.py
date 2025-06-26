import random
import os
import json
from mesures_generator import (
    generate_sort_exercises,
    generate_daily_encadrement_exercises,
    generate_compare_numbers_exercises,
    generate_logical_sequences_exercises,
    generate_measurement_story_problems
)


class InvalidFieldError(Exception):
    def __init__(self, field_name, value):
        super().__init__(f"Champ '{field_name}' invalide : '{value}' n'est pas un nombre valide.")
        self.field_name = field_name
        self.value = value


class ExerciseDataBuilder:
    @staticmethod
    def build(params):
        try:
            days = params['days']
            
            # Generate all exercise types
            result = {
                'days': days,
                **ExerciseDataBuilder._build_arithmetic_exercises(params),
                **ExerciseDataBuilder._build_conjugation_exercises(params, days),
                **ExerciseDataBuilder._build_grammar_exercises(params, days),
                **ExerciseDataBuilder._build_conversion_exercises(params, days),
                **ExerciseDataBuilder._build_english_exercises(params, days),
                **ExerciseDataBuilder._build_orthographe_exercises(params, days),
                **ExerciseDataBuilder._build_number_exercises(params, days),
                **ExerciseDataBuilder._build_math_problems(params, days)
            }
            
            return result
            
        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
            return None
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite dans ExerciseDataBuilder.build : {type(e).__name__} : {e}")
            traceback.print_exc()
            return None

    @staticmethod
    def _build_arithmetic_exercises(params):
        """Build arithmetic exercises (addition, subtraction, multiplication, division)"""
        operations = []
        params_list = []
        
        # Process each operation type
        operation_types = [
            {
                'name': 'addition',
                'french_name': 'addition',
                'count_key': 'addition_count',
                'digits_key': 'addition_digits',
                'num_operands_key': 'addition_num_operands',
                'decimals_key': 'addition_decimals',
                'default_num_operands': 2,
                'extra_params': {}
            },
            {
                'name': 'subtraction',
                'french_name': 'soustraction',
                'count_key': 'subtraction_count',
                'digits_key': 'subtraction_digits',
                'num_operands_key': 'subtraction_num_operands',
                'decimals_key': 'subtraction_decimals',
                'default_num_operands': 2,
                'extra_params': {'allow_negative': 'subtraction_negative'}
            },
            {
                'name': 'multiplication',
                'french_name': 'multiplication',
                'count_key': 'multiplication_count',
                'digits_key': 'multiplication_digits',
                'num_operands_key': 'multiplication_num_operands',
                'decimals_key': 'multiplication_decimals',
                'default_num_operands': 2,
                'extra_params': {}
            },
            {
                'name': 'division',
                'french_name': 'division',
                'count_key': 'division_count',
                'digits_key': 'division_digits',
                'num_operands_key': None,  # Division always uses 2 operands
                'decimals_key': 'division_decimals',
                'default_num_operands': 2,
                'extra_params': {
                    'division_reste': 'division_reste',
                    'division_quotient_decimal': lambda p: p.get('division_decimals', 0) > 0
                }
            }
        ]
        
        for op_type in operation_types:
            count = params.get(op_type['count_key'], 0)
            digits = params.get(op_type['digits_key'], 0)
            
            if count > 0 and digits > 0:
                # Get num_operands if applicable
                num_operands = op_type['default_num_operands']
                if op_type['num_operands_key']:
                    num_operands = params.get(op_type['num_operands_key'], op_type['default_num_operands'])
                
                # Get decimals
                decimals = params.get(op_type['decimals_key'], 0)
                
                # Build operation parameters
                op_params = {
                    'operation': op_type['french_name'],
                    'count': count,
                    'num_operands': num_operands,
                    'digits': digits,
                    'with_decimals': decimals > 0,
                    'decimals': decimals
                }
                
                # Add extra parameters
                for param_name, param_key in op_type['extra_params'].items():
                    if callable(param_key):
                        op_params[param_name] = param_key(params)
                    else:
                        op_params[param_name] = params.get(param_key, False)
                
                params_list.append(op_params)
                operations.append(op_type['french_name'])
        
        # Build the lists expected by generate_workbook_pdf
        operations_list = [param['operation'] for param in params_list]
        counts = [param['count'] for param in params_list]
        max_digits = [param['digits'] for param in params_list]
        
        return {
            'operations': operations_list,
            'counts': counts,
            'max_digits': max_digits,
            'params_list': params_list
        }

    @staticmethod
    def _build_conjugation_exercises(params, days):
        """Build conjugation exercises"""
        # Verbs conjugation
        groupes_choisis = params.get('conjugation_groups', [])
        include_usuels = params.get('conjugation_usual', False)
        temps_choisis = params.get('conjugation_tenses', [])
        verbes_par_jour = params.get('verbs_per_day', 0)
        VERBS = params.get('VERBS', {})
        
        # Get possible verbs
        verbes_possibles = []
        for g in groupes_choisis:
            verbes_possibles += VERBS.get(g, [])
        if include_usuels and "usuels" in VERBS:
            verbes_possibles += VERBS["usuels"]
            
        # Ensure there are verbs and tenses before continuing
        if not verbes_possibles or not temps_choisis:
            verbes_par_jour = 0
            
        # Handle case where there aren't enough unique verbs
        if verbes_par_jour > 0 and len(verbes_possibles) < verbes_par_jour * days:
            # Allow repetition if necessary
            extended_verbes_possibles = []
            while len(extended_verbes_possibles) < verbes_par_jour * days:
                random.shuffle(verbes_possibles)
                extended_verbes_possibles.extend(verbes_possibles)
            verbes_possibles = extended_verbes_possibles[:verbes_par_jour * days]
            
        # Generate conjugations
        conjugations = []
        index = 0
        for _ in range(days):
            daily_conjugations = []
            if verbes_par_jour > 0:
                for _ in range(verbes_par_jour):
                    if index < len(verbes_possibles):
                        verbe = verbes_possibles[index]
                        index += 1
                        temps = random.choice(temps_choisis)
                        daily_conjugations.append({"verb": verbe, "tense": temps})
            conjugations.append(daily_conjugations)
            
        # Complete sentences (Conjugation)
        all_conj_complete_sentence_exercises = ExerciseDataBuilder._generate_complete_exercises(
            params, days, 'conj_complete_sentence_count', 'Phrases_francais.json', temps_choisis
        )
        
        # Complete pronouns (Conjugation)
        all_conj_complete_pronoun_exercises = ExerciseDataBuilder._generate_complete_exercises(
            params, days, 'conj_complete_pronoun_count', 'pronoms_francais.json', temps_choisis
        )
        
        return {
            'conjugations': conjugations,
            'conj_complete_sentence_exercises': all_conj_complete_sentence_exercises,
            'conj_complete_pronoun_exercises': all_conj_complete_pronoun_exercises
        }
        
    @staticmethod
    def _generate_complete_exercises(params, days, count_key, json_filename, temps_choisis):
        """Helper method to generate complete sentence or pronoun exercises"""
        count = params.get(count_key, 0)
        all_exercises = []
        
        if count > 0:
            # Load data from JSON
            json_path = os.path.join(os.path.dirname(__file__), 'json', json_filename)
            with open(json_path, encoding='utf-8') as f:
                data = json.load(f)
                
            # Get tenses to use
            tenses_to_use = temps_choisis if temps_choisis else list(data.keys())
            
            # Create tuples of (content, tense) for uniqueness and tense information
            possible_items_with_tense = [
                (item, tense) for tense in tenses_to_use 
                if tense in data 
                for item in data[tense]
            ]
            
            if not possible_items_with_tense:
                # No matching items found
                for _ in range(days):
                    all_exercises.append([])
            else:
                # Shuffle to randomize order before sampling
                random.shuffle(possible_items_with_tense)
                for _ in range(days):
                    daily_ex = []
                    # Use random.sample for unique selection
                    num_to_select = min(count, len(possible_items_with_tense))
                    selected_items_with_tense = random.sample(possible_items_with_tense, k=num_to_select)
                    for content, tense_of_item in selected_items_with_tense:
                        daily_ex.append({'content': content, 'tense': tense_of_item})
                    all_exercises.append(daily_ex)
        else:
            # No exercises to generate
            for _ in range(days):
                all_exercises.append([])
                
        return all_exercises

    @staticmethod
    def _build_grammar_exercises(params, days):
        """Build grammar exercises"""
        grammar_sentence_count = params.get('grammar_sentence_count', 0)
        grammar_types = params.get('grammar_types', [])
        grammar_transformations = params.get('grammar_transformations', [])
        get_random_phrases = params.get('get_random_phrases')
        get_random_transformation = params.get('get_random_transformation')
        
        grammar_exercises = []
        for _ in range(days):
            daily_grammar = []
            if grammar_sentence_count > 0 and grammar_types and grammar_transformations and get_random_phrases and get_random_transformation:
                phrases_choisies = get_random_phrases(grammar_types, grammar_sentence_count)
                if phrases_choisies:
                    for phrase in phrases_choisies:
                        transformation = get_random_transformation(grammar_transformations)
                        if transformation:
                            daily_grammar.append({
                                'phrase': phrase,
                                'transformation': transformation
                            })
            grammar_exercises.append(daily_grammar)
            
        return {'grammar_exercises': grammar_exercises}

    @staticmethod
    def _build_conversion_exercises(params, days):
        """Build conversion exercises"""
        generate_conversion_exercises = params.get('generate_conversion_exercises')
        geo_ex_count = params.get('geo_ex_count', 0)
        geo_types = params.get('geo_types', [])
        geo_senses = params.get('geo_senses', [])
        level_order = params.get('level_order_for_conversions', [])
        current_level = params.get('current_level_for_conversions')
        
        all_geo_exercises = []
        if geo_types and geo_ex_count > 0 and geo_senses and generate_conversion_exercises:
            for _ in range(days):
                daily_geo_ex = generate_conversion_exercises(
                    types_selectionnes=geo_types,
                    n=geo_ex_count,
                    senses=geo_senses,
                    current_level=current_level,
                    level_order=level_order
                )
                all_geo_exercises.append(daily_geo_ex)
        else:
            for _ in range(days):
                all_geo_exercises.append([])
                
        return {'geo_exercises': all_geo_exercises}

    @staticmethod
    def _build_english_exercises(params, days):
        """Build English exercises"""
        english_types = params.get('english_types', [])
        generate_english_full_exercises_func = params.get('generate_english_full_exercises_func')
        n_complete_param = params.get('english_complete_count', 0)
        n_relier_param = params.get('english_relier_count', 0)
        n_mots_relies_param = params.get('relier_count', 0)
        selected_english_themes = params.get('selected_english_themes', [])
        
        english_exercises_data = []
        if generate_english_full_exercises_func:
            for _ in range(days):
                daily_english_ex = generate_english_full_exercises_func(
                    types=english_types,
                    n_complete=n_complete_param,
                    n_relier=n_relier_param,
                    n_mots_reliés=n_mots_relies_param,
                    selected_themes=selected_english_themes
                )
                english_exercises_data.append(daily_english_ex)
        else:
            for _ in range(days):
                english_exercises_data.append([])
                
        return {'english_exercises': english_exercises_data}

    @staticmethod
    def _build_orthographe_exercises(params, days):
        """Build orthographe exercises"""
        orthographe_ex_count = params.get('orthographe_ex_count', 0)
        orthographe_homophones = params.get('orthographe_homophones', [])
        
        orthographe_exercises = []
        if orthographe_ex_count > 0 and orthographe_homophones:
            # Load homophones data
            homophones_path = os.path.join(os.path.dirname(__file__), 'json', 'homophones.json')
            with open(homophones_path, encoding='utf-8') as f:
                homophones_data = json.load(f)
                
            for _ in range(days):
                daily_orthographe = []
                for _ in range(orthographe_ex_count):
                    homophone = random.choice(orthographe_homophones)
                    # Normalize key to match JSON format
                    homophone_key = homophone.replace(' / ', '/').replace(' ', '') if homophone.count('/') == 1 else homophone
                    if homophone_key not in homophones_data:
                        homophone_key = homophone.replace(' / ', '/').replace(' ', '')
                    
                    phrases = homophones_data.get(homophone_key, [])
                    if phrases:
                        phrase = random.choice(phrases)
                        daily_orthographe.append({
                            'type': 'homophone', 
                            'homophone': homophone, 
                            'content': phrase
                        })
                orthographe_exercises.append(daily_orthographe)
        else:
            for _ in range(days):
                orthographe_exercises.append([])
                
        return {'orthographe_exercises': orthographe_exercises}

    @staticmethod
    def _build_number_exercises(params, days):
        """Build number-related exercises (enumerate, sort, compare, logical sequences, encadrement)"""
        result = {}
        
        # Enumerate a number
        enumerate_count = params.get('enumerate_count', 0)
        enumerate_digits = params.get('enumerate_digits', 0)
        all_enumerate_exercises = []
        
        if enumerate_count > 0 and enumerate_digits > 0:
            for _ in range(days):
                daily_enum_ex = [random.randint(0, 10**enumerate_digits-1) for _ in range(enumerate_count)]
                all_enumerate_exercises.append(daily_enum_ex)
        else:
            all_enumerate_exercises = [[] for _ in range(days)]
        
        result['enumerate_exercises'] = all_enumerate_exercises
        
        # Sort numbers
        result['sort_exercises'] = generate_sort_exercises(params, days)
        
        # Compare numbers
        compare_numbers_build_params = {
            'count': params.get('compare_numbers_count', 0),
            'digits': params.get('compare_numbers_digits', 0)
        }
        result['compare_numbers_exercises_list'] = generate_compare_numbers_exercises(
            compare_numbers_build_params, days
        )
        
        # Logical sequences
        logical_sequences_build_params = params.get(
            'logical_sequences_params', {'count': 0, 'types': [], 'step': 1}
        )
        current_level_for_problems = params.get('current_level_for_problems')
        result['logical_sequences_exercises_list'] = generate_logical_sequences_exercises(
            logical_sequences_build_params, days, current_level_for_problems
        )
        
        # Encadrement (framing) of numbers
        encadrement_build_params = params.get(
            'encadrement_params', {'count': 0, 'digits': 0, 'types': []}
        )
        all_encadrement_exercises_list = []
        
        if (encadrement_build_params['count'] > 0 and 
            encadrement_build_params['digits'] > 0 and 
            encadrement_build_params['types']):
            for _ in range(days):
                daily_ex = generate_daily_encadrement_exercises(
                    encadrement_build_params['count'],
                    encadrement_build_params['digits'],
                    encadrement_build_params['types']
                )
                all_encadrement_exercises_list.append(daily_ex)
        else:
            all_encadrement_exercises_list = [[] for _ in range(days)]
            
        result['encadrement_exercises_list'] = all_encadrement_exercises_list
        
        return result

    @staticmethod
    def _build_math_problems(params, days):
        """Build math problem exercises"""
        result = {}
        
        # Regular math problems
        generate_math_problems_func = params.get('generate_math_problems_func')
        math_problems_count = params.get('math_problems_count', 0)
        selected_math_problem_types = params.get('selected_math_problem_types', [])
        current_level_for_problems = params.get('current_level_for_problems')
        
        all_math_problems = []
        if generate_math_problems_func and math_problems_count > 0 and selected_math_problem_types:
            for _ in range(days):
                daily_math_problems = generate_math_problems_func(
                    selected_problem_types=selected_math_problem_types,
                    num_problems=math_problems_count,
                    target_level=current_level_for_problems
                )
                all_math_problems.append(daily_math_problems)
        else:
            all_math_problems = [[] for _ in range(days)]
            
        result['math_problems'] = all_math_problems
        
        # Measurement story problems
        measurement_problems_count = params.get('measurement_problems_count', 0)
        selected_measurement_problem_types = params.get('selected_measurement_problem_types', [])
        
        all_measurement_problems = []
        if measurement_problems_count > 0 and selected_measurement_problem_types:
            for _ in range(days):
                daily_measurement_problems = generate_measurement_story_problems(
                    selected_problem_types=selected_measurement_problem_types,
                    num_problems=measurement_problems_count,
                    target_level=current_level_for_problems
                )
                all_measurement_problems.append(daily_measurement_problems)
        else:
            all_measurement_problems = [[] for _ in range(days)]
            
        result['measurement_problems'] = all_measurement_problems
        
        return result
