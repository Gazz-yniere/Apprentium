from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import random
import sys
import os

# Configuration des assets pour chaque section
SECTION_ASSETS = {
    "Calculs": {"image_path": "img/calculs.png", "color": (0.2, 0.4, 0.8)}, # Bleu
    "Mesures": {"image_path": "img/mesures.png", "color": (0.2, 0.6, 0.3)}, # Vert
    "Conjugaison": {"image_path": "img/conjugaison.png", "color": (0.7, 0.3, 0.2)}, # Rouge-brique
    "Grammaire": {"image_path": "img/grammaire.png", "color": (0.5, 0.2, 0.7)}, # Violet
    "Orthographe": {"image_path": "img/orthographe.png", "color": (1.0, 0.7, 0.0)}, # Orange
    "Anglais": {"image_path": "img/anglais.png", "color": (0.2, 0.6, 0.7)} # Bleu-vert
}
IMG_WIDTH, IMG_HEIGHT = 40, 40 # Taille standard pour les images de section
BOX_PADDING = 10 # Espacement interne des cadres de section
SECTION_CONTENT_BOTTOM_PADDING = 0 # Espacement interne en bas du contenu de la section (réduit de 5 à 2)
HEADER_HEIGHT_ESTIMATE = 2 * BOX_PADDING + max(2 * 10, 12) # Estimation de la hauteur de l'en-tête de section (numéro+titre)

def get_resource_path_pdf(relative_path):
    """ Obtient le chemin absolu d'une ressource, que ce soit en mode script ou compilé. """
    try:
        base_path = os.path.dirname(__file__)
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"Erreur dans get_resource_path_pdf pour {relative_path}: {e}")
        return None

def draw_rounded_box_with_color(pdf, x, y, w, h, radius=10, stroke_rgb_color=(0.7, 0.7, 0.7), fill_rgb_color=(1,1,1), stroke_width=1):
    pdf.setStrokeColorRGB(*stroke_rgb_color)
    pdf.setLineWidth(stroke_width)
    pdf.roundRect(x, y, w, h, radius, fill=0, stroke=1)

def draw_section_header(pdf, y_header_top, section_key, section_num, margin, page_width, title_font_size=12, number_in_circle_font_size=10):
    """
    Dessine l'en-tête de la section (numéro, titre, image).
    y_header_top: Coordonnée Y du bord supérieur où l'en-tête (et le cadre) doit commencer.
    Retourne:
        y_after_header: Nouvelle position Y sous l'en-tête, prête pour le contenu.
        exercise_content_x_start: Position X de début du contenu.
    """
    section_data = SECTION_ASSETS.get(section_key, {})
    section_color_rgb = section_data.get("color", (0, 0, 0)) # Couleur par défaut si non trouvée
    
    y_title_baseline = y_header_top - BOX_PADDING - title_font_size
    CIRCLE_RADIUS_PDF = 10
    circle_center_x = margin + BOX_PADDING + CIRCLE_RADIUS_PDF
    circle_center_y = y_title_baseline + title_font_size * 0.3 


    pdf.setFillColorRGB(1, 1, 1) 
    pdf.setStrokeColorRGB(*section_color_rgb) 
    pdf.circle(circle_center_x, circle_center_y, CIRCLE_RADIUS_PDF, fill=1, stroke=1)

    NUMBER_IN_CIRCLE_FONT_SIZE = 10
    pdf.setFont("Helvetica-Bold", NUMBER_IN_CIRCLE_FONT_SIZE)
    pdf.setFillColorRGB(*section_color_rgb)
    pdf.drawCentredString(circle_center_x, circle_center_y - (number_in_circle_font_size / 3.0), str(section_num))
    exercise_content_x_start = circle_center_x + CIRCLE_RADIUS_PDF + 7 

    pdf.setFont("Helvetica-Bold", title_font_size)
    pdf.setFillColorRGB(*section_color_rgb) 
    pdf.drawString(exercise_content_x_start, y_title_baseline, section_key)
    
    pdf.setFillColorRGB(0,0,0) # Reset fill color for subsequent content
    #y_after_header = y_title_baseline - (max(2 * CIRCLE_RADIUS_PDF, title_font_size) - title_font_size) - BOX_PADDING
    y_after_header = y_title_baseline - (2*CIRCLE_RADIUS_PDF)- BOX_PADDING
    return y_after_header, exercise_content_x_start

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

    if base_dir_for_output is None: 
        if getattr(sys, 'frozen', False): 
            app_base_path = os.path.dirname(sys.executable)
        else: 
            app_base_path = os.path.dirname(os.path.dirname(__file__)) 
        base_dir_for_output = os.path.join(app_base_path, 'output')

    os.makedirs(base_dir_for_output, exist_ok=True) 
    return os.path.join(base_dir_for_output, filename)

