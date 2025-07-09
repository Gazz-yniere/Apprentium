import random
import json
import sys
import os
from utils.resource_path import project_file_path

# Chargement dynamique des phrases depuis un fichier JSON
PHRASES_PATH = project_file_path('json/phrases_grammaire.json')
with open(PHRASES_PATH, encoding='utf-8') as f:
    PHRASES = json.load(f)

# Liste des transformations disponibles (restreinte et commentée)
TRANSFORMATIONS = [
    "Singulier ↔ Pluriel", # Transformation des noms, adjectifs et verbes en fonction du nombre
    "Masculin ↔ Féminin", # Transformation des noms et adjectifs en fonction du genre
    "Présent ↔ Passé composé", # Conjugaison des verbes à ces deux temps et compréhension de leur usage
    "Présent ↔ Imparfait",
    "Présent ↔ Futur simple",
    "Indicatif ↔ Impératif", # Utilisation du mode impératif pour donner des ordres ou des conseils
    "Voix active ↔ Voix passive", # Initiation et reconnaissance de cette transformation, surtout au cycle 3 (CM1-CM2)
    "Déclarative ↔ Interrogative", # Transformation pour poser des questions (intonation, 'est-ce que', inversion sujet-verbe de base)
    "Déclarative ↔ Exclamative", # Transformation pour exprimer une émotion
    "Déclarative ↔ Impérative", # Transformation pour donner un ordre
    "Affirmative ↔ Négative" # Utilisation de 'ne...pas' et autres formes négatives
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
