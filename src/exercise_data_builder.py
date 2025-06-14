import random

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
            random.shuffle(verbes_possibles)
            if len(verbes_possibles) < verbes_par_jour * jours:
                print("Pas assez de verbes pour couvrir tous les jours sans doublon.")
                return
            index = 0
            conjugations = []
            for _ in range(jours):
                daily_conjugations = []
                for _ in range(verbes_par_jour):
                    verbe = verbes_possibles[index]
                    index += 1
                    temps = random.choice(temps_choisis)
                    daily_conjugations.append({"verb": verbe, "tense": temps})
                conjugations.append(daily_conjugations)

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
                for phrase in phrases_choisies:
                    transformation = get_random_transformation(grammar_transformations)
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
            geo_exercises = []
            if geo_types and geo_ex_count > 0 and geo_senses:
                geo_exercises = generate_conversion_exercises(geo_types, geo_ex_count, geo_senses)

            # Anglais
            english_types = params.get('english_types', [])
            PHRASES_SIMPLES = params.get('PHRASES_SIMPLES', [])
            PHRASES_COMPLEXES = params.get('PHRASES_COMPLEXES', [])
            MOTS_A_RELIER = params.get('MOTS_A_RELIER', [])
            english_ex_count = params.get('english_ex_count', 0)
            relier_count = params.get('relier_count', 0)
            english_exercises = []
            for _ in range(jours):
                daily = []
                completion_types = []
                if 'simple' in english_types and PHRASES_SIMPLES:
                    completion_types.append('simple')
                if 'complexe' in english_types and PHRASES_COMPLEXES:
                    completion_types.append('complexe')
                for _ in range(english_ex_count):
                    if not completion_types:
                        break
                    t = random.choice(completion_types)
                    if t == 'simple':
                        daily.append({'type': 'simple', 'content': random.choice(PHRASES_SIMPLES)})
                    elif t == 'complexe':
                        daily.append({'type': 'complexe', 'content': random.choice(PHRASES_COMPLEXES)})
                if 'relier' in english_types and relier_count > 0 and MOTS_A_RELIER:
                    mots = random.sample(MOTS_A_RELIER, min(relier_count, len(MOTS_A_RELIER)))
                    daily.append({'type': 'relier', 'content': mots})
                english_exercises.append(daily)

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
            enumerate_exercises = []
            for _ in range(enumerate_count):
                if enumerate_digits > 0:
                    n = random.randint(0, 10**enumerate_digits-1)
                    enumerate_exercises.append(n)

            # Ranger les nombres
            sort_count = params.get('sort_count', 0)
            sort_digits = params.get('sort_digits', 0)
            sort_n_numbers = params.get('sort_n_numbers', 0)
            sort_type_croissant = params.get('sort_type_croissant', True)
            sort_type_decroissant = params.get('sort_type_decroissant', False)
            sort_exercises = []
            for _ in range(sort_count):
                if sort_digits > 0 and sort_n_numbers > 0:
                    numbers = [random.randint(0, 10**sort_digits-1) for _ in range(sort_n_numbers)]
                    sort_exercises.append({
                        'numbers': numbers,
                        'type': 'croissant' if sort_type_croissant else 'decroissant'
                    })

            # Encadrement de nombre
            encadrement_count = params.get('encadrement_count', 0)
            encadrement_digits = params.get('encadrement_digits', 0)
            encadrement_types = []
            if params.get('encadrement_unite', False):
                encadrement_types.append('unite')
            if params.get('encadrement_dizaine', False):
                encadrement_types.append('dizaine')
            if params.get('encadrement_centaine', False):
                encadrement_types.append('centaine')
            if params.get('encadrement_millier', False):
                encadrement_types.append('millier')
            encadrement_exercises = []
            for _ in range(encadrement_count):
                if encadrement_digits > 0 and encadrement_types:
                    n = random.randint(0, 10**encadrement_digits-1)
                    for t in encadrement_types:
                        encadrement_exercises.append({'number': n, 'type': t})

            return {
                'days': days,
                'operations': operations_list,
                'counts': counts,
                'max_digits': max_digits,
                'conjugations': conjugations,
                'params_list': params_list,
                'grammar_exercises': grammar_exercises,
                'geo_exercises': geo_exercises,
                'english_exercises': english_exercises,
                'orthographe_exercises': orthographe_exercises,
                'enumerate_exercises': enumerate_exercises,
                'sort_exercises': sort_exercises,
                'encadrement_exercises': encadrement_exercises
            }
        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite : {type(e).__name__} : {e}")
            traceback.print_exc()
