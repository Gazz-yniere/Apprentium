from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement
from docx.shared import RGBColor
from pdf_generator import generate_math_problems
import random
import warnings

# Ignorer l'avertissement spécifique de python-docx concernant la recherche de style
warnings.filterwarnings("ignore", message="style lookup by style_id is deprecated")

def get_output_path(filename, custom_output_dir=None):
    import sys, os
    base_dir_for_output = None

    if custom_output_dir and custom_output_dir.strip():
        custom_output_dir = custom_output_dir.strip()
        if os.path.isdir(custom_output_dir):
            base_dir_for_output = custom_output_dir
        else:
            try:
                os.makedirs(custom_output_dir, exist_ok=True)
                base_dir_for_output = custom_output_dir
            except OSError:
                print(f"Avertissement : Impossible de créer le dossier personnalisé '{custom_output_dir}'. Utilisation du dossier par défaut.")
                # Fallback ci-dessous

    if base_dir_for_output is None: # Si custom_output_dir n'est pas fourni ou a échoué
        if getattr(sys, 'frozen', False): # Exécutable PyInstaller
            app_base_path = os.path.dirname(sys.executable)
        else: # Mode script
            app_base_path = os.path.dirname(os.path.dirname(__file__)) # Remonte au dossier parent de src/
        base_dir_for_output = os.path.join(app_base_path, 'output')

    os.makedirs(base_dir_for_output, exist_ok=True) # S'assure que le dossier final existe
    return os.path.join(base_dir_for_output, filename)

def set_table_borders_invisible(table):
    """Rend toutes les bordures d'un tableau invisibles."""
    tbl = table._tbl
    tblPr = tbl.tblPr
    # Vérifie si tblBorders existe déjà, sinon le crée
    tblBorders = tblPr.first_child_found_in("w:tblBorders")
    if tblBorders is None:
        tblBorders = OxmlElement('w:tblBorders')
        tblPr.append(tblBorders)

    # Définit tous les types de bordures à 'nil'
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border_el = OxmlElement(f'w:{border_name}')
        border_el.set(qn('w:val'), 'nil')
        tblBorders.append(border_el)


