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
        "number_in_circle_font_size": 12,
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
    "story_problems":         {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "answer_font_name": "Helvetica", "answer_font_size": 10, "line_spacing_after_section_title": 10, "line_spacing_between_wrapped_lines": 3, "line_spacing_after_problem_text_block": 6, "line_spacing_after_answer_line": 11, "final_spacing_after_section": 8, },
    "calc_operations":        {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_after_title": 16, "line_spacing_per_item": 16, "spacing_after_section": 3,},
    "enumerate_numbers":      {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_after_title": 16, "line_spacing_per_item": 16, "spacing_after_section": 6,},
    "measures_conversions":   {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 5, },
    "measures_sort":          {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 8, },
    "measures_encadrement":   {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 8, },
    "conjugation":            {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_after_title": 10, "line_spacing_before_pronouns": 10, "line_spacing_per_pronoun": 16,"spacing_after_verb_block": 5, "spacing_after_last_verb_block": 10, "spacing_between_exercise_types": 15, }, # noqa E501
    "conj_completer":         {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_after_title": 16, "line_spacing_per_item": 22, "spacing_after_section": 8, }, # noqa E501
    "grammar":                {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_per_line": 13, "spacing_before_answer": 10, "line_spacing_answer": 22, "spacing_after_exercise_block": 10, }, # noqa E501
    "orthographe_homophones": {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_after_title": 16, "line_spacing_per_item": 16, "spacing_after_item": 10, }, # noqa E501
    "english_completer":      {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_after_title": 10, "spacing_before_first_item": 10, "line_spacing_per_item": 13, "spacing_after_item": 10, }, # noqa E501
    "english_relier":         {"title_font_name": "Helvetica-Bold", "title_font_size": 10, "content_font_name": "Helvetica", "content_font_size": 10, "line_spacing_after_title": 10, "spacing_before_first_item": 10, "line_spacing_per_item": 13, "spacing_after_block": 10, "x_offset_anglais": 0, "x_offset_bullet1": 75, "x_offset_bullet2_from_bullet1": 50, "x_offset_francais_from_bullet2": 20, }, # noqa E501
    "default_font":           {"name": "Helvetica", "size": 10, "color_rgb": (0, 0, 0)}
}

# Estimation de la hauteur de l'en-tête de section (numéro+titre)
cfg_sh = PDF_STYLE_CONFIG["section_header"]
# This estimate is for the total vertical space consumed by the header, from its highest point to the point where the content starts inside the frame.
HEADER_HEIGHT_ESTIMATE = (cfg_sh["overlap_offset"] + cfg_sh["circle_radius"] + cfg_sh["bg_padding_top"] + cfg_sh["content_top_padding"])