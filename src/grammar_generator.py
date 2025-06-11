import random
import sys
import os
import json

def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(__file__), filename)

# Chargement dynamique des phrases depuis un fichier JSON
PHRASES_PATH = get_resource_path('phrases_grammaire.json')
with open(PHRASES_PATH, encoding='utf-8') as f:
    PHRASES = json.load(f)

# Liste des transformations disponibles
TRANSFORMATIONS = [
    "Singulier ↔ Pluriel",
    "Masculin ↔ Féminin",
    "Présent ↔ Passé composé",
    "Présent ↔ Imparfait",
    "Présent ↔ Futur simple",
    "Indicatif ↔ Subjonctif",
    "Indicatif ↔ Impératif",
    "Infinitif ↔ Participe",
    "Positif ↔ Comparatif",
    "Positif ↔ Superlatif",
    "Voix active ↔ Voix passive",
    "Déclarative ↔ Interrogative",
    "Déclarative ↔ Exclamative",
    "Déclarative ↔ Impérative",
    "Affirmative ↔ Négative",
    "Personnelle ↔ Impersonnelle",
    "Coordination/Subordination",
    "Nominalisation",
    "Pronominalisation",
    "Topicalisation/Mise en relief",
    "Effacement/Ellipses"
]

# Complexité des phrases
COMPLEXITIES = ["simple", "complexe"]

def get_random_phrase(phrase_type, complexity="simple"):
    # Pour l'instant, la complexité n'est pas utilisée, mais on peut l'étendre
    return random.choice(PHRASES[phrase_type])

def get_random_transformation(selected_transformations):
    return random.choice(selected_transformations)

def get_random_phrases(phrase_types, n):
    """Retourne n phrases aléatoires parmi tous les types cochés, sans doublon immédiat, avec répétition possible si n > total."""
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

# Note : Pour PyInstaller, phrases_grammaire.json doit être à côté de l'exe pour édition après compilation.
