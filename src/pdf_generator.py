from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import random
import sys
import os

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
                a = round(random.uniform(10**(digits-1), 10**digits-1), decimals)
                b = round(random.uniform(10**(digits-1), 10**digits-1), decimals)
            else:
                a = random.randint(10**(digits-1), 10**digits-1)
                b = random.randint(10**(digits-1), 10**digits-1)
            problems.append(f"{a} + {b} = ")
        elif operation == "soustraction":
            if with_decimals:
                a = round(random.uniform(10**(digits-1), 10**digits-1), decimals)
                b = round(random.uniform(10**(digits-1), 10**digits-1), decimals)
            else:
                a = random.randint(10**(digits-1), 10**digits-1)
                b = random.randint(10**(digits-1), 10**digits-1)
            if not allow_negative and a < b:
                a, b = b, a
            problems.append(f"{a} - {b} = ")
        elif operation == "multiplication":
            if with_decimals:
                a = round(random.uniform(10**(digits-1), 10**digits-1), decimals)
                b = round(random.uniform(10**(digits-1), 10**digits-1), decimals)
            else:
                a = random.randint(10**(digits-1), 10**digits-1)
                b = random.randint(10**(digits-1), 10**digits-1)
            problems.append(f"{a} × {b} = ")
        elif operation == "division":
            min_divisor = 2 if digits < 2 else 10**(digits-1)
            max_divisor = 10**digits-1 if digits >= 2 else 9
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
        
def draw_section_title(pdf, width, y, title):
    margin = 50
    box_height = 22
    box_y = y - box_height
    # Fond gris clair (compatible N&B)
    pdf.setFillGray(0.90)
    pdf.setStrokeGray(0.75)
    pdf.rect(margin, box_y, width - 2*margin, box_height, fill=1, stroke=1)
    # Titre centré en gras, bien centré verticalement
    pdf.setFont("Helvetica-Bold", 12)
    pdf.setFillGray(0.0)
    pdf.drawCentredString(width // 2, box_y + box_height/2 - 2, title)
    # Espace après le bandeau
    y = box_y - 12
    return y

def generate_workbook_pdf(days, operations, counts, max_digits, conjugations, params_list, grammar_exercises, header_text=None, filename="workbook.pdf", division_entier=False, show_name=False, show_note=False):
    pdf = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 50

    for day in range(1, days + 1):
        y_position = height - margin
        # Affichage de l'en-tête (remplace le titre de la fiche)
        if header_text or show_name or show_note:
            y_header = y_position
            if show_name:
                pdf.setFont("Helvetica", 9)
                pdf.drawString(margin, y_header, "Nom : _________________")
            if show_note:
                pdf.setFont("Helvetica", 9)
                note_text = "Note : ____________"
                note_x = width - margin - pdf.stringWidth(note_text, "Helvetica", 9)
                pdf.drawString(note_x, y_header, note_text)
            if header_text:
                pdf.setFont("Helvetica-Bold", 18)
                pdf.setFillColorRGB(0, 0, 0)
                pdf.drawCentredString(width // 2, y_header - 7, header_text)
            y_position -= 35
        else:
            y_position -= 10
        pdf.setFont("Helvetica", 10)
        pdf.setFillColorRGB(0, 0, 0)

        # Section calculs (affichée seulement si des calculs sont générés)
        if any(counts):
            y_position = draw_section_title(pdf, width, y_position, "Calculs")
            pdf.setFont("Helvetica-Bold", 10)
            for i, operation in enumerate(operations):
                params = params_list[i]
                problems = generate_math_problems(operation, params)
                pdf.drawString(margin, y_position, f"{operation.capitalize()} :")
                y_position -= 15
                pdf.setFont("Helvetica", 9)
                for problem in problems:
                    pdf.drawString(margin + 20, y_position, problem)
                    y_position -= 13
                    if y_position < margin:
                        pdf.showPage()
                        y_position = height - margin
                y_position -= 5
                pdf.setFont("Helvetica-Bold", 10)
            y_position -= 10

        # Section conjugaison (affichée seulement si des conjugaisons sont générées)
        if any(len(day_conj) > 0 for day_conj in conjugations):
            y_position = draw_section_title(pdf, width, y_position, "Conjugaison")
            pdf.setFont("Helvetica-Bold", 10)
            from conjugation_generator import PRONOUNS
            from conjugation_generator import VERBS
            for conjugation in conjugations[day-1]:
                verb = conjugation["verb"]
                tense = conjugation["tense"]
                # Déterminer le groupe du verbe
                if verb in VERBS[1]:
                    groupe = "1er groupe"
                elif verb in VERBS[2]:
                    groupe = "2ème groupe"
                elif verb in VERBS[3]:
                    groupe = "3ème groupe"
                else:
                    groupe = "Groupe inconnu"
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(margin, y_position, f"Verbe : {verb}  |  Groupe : {groupe}  |  Temps : {tense}")
                y_position -= 13
                pdf.setFont("Helvetica", 9)
                for pronoun in PRONOUNS:
                    pdf.drawString(margin + 20, y_position, pronoun)
                    pdf.drawString(margin + 100, y_position, "____________________")
                    y_position -= 13
                    if y_position < margin:
                        pdf.showPage()
                        y_position = height - margin
                y_position -= 7
            y_position -= 10

        # Section grammaire (affichée seulement si des exercices sont générés)
        if grammar_exercises and any(len(day_gram) > 0 for day_gram in grammar_exercises):
            y_position = draw_section_title(pdf, width, y_position, "Grammaire")
            pdf.setFont("Helvetica", 9)
            for ex in grammar_exercises[day-1]:
                phrase = ex['phrase']
                transformation = ex['transformation']
                pdf.setFont("Helvetica-Bold", 9)
                pdf.drawString(margin, y_position, f"Phrase :")
                pdf.setFont("Helvetica", 9)
                pdf.drawString(margin + 55, y_position, phrase)
                y_position -= 13
                pdf.setFont("Helvetica-Bold", 9)
                pdf.drawString(margin, y_position, f"Transformation demandée :")
                pdf.setFont("Helvetica", 9)
                pdf.drawString(margin + 130, y_position, transformation)
                y_position -= 13
                pdf.drawString(margin, y_position, "Réponse : __________________________________________________________")
                y_position -= 18
                if y_position < margin:
                    pdf.showPage()
                    y_position = height - margin
            y_position -= 10
        pdf.showPage()

    pdf.save()
    print(f"PDF généré : {filename}")

def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(__file__), filename)