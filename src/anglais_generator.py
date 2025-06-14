import random
import json
import os
import sys

def get_resource_path(filename):
    import sys, os
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "json", filename)
    return os.path.join(os.path.dirname(__file__), "json", filename)

# Chargement des phrases à compléter simples
try:
    with open(get_resource_path('phrases_anglais_simple.json'), encoding='utf-8') as f:
        PHRASES_SIMPLES = json.load(f)
except Exception:
    PHRASES_SIMPLES = []
# Chargement des phrases à compléter complexes
try:
    with open(get_resource_path('phrases_anglais_complexe.json'), encoding='utf-8') as f:
        PHRASES_COMPLEXES = json.load(f)
except Exception:
    PHRASES_COMPLEXES = []
# Chargement des mots à relier
try:
    with open(get_resource_path('mots_a_relier.json'), encoding='utf-8') as f:
        MOTS_A_RELIER = json.load(f)
except Exception:
    MOTS_A_RELIER = []

def generate_english_exercises(types, n):
    exercises = []
    for _ in range(n):
        t = random.choice(types)
        if t == 'simple' and PHRASES_SIMPLES:
            phrase = random.choice(PHRASES_SIMPLES)
            exercises.append({
                'type': 'simple',
                'content': phrase
            })
        elif t == 'complexe' and PHRASES_COMPLEXES:
            phrase = random.choice(PHRASES_COMPLEXES)
            exercises.append({
                'type': 'complexe',
                'content': phrase
            })
        elif t == 'relier' and MOTS_A_RELIER:
            pair = random.choice(MOTS_A_RELIER)
            exercises.append({
                'type': 'relier',
                'content': pair
            })
        # Si la liste est vide, on saute simplement
    return exercises

# Nouvelle fonction adaptée à la nouvelle UI

def generate_english_full_exercises(types, n_complete, n_relier, n_mots_reliés):
    """
    types: liste de 'simple' et/ou 'complexe'
    n_complete: nombre de phrases à compléter
    n_relier: nombre de jeux à relier
    n_mots_reliés: nombre de mots par jeu
    """
    exercises = []
    # Génération des phrases à compléter
    if types and n_complete > 0:
        for _ in range(n_complete):
            t = random.choice(types)
            if t == 'simple' and PHRASES_SIMPLES:
                phrase = random.choice(PHRASES_SIMPLES)
                exercises.append({'type': 'simple', 'content': phrase})
            elif t == 'complexe' and PHRASES_COMPLEXES:
                phrase = random.choice(PHRASES_COMPLEXES)
                exercises.append({'type': 'complexe', 'content': phrase})
    # Génération des jeux à relier
    if n_relier > 0 and n_mots_reliés > 0 and MOTS_A_RELIER:
        for _ in range(n_relier):
            mots = random.sample(MOTS_A_RELIER, min(n_mots_reliés, len(MOTS_A_RELIER)))
            exercises.append({'type': 'relier', 'content': mots})
    return exercises
