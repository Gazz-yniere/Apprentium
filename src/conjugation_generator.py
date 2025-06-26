import random
import json
import sys
import os

def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "json", filename)
    return os.path.join(os.path.dirname(__file__), "json", filename)


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

PRONOUNS = [
    "je/j'",
    "tu",
    "il/elle/on",
    "nous",
    "vous",
    "ils/elles"
]

# Liste des temps de conjugaison utilisables (adaptée à l'école primaire)
TENSES = [
    "présent", # Présent de l'indicatif : action en cours ou habituelle
    "imparfait", # Imparfait de l'indicatif : action passée, description, habitude
    "passé simple", # Passé simple : récit, narration (principalement pour la reconnaissance)
    "futur simple", # Futur simple de l'indicatif : action à venir
    "passé composé", # Passé composé : action passée, résultat/conclusion
    "plus-que-parfait", # Plus-que-parfait de l'indicatif : action antérieure à une autre action passée
    "conditionnel présent", # Conditionnel présent : hypothèse, souhait, politesse
    "impératif présent" # Impératif présent : ordre, conseil
]


def get_random_verb(group, used_verbs):
    if group not in VERBS:
        raise ValueError(
            "Le groupe spécifié est invalide. Veuillez choisir 1, 2 ou 3.")

    available_verbs = list(set(VERBS[group]) - used_verbs)

    if not available_verbs:
        raise ValueError("Tous les verbes de ce groupe ont été utilisés.")

    verb = random.choice(available_verbs)
    used_verbs.add(verb)
    return verb
