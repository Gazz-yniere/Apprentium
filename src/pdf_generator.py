from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
# from reportlab.platypus import Spacer # Import non utilisé si write_math_problems est commenté
import random # Conservé pour english_relier
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

PDF_STYLE_CONFIG = {
    "page": {
        "margin": 40,
    },
    "general_header": { # En-tête de page (Nom, Titre, Note)
        "box_height": 30,
        "box_stroke_color_rgb": (0.6, 0.6, 0.6),
        "text_font_name": "Helvetica",
        "text_font_size": 10,
        "text_color_rgb": (0, 0, 0),
        "title_font_name": "Helvetica-Bold",
        "title_font_size": 14,
        "y_offset_after_box": 18,
        "y_offset_no_header": 3,
    },
    "section_frame": { # Cadre général d'une section d'exercices
        "radius": 15,
        "stroke_width": 2,
        "default_stroke_color_rgb": (0.7, 0.7, 0.7),
        "content_bottom_padding": -5,
        "y_offset_after_box": 15,
    },
    "section_header": { # Titre numéroté à l'intérieur du cadre de section
        "title_font_name": "Helvetica-Bold", # Police pour le nom de la section (ex: "Calculs")
        "title_font_size": 12,
        "number_in_circle_font_name": "Helvetica-Bold",
        "number_in_circle_font_size": 10,
        "circle_radius": 10,
        "box_padding": 10, # Espacement interne du cadre de section par rapport à son contenu
        "img_width": 40,
        "img_height": 40,
        "content_x_start_offset_from_circle": 7,
    },
    "story_problems": { # "Petits Problèmes"
        "title_font_name": "Helvetica-Bold",
        "title_font_size": 9,
        "content_font_name": "Helvetica", # Changé de Helvetica-Bold à Helvetica
        "content_font_size": 9,
        "answer_font_name": "Helvetica",
        "answer_font_size": 9,
        "line_spacing_after_section_title": 5,
        "line_spacing_between_wrapped_lines": 3,
        "line_spacing_after_problem_text_block": 3,
        "line_spacing_after_answer_line": 11,
        "final_spacing_after_section": 8,
    },
    "calc_operations": { # Addition, Soustraction, etc.
        "title_font_name": "Helvetica-Bold", "title_font_size": 9,
        "content_font_name": "Helvetica", "content_font_size": 9,
        "line_spacing_after_title": 13, "line_spacing_per_item": 22, "spacing_after_section": 8,
    },
    "enumerate_numbers": {
        "title_font_name": "Helvetica-Bold", "title_font_size": 9,
        "content_font_name": "Helvetica", "content_font_size": 9,
        "line_spacing_after_title": 14, "line_spacing_per_item": 22, "spacing_after_section": 8,
    },
    "measures_conversions":   {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 5,},
    "measures_sort":          {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 8,},
    "measures_encadrement":   {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 8,},
    "conjugation":            {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 13, "line_spacing_before_pronouns": 10, "line_spacing_per_pronoun": 16, "spacing_after_verb_block": 7, "spacing_after_last_verb_block": 10,},
    "grammar":                {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_per_line": 13, "spacing_before_answer": 10, "line_spacing_answer": 22, "spacing_after_exercise_block": 10,},
    "orthographe_homophones": {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_per_item": 16, "spacing_after_item": 6,},
    "english_completer":      {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 13, "spacing_before_first_item": 10, "line_spacing_per_item": 16, "spacing_after_item": 10,},
    "english_relier":         {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 13, "spacing_before_first_item": 10, "line_spacing_per_item": 13, "spacing_after_block": 10, "x_offset_anglais": 0, "x_offset_bullet1": 75, "x_offset_bullet2_from_bullet1": 50, "x_offset_francais_from_bullet2": 20,},
    "default_font": { "name": "Helvetica", "size": 10, "color_rgb": (0,0,0)}
}

# Estimation de la hauteur de l'en-tête de section (numéro+titre)
HEADER_HEIGHT_ESTIMATE = (2 * PDF_STYLE_CONFIG["section_header"]["box_padding"] +
                          max(2 * PDF_STYLE_CONFIG["section_header"]["circle_radius"], PDF_STYLE_CONFIG["section_header"]["title_font_size"]))

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

# La fonction write_math_problems suivante utilise Paragraph et inch, qui ne sont pas définis
# et n'est pas utilisée par generate_workbook_pdf. Elle est commentée.
# Si elle devait être réactivée, il faudrait ajouter :
# from reportlab.platypus import Paragraph, Spacer
# from reportlab.lib.units import inch
# def write_math_problems(story, problems_for_day, styles):
#     # This function was for story problems, which are now handled by draw_canvas_story_problems
#     if not problems_for_day:
#         return
#     story.append(Paragraph("<u>Petits Problèmes:</u>", styles['h2']))
#     for idx, problem_data in enumerate(problems_for_day):
#         problem_text = f"{idx + 1}. {problem_data['content']}"
#         story.append(Paragraph(problem_text, styles['Normal']))
#         story.append(Spacer(1, 0.2 * inch)) # Espace pour la réponse
#     story.append(Spacer(1, 0.1 * inch))

def draw_rounded_box_with_color(pdf, x, y, w, h, radius=10, stroke_rgb_color=(0.7, 0.7, 0.7), fill_rgb_color=(1,1,1), stroke_width=1):
    # Utilise les valeurs de config si stroke_rgb_color est le défaut de la fonction
    if stroke_rgb_color == (0.7, 0.7, 0.7): # Check against the default argument value
        stroke_rgb_color = PDF_STYLE_CONFIG["section_frame"]["default_stroke_color_rgb"]
    radius = PDF_STYLE_CONFIG["section_frame"]["radius"]
    stroke_width = PDF_STYLE_CONFIG["section_frame"]["stroke_width"]

    pdf.setStrokeColorRGB(*stroke_rgb_color)
    pdf.setLineWidth(stroke_width)
    pdf.roundRect(x, y, w, h, radius, fill=0, stroke=1)

def draw_section_header(pdf, y_header_top, section_key, section_num, margin, page_width):
    """
    Dessine l'en-tête de la section (numéro, titre, image).
    y_header_top: Coordonnée Y du bord supérieur où l'en-tête (et le cadre) doit commencer.
    Retourne:
        y_after_header: Nouvelle position Y sous l'en-tête, prête pour le contenu.
        exercise_content_x_start: Position X de début du contenu.
    """
    cfg_sh = PDF_STYLE_CONFIG["section_header"]
    section_data = SECTION_ASSETS.get(section_key, {})
    section_color_rgb = section_data.get("color", (0, 0, 0)) # Couleur par défaut si non trouvée
    
    y_title_baseline = y_header_top - cfg_sh["box_padding"] - cfg_sh["title_font_size"]
    circle_center_x = margin + cfg_sh["box_padding"] + cfg_sh["circle_radius"]
    circle_center_y = y_title_baseline + cfg_sh["title_font_size"] * 0.3 

    pdf.setFillColorRGB(1, 1, 1) 
    pdf.setStrokeColorRGB(*section_color_rgb) 
    pdf.circle(circle_center_x, circle_center_y, cfg_sh["circle_radius"], fill=1, stroke=1)

    pdf.setFont(cfg_sh["number_in_circle_font_name"], cfg_sh["number_in_circle_font_size"])
    pdf.setFillColorRGB(*section_color_rgb)
    pdf.drawCentredString(circle_center_x, circle_center_y - (cfg_sh["number_in_circle_font_size"] / 3.0), str(section_num))
    exercise_content_x_start = circle_center_x + cfg_sh["circle_radius"] + cfg_sh["content_x_start_offset_from_circle"]

    pdf.setFont(cfg_sh["title_font_name"], cfg_sh["title_font_size"])
    pdf.setFillColorRGB(*section_color_rgb) 
    pdf.drawString(exercise_content_x_start, y_title_baseline, section_key)
    
    pdf.setFillColorRGB(*PDF_STYLE_CONFIG["default_font"]["color_rgb"]) # Reset fill color
    y_after_header = y_title_baseline - (2 * cfg_sh["circle_radius"]) - cfg_sh["box_padding"]
    return y_after_header, exercise_content_x_start

def draw_canvas_story_problems(pdf, y_position, problems_for_day, exercise_content_x_start, margin, page_width, page_height,
                               current_frame_segment_top_y_ref, # Use a list [y] to pass by reference for updates
                               section_data_for_image, # For redrawing image on new page
                               section_color_rgb): # For redrawing frame on new page
    """Dessine les "Petits Problèmes" sur le canvas, gérant les sauts de page."""
    if not problems_for_day:
        return y_position

    # Espacements pour les "Petits Problèmes" (utilisent les valeurs de la config)
    # line_spacing_after_section_title = 6 # Remplacé par config
    # line_spacing_between_wrapped_lines = 3 # Remplacé par config
    # line_spacing_after_problem_text_block = 4 # Remplacé par config
    cfg_sp = PDF_STYLE_CONFIG["story_problems"]
    title_font_size = cfg_sp["title_font_size"]
    # La police du contenu sera "Helvetica" (normal) après la modification de la config
    # La police pour le numéro sera "Helvetica-Bold" (cfg_sp["title_font_name"])
    number_font_name = cfg_sp["title_font_name"] # Devrait être Helvetica-Bold
    content_font_size = cfg_sp["content_font_size"]

    # Ajustement du titre en fonction du nombre de problèmes
    if len(problems_for_day) == 1:
        title_text = "Petit Problème:"
    else:
        title_text = "Petits Problèmes:"
    title_height_estimate = title_font_size + cfg_sp["line_spacing_after_section_title"]

    if y_position - title_height_estimate < margin:
        draw_rounded_box_with_color(pdf, margin, margin, page_width - 2 * margin, current_frame_segment_top_y_ref[0] - margin, stroke_rgb_color=section_color_rgb)
        pdf.showPage()
        y_position = page_height - margin
        current_frame_segment_top_y_ref[0] = y_position
        draw_section_image_in_frame(pdf, section_data_for_image, current_frame_segment_top_y_ref[0], page_width, margin)

    pdf.setFont(cfg_sp["title_font_name"], title_font_size)
    pdf.drawString(exercise_content_x_start, y_position, title_text)
    y_position -= title_height_estimate # Utilise l'estimation basée sur la config

    # La police pour le contenu sera définie plus tard, avant de dessiner les lignes
    max_text_width = page_width - exercise_content_x_start - margin - PDF_STYLE_CONFIG["section_header"]["box_padding"]

    for idx, problem_data in enumerate(problems_for_day):
        number_prefix_str = f"{idx + 1}. "
        problem_content_text = problem_data['content']
        
        # Préparer les lignes en joignant le préfixe et le contenu pour le retour à la ligne
        full_statement_for_wrapping = number_prefix_str + problem_content_text
        words = full_statement_for_wrapping.split(' ')
        current_line = ""
        lines_to_draw = []

        for word in words:
            # Utiliser la police de contenu normale (Helvetica) pour le calcul de la largeur du retour à la ligne
            if pdf.stringWidth(current_line + word + " ", cfg_sp["content_font_name"], content_font_size) <= max_text_width:
                current_line += word + " "
            else:
                lines_to_draw.append(current_line.strip())
                current_line = word + " "
        lines_to_draw.append(current_line.strip()) # Add the last line

        for line_idx_in_problem, line_text_segment in enumerate(lines_to_draw):
            # Check if the current line fits, if not, page break
            line_height_check = content_font_size + cfg_sp["line_spacing_between_wrapped_lines"]
            if y_position - line_height_check < margin:
                draw_rounded_box_with_color(pdf, margin, margin, page_width - 2 * margin, current_frame_segment_top_y_ref[0] - margin, stroke_rgb_color=section_color_rgb)
                pdf.showPage()
                y_position = page_height - margin
                current_frame_segment_top_y_ref[0] = y_position
                draw_section_image_in_frame(pdf, section_data_for_image, current_frame_segment_top_y_ref[0], page_width, margin)
                # Redraw "Petits Problèmes (suite)" if it's a new page for problems
                # Ajustement du titre (suite)
                suite_title_text = "Petit Problème (suite):" if len(problems_for_day) == 1 else "Petits Problèmes (suite):"
                pdf.setFont(cfg_sp["title_font_name"], title_font_size)
                # Utiliser le titre original pour la première page de la section,
                # et le titre "(suite)" pour les pages suivantes de la même section de problèmes.
                # La logique ici est pour quand on saute une page AU MILIEU des problèmes.
                pdf.drawString(exercise_content_x_start, y_position, suite_title_text)
                y_position -= (title_font_size + cfg_sp["line_spacing_after_section_title"])

            current_x_cursor = exercise_content_x_start
            if line_idx_in_problem == 0 and line_text_segment.startswith(number_prefix_str):
                # Première ligne du problème, commençant par le numéro
                # Dessiner le numéro en gras
                pdf.setFont(number_font_name, content_font_size) # Police grasse (ex: Helvetica-Bold)
                pdf.drawString(current_x_cursor, y_position, number_prefix_str)
                current_x_cursor += pdf.stringWidth(number_prefix_str, number_font_name, content_font_size)
                
                # Dessiner le reste de la première ligne en police normale
                text_after_prefix = line_text_segment[len(number_prefix_str):]
                pdf.setFont(cfg_sp["content_font_name"], content_font_size) # Police normale (ex: Helvetica)
                pdf.drawString(current_x_cursor, y_position, text_after_prefix)
            else:
                # Lignes suivantes du problème, ou première ligne si elle ne commence pas par le numéro (improbable)
                pdf.setFont(cfg_sp["content_font_name"], content_font_size) # Police normale
                pdf.drawString(current_x_cursor, y_position, line_text_segment)
            
            y_position -= (content_font_size + cfg_sp["line_spacing_between_wrapped_lines"])

        y_position -= (cfg_sp["line_spacing_after_problem_text_block"] - cfg_sp["line_spacing_between_wrapped_lines"]) 

        # "Réponse:" line
        answer_line_total_height = cfg_sp["answer_font_size"] + cfg_sp["line_spacing_after_answer_line"]
        if y_position - answer_line_total_height < margin:
            draw_rounded_box_with_color(pdf, margin, margin, page_width - 2 * margin, current_frame_segment_top_y_ref[0] - margin, stroke_rgb_color=section_color_rgb)
            pdf.showPage()
            y_position = page_height - margin
            current_frame_segment_top_y_ref[0] = y_position
            draw_section_image_in_frame(pdf, section_data_for_image, current_frame_segment_top_y_ref[0], page_width, margin)
            suite_title_text = "Petit Problème (suite):" if len(problems_for_day) == 1 else "Petits Problèmes (suite):"
            pdf.setFont(cfg_sp["title_font_name"], title_font_size) # Redraw title if new page starts with answer
            pdf.drawString(exercise_content_x_start, y_position, suite_title_text)
            y_position -= (title_font_size + cfg_sp["line_spacing_after_section_title"])
        
        pdf.setFont(cfg_sp["answer_font_name"], cfg_sp["answer_font_size"]) # Police pour "Réponse:"
        pdf.drawString(exercise_content_x_start + cfg_sp["answer_font_size"], y_position, "Réponse: _________________________________")
        y_position -= answer_line_total_height

    y_position -= cfg_sp["final_spacing_after_section"]
    return y_position

# La fonction generate_math_problems (pour l'arithmétique) a été déplacée vers calculs_generator.py
# et renommée en generate_arithmetic_problems.
from calculs_generator import generate_arithmetic_problems

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
    cfg_sh = PDF_STYLE_CONFIG["section_header"]
    image_file_path = get_resource_path_pdf(section_data.get("image_path", ""))
    if image_file_path and os.path.exists(image_file_path):
        img_draw_x = page_width - page_margin - cfg_sh["box_padding"] - cfg_sh["img_width"]
        img_draw_y = current_frame_top_y - cfg_sh["box_padding"] - cfg_sh["img_height"] # Y for bottom-left corner of image
        try:
            pdf.drawImage(image_file_path, img_draw_x, img_draw_y, width=cfg_sh["img_width"], height=cfg_sh["img_height"], mask='auto')
        except Exception as e:
            print(f"Erreur drawImage (in-frame) pour {image_file_path}: {e}")

def generate_workbook_pdf(days, operations, counts, max_digits, conjugations, params_list, grammar_exercises, orthographe_exercises, enumerate_exercises, sort_exercises, 
                          story_math_problems_by_day=None, 
                          geo_exercises=None, english_exercises=None, 
                          encadrement_exercises_list=None, 
                          header_text=None, filename="workbook.pdf", division_entier=False, show_name=False, show_note=False, output_dir_override=None,
                          compare_numbers_exercises_list=None, # Nouveau
                          logical_sequences_exercises_list=None): # Nouveau
    if geo_exercises is None:
        geo_exercises = []
    if english_exercises is None: english_exercises = [] # Initialisation
    if encadrement_exercises_list is None: encadrement_exercises_list = [] # Liste de listes (une par jour)
    if story_math_problems_by_day is None: story_math_problems_by_day = []

    cfg_page = PDF_STYLE_CONFIG["page"]
    cfg_gen_header = PDF_STYLE_CONFIG["general_header"]
    cfg_def_font = PDF_STYLE_CONFIG["default_font"]

    out_path = get_output_path(filename, output_dir_override)
    pdf = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    margin = cfg_page["margin"]

    for day in range(1, days + 1):
        y_position = height - margin
        if header_text or show_name or show_note:
            box_height = cfg_gen_header["box_height"]
            # Ajustement pour que la largeur du cadre de l'en-tête corresponde à celle des sections
            box_x_header = margin 
            box_width_header = width - 2 * margin
            box_y_header = y_position - box_height
            draw_rounded_box_with_color(pdf, 
                                       box_x_header, 
                                       box_y_header, 
                                       box_width_header, 
                                       box_height, 
                                       stroke_rgb_color=cfg_gen_header["box_stroke_color_rgb"])
            y_header_text = box_y_header + 10
            
            pdf.setFont(cfg_gen_header["text_font_name"], cfg_gen_header["text_font_size"])
            pdf.setFillColorRGB(*cfg_gen_header["text_color_rgb"])

            if show_name:
                pdf.drawString(margin + 10, y_header_text, "Nom : _________________")
            if header_text:
                pdf.setFont(cfg_gen_header["title_font_name"], cfg_gen_header["title_font_size"])
                pdf.drawCentredString(width // 2, y_header_text + 1, header_text)
                pdf.setFont(cfg_gen_header["text_font_name"], cfg_gen_header["text_font_size"])
                pdf.setFillColorRGB(*cfg_gen_header["text_color_rgb"])
            if show_note:
                note_text = "Note : ____________" # Utiliser la police et taille par défaut pour stringWidth
                note_x = width - margin - 10 - pdf.stringWidth(note_text, cfg_gen_header["text_font_name"], cfg_gen_header["text_font_size"])
                pdf.drawString(note_x, y_header_text, note_text)
            y_position = box_y_header - cfg_gen_header["y_offset_after_box"]
        else:
            y_position -= cfg_gen_header["y_offset_no_header"]
        
        pdf.setFont(cfg_def_font["name"], cfg_def_font["size"])
        pdf.setFillColorRGB(*cfg_def_font["color_rgb"])

        section_num = 1
        
        current_day_story_problems = story_math_problems_by_day[day-1] if len(story_math_problems_by_day) >= day else None

        # Section Calculs
        if (
            (enumerate_exercises and len(enumerate_exercises) >= day and enumerate_exercises[day-1])
            or any(counts)
            or current_day_story_problems # Condition ajoutée pour les "Petits Problèmes"
        ):
            cfg_calc_enum = PDF_STYLE_CONFIG["enumerate_numbers"]
            cfg_calc_ops = PDF_STYLE_CONFIG["calc_operations"]

            section_key = "Calculs"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.2, 0.4, 0.8))
            
            first_block_content_height = 0
            if enumerate_exercises and len(enumerate_exercises) >= day and enumerate_exercises[day-1]:
                first_block_content_height = cfg_calc_enum["line_spacing_after_title"] + cfg_calc_enum["line_spacing_per_item"] + cfg_calc_enum["spacing_after_section"]
            elif current_day_story_problems: # Estimation pour "Petits Problèmes"
                first_block_content_height = 10 + 6 + 9 + 4 + 9 + 13 # Title + space + problem + space + answer + space
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

            current_frame_top_y_list = [current_frame_segment_top_y]
            
            if enumerate_exercises and len(enumerate_exercises) >= day and enumerate_exercises[day-1]:
                pdf.setFont(cfg_calc_enum["title_font_name"], cfg_calc_enum["title_font_size"])
                pdf.drawString(exercise_content_x_start, y_position, "Écris chaque nombre en toutes lettres :")
                y_position -= cfg_calc_enum["line_spacing_after_title"]
                pdf.setFont(cfg_calc_enum["content_font_name"], cfg_calc_enum["content_font_size"])
                for n in enumerate_exercises[day-1]: 
                    pdf.drawString(exercise_content_x_start, y_position, f"{n} = _____________________________________________")
                    y_position -= cfg_calc_enum["line_spacing_per_item"]
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position # Mettre à jour le haut du segment de cadre
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_calc_enum["content_font_name"], cfg_calc_enum["content_font_size"])
                y_position -= cfg_calc_enum["spacing_after_section"]
            
            if any(counts):
                pdf.setFont(cfg_calc_ops["title_font_name"], cfg_calc_ops["title_font_size"])
                for i, operation in enumerate(operations):
                    params = params_list[i]
                    problems = generate_arithmetic_problems(operation, params) # Utilise la fonction importée
                    pdf.drawString(exercise_content_x_start, y_position, f"{operation.capitalize()} :")
                    y_position -= cfg_calc_ops["line_spacing_after_title"]
                    pdf.setFont(cfg_calc_ops["content_font_name"], cfg_calc_ops["content_font_size"])
                    for problem in problems:
                        calc_str = problem.strip().replace(' =', '')
                        pdf.drawString(exercise_content_x_start, y_position, f"{calc_str} = _____________________________________________")
                        y_position -= cfg_calc_ops["line_spacing_per_item"]
                        if y_position < margin:
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position # Mettre à jour le haut du segment de cadre
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont(cfg_calc_ops["content_font_name"], cfg_calc_ops["content_font_size"])
                    pdf.setFont(cfg_calc_ops["title_font_name"], cfg_calc_ops["title_font_size"]) # Reset for next operation title
                y_position -= cfg_calc_ops["spacing_after_section"]

            # Déplacer les "Petits Problèmes" ici, après les calculs et énumérations
            if current_day_story_problems:
                original_font_calc, original_size_calc = pdf._fontname, pdf._fontsize
                original_fill_color_obj = pdf._fillColorObj

                current_frame_top_y_list[0] = current_frame_segment_top_y

                y_position = draw_canvas_story_problems(pdf, y_position, current_day_story_problems,
                                                        exercise_content_x_start, margin, width, height,
                                                        current_frame_top_y_list,
                                                        section_data, section_color_rgb)
                current_frame_segment_top_y = current_frame_top_y_list[0] # Récupérer la mise à jour si story_problems a sauté une page
                
                pdf.setFont(original_font_calc, original_size_calc)
                pdf.setFillColor(original_fill_color_obj)
            
            box_actual_bottom_y = y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"]
            draw_rounded_box_with_color(pdf, 
                                       margin, box_actual_bottom_y, 
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y, 
                                       stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        # Section Mesures
        current_day_encadrement_lines = encadrement_exercises_list[day-1] if len(encadrement_exercises_list) >= day else None
        
        has_mesures_content_for_day = False
        if current_day_encadrement_lines: has_mesures_content_for_day = True
        current_day_compare_numbers = compare_numbers_exercises_list[day-1] if compare_numbers_exercises_list and len(compare_numbers_exercises_list) >= day else None
        if current_day_compare_numbers: has_mesures_content_for_day = True
        current_day_logical_sequences = logical_sequences_exercises_list[day-1] if logical_sequences_exercises_list and len(logical_sequences_exercises_list) >= day else None
        if current_day_logical_sequences: has_mesures_content_for_day = True
        
        if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]: has_mesures_content_for_day = True
        if sort_exercises and len(sort_exercises) >= day and sort_exercises[day-1]: has_mesures_content_for_day = True

        if has_mesures_content_for_day:
            cfg_mes_conv = PDF_STYLE_CONFIG["measures_conversions"]
            cfg_mes_sort = PDF_STYLE_CONFIG["measures_sort"]
            cfg_mes_enc = PDF_STYLE_CONFIG["measures_encadrement"]

            section_key = "Mesures"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.2, 0.6, 0.3))

            first_block_content_height = 0
            if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]:
                 first_block_content_height = cfg_mes_conv["line_spacing_after_title"] + cfg_mes_conv["line_spacing_per_item"] + cfg_mes_conv["spacing_after_section"]
            elif sort_exercises and len(sort_exercises) >= day and sort_exercises[day-1]:
                 first_block_content_height = cfg_mes_sort["line_spacing_after_title"] + cfg_mes_sort["line_spacing_per_item"] + cfg_mes_sort["spacing_after_section"]
            elif current_day_encadrement_lines:
                 first_block_content_height = 16 + 22 + 8 # Encadrement title + first item + spacing
            elif current_day_compare_numbers: # Estimation pour comparer des nombres
                 first_block_content_height = 16 + 22 + 8 # Titre + premier item + espacement
            elif current_day_logical_sequences: # Estimation pour suites logiques
                 first_block_content_height = 16 + 22 + 8 # Titre + premier item + espacement

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
            
            pdf.setFont(cfg_def_font["name"], cfg_def_font["size"]) # Default content font
            if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]:
                current_day_geo_exercises = geo_exercises[day-1]
                if current_day_geo_exercises: 
                    pdf.setFont(cfg_mes_conv["title_font_name"], cfg_mes_conv["title_font_size"])
                    # Ajustement du titre en fonction du nombre d'exercices de conversion
                    if len(current_day_geo_exercises) == 1:
                        pdf.drawString(exercise_content_x_start, y_position, "Conversion :")
                    else:
                        pdf.drawString(exercise_content_x_start, y_position, "Conversions :")
                    y_position -= cfg_mes_conv["line_spacing_after_title"]
                    pdf.setFont(cfg_mes_conv["content_font_name"], cfg_mes_conv["content_font_size"])
                    for ex_geo in current_day_geo_exercises:
                        pdf.drawString(exercise_content_x_start, y_position, ex_geo)
                        y_position -= cfg_mes_conv["line_spacing_per_item"]
                        if y_position < margin:
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont(cfg_mes_conv["content_font_name"], cfg_mes_conv["content_font_size"])
                    y_position -= cfg_mes_conv["spacing_after_section"]

            if sort_exercises and len(sort_exercises) >= day and sort_exercises[day-1]:
                current_day_sort_exercises = sort_exercises[day-1]
                if current_day_sort_exercises: 
                    pdf.setFont(cfg_mes_sort["title_font_name"], cfg_mes_sort["title_font_size"])
                    ordre = "ordre croissant" if current_day_sort_exercises[0]['type'] == 'croissant' else "ordre décroissant"
                    pdf.drawString(exercise_content_x_start, y_position, f"Range les nombres suivants dans l'{ordre} :")
                    y_position -= cfg_mes_sort["line_spacing_after_title"]
                    pdf.setFont(cfg_mes_sort["content_font_name"], cfg_mes_sort["content_font_size"])
                    for ex_sort in current_day_sort_exercises:
                        numbers_str = ", ".join(str(n) for n in ex_sort['numbers'])
                        pdf.drawString(exercise_content_x_start, y_position, f"{numbers_str} = _____________________________________________")
                        y_position -= cfg_mes_sort["line_spacing_per_item"]
                        if y_position < margin:
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont(cfg_mes_sort["content_font_name"], cfg_mes_sort["content_font_size"])
                    y_position -= cfg_mes_sort["spacing_after_section"]

            if current_day_encadrement_lines:
                pdf.setFont(cfg_mes_enc["title_font_name"], cfg_mes_enc["title_font_size"])
                # Ajustement du titre en fonction du nombre d'exercices d'encadrement
                if len(current_day_encadrement_lines) == 1:
                    pdf.drawString(exercise_content_x_start, y_position, "Encadre le nombre :")
                else:
                    pdf.drawString(exercise_content_x_start, y_position, "Encadre les nombres :")
                y_position -= cfg_mes_enc["line_spacing_after_title"]
                pdf.setFont(cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                for ex in current_day_encadrement_lines:
                    n = ex['number']
                    t = ex['type']
                    label = f"à l'{t}" if t == "unité" else f"à la {t}" if t in ["dizaine", "centaine"] else f"au {t}"
                    pdf.drawString(exercise_content_x_start, y_position, f"{n} {label} : ______  {n}  ______")
                    y_position -= 22
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                y_position -= cfg_mes_enc["spacing_after_section"]
            
            # Intégration de "Comparer des nombres" dans la section Mesures
            if current_day_compare_numbers:
                pdf.setFont(cfg_mes_enc["title_font_name"], cfg_mes_enc["title_font_size"]) # Utilise le style d'encadrement pour le titre
                pdf.drawString(exercise_content_x_start, y_position, "Comparer les nombres (<, >, =) :")
                y_position -= cfg_mes_enc["line_spacing_after_title"]
                pdf.setFont(cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                for ex_compare in current_day_compare_numbers:
                    pdf.drawString(exercise_content_x_start, y_position, f"{ex_compare['num1']} ______ {ex_compare['num2']}")
                    y_position -= cfg_mes_enc["line_spacing_per_item"] # Utilise l'espacement d'encadrement
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                y_position -= cfg_mes_enc["spacing_after_section"]

            # Intégration de "Suites Logiques" dans la section Mesures
            if current_day_logical_sequences:
                pdf.setFont(cfg_mes_enc["title_font_name"], cfg_mes_enc["title_font_size"])
                pdf.drawString(exercise_content_x_start, y_position, "Complète les suites logiques :")
                y_position -= cfg_mes_enc["line_spacing_after_title"]
                pdf.setFont(cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                for ex_seq in current_day_logical_sequences:
                    sequence_str = " ".join(map(str, ex_seq['sequence_displayed']))
                    # type_desc = ""
                    # if ex_seq['type'] == 'arithmetic_plus':
                    #     type_desc = f" (+{ex_seq['step']})"
                    # elif ex_seq['type'] == 'arithmetic_minus':
                    #     type_desc = f" (-{ex_seq['step']})"
                    pdf.drawString(exercise_content_x_start, y_position, f"{sequence_str}")
                    y_position -= cfg_mes_enc["line_spacing_per_item"]
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                y_position -= cfg_mes_enc["spacing_after_section"]
            
            box_actual_bottom_y = y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"]
            draw_rounded_box_with_color(pdf,
                                       margin, box_actual_bottom_y,
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y,
                                       stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        # Section Conjugaison
        if conjugations and len(conjugations) >= day and conjugations[day-1]:
            cfg_conj = PDF_STYLE_CONFIG["conjugation"]
            section_key = "Conjugaison"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.7, 0.3, 0.2))

            # Calculate required height for header + first block
            first_block_content_height = (cfg_conj["line_spacing_after_title"] + cfg_conj["line_spacing_before_pronouns"] +
                                          cfg_conj["line_spacing_per_pronoun"] + cfg_conj["spacing_after_verb_block"])
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

                pdf.setFont(cfg_conj["title_font_name"], cfg_conj["title_font_size"])
                pdf.drawString(exercise_content_x_start, y_position, f"Verbe : {verb}  |  Groupe : {groupe}  |  Temps : {tense}")
                y_position -= cfg_conj["line_spacing_after_title"]
                pdf.setFont(cfg_conj["content_font_name"], cfg_conj["content_font_size"])
                y_position -= cfg_conj["line_spacing_before_pronouns"]
                for pronoun in PRONOUNS:
                    pdf.drawString(exercise_content_x_start, y_position, pronoun)
                    pdf.drawString(exercise_content_x_start + 100, y_position, "____________________")
                    y_position -= cfg_conj["line_spacing_per_pronoun"]
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_conj["content_font_name"], cfg_conj["content_font_size"])
                y_position -= cfg_conj["spacing_after_verb_block"]
                y_position -= cfg_conj["spacing_after_last_verb_block"]
            
            box_actual_bottom_y = y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"]
            draw_rounded_box_with_color(pdf,
                                       margin, box_actual_bottom_y,
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y,
                                       stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        # Section Grammaire
        if grammar_exercises and len(grammar_exercises) >= day and grammar_exercises[day-1]:
            cfg_gram = PDF_STYLE_CONFIG["grammar"]
            section_key = "Grammaire"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.5, 0.2, 0.7))

            # Calculate required height for header + first block
            first_block_content_height = (cfg_gram["line_spacing_per_line"] * 2 + cfg_gram["spacing_before_answer"] +
                                          cfg_gram["line_spacing_answer"] + cfg_gram["spacing_after_exercise_block"])
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
            
            pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])
            for ex in grammar_exercises[day-1]:
                phrase = ex['phrase']
                transformation = ex['transformation']
                pdf.setFont(cfg_gram["title_font_name"], cfg_gram["title_font_size"])
                pdf.drawString(exercise_content_x_start, y_position, f"Phrase :")
                pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])
                pdf.drawString(exercise_content_x_start + 55, y_position, phrase)
                y_position -= cfg_gram["line_spacing_per_line"]
                if y_position < margin:
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])

                pdf.setFont(cfg_gram["title_font_name"], cfg_gram["title_font_size"])
                pdf.drawString(exercise_content_x_start, y_position, f"Transformation demandée :")
                pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])
                pdf.drawString(exercise_content_x_start + 130, y_position, transformation)
                y_position -= cfg_gram["line_spacing_per_line"]
                if y_position < margin:
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])

                y_position -= cfg_gram["spacing_before_answer"]
                pdf.drawString(exercise_content_x_start, y_position, "Réponse : __________________________________________________________")
                y_position -= cfg_gram["line_spacing_answer"]
                y_position -= cfg_gram["spacing_after_exercise_block"]
                if y_position < margin: # Check after full exercise block
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])
            
            box_actual_bottom_y = y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"]
            draw_rounded_box_with_color(pdf,
                                       margin, box_actual_bottom_y,
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y,
                                       stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        # Section Orthographe
        if orthographe_exercises and len(orthographe_exercises) >= day and orthographe_exercises[day-1]:
            cfg_ortho = PDF_STYLE_CONFIG["orthographe_homophones"]
            section_key = "Orthographe"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (1.0, 0.7, 0.0))

            # Calculate required height for header + first block
            first_block_content_height = 0
            # Homophone line + spacing
            first_block_content_height = cfg_ortho["line_spacing_per_item"] + cfg_ortho["spacing_after_item"]
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
            
            pdf.setFont(cfg_ortho["content_font_name"], cfg_ortho["content_font_size"])
            for ex in orthographe_exercises[day-1]:
                if ex['type'] == 'homophone':
                    pdf.setFont(cfg_ortho["title_font_name"], cfg_ortho["title_font_size"])
                    pdf.drawString(exercise_content_x_start, y_position, f"{ex['homophone']} :")
                    pdf.setFont(cfg_ortho["content_font_name"], cfg_ortho["content_font_size"])
                    pdf.drawString(exercise_content_x_start + 60, y_position, ex['content']) 
                    y_position -= cfg_ortho["line_spacing_per_item"]
                    y_position -= cfg_ortho["spacing_after_item"]
                if y_position < margin: # Check after each exercise item
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont(cfg_ortho["content_font_name"], cfg_ortho["content_font_size"])

            box_actual_bottom_y = y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"]
            draw_rounded_box_with_color(pdf,
                                       margin, box_actual_bottom_y,
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y,
                                       stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        # Section Anglais
        if english_exercises and len(english_exercises) >= day and english_exercises[day-1]:
            cfg_eng_comp = PDF_STYLE_CONFIG["english_completer"]
            cfg_eng_rel = PDF_STYLE_CONFIG["english_relier"]
            section_key = "Anglais"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.2, 0.6, 0.7))

            # Calculate required height for header + first block
            first_block_content_height = 0
            if english_exercises[day-1]: # Check if there's at least one exercise
                first_ex = english_exercises[day-1][0]
                if first_ex['type'] in ('simple', 'complexe'):
                    first_block_content_height = (cfg_eng_comp["line_spacing_after_title"] + cfg_eng_comp["spacing_before_first_item"] +
                                                  cfg_eng_comp["line_spacing_per_item"] + cfg_eng_comp["spacing_after_item"])
                elif first_ex['type'] == 'relier':
                    first_block_content_height = (cfg_eng_rel["line_spacing_after_title"] + cfg_eng_rel["spacing_before_first_item"] +
                                                  cfg_eng_rel["line_spacing_per_item"] + cfg_eng_rel["spacing_after_block"])
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
            
            pdf.setFont(cfg_def_font["name"], cfg_def_font["size"])
            completer_shown = False
            for ex_idx, ex in enumerate(english_exercises[day-1]):
                if ex['type'] in ('simple', 'complexe'):
                    if not completer_shown:
                        pdf.setFont(cfg_eng_comp["title_font_name"], cfg_eng_comp["title_font_size"])
                        pdf.drawString(exercise_content_x_start, y_position, "Compléter :")
                        pdf.setFont(cfg_eng_comp["content_font_name"], cfg_eng_comp["content_font_size"])
                        y_position -= cfg_eng_comp["line_spacing_after_title"]
                        completer_shown = True
                        y_position -= cfg_eng_comp["spacing_before_first_item"]
                        if y_position < margin:
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont(cfg_eng_comp["content_font_name"], cfg_eng_comp["content_font_size"])

                    pdf.drawString(exercise_content_x_start, y_position, ex['content'])
                    y_position -= cfg_eng_comp["line_spacing_per_item"]
                    y_position -= cfg_eng_comp["spacing_after_item"]
                elif ex['type'] == 'relier':
                    completer_shown = False 
                    pdf.setFont(cfg_eng_rel["title_font_name"], cfg_eng_rel["title_font_size"])
                    pdf.drawString(exercise_content_x_start, y_position, "Jeu de mots à relier :")
                    pdf.setFont(cfg_eng_rel["content_font_name"], cfg_eng_rel["content_font_size"])
                    y_position -= cfg_eng_rel["line_spacing_after_title"]
                    y_position -= cfg_eng_rel["spacing_before_first_item"]
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_eng_rel["content_font_name"], cfg_eng_rel["content_font_size"])

                    mots = ex['content']
                    anglais_words = [m['english'] for m in mots]
                    francais_words = [m['french'] for m in mots]
                    random.shuffle(anglais_words)
                    
                    max_len = max(len(anglais_words), len(francais_words))
                    x_anglais = exercise_content_x_start + cfg_eng_rel["x_offset_anglais"]
                    x_bullet1 = exercise_content_x_start + cfg_eng_rel["x_offset_bullet1"]
                    x_bullet2 = x_bullet1 + cfg_eng_rel["x_offset_bullet2_from_bullet1"]
                    x_francais = x_bullet2 + cfg_eng_rel["x_offset_francais_from_bullet2"]

                    for i in range(max_len):
                        a = anglais_words[i] if i < len(anglais_words) else ''
                        f = francais_words[i] if i < len(francais_words) else ''
                        pdf.drawString(x_anglais, y_position, a)
                        pdf.drawString(x_bullet1, y_position, '\u2022')
                        pdf.drawString(x_bullet2, y_position, '\u2022')
                        pdf.drawString(x_francais, y_position, f)
                        y_position -= cfg_eng_rel["line_spacing_per_item"]
                        if y_position < margin:
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont(cfg_eng_rel["content_font_name"], cfg_eng_rel["content_font_size"])
                    y_position -= cfg_eng_rel["spacing_after_block"]

                # General check after each exercise item in the loop
                if y_position < margin and ex_idx < len(english_exercises[day-1]) -1 : # Avoid if it's the last item and box will be drawn after loop
                    # This check might be redundant if sub-types already handled it, but acts as a fallback.
                    # Ensure not to draw box if it's already handled by inner logic or if it's the end of section
                    if not (y_position == height - margin and current_frame_segment_top_y == y_position): # Avoid double draw if already page breaked
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb)
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont(cfg_def_font["name"], cfg_def_font["size"]) # Reset to default content font
            
            box_actual_bottom_y = y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"]
            draw_rounded_box_with_color(pdf,
                                       margin, box_actual_bottom_y,
                                       width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y,
                                       stroke_rgb_color=section_color_rgb)
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        if day < days:
            pdf.showPage()

    pdf.save()
    print(f"PDF généré : {out_path}")
    return out_path