def generate_workbook_docx(days, operations, counts, max_digits, conjugations, params_list, grammar_exercises,
                           orthographe_exercises=None, enumerate_exercises=None, sort_exercises=None,
                           geo_exercises=None, english_exercises=None, encadrement_exercises=None,
                           header_text=None, show_name=False, show_note=False, filename="workbook.docx", output_dir_override=None):
    if geo_exercises is None:
        geo_exercises = []
    if english_exercises is None:
        english_exercises = []
    if orthographe_exercises is None: orthographe_exercises = [] # Initialisation pour la cohérence
    if enumerate_exercises is None: enumerate_exercises = []
    if sort_exercises is None: sort_exercises = []
    if encadrement_exercises is None: encadrement_exercises = {'count': 0, 'digits': 0, 'types': []}

    doc = Document()
    # Style général
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0, 0, 0)
    # Réduction des marges haut et bas
    doc_section = doc.sections[0]
    doc_section.top_margin = Inches(0.4)
    doc_section.bottom_margin = Inches(0.4)
    doc_section.left_margin = Inches(0.7) # Un peu plus de marge à gauche pour l'ensemble
    doc_section.right_margin = Inches(0.7)

    CONTENT_INDENT = Cm(0.8) # Décalage pour le contenu des sections

    # Applique l'espacement après à tous les paragraphes créés
    def add_paragraph(text="", style=None, indent=False):
        para = doc.add_paragraph(text, style=style) if style else doc.add_paragraph(text)
        para.paragraph_format.space_after = Cm(0.05)
        if indent:
            para.paragraph_format.left_indent = CONTENT_INDENT
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

        section_num = 1 # Compteur pour la numérotation des sections

        # Section Calculs
        has_calculs_content = any(counts) or \
                              (enumerate_exercises and len(enumerate_exercises) >= day and enumerate_exercises[day-1])
        if has_calculs_content:
            p = add_paragraph()
            run = p.add_run(f"{section_num}. Calculs")
            run.bold = True
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(51, 102, 204) # Bleu
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT # Aligné à gauche
            section_num += 1

            # Enumérer un nombre (si présent pour le jour)
            if enumerate_exercises and len(enumerate_exercises) >= day and enumerate_exercises[day-1]:
                para_enum = add_paragraph(indent=True)
                run_enum = para_enum.add_run("Écris chaque nombre en toutes lettres :")
                run_enum.bold = True
                for n_enum in enumerate_exercises[day-1]:
                    add_paragraph(f"{n_enum} = _____________________________________________", style='ListContinue', indent=True)
                add_paragraph(indent=True) # Espace

            # Opérations classiques
            if any(counts):
                for i, operation in enumerate(operations):
                    # Vérifier si cette opération spécifique a des exercices
                    if params_list[i].get('count', 0) > 0:
                        p_op = add_paragraph(indent=True)
                        run_op = p_op.add_run(f"{operation.capitalize()} :")
                        run_op.bold = True
                        problems = generate_math_problems(operation, params_list[i])
                        for problem in problems:
                            calc_str = problem.strip().replace(' =', '')
                            add_paragraph(f"{calc_str} = ________________________________", style='ListContinue', indent=True)
                add_paragraph(indent=True) # Espace après la section calculs

        # Section Conjugaison
        if conjugations and len(conjugations) >= day and conjugations[day-1]:
            p = add_paragraph()
            run = p.add_run(f"{section_num}. Conjugaison")
            run.bold = True
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(178, 76, 51) # Rouge-brique
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT # Aligné à gauche
            section_num += 1
            from conjugation_generator import PRONOUNS, VERBS
            for conjugation in conjugations[day-1]:
                verb = conjugation["verb"]
                tense = conjugation["tense"]
                groupe = None
                for g in (1, 2, 3):
                    if verb in VERBS.get(g, []): # Utiliser .get pour éviter KeyError si groupe absent
                        groupe = f"{g}er groupe"
                        break
                if not groupe:
                    groupe = "usuel"
                p_conj_details = add_paragraph(indent=True)
                run = p_conj_details.add_run(f"Verbe : {verb}  |  Groupe : {groupe}  |  Temps : {tense}") # Correction: run sur p_conj_details
                run.bold = True
                for pronoun in PRONOUNS:
                    add_paragraph(f"{pronoun} ____________________", indent=True)
            add_paragraph(indent=True) # Espace

        # Section Grammaire
        if grammar_exercises and len(grammar_exercises) >= day and grammar_exercises[day-1]:
            # Paragraphe pour le titre principal de la section
            title_paragraph_gram = add_paragraph()
            title_run_gram = title_paragraph_gram.add_run(f"{section_num}. Grammaire")
            title_run_gram.bold = True
            title_run_gram.font.size = Pt(14)
            title_run_gram.font.color.rgb = RGBColor(127, 51, 178) # Violet
            title_paragraph_gram.alignment = WD_ALIGN_PARAGRAPH.LEFT # Aligné à gauche
            section_num += 1

            for ex in grammar_exercises[day-1]:
                phrase_content = ex['phrase']
                transformation_content = ex['transformation']

                # Nouveau paragraphe pour la ligne "Phrase : ..."
                phrase_line_para = add_paragraph(indent=True)
                phrase_label_run = phrase_line_para.add_run("Phrase : ")
                phrase_label_run.bold = True
                phrase_line_para.add_run(phrase_content)

                # Nouveau paragraphe pour la ligne "Transformation demandée : ..."
                transfo_line_para = add_paragraph(indent=True)
                transfo_label_run = transfo_line_para.add_run("Transformation demandée : ")
                transfo_label_run.bold = True
                transfo_line_para.add_run(transformation_content)

                add_paragraph("Réponse : __________________________________________________________", indent=True)
            add_paragraph(indent=True) # Espace

        # Section Mesures (Conversions, Rangement, Encadrement)
        has_mesures_content_for_day = False
        if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]:
            has_mesures_content_for_day = True
        if sort_exercises and len(sort_exercises) >= day and sort_exercises[day-1]:
            has_mesures_content_for_day = True

        encadrement_lines_word = [] # Généré par jour pour Word
        if encadrement_exercises and encadrement_exercises.get('count', 0) > 0 and \
           encadrement_exercises.get('digits', 0) > 0 and encadrement_exercises.get('types'):
            has_mesures_content_for_day = True # Si encadrement est activé
            digits = encadrement_exercises['digits']
            types = encadrement_exercises['types']
            if digits > 0: # S'assurer que digits est positif
                min_val = 0
                if digits == 1: max_val = 9
                elif digits > 1:
                    min_val = 10**(digits-1)
                    max_val = 10**digits - 1
                else: max_val = 0 # Ne devrait pas arriver si digits > 0

                for _ in range(encadrement_exercises['count']):
                    t = random.choice(types)
                    n = random.randint(min_val, max_val)
                    encadrement_lines_word.append({'number': n, 'type': t})

        if has_mesures_content_for_day:
            p_mesures = add_paragraph()
            run_mesures = p_mesures.add_run(f"{section_num}. Mesures")
            run_mesures.bold = True; run_mesures.font.size = Pt(14); p_mesures.alignment = WD_ALIGN_PARAGRAPH.LEFT # Aligné à gauche
            run_mesures.font.color.rgb = RGBColor(51, 153, 76) # Vert
            section_num += 1

            # Exercices de conversion (si présents pour le jour)
            if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]:
                current_day_geo_ex = geo_exercises[day-1]
                if current_day_geo_ex:
                    para_conv_title = add_paragraph(indent=True)
                    run_conv_title = para_conv_title.add_run("Conversions :")
                    run_conv_title.bold = True
                    for ex_conv in current_day_geo_ex:
                        add_paragraph(ex_conv, indent=True)
                    add_paragraph(indent=True) # Espace

            # Exercices de rangement (si présents pour le jour)
            if sort_exercises and len(sort_exercises) >= day and sort_exercises[day-1]:
                current_day_sort_ex = sort_exercises[day-1]
                if current_day_sort_ex:
                    para_sort_title = add_paragraph(indent=True)
                    ordre = "croissant" if current_day_sort_ex[0]['type'] == 'croissant' else "décroissant"
                    run_sort_title = para_sort_title.add_run(f"Range les nombres suivants dans l'ordre {ordre} :")
                    run_sort_title.bold = True
                    for ex_sort in current_day_sort_ex:
                        numbers_str = ", ".join(str(n) for n in ex_sort['numbers'])
                        add_paragraph(f"{numbers_str} = _________________________________", indent=True)
                    add_paragraph(indent=True) # Espace

            # Exercices d'encadrement
            if encadrement_lines_word:
                para_enc_title = add_paragraph(indent=True)
                run_enc_title = para_enc_title.add_run("Encadre les nombres :")
                run_enc_title.bold = True
                for ex_enc in encadrement_lines_word:
                    n_enc, t_enc = ex_enc['number'], ex_enc['type']
                    label = f"à l'{t_enc}" if t_enc == "unité" else f"à la {t_enc}" if t_enc in ["dizaine", "centaine"] else f"au {t_enc}"
                    add_paragraph(f"{n_enc} {label} : ______  {n_enc}  ______", indent=True)
                add_paragraph(indent=True) # Espace
            add_paragraph(indent=True) # Espace après la section mesures

        # Section Géométrie/Mesures (exercices de conversion)
        # (Maintenant intégré dans la section "Mesures" ci-dessus pour une meilleure structure)

        # Section Anglais (exercices)
        if english_exercises and len(english_exercises) >= day and english_exercises[day-1]: # Vérifie si la liste du jour n'est pas vide
            p = add_paragraph()
            run = p.add_run(f"{section_num}. Anglais")
            run.bold = True
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(51, 153, 178) # Bleu-vert
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT # Aligné à gauche
            section_num += 1

            # Indicateurs pour savoir si les sous-titres ont été affichés
            completer_subtitle_shown = False
            relier_subtitle_shown = False

            for ex in english_exercises[day-1]:
                if ex['type'] in ('simple', 'complexe'):
                    if not completer_subtitle_shown:
                        para_complete_title = add_paragraph(indent=True)
                        run_complete_title = para_complete_title.add_run("Compléter :")
                        run_complete_title.bold = True
                        completer_subtitle_shown = True
                    add_paragraph(ex['content'], indent=True)
                elif ex['type'] == 'relier':
                    # Ajoute le titre "Jeu de mots à relier :" pour chaque jeu de ce type
                    para_relier_title = add_paragraph(indent=True)
                    run_relier_title = para_relier_title.add_run("Jeu de mots à relier :")
                    run_relier_title.bold = True
                    
                    mots_a_relier_pour_jeu = ex['content']
                    
                    # Préparer les listes de mots anglais et français
                    liste_anglais = [item['english'] for item in mots_a_relier_pour_jeu]
                    liste_francais = [item['french'] for item in mots_a_relier_pour_jeu]
                    random.shuffle(liste_francais) # Mélanger une des listes pour le jeu

                    max_items = len(liste_anglais) # Ou len(mots_a_relier_pour_jeu)

                    for i in range(max_items):
                        mot_anglais = liste_anglais[i]
                        mot_francais = liste_francais[i] # Prend le mot français mélangé correspondant

                        # Créer un tableau à 5 colonnes pour chaque paire
                        table = doc.add_table(rows=1, cols=5)
                        table.autofit = False 
                        table.allow_autofit = False 

                        # Définir la largeur préférée du tableau
                        # Accéder à table._tbl.tblPr crée l'élément tblPr s'il n'existe pas.
                        tblPr = table._tbl.tblPr

                        # Largeur cible pour le tableau (somme des largeurs de colonnes ci-dessous)
                        target_table_width_inches = 1.3 + 0.2 + 0.6 + 0.2 + 1.3 # = 3.6 inches
                        target_table_width_dxa = int(target_table_width_inches * 1440) # Conversion en DXA (twips)
                        tblW = OxmlElement('w:tblW')
                        tblW.set(qn('w:w'), str(target_table_width_dxa))
                        tblW.set(qn('w:type'), 'dxa') 
                        tblPr.append(tblW)

                        # Définir les largeurs des colonnes
                        # Colonnes centrales fixes et étroites :
                        col_bullet_width = Inches(0.2)
                        col_space_width = Inches(0.6)
                        # Colonnes des mots (ajustez pour la longueur typique des mots sans retour à la ligne)
                        col_word_width = Inches(1.3) # Un peu moins pour que le total soit plus petit

                        table.columns[0].width = col_word_width  # Mot anglais
                        table.columns[1].width = col_bullet_width # Premier point
                        table.columns[2].width = col_space_width  # Espace pour tracer la ligne
                        table.columns[3].width = col_bullet_width # Deuxième point
                        table.columns[4].width = col_word_width  # Mot français
                        # Largeur totale indicative : 1.3 + 0.2 + 0.6 + 0.2 + 1.3 = 3.6 inches

                        row_cells = table.rows[0].cells
                        
                        # Remplir les cellules
                        # Appliquer un style de paragraphe compact aux cellules du tableau
                        contents = [mot_anglais, "\u2022", "", "\u2022", mot_francais]
                        alignments = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, 
                                      WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, 
                                      WD_ALIGN_PARAGRAPH.LEFT]

                        for idx, content_text in enumerate(contents):
                            cell = row_cells[idx]
                            cell.text = content_text # Remplace le contenu du premier paragraphe de la cellule
                            
                            paragraph = cell.paragraphs[0]
                            # Optionnel: réduire la taille de la police dans le tableau si besoin
                            # paragraph.runs[0].font.size = Pt(10) 
                            paragraph.paragraph_format.space_before = Pt(0)
                            paragraph.paragraph_format.space_after = Pt(1) # Très petit espace après
                            paragraph.alignment = alignments[idx]
                        
                        set_table_borders_invisible(table) # Rendre les bordures invisibles
            add_paragraph(indent=True) # Espace

        # Section Orthographe (si présente pour le jour)
        if orthographe_exercises and len(orthographe_exercises) >= day and orthographe_exercises[day-1]:
            p_ortho = add_paragraph()
            run_ortho = p_ortho.add_run(f"{section_num}. Orthographe")
            run_ortho.bold = True; run_ortho.font.size = Pt(14); p_ortho.alignment = WD_ALIGN_PARAGRAPH.LEFT # Aligné à gauche
            run_ortho.font.color.rgb = RGBColor(255, 178, 0) # Orange
            section_num += 1
            for ex_ortho in orthographe_exercises[day-1]:
                if ex_ortho['type'] == 'homophone':
                    para_homo = add_paragraph(indent=True)
                    run_homo_type = para_homo.add_run(f"{ex_ortho['homophone']} : ")
                    run_homo_type.bold = True
                    para_homo.add_run(ex_ortho['content'])
            add_paragraph(indent=True) # Espace

        if day < days: # N'ajoute pas de saut de page après le dernier jour
            doc.add_page_break()
    out_path = get_output_path(filename, output_dir_override)
    doc.save(out_path)
    print(f"Word généré : {out_path}")
    return out_path
