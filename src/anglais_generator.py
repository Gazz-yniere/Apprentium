import random
import json
import os
import sys

def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(__file__), filename)

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
