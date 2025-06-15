import random

# Dictionnaire des types de conversions et des unités associées
CONVERSION_TYPES = {
    'longueur': [
        ('km', 'm', 1000),
        #('km', 'dam', 100),
        #('km', 'hm', 10),
        #('hm', 'm', 100),
        #('dam', 'm', 10),
        ('m', 'cm', 100),
        ('m', 'dm', 10),
        ('m', 'mm', 1000),
        ('dm', 'cm', 10),
        ('dm', 'mm', 100),
        ('cm', 'mm', 10),
        ('km', 'cm', 100000),
        ('km', 'mm', 1000000),
    ],
    'masse': [
        ('kg', 'g', 1000),
        #('kg', 'hg', 10),
        #('kg', 'dag', 100),
        #('hg', 'g', 100),
        #('dag', 'g', 10),
        ('g', 'mg', 1000),
        #('g', 'dg', 10),
        #('g', 'cg', 100),
        #('dg', 'mg', 100),
        #('cg', 'mg', 10),
        #('kg', 'mg', 1000000),
        ('t', 'kg', 1000), # Tonne
        #('q', 'kg', 100),  # Quintal
    ],
    'volume': [
        ('L', 'cL', 100),
        ('L', 'dL', 10),
        ('L', 'mL', 1000),
        #('hL', 'L', 100),
        #('daL', 'L', 10),
        ('dL', 'cL', 10),
        ('cL', 'mL', 10),
        # Unités de volume cubiques (plus complexes, ajouter avec prudence pour le niveau scolaire)
        # ('m³', 'dm³', 1000), # 1 m³ = 1000 L
        # ('dm³', 'cm³', 1000), # 1 dm³ = 1 L
        # ('cm³', 'mL', 1),     # 1 cm³ = 1 mL
    ],
    'temps': [
        ('h', 'min', 60),
        ('min', 's', 60),
        ('h', 's', 3600),
        #('jour', 'h', 24),
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
