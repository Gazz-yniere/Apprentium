from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import random
import sys
import os

def draw_rounded_box(pdf, x, y, w, h, radius=10, stroke_color=0.7):
    """
    Dessine un cadre à bords arrondis (compatible N&B, fond blanc).
    x, y = coin inférieur gauche
    w, h = largeur, hauteur
    radius = rayon des coins
    stroke_color = gris du contour
    """
    pdf.setFillGray(1.0)  # fond blanc
    pdf.setStrokeGray(stroke_color)
    pdf.roundRect(x, y, w, h, radius, fill=1, stroke=1)

def generate_math_problems(operation, params):
    problems = []
    count = params.get('count', 5)
    digits = params.get('digits', 2)
    decimals = params.get('decimals', 0)
    with_decimals = decimals > 0
    allow_negative = params.get('allow_negative', False)
    division_reste = params.get('division_reste', False)
    division_quotient_decimal = params.get('division_quotient_decimal', False)
    division_decimals = params.get('division_decimals', 0)

    for _ in range(count):
        if operation == "addition":
            if with_decimals:
                a = round(random.uniform(0, 10**digits-1), decimals)
                b = round(random.uniform(0, 10**digits-1), decimals)
            else:
                a = random.randint(0, 10**digits-1)
                b = random.randint(0, 10**digits-1)
            problems.append(f"{a} + {b} = ")
        elif operation == "soustraction":
            if with_decimals:
                a = round(random.uniform(0, 10**digits-1), decimals)
                b = round(random.uniform(0, 10**digits-1), decimals)
            else:
                a = random.randint(0, 10**digits-1)
                b = random.randint(0, 10**digits-1)
            if not allow_negative and a < b:
                a, b = b, a
            problems.append(f"{a} - {b} = ")
        elif operation == "multiplication":
            if with_decimals:
                a = round(random.uniform(0, 10**digits-1), decimals)
                b = round(random.uniform(0, 10**digits-1), decimals)
            else:
                a = random.randint(0, 10**digits-1)
                b = random.randint(0, 10**digits-1)
            problems.append(f"{a} × {b} = ")
        elif operation == "division":
            min_divisor = 2 if digits < 2 else 1
            max_divisor = 10**digits-1 if digits >= 1 else 9
            if division_quotient_decimal and division_decimals > 0:
                divisor = round(random.uniform(min_divisor, max_divisor), division_decimals)
                quotient = round(random.uniform(1, 10), division_decimals)
                dividend = round(divisor * quotient, division_decimals)
                problems.append(f"{dividend} ÷ {divisor} = ")
            elif not division_reste:
                divisor = random.randint(min_divisor, max_divisor)
                quotient = random.randint(2, 10)
                dividend = divisor * quotient
                problems.append(f"{dividend} ÷ {divisor} = ")
            else:
                divisor = random.randint(min_divisor, max_divisor)
                quotient = random.randint(2, 10)
                reste = random.randint(1, divisor-1)
                dividend = divisor * quotient + reste
                problems.append(f"{dividend} ÷ {divisor} = ")
    return problems
        
def draw_section_title(pdf, width, y, title, number, color=(0.2, 0.4, 0.8)):
    """
    Affiche un titre de section avec numéro entouré à gauche et titre en gras/couleur.
    - number : numéro de la section (int)
    - color : tuple RGB (0-1)
    """
    margin = 50
    box_height = 20
    box_y = y - box_height
    circle_radius = 12
    circle_x = margin + circle_radius
    circle_y = box_y + box_height/2
    # Cercle pour le numéro
    pdf.setFillColorRGB(1, 1, 1)
    pdf.setStrokeColorRGB(*color)
    pdf.circle(circle_x, circle_y, circle_radius, fill=1, stroke=1)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.setFillColorRGB(*color)
    pdf.drawCentredString(circle_x, circle_y-4, str(number))
    # Titre à droite du cercle
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColorRGB(*color)
    pdf.drawString(circle_x + circle_radius + 10, circle_y-7, title)
    # Restaure la couleur noire pour le reste du contenu
    pdf.setFillColorRGB(0, 0, 0)
    # Espace après le bandeau (retour à l'origine)
    y = box_y - 12
    return y

