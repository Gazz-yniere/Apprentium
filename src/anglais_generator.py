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
        MOTS_A_RELIER = json.load(f) # Sera maintenant un dictionnaire de thèmes
except Exception:
    MOTS_A_RELIER = {} # Par défaut un dictionnaire vide

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

def generate_english_full_exercises(types, n_complete, n_relier, n_mots_reliés, selected_themes=None):
    """
    types: liste de 'simple' et/ou 'complexe'
    n_complete: nombre de phrases à compléter
    n_relier: nombre de jeux à relier
    n_mots_reliés: nombre de mots par jeu
    selected_themes: liste des thèmes choisis pour les mots à relier
    """
    print(f"DEBUG AnglaisGen: Thèmes reçus pour génération: {selected_themes}, Types: {types}, NComplete: {n_complete}, NRelier: {n_relier}, NMotsRelies: {n_mots_reliés}") # DEBUG
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
        candidate_words_for_relier = []
        if selected_themes:
            for theme in selected_themes:
                candidate_words_for_relier.extend(MOTS_A_RELIER.get(theme, []))
        else: # Aucun thème spécifique sélectionné, utiliser tous les mots de tous les thèmes
            for theme_words_list in MOTS_A_RELIER.values():
                candidate_words_for_relier.extend(theme_words_list)

        print(f"DEBUG AnglaisGen: Mots candidats après filtrage: {candidate_words_for_relier}") # Nouveau print
        if candidate_words_for_relier: # S'il y a des mots disponibles
            for _ in range(n_relier):
                if len(candidate_words_for_relier) == 0: # Au cas où la liste deviendrait vide (ne devrait pas arriver ici)
                    break
                num_to_sample = min(n_mots_reliés, len(candidate_words_for_relier))
                if num_to_sample > 0 :
                    mots = random.sample(candidate_words_for_relier, num_to_sample)
                    exercises.append({'type': 'relier', 'content': mots})
                # Si num_to_sample est 0 (parce que n_mots_reliés est 0 ou candidate_words_for_relier est vide),
                # on ne fait rien pour ce jeu.
        # else:
            # print("Avertissement: Aucun mot à relier disponible pour les thèmes sélectionnés ou aucun mot défini.")

    return exercises
