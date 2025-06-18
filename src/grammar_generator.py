import random
import json
import os


def get_resource_path(filename):
    import sys
    import os
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "json", filename)
    return os.path.join(os.path.dirname(__file__), "json", filename)


# Chargement dynamique des phrases depuis un fichier JSON
PHRASES_PATH = get_resource_path('phrases_grammaire.json')
with open(PHRASES_PATH, encoding='utf-8') as f:
    PHRASES = json.load(f)

# Liste des transformations disponibles (restreinte et commentée)
TRANSFORMATIONS = [
    # Transformation des noms, adjectifs et verbes en fonction du nombre
    "Singulier ↔ Pluriel",
    # Transformation des noms et adjectifs en fonction du genre
    "Masculin ↔ Féminin",
    # Conjugaison des verbes à ces deux temps et compréhension de leur usage
    "Présent ↔ Passé composé",
    "Présent ↔ Imparfait",
    "Présent ↔ Futur simple",
    # Utilisation du mode impératif pour donner des ordres ou des conseils
    "Indicatif ↔ Impératif",
    # Initiation et reconnaissance de cette transformation, surtout au cycle 3 (CM1-CM2)
    "Voix active ↔ Voix passive",
    # Transformation pour poser des questions (intonation, 'est-ce que', inversion sujet-verbe de base)
    "Déclarative ↔ Interrogative",
    # Transformation pour exprimer une émotion
    "Déclarative ↔ Exclamative",
    # Transformation pour donner un ordre
    "Déclarative ↔ Impérative",
    # Utilisation de 'ne...pas' et autres formes négatives
    "Affirmative ↔ Négative"
]

# Complexité des phrases
COMPLEXITIES = ["simple", "complexe"]


def get_random_phrase(phrase_type, complexity="simple"):
    # Pour l'instant, la complexité n'est pas utilisée, mais on peut l'étendre
    return random.choice(PHRASES[phrase_type])


def get_random_transformation(selected_transformations):
    if not selected_transformations:
        return None
    return random.choice(selected_transformations)


def get_random_phrases(phrase_types, n):
    """Retourne n phrases aléatoires parmi tous les types cochés, sans doublon immédiat, avec répétition possible si n > total."""  # noqa: E501
    pool = []
    for t in phrase_types:
        pool.extend(PHRASES[t])
    if not pool:
        return []
    result = []
    last = None
    for _ in range(n):
        candidates = [p for p in pool if p != last] if len(pool) > 1 else pool
        phrase = random.choice(candidates)
        result.append(phrase)
        last = phrase
    return result

# Note : Pour PyInstaller, phrases_grammaire.json doit être à côté de l'exe pour édition après compilation.  # noqa: E501
