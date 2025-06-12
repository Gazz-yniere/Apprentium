import random

# Dictionnaire des types de conversions et des unités associées
CONVERSION_TYPES = {
    'longueur': [
        ('km', 'm', 1000),
        ('m', 'cm', 100),
        ('cm', 'mm', 10),
        ('m', 'mm', 1000),
        ('km', 'cm', 100000),
    ],
    'masse': [
        ('kg', 'g', 1000),
        ('g', 'mg', 1000),
        ('kg', 'mg', 1000000),
    ],
    'volume': [
        ('L', 'cL', 100),
        ('cL', 'mL', 10),
        ('L', 'mL', 1000),
    ],
    'temps': [
        ('h', 'min', 60),
        ('min', 's', 60),
        ('h', 's', 3600),
    ],
    'monnaie': [
        ('€', 'centimes', 100),
    ]
}

# Génère des exercices de conversion aléatoires
# types_selectionnés : liste de types (ex : ['longueur', 'masse'])
# n : nombre d'exercices à générer
# sens : liste de sens de conversion possibles (ex : ['direct', 'inverse'])
# Retourne une liste de chaînes (exercices)
def generate_conversion_exercises(types_selectionnes, n, senses):
    exercises = []
    for _ in range(n):
        type_conv = random.choice(types_selectionnes)
        couples = CONVERSION_TYPES[type_conv]
        unit_from, unit_to, factor = random.choice(couples)
        # Sens de la conversion (direct ou inverse)
        sens = random.choice(senses)
        if sens == 'direct':
            value = random.randint(1, 100)
            exercises.append(f"{value} {unit_from} = ____________ {unit_to}")
        else:
            value = random.randint(1, 100) * factor
            exercises.append(f"{value} {unit_to} = ____________ {unit_from}")
    return exercises
