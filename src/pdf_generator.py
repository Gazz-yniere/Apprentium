from calculs_generator import generate_arithmetic_problems
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
# from reportlab.platypus import Spacer # Import non utilisé si write_math_problems est commenté
import random  # Conservé pour english_relier
import sys
import os

# Configuration des assets pour chaque section
SECTION_ASSETS = {
    # Bleu
    "Calculs": {"image_path": "img/calculs.png", "color": (0.2, 0.4, 0.8)},
    # Vert
    "Mesures": {"image_path": "img/mesures.png", "color": (0.2, 0.6, 0.3)},
    # Rouge-brique
    "Conjugaison": {"image_path": "img/conjugaison.png", "color": (0.7, 0.3, 0.2)},
    # Violet
    "Grammaire": {"image_path": "img/grammaire.png", "color": (0.5, 0.2, 0.7)},
    # Orange
    "Orthographe": {"image_path": "img/orthographe.png", "color": (1.0, 0.7, 0.0)},
    # Bleu-vert
    "Anglais": {"image_path": "img/anglais.png", "color": (0.2, 0.6, 0.7)},
}

PDF_STYLE_CONFIG = {
    "page": {
        "margin": 35,
    },
    "general_header": {  # En-tête de page (Nom, Titre, Note)
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
    "section_frame": {  # Cadre général d'une section d'exercices
        "radius": 15,
        "stroke_width": 2,
        "default_stroke_color_rgb": (0.7, 0.7, 0.7),
        "content_bottom_padding": -10,
        "y_offset_after_box": 15,
    },
    "section_header": {  # Titre numéroté à l'intérieur du cadre de section
        # Police pour le nom de la section (ex: "Calculs")
        "title_font_name": "Helvetica-Bold",
        "title_font_size": 12,
        "number_in_circle_font_name": "Helvetica-Bold",
        "number_in_circle_font_size": 10,
        "circle_radius": 10,
        "box_padding_horizontal": 20,  # Espacement horizontal interne du cadre
        "content_top_padding": 20, # Espace entre l'en-tête et le premier contenu
        "img_width": 50,
        "img_height": 50,
        "img_top_padding": 5, # Padding for the image from the top of the frame
        "content_x_start_offset_from_circle": 7,
        "overlap_offset": 3,  # How much the header visually overlaps above the frame top line
        "bg_padding_top": 7,  # Extra padding above the header text
        "bg_padding_bottom": 3,  # Extra padding below the header text
        "bg_padding_horizontal": 5,  # Extra padding for the white background box
        "horizontal_shift": 10, # New parameter to shift everything right
        "vertical_shift": 2,  # Shift the title and number down by this amount
        "bg_vertical_shift": 5, # Shift the background box down
    },
    "story_problems": {  # "Petits Problèmes"
        "title_font_name": "Helvetica-Bold",
        "title_font_size": 9,
        "content_font_name": "Helvetica",  # Changé de Helvetica-Bold à Helvetica
        "content_font_size": 9,
        "answer_font_name": "Helvetica", # noqa E501
        "answer_font_size": 9,
        "line_spacing_after_section_title": 10,
        "line_spacing_between_wrapped_lines": 3,
        "line_spacing_after_problem_text_block": 6,
        "line_spacing_after_answer_line": 11,
        "final_spacing_after_section": 8,
    },
    "calc_operations": {  # Addition, Soustraction, etc.
        "title_font_name": "Helvetica-Bold", "title_font_size": 9,
        "content_font_name": "Helvetica", "content_font_size": 9, # noqa E501
        "line_spacing_after_title": 16, "line_spacing_per_item": 16, "spacing_after_section": 3, # noqa E501
    },
    "enumerate_numbers": {
        "title_font_name": "Helvetica-Bold", "title_font_size": 9,
        "content_font_name": "Helvetica", "content_font_size": 9, # noqa E501
        "line_spacing_after_title": 16, "line_spacing_per_item": 16, "spacing_after_section": 6, # noqa E501
    },
    "measures_conversions":   {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 5, },
    "measures_sort":          {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 8, },
    "measures_encadrement":   {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 8, },
    "conjugation":            {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 10, "line_spacing_before_pronouns": 10, "line_spacing_per_pronoun": 16,"spacing_after_verb_block": 5, "spacing_after_last_verb_block": 10, "spacing_between_exercise_types": 15, }, # noqa E501
    "conj_completer":         {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 8, }, # noqa E501
    "grammar":                {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_per_line": 13, "spacing_before_answer": 10, "line_spacing_answer": 22, "spacing_after_exercise_block": 10, }, # noqa E501
    "orthographe_homophones": {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 16, "line_spacing_per_item": 16, "spacing_after_item": 10, }, # noqa E501
    "english_completer":      {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 10, "spacing_before_first_item": 10, "line_spacing_per_item": 13, "spacing_after_item": 10, }, # noqa E501
    "english_relier":         {"title_font_name": "Helvetica-Bold", "title_font_size": 9, "content_font_name": "Helvetica", "content_font_size": 9, "line_spacing_after_title": 10, "spacing_before_first_item": 10, "line_spacing_per_item": 13, "spacing_after_block": 10, "x_offset_anglais": 0, "x_offset_bullet1": 75, "x_offset_bullet2_from_bullet1": 50, "x_offset_francais_from_bullet2": 20, }, # noqa E501
    "default_font": {"name": "Helvetica", "size": 10, "color_rgb": (0, 0, 0)}
}

# Estimation de la hauteur de l'en-tête de section (numéro+titre)
cfg_sh = PDF_STYLE_CONFIG["section_header"]
# This estimate is for the total vertical space consumed by the header, from its highest point to the point where the content starts inside the frame.
HEADER_HEIGHT_ESTIMATE = (cfg_sh["overlap_offset"] + cfg_sh["circle_radius"] + cfg_sh["bg_padding_top"] + cfg_sh["content_top_padding"])


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

def draw_rounded_box_with_color(pdf, x, y, w, h, radius=10, stroke_rgb_color=(0.7, 0.7, 0.7), fill_rgb_color=(1, 1, 1), stroke_width=1, sides='all'):
    # Utilise les valeurs de config si stroke_rgb_color est le défaut de la fonction
    # Check against the default argument value
    if stroke_rgb_color == (0.7, 0.7, 0.7):
        stroke_rgb_color = PDF_STYLE_CONFIG["section_frame"]["default_stroke_color_rgb"]
    radius = PDF_STYLE_CONFIG["section_frame"]["radius"]
    stroke_width = PDF_STYLE_CONFIG["section_frame"]["stroke_width"]

    pdf.setStrokeColorRGB(*stroke_rgb_color)
    pdf.setLineWidth(stroke_width)

    if sides == 'all':
        pdf.roundRect(x, y, w, h, radius, fill=0, stroke=1)
        return

    # Coordinates for corners and lines
    x_left = x
    x_right = x + w
    y_bottom = y
    y_top = y + h

    if 'top' in sides:
        pdf.line(x_left + radius, y_top, x_right - radius, y_top)  # top line
        pdf.arc(x_left, y_top - 2 * radius, x_left + 2 * radius, y_top, 90, 90)  # top-left arc
        pdf.arc(x_right - 2 * radius, y_top - 2 * radius, x_right, y_top, 0, 90)  # top-right arc

    if 'bottom' in sides:
        pdf.line(x_left + radius, y_bottom, x_right - radius, y_bottom)  # bottom line
        pdf.arc(x_left, y_bottom, x_left + 2 * radius, y_bottom + 2 * radius, 180, 90)  # bottom-left arc
        pdf.arc(x_right - 2 * radius, y_bottom, x_right, y_bottom + 2 * radius, 270, 90)  # bottom-right arc

    if 'left' in sides:
        pdf.line(x_left, y_bottom + radius, x_left, y_top - radius)  # left line

    if 'right' in sides:
        pdf.line(x_right, y_bottom + radius, x_right, y_top - radius)  # right line


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
    # Couleur par défaut si non trouvée
    section_color_rgb = section_data.get("color", (0, 0, 0))

    # --- New positioning for superimposed effect ---
    # Place the center of the circle slightly above the frame's top line
    circle_center_y = y_header_top + cfg_sh["overlap_offset"] - cfg_sh["vertical_shift"]

    # Calculate text baseline relative to circle center
    y_title_baseline = circle_center_y - (cfg_sh["title_font_size"] * 0.3)  # Empirical adjustment for visual alignment

    # Calculate x positions
    circle_center_x = margin + cfg_sh["box_padding_horizontal"] + cfg_sh["circle_radius"] + cfg_sh["horizontal_shift"] # Position du cercle (décalé)
    header_title_x_start = (circle_center_x + cfg_sh["circle_radius"] + cfg_sh["content_x_start_offset_from_circle"]) # Position du titre (décalé)

    # Calculate width of the section title text
    pdf.setFont(cfg_sh["title_font_name"], cfg_sh["title_font_size"])  # Set font to measure width
    title_text_width = pdf.stringWidth(section_key, cfg_sh["title_font_name"], cfg_sh["title_font_size"])

    # --- Draw white background rectangle to mask the frame line ---
    # This rectangle should cover the area where the header overlaps the frame
    # and extend slightly into the frame for a clean cut.
    # It needs to be wide enough to cover the circle and the text.
    # La position de départ du fond inclut le décalage horizontal
    bg_x_start = margin + cfg_sh["box_padding_horizontal"] - cfg_sh["bg_padding_horizontal"] + cfg_sh["horizontal_shift"]

    # La largeur du fond est calculée sur la taille du contenu (cercle + titre) plus le padding,
    # SANS inclure le décalage horizontal dans la largeur elle-même.
    content_width_for_bg = (2 * cfg_sh["circle_radius"] + cfg_sh["content_x_start_offset_from_circle"] + title_text_width)
    bg_width = content_width_for_bg + 2 * cfg_sh["bg_padding_horizontal"]

    # La fin du fond est simplement le début + la largeur
    bg_x_end = bg_x_start + bg_width

    bg_y_top = circle_center_y + cfg_sh["circle_radius"] + cfg_sh["bg_padding_top"]
    bg_y_bottom = circle_center_y - cfg_sh["circle_radius"] - cfg_sh["bg_padding_bottom"]
    
    # Apply the new vertical shift for the background
    bg_vertical_shift = cfg_sh.get("bg_vertical_shift", 0)
    bg_y_top -= bg_vertical_shift
    bg_y_bottom -= bg_vertical_shift
    
    pdf.setFillColorRGB(1, 1, 1)  # White fill
    pdf.setStrokeColorRGB(1, 1, 1)  # White stroke to hide any border
    pdf.rect(bg_x_start, bg_y_bottom, bg_width, bg_y_top - bg_y_bottom, fill=1, stroke=1)  # Draw filled white rectangle

    # --- Draw circle and text on top of the white background ---
    pdf.setStrokeColorRGB(*section_color_rgb)
    pdf.setLineWidth(PDF_STYLE_CONFIG["section_frame"]["stroke_width"]) # Fix for thin border
    pdf.circle(circle_center_x, circle_center_y,
               cfg_sh["circle_radius"], fill=1, stroke=1)
    pdf.setFont(cfg_sh["number_in_circle_font_name"],
                cfg_sh["number_in_circle_font_size"])
    pdf.setFillColorRGB(*section_color_rgb)
    pdf.drawCentredString(circle_center_x, circle_center_y - (cfg_sh["number_in_circle_font_size"] / 3.0), str(section_num))  # noqa E501
    pdf.setFont(cfg_sh["title_font_name"], cfg_sh["title_font_size"]) # Set font to measure width
    pdf.setFillColorRGB(*section_color_rgb) # Set color for the title text
    pdf.drawString(header_title_x_start, y_title_baseline, section_key) # Draw the title text
    # Reset fill color # noqa E501
    pdf.setFillColorRGB(*PDF_STYLE_CONFIG["default_font"]["color_rgb"])

    # --- Calculate y_after_header for content inside the frame ---
    # Content should start below the frame's top edge, with some padding.
    # The frame's top edge is y_header_top.
    y_after_header = y_header_top - cfg_sh["content_top_padding"]

    # --- Calculate exercise_content_x_start for content inside the frame (NON-DÉCALÉ) ---
    exercise_content_x_start_for_content = margin + cfg_sh["box_padding_horizontal"]

    return y_after_header, exercise_content_x_start_for_content


def draw_canvas_story_problems(pdf, y_position, problems_for_day, exercise_content_x_start, margin, page_width, page_height,
                               # Use a list [y] to pass by reference for updates
                               current_frame_segment_top_y_ref,
                               section_data_for_image,  # For redrawing image on new page
                               section_color_rgb):  # For redrawing frame on new page
    """Dessine les "Petits Problèmes" sur le canvas, gérant les sauts de page."""
    if not problems_for_day:
        return y_position

    cfg_sp = PDF_STYLE_CONFIG["story_problems"]
    title_font_size = cfg_sp["title_font_size"]
    number_font_name = cfg_sp["title_font_name"]
    content_font_size = cfg_sp["content_font_size"]

    if len(problems_for_day) == 1:
        title_text = "Petit Problème:"
    else:
        title_text = "Petits Problèmes:"
    title_height_estimate = (title_font_size + cfg_sp["line_spacing_after_section_title"])

    if y_position - title_height_estimate < margin:
        # Close previous frame segment
        draw_rounded_box_with_color(pdf, margin, margin, page_width - 2 * margin, current_frame_segment_top_y_ref[0] - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
        pdf.showPage()
        y_position = page_height - margin
        current_frame_segment_top_y_ref[0] = y_position
        # Draw top of new frame segment
        draw_rounded_box_with_color(pdf, margin, y_position, page_width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
        draw_section_image_in_frame(pdf, section_data_for_image, current_frame_segment_top_y_ref[0], page_width, margin)

    pdf.setFont(cfg_sp["title_font_name"], title_font_size)
    pdf.drawString(exercise_content_x_start, y_position, title_text)
    y_position -= title_height_estimate

    max_text_width = (page_width - exercise_content_x_start - margin - PDF_STYLE_CONFIG["section_header"]["box_padding_horizontal"]) # Utilise la nouvelle valeur de exercise_content_x_start

    for idx, problem_data in enumerate(problems_for_day):
        number_prefix_str = f"{idx + 1}. "
        problem_content_text = problem_data['content']
        full_statement_for_wrapping = number_prefix_str + problem_content_text
        words = full_statement_for_wrapping.split(' ')
        current_line = ""
        lines_to_draw = []

        for word in words:
            if pdf.stringWidth(current_line + word + " ", cfg_sp["content_font_name"], content_font_size) <= max_text_width:
                current_line += word + " "
            else:
                lines_to_draw.append(current_line.strip())
                current_line = word + " "
        lines_to_draw.append(current_line.strip())

        for line_idx_in_problem, line_text_segment in enumerate(lines_to_draw):
            line_height_check = (content_font_size + cfg_sp["line_spacing_between_wrapped_lines"])
            if y_position - line_height_check < margin:
                # Close previous frame segment
                draw_rounded_box_with_color(pdf, margin, margin, page_width - 2 * margin, current_frame_segment_top_y_ref[0] - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                pdf.showPage()
                y_position = page_height - margin
                current_frame_segment_top_y_ref[0] = y_position
                # Draw top of new frame segment
                draw_rounded_box_with_color(pdf, margin, y_position, page_width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                draw_section_image_in_frame(
                    pdf, section_data_for_image, current_frame_segment_top_y_ref[0], page_width, margin)
                suite_title_text = "Petit Problème (suite):" if len(
                    problems_for_day) == 1 else "Petits Problèmes (suite):"
                pdf.setFont(cfg_sp["title_font_name"], title_font_size)
                pdf.drawString(exercise_content_x_start, y_position, suite_title_text)
                y_position -= (title_font_size + cfg_sp["line_spacing_after_section_title"])

            current_x_cursor = exercise_content_x_start
            if line_idx_in_problem == 0 and line_text_segment.startswith(number_prefix_str):
                pdf.setFont(number_font_name, content_font_size)
                pdf.drawString(current_x_cursor, y_position, number_prefix_str)
                current_x_cursor += pdf.stringWidth(number_prefix_str, number_font_name, content_font_size)
                text_after_prefix = line_text_segment[len(number_prefix_str):]
                pdf.setFont(cfg_sp["content_font_name"], content_font_size)
                pdf.drawString(current_x_cursor, y_position, text_after_prefix)
            else:
                pdf.setFont(cfg_sp["content_font_name"], content_font_size)
                pdf.drawString(current_x_cursor, y_position, line_text_segment)
            y_position -= (content_font_size + cfg_sp["line_spacing_between_wrapped_lines"])

        y_position -= (cfg_sp["line_spacing_after_problem_text_block"] - cfg_sp["line_spacing_between_wrapped_lines"])

        answer_line_total_height = (cfg_sp["answer_font_size"] + cfg_sp["line_spacing_after_answer_line"])
        if y_position - answer_line_total_height < margin:
            # Close previous frame segment
            draw_rounded_box_with_color(pdf, margin, margin, page_width - 2 * margin, current_frame_segment_top_y_ref[0] - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
            pdf.showPage()
            y_position = page_height - margin
            current_frame_segment_top_y_ref[0] = y_position
            # Draw top of new frame segment
            draw_rounded_box_with_color(pdf, margin, y_position, page_width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
            draw_section_image_in_frame(
                pdf, section_data_for_image, current_frame_segment_top_y_ref[0], page_width, margin)
            suite_title_text = "Petit Problème (suite):" if len(
                problems_for_day) == 1 else "Petits Problèmes (suite):"
            pdf.setFont(cfg_sp["title_font_name"], title_font_size)
            pdf.drawString(exercise_content_x_start, y_position, suite_title_text)
            y_position -= (title_font_size + cfg_sp["line_spacing_after_section_title"])

        pdf.setFont(cfg_sp["answer_font_name"], cfg_sp["answer_font_size"])
        pdf.drawString(exercise_content_x_start + cfg_sp["answer_font_size"], y_position, "Réponse: _________________________________")
        y_position -= answer_line_total_height

    y_position -= cfg_sp["final_spacing_after_section"]
    return y_position


def get_output_path(filename, custom_output_dir=None):
    import sys
    import os
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
                print(
                    f"Avertissement : Impossible de créer le dossier personnalisé '{custom_output_dir}'. Utilisation du dossier par défaut.")

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
    if image_file_path and os.path.exists(image_file_path): # noqa E501
        img_draw_x = (page_width - page_margin - cfg_sh["box_padding_horizontal"] - cfg_sh["img_width"]) # noqa E501
        img_draw_y = (current_frame_top_y - cfg_sh["img_top_padding"] - cfg_sh["img_height"]) # noqa E501
        try:
            pdf.drawImage(image_file_path, img_draw_x, img_draw_y, width=cfg_sh["img_width"], height=cfg_sh["img_height"], mask='auto')
        except Exception as e:
            print(f"Erreur drawImage (in-frame) pour {image_file_path}: {e}")


def generate_workbook_pdf(days, operations, counts, max_digits, conjugations, params_list, grammar_exercises, orthographe_exercises, enumerate_exercises, sort_exercises, story_math_problems_by_day=None, geo_exercises=None, english_exercises=None, encadrement_exercises_list=None, header_text=None, filename="workbook.pdf", division_entier=False, show_name=False, show_note=False, output_dir_override=None, compare_numbers_exercises_list=None, logical_sequences_exercises_list=None, conj_complete_sentence_exercises=None, conj_complete_pronoun_exercises=None, measurement_problems=None):
    if geo_exercises is None:
        geo_exercises = []
    if english_exercises is None:
        english_exercises = []
    if encadrement_exercises_list is None:
        encadrement_exercises_list = []
    if conj_complete_sentence_exercises is None:
        conj_complete_sentence_exercises = []
    if conj_complete_pronoun_exercises is None:
        conj_complete_pronoun_exercises = []
    if measurement_problems is None:
        measurement_problems = []
    if story_math_problems_by_day is None:
        story_math_problems_by_day = []

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
            box_x_header = margin
            box_width_header = width - 2 * margin
            box_y_header = y_position - box_height
            draw_rounded_box_with_color(pdf, box_x_header, box_y_header, box_width_header, box_height, stroke_rgb_color=cfg_gen_header["box_stroke_color_rgb"], sides='all') # L'en-tête général est un cadre complet
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
                note_text = "Note : ____________"
                note_x = (width - margin - 10 - pdf.stringWidth(note_text, cfg_gen_header["text_font_name"], cfg_gen_header["text_font_size"]))
                pdf.drawString(note_x, y_header_text, note_text)
            y_position = box_y_header - cfg_gen_header["y_offset_after_box"]
        else:
            y_position -= cfg_gen_header["y_offset_no_header"]

        pdf.setFont(cfg_def_font["name"], cfg_def_font["size"])
        pdf.setFillColorRGB(*cfg_def_font["color_rgb"])

        current_day_conjugations = conjugations[day-1] if conjugations and len(conjugations) >= day else None
        current_day_complete_sentence = conj_complete_sentence_exercises[day-1] if conj_complete_sentence_exercises and len(conj_complete_sentence_exercises) >= day else None
        current_day_complete_pronoun = conj_complete_pronoun_exercises[day-1] if conj_complete_pronoun_exercises and len( conj_complete_pronoun_exercises) >= day else None

        section_num = 1
        pdf._ortho_homophone_title_drawn = False # Reset flag for the current day's Orthographe section

        current_day_story_problems = story_math_problems_by_day[day-1] if len(story_math_problems_by_day) >= day else None

        # Section Calculs
        if ((enumerate_exercises and len(enumerate_exercises) >= day and enumerate_exercises[day-1]) or any(counts)or current_day_story_problems):
            cfg_calc_enum = PDF_STYLE_CONFIG["enumerate_numbers"]
            cfg_calc_ops = PDF_STYLE_CONFIG["calc_operations"]

            section_key = "Calculs"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.2, 0.4, 0.8))

            first_block_content_height = 0
            if enumerate_exercises and len(enumerate_exercises) >= day and enumerate_exercises[day-1]:
                first_block_content_height = (cfg_calc_enum["line_spacing_after_title"] + cfg_calc_enum["line_spacing_per_item"] + cfg_calc_enum["spacing_after_section"])
            elif current_day_story_problems:
                first_block_content_height = 10 + 6 + 9 + 4 + 9 + 13
            elif any(counts):
                first_block_content_height = 13 + 22 + 8

            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin

            current_frame_segment_top_y = y_position

            # Draw top of frame
            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])

            y_position_for_content, exercise_content_x_start = draw_section_header(pdf, current_frame_segment_top_y, section_key, section_num, margin, width)
            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin) 
            y_position = y_position_for_content
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
                        # Close previous frame segment
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        # Draw top of new frame segment
                        draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_calc_enum["content_font_name"], cfg_calc_enum["content_font_size"])
                y_position -= cfg_calc_enum["spacing_after_section"]

            if any(counts):
                pdf.setFont(cfg_calc_ops["title_font_name"], cfg_calc_ops["title_font_size"])
                for i, operation in enumerate(operations):
                    params = params_list[i]
                    problems = generate_arithmetic_problems(operation, params)
                    pdf.drawString(exercise_content_x_start, y_position, f"{operation.capitalize()} :")
                    y_position -= cfg_calc_ops["line_spacing_after_title"]
                    pdf.setFont( cfg_calc_ops["content_font_name"], cfg_calc_ops["content_font_size"])
                    for problem in problems:
                        calc_str = problem.strip().replace(' =', '')
                        pdf.drawString(exercise_content_x_start, y_position, f"{calc_str} = _____________________________________________")
                        y_position -= cfg_calc_ops["line_spacing_per_item"]
                        if y_position < margin:
                            # Close previous frame segment
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            # Draw top of new frame segment
                            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont(cfg_calc_ops["content_font_name"], cfg_calc_ops["content_font_size"])
                    pdf.setFont(cfg_calc_ops["title_font_name"], cfg_calc_ops["title_font_size"])
                y_position -= cfg_calc_ops["spacing_after_section"]

            if current_day_story_problems:
                original_font_calc, original_size_calc = pdf._fontname, pdf._fontsize
                original_fill_color_obj = pdf._fillColorObj
                current_frame_top_y_list[0] = current_frame_segment_top_y
                y_position = draw_canvas_story_problems(pdf, y_position, current_day_story_problems, exercise_content_x_start, margin, width, height, current_frame_top_y_list, section_data, section_color_rgb)
                current_frame_segment_top_y = current_frame_top_y_list[0]
                pdf.setFont(original_font_calc, original_size_calc)
                pdf.setFillColor(original_fill_color_obj)

            box_actual_bottom_y = (y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"])
            draw_rounded_box_with_color(pdf, margin, box_actual_bottom_y, width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        # Section Mesures
        current_day_encadrement_lines = encadrement_exercises_list[day-1] if len(encadrement_exercises_list) >= day else None

        has_mesures_content_for_day = False
        if current_day_encadrement_lines:
            has_mesures_content_for_day = True
        current_day_compare_numbers = compare_numbers_exercises_list[day-1] if compare_numbers_exercises_list and len(compare_numbers_exercises_list) >= day else None
        if current_day_compare_numbers:
            has_mesures_content_for_day = True
        current_day_logical_sequences = logical_sequences_exercises_list[day-1] if logical_sequences_exercises_list and len(logical_sequences_exercises_list) >= day else None
        if current_day_logical_sequences:
            has_mesures_content_for_day = True

        if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]:
            has_mesures_content_for_day = True
        if sort_exercises and len(sort_exercises) >= day and sort_exercises[day-1]:
            has_mesures_content_for_day = True

        current_day_measurement_problems = measurement_problems[day-1] if len(measurement_problems) >= day else None
        if current_day_measurement_problems:
            has_mesures_content_for_day = True
        if has_mesures_content_for_day:
            cfg_mes_conv = PDF_STYLE_CONFIG["measures_conversions"]
            cfg_mes_sort = PDF_STYLE_CONFIG["measures_sort"]
            cfg_mes_enc = PDF_STYLE_CONFIG["measures_encadrement"]

            section_key = "Mesures"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.2, 0.6, 0.3))

            first_block_content_height = 0
            if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]:
                first_block_content_height = (cfg_mes_conv["line_spacing_after_title"] + cfg_mes_conv["line_spacing_per_item"] + cfg_mes_conv["spacing_after_section"])
            elif sort_exercises and len(sort_exercises) >= day and sort_exercises[day-1]:
                first_block_content_height = (cfg_mes_sort["line_spacing_after_title"] + cfg_mes_sort["line_spacing_per_item"] + cfg_mes_sort["spacing_after_section"])
            elif current_day_encadrement_lines:
                first_block_content_height = 16 + 22 + 8
            elif current_day_compare_numbers:
                first_block_content_height = 16 + 22 + 8
            elif current_day_logical_sequences:
                first_block_content_height = 16 + 22 + 8
            elif current_day_measurement_problems:
                first_block_content_height = 10 + 6 + 9 + 4 + 9 + 13 # Estimate for story problems

            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin
            current_frame_segment_top_y = y_position
            # Draw top of frame
            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
            y_position_for_content, exercise_content_x_start = draw_section_header(pdf, current_frame_segment_top_y, section_key, section_num, margin, width)
            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
            y_position = y_position_for_content
            section_num += 1

            pdf.setFont(cfg_def_font["name"], cfg_def_font["size"])
            if geo_exercises and len(geo_exercises) >= day and geo_exercises[day-1]:
                current_day_geo_exercises = geo_exercises[day-1]
                if current_day_geo_exercises:
                    pdf.setFont(cfg_mes_conv["title_font_name"], cfg_mes_conv["title_font_size"])
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
                            # Close previous frame segment
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            # Draw top of new frame segment
                            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
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
                        numbers_str = ", ".join(str(n)
                                                for n in ex_sort['numbers'])
                        pdf.drawString(exercise_content_x_start, y_position, f"{numbers_str} = _____________________________________________")
                        y_position -= cfg_mes_sort["line_spacing_per_item"]
                        if y_position < margin:
                            # Close previous frame segment
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            # Draw top of new frame segment
                            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                            draw_section_image_in_frame(
                                pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont(cfg_mes_sort["content_font_name"], cfg_mes_sort["content_font_size"])
                    y_position -= cfg_mes_sort["spacing_after_section"]

            if current_day_encadrement_lines:
                pdf.setFont(cfg_mes_enc["title_font_name"], cfg_mes_enc["title_font_size"])
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
                        # Close previous frame segment
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        # Draw top of new frame segment
                        draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                y_position -= cfg_mes_enc["spacing_after_section"]

            if current_day_compare_numbers:
                pdf.setFont(cfg_mes_enc["title_font_name"], cfg_mes_enc["title_font_size"])
                pdf.drawString(exercise_content_x_start, y_position,"Compare les nombres (<, >, =) :")
                y_position -= cfg_mes_enc["line_spacing_after_title"]
                pdf.setFont(cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                for ex_compare in current_day_compare_numbers:
                    pdf.drawString(exercise_content_x_start, y_position, f"{ex_compare['num1']} ______ {ex_compare['num2']}")
                    y_position -= cfg_mes_enc["line_spacing_per_item"]
                    if y_position < margin:
                        # Close previous frame segment
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        # Draw top of new frame segment
                        draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                y_position -= cfg_mes_enc["spacing_after_section"]

            if current_day_logical_sequences:
                pdf.setFont(cfg_mes_enc["title_font_name"], cfg_mes_enc["title_font_size"])
                if len(current_day_logical_sequences) == 1:
                    title_text_seq = "Complète la suite logique :"
                else:
                    title_text_seq = "Complète les suites logiques :"
                pdf.drawString(exercise_content_x_start, y_position, title_text_seq)
                y_position -= cfg_mes_enc["line_spacing_after_title"]
                pdf.setFont(cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                for ex_seq in current_day_logical_sequences:
                    sequence_str = ", ".join( map(str, ex_seq['sequence_displayed']))
                    pdf.drawString(exercise_content_x_start, y_position, f"{sequence_str}")
                    y_position -= cfg_mes_enc["line_spacing_per_item"]
                    if y_position < margin:
                        # Close previous frame segment
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        # Draw top of new frame segment
                        draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                        draw_section_image_in_frame( pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont( cfg_mes_enc["content_font_name"], cfg_mes_enc["content_font_size"])
                y_position -= cfg_mes_enc["spacing_after_section"]

            if current_day_measurement_problems:
                original_font_mes, original_size_mes = pdf._fontname, pdf._fontsize
                original_fill_color_obj_mes = pdf._fillColorObj
                current_frame_top_y_list = [current_frame_segment_top_y] # Re-initialize for this section
                y_position = draw_canvas_story_problems(pdf, y_position, current_day_measurement_problems, exercise_content_x_start, margin, width, height, current_frame_top_y_list, section_data, section_color_rgb)
                current_frame_segment_top_y = current_frame_top_y_list[0]
                pdf.setFont(original_font_mes, original_size_mes)
                pdf.setFillColor(original_fill_color_obj_mes)
            box_actual_bottom_y = (y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"])
            draw_rounded_box_with_color(pdf, margin, box_actual_bottom_y, width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        # Section Conjugaison
        if current_day_conjugations or current_day_complete_sentence or current_day_complete_pronoun:
            cfg_conj = PDF_STYLE_CONFIG["conjugation"]
            cfg_conj_comp = PDF_STYLE_CONFIG["conj_completer"]
            section_key = "Conjugaison"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.7, 0.3, 0.2))

            first_block_content_height = (cfg_conj["line_spacing_after_title"] + cfg_conj["line_spacing_before_pronouns"] + cfg_conj["line_spacing_per_pronoun"] + cfg_conj["spacing_after_verb_block"])
            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin

            current_frame_segment_top_y = y_position
            # Draw top of frame
            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
            y_position_for_content, exercise_content_x_start = draw_section_header(  pdf, current_frame_segment_top_y, section_key, section_num, margin, width)
            draw_section_image_in_frame( pdf, section_data, current_frame_segment_top_y, width, margin)
            y_position = y_position_for_content
            section_num += 1

            if current_day_conjugations:
                from conjugation_generator import PRONOUNS, VERBS
                for conjugation_item in current_day_conjugations:
                    verb = conjugation_item["verb"]
                    tense = conjugation_item["tense"]
                    groupe = None
                    for g_num_key in VERBS:
                        if isinstance(g_num_key, int) or str(g_num_key).isdigit():
                            if verb in VERBS[g_num_key]:
                                groupe = f"{g_num_key}er groupe"
                                break
                    if not groupe and "usuels" in VERBS and verb in VERBS["usuels"]:
                        groupe = "usuel"
                    if not groupe:
                        groupe = "inconnu"

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
                            # Close previous frame segment
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            # Draw top of new frame segment
                            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                            draw_section_image_in_frame(
                                pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont(cfg_conj["content_font_name"], cfg_conj["content_font_size"])
                    y_position -= cfg_conj["spacing_after_verb_block"] # Spacing between individual verb blocks
                    y_position -= cfg_conj["spacing_after_last_verb_block"] # Spacing after the last verb block

            # Compléter les phrases
            if current_day_complete_sentence:
                pdf.setFont(cfg_conj_comp["title_font_name"], cfg_conj_comp["title_font_size"])
                if len(current_day_complete_sentence) == 1:
                    title_text = "Complète la phrase en conjuguant le verbe :"
                else:
                    title_text = "Complète les phrases en conjuguant les verbes :"
                pdf.drawString(exercise_content_x_start, y_position, title_text)
                y_position -= cfg_conj_comp["line_spacing_after_title"]
                pdf.setFont(cfg_conj_comp["content_font_name"], cfg_conj_comp["content_font_size"]) # Reset font for content
                for ex in current_day_complete_sentence:
                    pdf.drawString(exercise_content_x_start, y_position, ex['content'] + " (Temps: " + ex['tense'].capitalize() + ")")
                    y_position -= cfg_conj_comp["line_spacing_per_item"]
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_conj_comp["content_font_name"], cfg_conj_comp["content_font_size"])
                y_position -= cfg_conj_comp["spacing_after_section"] # Spacing after this block

            # Compléter les pronoms
            if current_day_complete_pronoun:
                pdf.setFont(cfg_conj_comp["title_font_name"], cfg_conj_comp["title_font_size"])
                if len(current_day_complete_pronoun) == 1:
                    title_text = "Complète la phrase avec le pronom qui convient :"
                else:
                    title_text = "Complète les phrases avec le pronom qui convient :"
                pdf.drawString(exercise_content_x_start, y_position, title_text)
                y_position -= cfg_conj_comp["line_spacing_after_title"]
                pdf.setFont(cfg_conj_comp["content_font_name"], cfg_conj_comp["content_font_size"]) # Reset font for content
                for ex in current_day_complete_pronoun:
                    pdf.drawString(exercise_content_x_start, y_position, ex['content'])
                    y_position -= cfg_conj_comp["line_spacing_per_item"]
                    if y_position < margin:
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                        draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_conj_comp["content_font_name"], cfg_conj_comp["content_font_size"])

            box_actual_bottom_y = (y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"])
            draw_rounded_box_with_color(pdf, margin, box_actual_bottom_y, width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]
        # Section Grammaire
        if grammar_exercises and len(grammar_exercises) >= day and grammar_exercises[day-1]:
            cfg_gram = PDF_STYLE_CONFIG["grammar"]
            section_key = "Grammaire"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.5, 0.2, 0.7))

            first_block_content_height = (cfg_gram["line_spacing_per_line"] * 2 + cfg_gram["spacing_before_answer"] + cfg_gram["line_spacing_answer"] + cfg_gram["spacing_after_exercise_block"])
            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin

            current_frame_segment_top_y = y_position
            # Draw top of frame
            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
            y_position_for_content, exercise_content_x_start = draw_section_header( pdf, current_frame_segment_top_y, section_key, section_num, margin, width)
            draw_section_image_in_frame( pdf, section_data, current_frame_segment_top_y, width, margin)
            y_position = y_position_for_content
            section_num += 1

            pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])
            for ex in grammar_exercises[day-1]:
                phrase = ex['phrase']
                transformation = ex['transformation']
                pdf.setFont(cfg_gram["title_font_name"], cfg_gram["title_font_size"])
                pdf.drawString(exercise_content_x_start, y_position, "Phrase :")
                pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])
                pdf.drawString(exercise_content_x_start + 55, y_position, phrase)
                y_position -= cfg_gram["line_spacing_per_line"]
                if y_position < margin:
                    # Close previous frame segment
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    # Draw top of new frame segment
                    draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])

                pdf.setFont(cfg_gram["title_font_name"], cfg_gram["title_font_size"])
                pdf.drawString(exercise_content_x_start, y_position, "Transformation demandée :")
                pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])
                pdf.drawString(exercise_content_x_start + 130, y_position, transformation)
                y_position -= cfg_gram["line_spacing_per_line"]
                if y_position < margin:
                    # Close previous frame segment
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    # Draw top of new frame segment
                    draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                    draw_section_image_in_frame( pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])

                y_position -= cfg_gram["spacing_before_answer"]
                pdf.drawString(exercise_content_x_start, y_position, "Réponse : __________________________________________________________")
                y_position -= cfg_gram["line_spacing_answer"]
                y_position -= cfg_gram["spacing_after_exercise_block"]
                if y_position < margin:
                    # Close previous frame segment
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    # Draw top of new frame segment
                    draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                    draw_section_image_in_frame( pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont(cfg_gram["content_font_name"], cfg_gram["content_font_size"])

            box_actual_bottom_y = (y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"])
            draw_rounded_box_with_color(pdf, margin, box_actual_bottom_y, width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        # Section Orthographe
        if orthographe_exercises and len(orthographe_exercises) >= day and orthographe_exercises[day-1]:
            cfg_ortho = PDF_STYLE_CONFIG["orthographe_homophones"]
            section_key = "Orthographe"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (1.0, 0.7, 0.0))

            first_block_content_height = (cfg_ortho["line_spacing_per_item"] + cfg_ortho["spacing_after_item"])
            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin
            current_frame_segment_top_y = y_position
            # Draw top of frame
            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
            y_position_for_content, exercise_content_x_start = draw_section_header( pdf, current_frame_segment_top_y, section_key, section_num, margin, width)
            draw_section_image_in_frame( pdf, section_data, current_frame_segment_top_y, width, margin)
            y_position = y_position_for_content
            section_num += 1

            pdf.setFont(cfg_ortho["content_font_name"], cfg_ortho["content_font_size"])
            for ex in orthographe_exercises[day-1]:
                # Filter homophone exercises for the day
                homophone_exercises_for_day = [e for e in orthographe_exercises[day-1] if e['type'] == 'homophone']

                # Draw the main title for homophones once per section
                if homophone_exercises_for_day and not pdf._ortho_homophone_title_drawn:
                    if len(homophone_exercises_for_day) == 1: # Check length of filtered list
                        exercise_title = "Complète l'homophone :"
                    else:
                        exercise_title = "Complète les homophones :"

                    pdf.setFont(cfg_ortho["title_font_name"], cfg_ortho["title_font_size"])
                    pdf.drawString(exercise_content_x_start, y_position, exercise_title)
                    y_position -= cfg_ortho["line_spacing_after_title"] # Use the dedicated spacing after title
                    pdf.setFont(cfg_ortho["content_font_name"], cfg_ortho["content_font_size"]) # Reset font for content
                    pdf._ortho_homophone_title_drawn = True # Set flag to true after drawing

                if ex['type'] == 'homophone':
                    pdf.setFont(cfg_ortho["title_font_name"], cfg_ortho["title_font_size"]) # Set font for homophone
                    pdf.drawString(exercise_content_x_start, y_position, f"{ex['homophone']} :")  # Draw the homophone
                    pdf.setFont(cfg_ortho["content_font_name"], cfg_ortho["content_font_size"])
                    pdf.drawString(exercise_content_x_start + 60, y_position, ex['content'])
                    y_position -= cfg_ortho["line_spacing_per_item"]
                    y_position -= cfg_ortho["spacing_after_item"]
                if y_position < margin:
                    # Close previous frame segment
                    draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    # Draw top of new frame segment
                    draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                    draw_section_image_in_frame( pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont(cfg_ortho["content_font_name"], cfg_ortho["content_font_size"])

            box_actual_bottom_y = (y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"])
            draw_rounded_box_with_color(pdf, margin, box_actual_bottom_y, width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        # Section Anglais
        if english_exercises and len(english_exercises) >= day and english_exercises[day-1]:
            cfg_eng_comp = PDF_STYLE_CONFIG["english_completer"]
            cfg_eng_rel = PDF_STYLE_CONFIG["english_relier"]
            section_key = "Anglais"
            section_data = SECTION_ASSETS.get(section_key, {})
            section_color_rgb = section_data.get("color", (0.2, 0.6, 0.7))

            first_block_content_height = 0
            if english_exercises[day-1]:
                first_ex = english_exercises[day-1][0]
                if first_ex['type'] in ('simple', 'complexe'):
                    first_block_content_height = (cfg_eng_comp["line_spacing_after_title"] + cfg_eng_comp["spacing_before_first_item"] + cfg_eng_comp["line_spacing_per_item"] + cfg_eng_comp["spacing_after_item"])
                elif first_ex['type'] == 'relier':
                    first_block_content_height = (cfg_eng_rel["line_spacing_after_title"] + cfg_eng_rel["spacing_before_first_item"] + cfg_eng_rel["line_spacing_per_item"] + cfg_eng_rel["spacing_after_block"])
            required_height_for_first_block = HEADER_HEIGHT_ESTIMATE + first_block_content_height

            if y_position - required_height_for_first_block < margin:
                pdf.showPage()
                y_position = height - margin
            current_frame_segment_top_y = y_position
            # Draw top of frame
            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
            y_position_for_content, exercise_content_x_start = draw_section_header( pdf, current_frame_segment_top_y, section_key, section_num, margin, width)
            draw_section_image_in_frame( pdf, section_data, current_frame_segment_top_y, width, margin)
            y_position = y_position_for_content
            section_num += 1

            pdf.setFont(cfg_def_font["name"], cfg_def_font["size"])
            completer_shown = False
            for ex_idx, ex in enumerate(english_exercises[day-1]):
                # Count completer exercises for the current day
                completer_exercises_for_day = [e for e in english_exercises[day-1] if e['type'] in ('simple', 'complexe')]

                if ex['type'] in ('simple', 'complexe'):
                    if not completer_shown:
                        if len(completer_exercises_for_day) == 1:
                            completer_title_text = "Complète la phrase :"
                        else:
                            completer_title_text = "Complète les phrases :"
                        pdf.setFont( cfg_eng_comp["title_font_name"], cfg_eng_comp["title_font_size"])
                        pdf.drawString(exercise_content_x_start, y_position, completer_title_text)
                        pdf.setFont( cfg_eng_comp["content_font_name"], cfg_eng_comp["content_font_size"])
                        y_position -= cfg_eng_comp["line_spacing_after_title"]
                        completer_shown = True
                        y_position -= cfg_eng_comp["spacing_before_first_item"]
                        if y_position < margin:
                            # Close previous frame segment
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            # Draw top of new frame segment
                            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                            draw_section_image_in_frame( pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont( cfg_eng_comp["content_font_name"], cfg_eng_comp["content_font_size"])

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
                        # Close previous frame segment
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                        pdf.showPage()
                        y_position = height - margin
                        current_frame_segment_top_y = y_position
                        # Draw top of new frame segment
                        draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                        draw_section_image_in_frame( pdf, section_data, current_frame_segment_top_y, width, margin)
                        pdf.setFont(cfg_eng_rel["content_font_name"], cfg_eng_rel["content_font_size"])

                    mots = ex['content']
                    anglais_words = [m['english'] for m in mots]
                    francais_words = [m['french'] for m in mots]
                    random.shuffle(anglais_words)

                    max_len = max(len(anglais_words), len(francais_words))
                    x_anglais = (exercise_content_x_start + cfg_eng_rel["x_offset_anglais"])
                    x_bullet1 = (exercise_content_x_start + cfg_eng_rel["x_offset_bullet1"])
                    x_bullet2 = (x_bullet1 + cfg_eng_rel["x_offset_bullet2_from_bullet1"])
                    x_francais = (x_bullet2 + cfg_eng_rel["x_offset_francais_from_bullet2"])

                    for i in range(max_len):
                        a = anglais_words[i] if i < len(anglais_words) else ''
                        f = francais_words[i] if i < len(
                            francais_words) else ''
                        pdf.drawString(x_anglais, y_position, a)
                        pdf.drawString(x_bullet1, y_position, '\u2022')
                        pdf.drawString(x_bullet2, y_position, '\u2022')
                        pdf.drawString(x_francais, y_position, f)
                        y_position -= cfg_eng_rel["line_spacing_per_item"]
                        if y_position < margin:
                            # Close previous frame segment
                            draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                            pdf.showPage()
                            y_position = height - margin
                            current_frame_segment_top_y = y_position
                            # Draw top of new frame segment
                            draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                            draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                            pdf.setFont(cfg_eng_rel["content_font_name"], cfg_eng_rel["content_font_size"])
                    y_position -= cfg_eng_rel["spacing_after_block"]

                if y_position < margin and ex_idx < len(english_exercises[day-1]) - 1:
                    if not (y_position == height - margin and current_frame_segment_top_y == y_position):
                        # Close previous frame segment
                        draw_rounded_box_with_color(pdf, margin, margin, width - 2 * margin, current_frame_segment_top_y - margin, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
                    pdf.showPage()
                    y_position = height - margin
                    current_frame_segment_top_y = y_position
                    # Draw top of new frame segment
                    draw_rounded_box_with_color(pdf, margin, y_position, width - 2 * margin, 0, stroke_rgb_color=section_color_rgb, sides=['top'])
                    draw_section_image_in_frame(pdf, section_data, current_frame_segment_top_y, width, margin)
                    pdf.setFont(cfg_def_font["name"], cfg_def_font["size"])

            box_actual_bottom_y = (y_position - PDF_STYLE_CONFIG["section_frame"]["content_bottom_padding"])
            draw_rounded_box_with_color(pdf, margin, box_actual_bottom_y, width - 2 * margin, current_frame_segment_top_y - box_actual_bottom_y, stroke_rgb_color=section_color_rgb, sides=['bottom', 'left', 'right'])
            y_position = box_actual_bottom_y - PDF_STYLE_CONFIG["section_frame"]["y_offset_after_box"]

        if day < days:
            pdf.showPage()

    pdf.save()
    print(f"PDF généré : {out_path}")
    return out_path