def draw_section_image_in_frame(pdf, section_data, current_frame_top_y, page_width, page_margin):
    """Dessine l'image de la section en haut à droite à l'intérieur du cadre."""
    image_file_path = get_resource_path_pdf(section_data.get("image_path", ""))
    if image_file_path and os.path.exists(image_file_path):
        img_draw_x = page_width - page_margin - BOX_PADDING - IMG_WIDTH
        img_draw_y = current_frame_top_y - BOX_PADDING - IMG_HEIGHT # Y for bottom-left corner of image
        try:
            pdf.drawImage(image_file_path, img_draw_x, img_draw_y, width=IMG_WIDTH, height=IMG_HEIGHT, mask='auto')
        except Exception as e:
            print(f"Erreur drawImage (in-frame) pour {image_file_path}: {e}")

def generate_workbook_pdf(days, operations, counts, max_digits, conjugations, params_list, grammar_exercises, orthographe_exercises, enumerate_exercises, sort_exercises, geo_exercises=None, english_exercises=None, encadrement_exercises=None, header_text=None, filename="workbook.pdf", division_entier=False, show_name=False, show_note=False, output_dir_override=None):
    if geo_exercises is None:
        geo_exercises = []
    if english_exercises is None:
        english_exercises = []
    if encadrement_exercises is None:
        encadrement_exercises = {'count': 0, 'digits': 0, 'types': []}
    out_path = get_output_path(filename, output_dir_override)
    pdf = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    margin = 50

    for day in range(1, days + 1):
        y_position = height - margin
        if header_text or show_name or show_note:
            box_height = 30
            # Ajustement pour que la largeur du cadre de l'en-tête corresponde à celle des sections
            box_x_header = margin 
            box_width_header = width - 2 * margin
            box_y_header = y_position - box_height
            draw_rounded_box_with_color(pdf, 
                                       box_x_header, 
                                       box_y_header, 
                                       box_width_header, 
                                       box_height, 
                                       radius=10, 
                                       stroke_rgb_color=(0.6, 0.6, 0.6)) # Couleur du cadre de l'en-tête
            y_header_text = box_y_header + 10
            
            # Style par défaut pour Nom et Note
            default_font_name = "Helvetica"
            default_font_size = 10
            default_font_color = (0, 0, 0)

            pdf.setFont(default_font_name, default_font_size)
            pdf.setFillColorRGB(*default_font_color)

            if show_name:
                pdf.drawString(margin + 10, y_header_text, "Nom : _________________")
            if header_text:
                pdf.setFont("Helvetica-Bold", 14)
                pdf.drawCentredString(width // 2, y_header_text + 1, header_text)
                pdf.setFont(default_font_name, default_font_size) # Réinitialiser à la police par défaut après le titre
                pdf.setFillColorRGB(*default_font_color) # Réinitialiser la couleur
            if show_note:
                note_text = "Note : ____________"
                note_x = width - margin - 10 - pdf.stringWidth(note_text, "Helvetica", 10) # Default font for note
                pdf.drawString(note_x, y_header_text, note_text)
            y_position = box_y_header - 18
        else:
            y_position -= 3
        
        pdf.setFont("Helvetica", 10) # Default font before sections
        pdf.setFillColorRGB(0, 0, 0)

        section_num = 1
        
        # Section Calculs
        if (
            (enumerate_exercises and len(enumerate_exercises) >= day and enumerate_exercises[day-1])
            or any(counts)
        ):
            section_key = "Calculs"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.2, 0.4, 0.8))
            
            # Calculate required height for header + first block of content
            first_block_content_height = 0
            if enumerate_exercises and len(enumerate_exercises) >= day and enumerate_exercises[day-1]:
                 first_block_content_height = 16 + 22 + 8 # Enumerate title + first item + spacing
            elif any(counts):
                 first_block_content_height = 13 + 22 + 8 # Operation title + first item + spacing

            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            # Check if the first block fits on the current page
            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin

            current_frame_segment_top_y = y_position # Le haut du cadre est la y_position actuelle
            
            # draw_section_header dessine le titre/numéro À L'INTÉRIEUR du cadre,
            # en utilisant current_frame_segment_top_y comme référence supérieure.
            # Elle retourne la y_position pour le contenu (exercices), sous le titre/numéro.
            y_position_for_content, exercise_content_x_start = draw_section_header(
                pdf, current_frame_segment_top_y, section_key, section_num, margin, width
            )
            y_position = y_position_for_content # Mettre à jour y_position pour le début des exercices
            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
            section_num += 1
            
            if enumerate_exercises and len(enumerate_exercises) >= day and enumerate_exercises[day-1]:
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(exercise_content_x_start, y_position, "Écris chaque nombre en toutes lettres :")
                y_position -= 16
                pdf.setFont("Helvetica", 9)
                for n in enumerate_exercises[day-1]: 
                    pdf.drawString(exercise_content_x_start, y_position, f"{n} = _____________________________________________")
                    y_position -= 22
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont("Helvetica", 9) 
                y_position -= 8
            
            if any(counts):
                pdf.setFont("Helvetica-Bold", 10)
                for i, operation in enumerate(operations):
                    params = params_list[i]
                    problems = generate_math_problems(operation, params)
                    pdf.drawString(exercise_content_x_start, y_position, f"{operation.capitalize()} :")
                    y_position -= 13
                    pdf.setFont("Helvetica", 9)
                    for problem in problems:
                        calc_str = problem.strip().replace(' =', '')
                        pdf.drawString(exercise_content_x_start, y_position, f"{calc_str} = _____________________________________________")
                        y_position -= 22
                        if y_position < margin:
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont("Helvetica", 9) 
                    pdf.setFont("Helvetica-Bold", 10) # Reset for next operation title
                y_position -= 8
            
            box_actual_bottom_y = y_position - SECTION_CONTENT_BOTTOM_PADDING
            draw_rounded_box_with_color(pdf, 
                                       margin, box_actual_bottom_y, 
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y, 
                                       radius=10, stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - 15

        # Section Mesures
        encadrement_lines = []
        if encadrement_exercises and encadrement_exercises['count'] > 0 and encadrement_exercises['digits'] > 0 and encadrement_exercises['types']:
            digits = encadrement_exercises['digits']
            min_n = 10**(digits-1) if digits > 0 else 0 
            max_n = (10**digits - 1) if digits > 0 else 0
            types_enc = encadrement_exercises['types']
            for _ in range(encadrement_exercises['count']):
                t = random.choice(types_enc)
                n = random.randint(min_n, max_n)
                encadrement_lines.append({'number': n, 'type': t})
        
        has_mesures_content_for_day = False
        if encadrement_lines: has_mesures_content_for_day = True
        if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]: has_mesures_content_for_day = True
        if sort_exercises and len(sort_exercises) >= day and sort_exercises[day-1]: has_mesures_content_for_day = True

        if has_mesures_content_for_day:
            section_key = "Mesures"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.2, 0.6, 0.3))

            # Calculate required height for header + first block
            first_block_content_height = 0
            if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]:
                 first_block_content_height = 16 + 22 + 5 # Geo title + first item + spacing
            elif sort_exercises and len(sort_exercises) >= day and sort_exercises[day-1]:
                 first_block_content_height = 16 + 22 + 8 # Sort title + first item + spacing
            elif encadrement_lines:
                 first_block_content_height = 16 + 22 + 8 # Encadrement title + first item + spacing

            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin
            current_frame_segment_top_y = y_position
            y_position_for_content, exercise_content_x_start = draw_section_header(
                pdf, current_frame_segment_top_y, section_key, section_num, margin, width
            )
            y_position = y_position_for_content
            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
            section_num += 1
            
            pdf.setFont("Helvetica", 9) # Default content font for this section
            if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]:
                current_day_geo_exercises = geo_exercises[day-1]
                if current_day_geo_exercises: 
                    pdf.setFont("Helvetica-Bold", 10)
                    pdf.drawString(exercise_content_x_start, y_position, "Conversions :")
                    y_position -= 16
                    pdf.setFont("Helvetica", 9)
                    for ex_geo in current_day_geo_exercises:
                        pdf.drawString(exercise_content_x_start, y_position, ex_geo)
                        y_position -= 22
                        if y_position < margin:
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont("Helvetica", 9)
                    y_position -= 5

            if sort_exercises and len(sort_exercises) >= day and sort_exercises[day-1]:
                current_day_sort_exercises = sort_exercises[day-1]
                if current_day_sort_exercises: 
                    pdf.setFont("Helvetica-Bold", 10)
                    ordre = "ordre croissant" if current_day_sort_exercises[0]['type'] == 'croissant' else "ordre décroissant"
                    pdf.drawString(exercise_content_x_start, y_position, f"Range les nombres suivants dans l'{ordre} :")
                    y_position -= 16
                    pdf.setFont("Helvetica", 9)
                    for ex_sort in current_day_sort_exercises:
                        numbers_str = ", ".join(str(n) for n in ex_sort['numbers'])
                        pdf.drawString(exercise_content_x_start, y_position, f"{numbers_str} = _____________________________________________")
                        y_position -= 22
                        if y_position < margin:
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont("Helvetica", 9)
                    y_position -= 8

            if encadrement_lines:
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(exercise_content_x_start, y_position, "Encadre les nombres :")
                y_position -= 16
                pdf.setFont("Helvetica", 9)
                for ex in encadrement_lines:
                    n = ex['number']
                    t = ex['type']
                    label = f"à l'{t}" if t == "unité" else f"à la {t}" if t in ["dizaine", "centaine"] else f"au {t}"
                    pdf.drawString(exercise_content_x_start, y_position, f"{n} {label} : ______  {n}  ______")
                    y_position -= 22
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont("Helvetica", 9)
                y_position -= 8
            
            box_actual_bottom_y = y_position - SECTION_CONTENT_BOTTOM_PADDING
            draw_rounded_box_with_color(pdf,
                                       margin, box_actual_bottom_y,
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y,
                                       radius=10, stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - 15

        # Section Conjugaison
        if conjugations and len(conjugations) >= day and conjugations[day-1]:
            section_key = "Conjugaison"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.7, 0.3, 0.2))

            # Calculate required height for header + first block
            first_block_content_height = 0
            # Verb/Tense title + spacing + first pronoun line + spacing
            first_block_content_height = 13 + 10 + 16 + 7
            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin

            current_frame_segment_top_y = y_position
            y_position_for_content, exercise_content_x_start = draw_section_header(
                pdf, current_frame_segment_top_y, section_key, section_num, margin, width
            )
            y_position = y_position_for_content
            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
            section_num += 1
            
            from conjugation_generator import PRONOUNS, VERBS # Keep import local if specific
            for conjugation_item in conjugations[day-1]:
                verb = conjugation_item["verb"]
                tense = conjugation_item["tense"]
                groupe = None
                for g_num_key in VERBS: 
                    if isinstance(g_num_key, int) or str(g_num_key).isdigit(): 
                        if verb in VERBS[g_num_key]:
                            groupe = f"{g_num_key}er groupe"
                            break
                if not groupe and "usuels" in VERBS and verb in VERBS["usuels"]: groupe = "usuel"
                if not groupe: groupe = "inconnu"

                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(exercise_content_x_start, y_position, f"Verbe : {verb}  |  Groupe : {groupe}  |  Temps : {tense}")
                y_position -= 13
                pdf.setFont("Helvetica", 9)
                y_position -= 10  
                for pronoun in PRONOUNS:
                    pdf.drawString(exercise_content_x_start, y_position, pronoun)
                    pdf.drawString(exercise_content_x_start + 100, y_position, "____________________")
                    y_position -= 16  
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont("Helvetica", 9)
                y_position -= 7
                y_position -= 10  
            
            box_actual_bottom_y = y_position - SECTION_CONTENT_BOTTOM_PADDING
            draw_rounded_box_with_color(pdf,
                                       margin, box_actual_bottom_y,
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y,
                                       radius=10, stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - 15

        # Section Grammaire
        if grammar_exercises and len(grammar_exercises) >= day and grammar_exercises[day-1]:
            section_key = "Grammaire"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.5, 0.2, 0.7))

            # Calculate required height for header + first block
            first_block_content_height = 0
            # Phrase + Transformation + spacing + Reponse + spacing
            first_block_content_height = 13 + 13 + 10 + 22 + 10
            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin

            current_frame_segment_top_y = y_position
            y_position_for_content, exercise_content_x_start = draw_section_header(
                pdf, current_frame_segment_top_y, section_key, section_num, margin, width
            )
            y_position = y_position_for_content
            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
            section_num += 1
            
            pdf.setFont("Helvetica", 9) 
            for ex in grammar_exercises[day-1]:
                phrase = ex['phrase']
                transformation = ex['transformation']
                pdf.setFont("Helvetica-Bold", 9)
                pdf.drawString(exercise_content_x_start, y_position, f"Phrase :")
                pdf.setFont("Helvetica", 9)
                pdf.drawString(exercise_content_x_start + 55, y_position, phrase)
                y_position -= 13
                if y_position < margin:
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont("Helvetica", 9)

                pdf.setFont("Helvetica-Bold", 9)
                pdf.drawString(exercise_content_x_start, y_position, f"Transformation demandée :")
                pdf.setFont("Helvetica", 9)
                pdf.drawString(exercise_content_x_start + 130, y_position, transformation)
                y_position -= 13
                if y_position < margin:
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont("Helvetica", 9)

                y_position -= 10  
                pdf.drawString(exercise_content_x_start, y_position, "Réponse : __________________________________________________________")
                y_position -= 22  
                y_position -= 10  
                if y_position < margin: # Check after full exercise block
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont("Helvetica", 9)
            
            box_actual_bottom_y = y_position - SECTION_CONTENT_BOTTOM_PADDING
            draw_rounded_box_with_color(pdf,
                                       margin, box_actual_bottom_y,
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y,
                                       radius=10, stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - 15

        # Section Orthographe
        if orthographe_exercises and len(orthographe_exercises) >= day and orthographe_exercises[day-1]:
            section_key = "Orthographe"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (1.0, 0.7, 0.0))

            # Calculate required height for header + first block
            first_block_content_height = 0
            # Homophone line + spacing
            first_block_content_height = 16 + 6
            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin
            current_frame_segment_top_y = y_position
            y_position_for_content, exercise_content_x_start = draw_section_header(
                pdf, current_frame_segment_top_y, section_key, section_num, margin, width
            )
            y_position = y_position_for_content
            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
            section_num += 1
            
            pdf.setFont("Helvetica", 9) 
            for ex in orthographe_exercises[day-1]:
                if ex['type'] == 'homophone':
                    pdf.setFont("Helvetica-Bold", 9)
                    pdf.drawString(exercise_content_x_start, y_position, f"{ex['homophone']} :")
                    pdf.setFont("Helvetica", 9)
                    pdf.drawString(exercise_content_x_start + 60, y_position, ex['content']) 
                    y_position -= 16
                    y_position -= 6  
                if y_position < margin: # Check after each exercise item
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont("Helvetica", 9)

            box_actual_bottom_y = y_position - SECTION_CONTENT_BOTTOM_PADDING
            draw_rounded_box_with_color(pdf,
                                       margin, box_actual_bottom_y,
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y,
                                       radius=10, stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - 15

        # Section Anglais
        if english_exercises and len(english_exercises) >= day and english_exercises[day-1]:
            section_key = "Anglais"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.2, 0.6, 0.7))

            # Calculate required height for header + first block
            first_block_content_height = 0
            if english_exercises[day-1]: # Check if there's at least one exercise
                first_ex = english_exercises[day-1][0]
                if first_ex['type'] in ('simple', 'complexe'):
                    first_block_content_height = 13 + 10 + 16 + 10 # Compléter title + spacing + first item + spacing
                elif first_ex['type'] == 'relier':
                    first_block_content_height = 13 + 10 + 13 + 10 # Relier title + spacing + first line + spacing
            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin
            current_frame_segment_top_y = y_position
            y_position_for_content, exercise_content_x_start = draw_section_header(
                pdf, current_frame_segment_top_y, section_key, section_num, margin, width
            )
            y_position = y_position_for_content
            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
            section_num += 1
            
            pdf.setFont("Helvetica", 9) 
            completer_shown = False
            for ex_idx, ex in enumerate(english_exercises[day-1]):
                if ex['type'] in ('simple', 'complexe'):
                    if not completer_shown:
                        pdf.setFont("Helvetica-Bold", 9)
                        pdf.drawString(exercise_content_x_start, y_position, "Compléter :")
                        pdf.setFont("Helvetica", 9) 
                        y_position -= 13
                        completer_shown = True
                        y_position -= 10  
                        if y_position < margin:
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont("Helvetica", 9) # Reset font, completer_shown state might need re-evaluation or header re-draw

                    pdf.drawString(exercise_content_x_start, y_position, ex['content'])
                    y_position -= 16  
                    y_position -= 10  
                elif ex['type'] == 'relier':
                    completer_shown = False 
                    pdf.setFont("Helvetica-Bold", 9)
                    pdf.drawString(exercise_content_x_start, y_position, "Jeu de mots à relier :")
                    pdf.setFont("Helvetica", 9) 
                    y_position -= 13
                    y_position -= 10  
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont("Helvetica", 9)

                    mots = ex['content']
                    anglais_words = [m['english'] for m in mots]
                    francais_words = [m['french'] for m in mots]
                    random.shuffle(anglais_words)
                    # random.shuffle(francais_words) # Shuffling both might make it too hard to match if lists are long
                    
                    max_len = max(len(anglais_words), len(francais_words))
                    x_anglais = exercise_content_x_start
                    x_bullet1 = exercise_content_x_start + 75 # Réduction de l'espacement
                    x_bullet2 = x_bullet1 + 50 
                    x_francais = x_bullet2 + 20

                    for i in range(max_len):
                        a = anglais_words[i] if i < len(anglais_words) else ''
                        f = francais_words[i] if i < len(francais_words) else ''
                        pdf.drawString(x_anglais, y_position, a)
                        pdf.drawString(x_bullet1, y_position, '\u2022') # Bullet point
                        pdf.drawString(x_bullet2, y_position, '\u2022') # Bullet point
                        pdf.drawString(x_francais, y_position, f)
                        y_position -= 13 # Space for each line
                        if y_position < margin:
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont("Helvetica", 9) 
                    y_position -= 10  

                # General check after each exercise item in the loop
                if y_position < margin and ex_idx < len(english_exercises[day-1]) -1 : # Avoid if it's the last item and box will be drawn after loop
                    # This check might be redundant if sub-types already handled it, but acts as a fallback.
                    # Ensure not to draw box if it's already handled by inner logic or if it's the end of section
                    if not (y_position == height - margin and current_frame_segment_top_y == y_position): # Avoid double draw if already page breaked
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, radius=10, stroke_rgb_color=section_color_rgb)
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont("Helvetica", 9)
            
            box_actual_bottom_y = y_position - SECTION_CONTENT_BOTTOM_PADDING
            draw_rounded_box_with_color(pdf,
                                       margin, box_actual_bottom_y,
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y,
                                       radius=10, stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - 15

        if day < days:
            pdf.showPage()

    pdf.save()
    print(f"PDF généré : {out_path}")
    return out_path