def get_output_path(filename):
    import sys, os
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(__file__)
    output_dir = os.path.join(base, 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return os.path.join(output_dir, filename)

def generate_workbook_pdf(days, operations, counts, max_digits, conjugations, params_list, grammar_exercises, orthographe_exercises, enumerate_exercises, sort_exercises, geo_exercises=None, english_exercises=None, encadrement_exercises=None, header_text=None, filename="workbook.pdf", division_entier=False, show_name=False, show_note=False):
    if geo_exercises is None:
        geo_exercises = []
    if english_exercises is None:
        english_exercises = []
    if encadrement_exercises is None:
        encadrement_exercises = {'count': 0, 'digits': 0, 'types': []}
    out_path = get_output_path(filename)
    pdf = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    margin = 50

    offset_section = 30  # Décalage à droite pour le contenu des sections
    for day in range(1, days + 1):
        y_position = height - margin
        # Affichage de l'en-tête (remplace le titre de la fiche)
        if header_text or show_name or show_note:
            # Hauteur fixe pour garantir l'affichage de tous les champs
            box_height = 30
            box_y = y_position - box_height
            draw_rounded_box(pdf, margin-10, box_y, width-2*margin+20, box_height, radius=14, stroke_color=0.6)
            y_header = box_y + box_height/2 + 5
            # Affichage sur une seule ligne : Nom | Titre | Note
            pdf.setFont("Helvetica", 10)
            pdf.setFillColorRGB(0, 0, 0)
            y_header = box_y + 10  # proche du bas du cadre
            if show_name:
                pdf.drawString(margin + 10, y_header, "Nom : _________________")
            if header_text:
                pdf.setFont("Helvetica-Bold", 14)
                pdf.setFillColorRGB(0, 0, 0)
                pdf.drawCentredString(width // 2, y_header + 1, header_text)
                pdf.setFont("Helvetica", 10)
            if show_note:
                note_text = "Note : ____________"
                note_x = width - margin - 10 - pdf.stringWidth(note_text, "Helvetica", 10)
                pdf.drawString(note_x, y_header, note_text)
            y_position = box_y - 18
        else:
            y_position -= 3
        pdf.setFont("Helvetica", 10)
        pdf.setFillColorRGB(0, 0, 0)

        # Section calculs (affichée seulement si des calculs sont générés)
        section_num = 1
        # Section Calculs (tout sous un seul titre)
        if (
            (enumerate_exercises and len(enumerate_exercises) > 0)
            or any(counts)
        ):
            y_position = draw_section_title(pdf, width, y_position, "Calculs", section_num, color=(0.2,0.4,0.8))
            y_position -= 3
            section_num += 1
            # Enumérer un nombre
            if enumerate_exercises and len(enumerate_exercises) > 0:
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(margin + offset_section, y_position, "Écris chaque nombre en toutes lettres :")
                y_position -= 16
                pdf.setFont("Helvetica", 9)
                for n in enumerate_exercises:
                    pdf.drawString(margin + offset_section, y_position, f"{n} = _____________________________________________")
                    y_position -= 22
                    if y_position < margin:
                        pdf.showPage()
                        y_position = height - margin
                y_position -= 8
            # Opérations classiques
            if any(counts):
                pdf.setFont("Helvetica-Bold", 10)
                for i, operation in enumerate(operations):
                    params = params_list[i]
                    problems = generate_math_problems(operation, params)
                    pdf.drawString(margin + offset_section, y_position, f"{operation.capitalize()} :")
                    y_position -= 13
                    pdf.setFont("Helvetica", 9)
                    for problem in problems:
                        # On veut le calcul à gauche, puis =, puis le trait
                        calc_str = problem.strip().replace(' =', '')
                        pdf.drawString(margin + offset_section, y_position, f"{calc_str} = _____________________________________________")
                        y_position -= 22
                        if y_position < margin:
                            pdf.showPage()
                            y_position = height - margin
                    pdf.setFont("Helvetica-Bold", 10)
                y_position -= 8

        # Section géométrie/mesures (exercices de conversion, rangement, encadrement)
        # Génération des exercices d'encadrement à partir des paramètres
        encadrement_lines = []
        # (Suppression du debug encadrement_exercises)
        if encadrement_exercises and encadrement_exercises['count'] > 0 and encadrement_exercises['digits'] > 0 and encadrement_exercises['types']:
            digits = encadrement_exercises['digits']
            min_n = 10**(digits-1)
            max_n = 10**digits - 1
            types = encadrement_exercises['types']
            for _ in range(encadrement_exercises['count']):
                t = random.choice(types)
                n = random.randint(min_n, max_n)
                encadrement_lines.append({'number': n, 'type': t})
        if geo_exercises or encadrement_lines or (sort_exercises and len(sort_exercises) > 0):
            y_position = draw_section_title(pdf, width, y_position, "Mesures", section_num, color=(0.2,0.6,0.3))
            y_position -= 3
            section_num += 1
            pdf.setFont("Helvetica", 9)
            # Exercices de conversion
            if geo_exercises:
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(margin + offset_section, y_position, "Conversions :")
                y_position -= 16
                pdf.setFont("Helvetica", 9)
                for ex in geo_exercises:
                    pdf.drawString(margin + offset_section, y_position, ex)
                    y_position -= 22
                    if y_position < margin:
                        pdf.showPage()
                        y_position = height - margin
                y_position -= 5
            # Exercices de rangement
            if sort_exercises and len(sort_exercises) > 0:
                pdf.setFont("Helvetica-Bold", 10)
                ordre = "ordre croissant" if sort_exercises[0]['type'] == 'croissant' else "ordre décroissant"
                pdf.drawString(margin + offset_section, y_position, f"Range les nombres suivants dans l'{ordre} :")
                y_position -= 16
                pdf.setFont("Helvetica", 9)
                for idx, ex in enumerate(sort_exercises):
                    numbers_str = ", ".join(str(n) for n in ex['numbers'])
                    pdf.drawString(margin + offset_section, y_position, f"{numbers_str} = _____________________________________________")
                    y_position -= 22
                    if y_position < margin:
                        pdf.showPage()
                        y_position = height - margin
                y_position -= 8
            # Exercices d'encadrement
            if encadrement_lines:
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(margin + offset_section, y_position, "Encadre les nombres :")
                y_position -= 16
                pdf.setFont("Helvetica", 9)
                for ex in encadrement_lines:
                    n = ex['number']
                    t = ex['type']
                    if t == 'unité':
                        base = n
                        sup = n + 1
                        label = "à l'unité"
                    elif t == 'dizaine':
                        base = (n // 10) * 10
                        sup = base + 10
                        label = "à la dizaine"
                    elif t == 'centaine':
                        base = (n // 100) * 100
                        sup = base + 100
                        label = "à la centaine"
                    elif t == 'millier':
                        base = (n // 1000) * 1000
                        sup = base + 1000
                        label = "au millier"
                    else:
                        base = 0
                        sup = 0
                        label = t
                    pdf.drawString(margin + offset_section, y_position, f"{n} {label} : ______  {n}  ______")
                    y_position -= 22
                    if y_position < margin:
                        pdf.showPage()
                        y_position = height - margin
                y_position -= 8

        # Section conjugaison (affichée seulement si des conjugaisons sont générées)
        if conjugations and len(conjugations) >= day and conjugations[day-1]:
            y_position = draw_section_title(pdf, width, y_position, "Conjugaison", section_num, color=(0.7,0.3,0.2))
            y_position -= 3
            section_num += 1
            pdf.setFont("Helvetica-Bold", 10)
            from conjugation_generator import PRONOUNS
            from conjugation_generator import VERBS
            for conjugation in conjugations[day-1]:
                verb = conjugation["verb"]
                tense = conjugation["tense"]
                # Recherche du vrai groupe
                groupe = None
                for g in (1, 2, 3):
                    if verb in VERBS[g]:
                        groupe = f"{g}er groupe"
                        break
                if not groupe:
                    groupe = "usuel"
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(margin + offset_section, y_position, f"Verbe : {verb}  |  Groupe : {groupe}  |  Temps : {tense}")
                y_position -= 13
                pdf.setFont("Helvetica", 9)
                y_position -= 10  # espace avant la première ligne de réponse
                for pronoun in PRONOUNS:
                    pdf.drawString(margin + offset_section, y_position, pronoun)
                    pdf.drawString(margin + offset_section + 100, y_position, "____________________")
                    y_position -= 16  # espace réduit mais suffisant pour écrire à la main
                    if y_position < margin:
                        pdf.showPage()
                        y_position = height - margin
                y_position -= 7
                y_position -= 10  # espace supplémentaire entre chaque conjugaison
            # y_position -= 5  # harmonisation : déjà fait dans la boucle

        # Section grammaire (affichée seulement si des exercices sont générés)
        if grammar_exercises and len(grammar_exercises) >= day and grammar_exercises[day-1]:
            y_position = draw_section_title(pdf, width, y_position, "Grammaire", section_num, color=(0.5,0.2,0.7))
            y_position -= 3
            section_num += 1
            pdf.setFont("Helvetica", 9)
            for ex in grammar_exercises[day-1]:
                phrase = ex['phrase']
                transformation = ex['transformation']
                pdf.setFont("Helvetica-Bold", 9)
                pdf.drawString(margin + offset_section, y_position, f"Phrase :")
                pdf.setFont("Helvetica", 9)
                pdf.drawString(margin + offset_section + 55, y_position, phrase)
                y_position -= 13
                pdf.setFont("Helvetica-Bold", 9)
                pdf.drawString(margin + offset_section, y_position, f"Transformation demandée :")
                pdf.setFont("Helvetica", 9)
                pdf.drawString(margin + offset_section + 130, y_position, transformation)
                y_position -= 13
                y_position -= 10  # espace avant la ligne de réponse
                pdf.drawString(margin + offset_section, y_position, "Réponse : __________________________________________________________")
                y_position -= 22  # espace réduit mais suffisant pour écrire à la main
                y_position -= 10  # espace supplémentaire entre chaque exercice
                if y_position < margin:
                    pdf.showPage()
                    y_position = height - margin
        # Section orthographe (affichée seulement si des exercices sont générés)
        if orthographe_exercises and len(orthographe_exercises) >= day and orthographe_exercises[day-1]:
            y_position = draw_section_title(pdf, width, y_position, "Orthographe", section_num, color=(1.0,0.7,0.0))
            y_position -= 3
            section_num += 1
            pdf.setFont("Helvetica", 9)
            for ex in orthographe_exercises[day-1]:
                if ex['type'] == 'homophone':
                    pdf.setFont("Helvetica-Bold", 9)
                    pdf.drawString(margin + offset_section, y_position, f"{ex['homophone']} :")
                    pdf.setFont("Helvetica", 9)
                    pdf.drawString(margin + offset_section + 60, y_position, ex['content'])
                    y_position -= 16
                    y_position -= 6  # espace supplémentaire entre chaque phrase
                if y_position < margin:
                    pdf.showPage()
                    y_position = height - margin
        # Section anglais (exercices)
        if english_exercises and len(english_exercises) >= day and english_exercises[day-1]:
            y_position = draw_section_title(pdf, width, y_position, "Anglais", section_num, color=(0.2,0.6,0.7))
            y_position -= 3
            section_num += 1
            pdf.setFont("Helvetica-Bold", 10)
            y_position -= 2
            pdf.setFont("Helvetica", 9)
            completer_shown = False
            for ex in english_exercises[day-1]:
                if ex['type'] in ('simple', 'complexe'):
                    if not completer_shown:
                        pdf.setFont("Helvetica-Bold", 9)
                        pdf.drawString(margin + offset_section, y_position, "Compléter :")
                        y_position -= 13
                        pdf.setFont("Helvetica", 9)
                        completer_shown = True
                        y_position -= 10  # espace avant la première phrase à compléter
                    pdf.drawString(margin + offset_section, y_position, ex['content'])
                    y_position -= 16  # espace réduit mais suffisant pour écrire à la main
                    y_position -= 10  # espace supplémentaire entre chaque phrase à compléter
                elif ex['type'] == 'relier':
                    completer_shown = False
                    pdf.setFont("Helvetica-Bold", 9)
                    pdf.drawString(margin + offset_section, y_position, "Jeu de mots à relier :")
                    y_position -= 13
                    y_position -= 10  # espace avant le début du jeu à relier
                    pdf.setFont("Helvetica", 9)
                    mots = ex['content']
                    anglais = [m['english'] for m in mots]
                    francais = [m['french'] for m in mots]
                    random.shuffle(anglais)
                    random.shuffle(francais)
                    max_len = max(len(anglais), len(francais))
                    col1_x = margin + offset_section + 10
                    col2_x = margin + offset_section + 60  # point anglais
                    col3_x = margin + offset_section + 110 # point français
                    col4_x = margin + offset_section + 130 # mot français
                    for i in range(max_len):
                        a = anglais[i] if i < len(anglais) else ''
                        f = francais[i] if i < len(francais) else ''
                        pdf.drawString(margin + offset_section, y_position, a)
                        pdf.drawString(margin + offset_section + 60, y_position, '\u2022')
                        pdf.drawString(margin + offset_section + 110, y_position, '\u2022')
                        pdf.drawString(margin + offset_section + 130, y_position, f)
                        y_position -= 13
                    y_position -= 10  # espace supplémentaire entre chaque bloc à relier
                if y_position < margin:
                    pdf.showPage()
                    y_position = height - margin
            # Saut de page forcé entre chaque jour (sauf le dernier)
        if day < days:
            pdf.showPage()

    pdf.save()
    print(f"PDF généré : {out_path}")

def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(__file__), filename)