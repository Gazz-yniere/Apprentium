import random
import sys
import os
import json

def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(__file__), filename)

# Chargement dynamique des verbes depuis un fichier JSON
VERBS_PATH = get_resource_path('verbes.json')
with open(VERBS_PATH, encoding='utf-8') as f:
    _VERBS = json.load(f)
    VERBS = {}
    for k, v in _VERBS.items():
        if k.isdigit():
            VERBS[int(k)] = v
        else:
            VERBS[k] = v

PRONOUNS = ["je", "tu", "il/elle/on", "nous", "vous", "ils/elles"]

# Liste des temps de conjugaison utilisables (adaptée à l'école primaire)
TENSES = [
    # Présent de l'indicatif : action en cours ou habituelle
    "présent",
    # Imparfait de l'indicatif : action passée, description, habitude
    "imparfait",
    # Passé simple : récit, narration (principalement pour la reconnaissance)
    "passé simple",
    # Futur simple de l'indicatif : action à venir
    "futur simple",
    # Passé composé : action passée, résultat/conclusion
    "passé composé",
    # Plus-que-parfait de l'indicatif : action antérieure à une autre action passée
    "plus-que-parfait",
    # Conditionnel présent : hypothèse, souhait, politesse
    "conditionnel présent",
    # Impératif présent : ordre, conseil
    "impératif présent"
]

def get_random_verb(group, used_verbs):
    if group not in VERBS:
        raise ValueError("Le groupe spécifié est invalide. Veuillez choisir 1, 2 ou 3.")

    available_verbs = list(set(VERBS[group]) - used_verbs)

    if not available_verbs:
        raise ValueError("Tous les verbes de ce groupe ont été utilisés.")

    verb = random.choice(available_verbs)
    used_verbs.add(verb)
    return verb

# Note : Pour PyInstaller, verbes.json doit être à côté de l'exe pour édition après compilation.