from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import RGBColor
from pdf_generator import generate_math_problems
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import random

def generate_workbook_docx(days, operations, counts, max_digits, conjugations, params_list, grammar_exercises, geo_exercises=None, english_exercises=None, header_text=None, show_name=False, show_note=False, filename="workbook.docx"):
    if geo_exercises is None:
        geo_exercises = []
    if english_exercises is None:
        english_exercises = []
    doc = Document()
    # Style général
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0, 0, 0)
    # Réduction des marges haut et bas
    section = doc.sections[0]
    section.top_margin = Inches(0.4)
    section.bottom_margin = Inches(0.4)
    # Applique l'espacement après à tous les paragraphes créés
    def add_paragraph(text="", style=None):
        para = doc.add_paragraph(text, style=style) if style else doc.add_paragraph(text)
        para.paragraph_format.space_after = Cm(0.05)
        return para
    for day in range(1, days + 1):
        # En-tête
        if header_text or show_name or show_note:
            table = doc.add_table(rows=1, cols=3)
            table.autofit = False
            row = table.rows[0]
            if show_name:
                cell = row.cells[0]
                p = cell.paragraphs[0]
                run = p.add_run("Nom : ____________________")
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                row.cells[0].text = ""
            cell = row.cells[1]
            p = cell.paragraphs[0]
            run = p.add_run(header_text or "")
            run.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if show_note:
                cell = row.cells[2]
                p = cell.paragraphs[0]
                run = p.add_run("Note : _______")
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                row.cells[2].text = ""
            add_paragraph("")
        # Section Calculs
        if any(counts):
            p = add_paragraph()
            run = p.add_run("Calculs")
            run.bold = True
            run.font.size = Pt(14)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for i, operation in enumerate(operations):
                p = add_paragraph()
                run = p.add_run(f"{operation.capitalize()} :")
                run.bold = True
                problems = generate_math_problems(operation, params_list[i])
                for problem in problems:
                    add_paragraph(problem, style='List Bullet')
        # Section Conjugaison
        if any(len(day_conj) > 0 for day_conj in conjugations):
            p = add_paragraph()
            run = p.add_run("Conjugaison")
            run.bold = True
            run.font.size = Pt(14)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            from conjugation_generator import PRONOUNS, VERBS
            for conjugation in conjugations[day-1]:
                verb = conjugation["verb"]
                tense = conjugation["tense"]
                groupe = None
                for g in (1, 2, 3):
                    if verb in VERBS[g]:
                        groupe = f"{g}er groupe"
                        break
                if not groupe:
                    groupe = "usuel"
                p = add_paragraph()
                run = p.add_run(f"Verbe : {verb}  |  Groupe : {groupe}  |  Temps : {tense}")
                run.bold = True
                for pronoun in PRONOUNS:
                    add_paragraph(f"{pronoun} ____________________")
        # Section Grammaire
        if grammar_exercises and any(len(day_gram) > 0 for day_gram in grammar_exercises):
            p = add_paragraph()
            run = p.add_run("Grammaire")
            run.bold = True
            run.font.size = Pt(14)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for ex in grammar_exercises[day-1]:
                phrase = ex['phrase']
                transformation = ex['transformation']
                p = add_paragraph()
                run = p.add_run("Phrase : ")
                run.bold = True
                p.add_run(phrase)
                p = add_paragraph()
                run = p.add_run("Transformation demandée : ")
                run.bold = True
                p.add_run(transformation)
                add_paragraph("Réponse : __________________________________________________________")
        # Section Géométrie/Mesures (exercices de conversion)
        if geo_exercises:
            p = add_paragraph()
            run = p.add_run("Mesures")
            run.bold = True
            run.font.size = Pt(14)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for ex in geo_exercises:
                add_paragraph(ex)
        # Section Anglais (exercices)
        if english_exercises and len(english_exercises) >= day:
            p = add_paragraph()
            run = p.add_run("Anglais")
            run.bold = True
            run.font.size = Pt(14)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for ex in english_exercises[day-1]:
                if ex['type'] in ('simple', 'complexe'):
                    # Ajout de la consigne avant le premier exercice de complétion
                    if ex == english_exercises[day-1][0] or (
                        english_exercises[day-1][english_exercises[day-1].index(ex)-1]['type'] not in ('simple', 'complexe')):
                        para = add_paragraph()
                        run = para.add_run("Compléter :")
                        run.bold = True
                    add_paragraph(ex['content'])
                elif ex['type'] == 'relier':
                    para = add_paragraph()
                    run = para.add_run("Jeu de mots à relier :")
                    run.bold = True
                    mots = ex['content']
                    anglais = [m['english'] for m in mots]
                    francais = [m['french'] for m in mots]
                    random.shuffle(anglais)
                    random.shuffle(francais)
                    max_len = max(len(anglais), len(francais))
                    col_width = 20  # Largeur pour aligner les colonnes
                    for i in range(max_len):
                        a = anglais[i] if i < len(anglais) else ''
                        f = francais[i] if i < len(francais) else ''
                        # Point avant chaque mot, alignement colonne
                        line = f"\u2022 {a:<{col_width}}    \u2022 {f}"
                        add_paragraph(line)
        doc.add_page_break()
    doc.save(filename)
    print(f"Word généré : {filename}")
