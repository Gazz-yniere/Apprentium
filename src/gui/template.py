UI_STYLE_CONFIG = {
    "palette": {
        "window": (30, 30, 30),
        "window_text": (255, 255, 255),
        "base": (20, 20, 20),
        "alternate_base": (30, 30, 30),
        "tooltip_base": (255, 255, 255),
        "tooltip_text": (255, 255, 255),
        "text": (255, 255, 255),
        "button": (45, 45, 45),
        "button_text": (255, 255, 255),
        "bright_text": (255, 0, 0),
        "highlight": (0, 120, 215),
        "highlighted_text": (0, 0, 0),
    },
    "window": {
        "minimum_width": 1400,
        "minimum_height": 900,
    },
    "labels": {
        "header_label":       "font-weight: bold; font-size: 16px; color: #E0E0E0; margin-right: 10px;",
        "days_label":         "font-weight: bold; font-size: 16px; color: #E0E0E0;",
        "level_selection":    "font-weight: bold; font-size: 16px; color: #E0E0E0; margin-right: 10px;",
        "column_title_base":  "font-weight: bold; font-size: 20px; margin-bottom: 8px; margin-top: 0px;",
        "column_title_colors": {
            # Bleu clair, Violet clair, Vert clair
            "calc":      "#4FC3F7", "geo":       "#BA68C8", "conj":      "#81C784",
            # Jaune/Or, Orange, Sarcelle (Teal)
            "grammar":   "#FFD54F", "ortho":     "#FFB300", "english":   "#4DB6AC",
        },
        # Style pour la plupart des labels de champ
        "field_label":        "color: #e0e0e0; font-size: 14px; font-weight: normal;",
        # Harmonisé avec field_label
        "filename_label":     "font-weight: bold; font-size: 16px; color: #E0E0E0;",
        "output_path_display_default": "font-style: italic; color: #B0BEC5;",
        "output_path_display_set": "font-style: normal; color: #E0E0E0;",
        # NOUVEAUX STYLES POUR LE FOOTER :
        "footer_label":       "font-size: 11px; color: #B0BEC5; margin-left: 5px;",
        "version_label":      "font-size: 11px; color: #B0BEC5; margin-right: 5px;",
    },
    "line_edits": {
        "default":            "color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;",
        "days_invalid_border": "border: 2px solid red;",
        "header_placeholder": "Optionnel",
    },
    "group_boxes": {
        "base_style_template": "QGroupBox {{ margin-top: 2px; margin-bottom: 2px; padding: 5px 6px 5px 6px; border: 3px solid {border_color}; border-radius: 15px; }} QGroupBox:title {{ font-size: 15px; color: {border_color}; background: #232323; subcontrol-origin: margin; subcontrol-position: top left; left: 15px; top: -4px; padding: 0 12px; font-weight: bold; }}",
        "border_colors": {  # Mêmes clés que column_title_colors pour la cohérence
            # Bleu clair, Violet clair, Vert clair
            "calc":      "#4FC3F7", "geo":       "#BA68C8", "conj":      "#81C784",
            # Jaune/Or, Orange, Sarcelle (Teal)
            "grammar":   "#FFD54F", "ortho":     "#FFB300", "english":   "#4DB6AC",
        }
    },
    "buttons": {
        "level_button_base_style_template": """
            QPushButton {{
                color: {text_color}; font-weight: bold; font-size: 14px;
                padding: 6px 15px; border-radius: 8px; border: none;
                background-color: {bg_color};
            }}
            QPushButton:hover {{ background-color: {hover_bg_color}; }}
            QPushButton:pressed {{ background-color: {pressed_bg_color}; }}
            QPushButton[selected="true"] {{ padding: 6px 15px; }}
        """,
        "level_button_text_color": "black",
        "level_colors": {  # Couleurs de fond pour les boutons de niveau
            "CP":  "#EF9A9A",  # Rouge clair (était CM2)
            "CE1": "#FFCC80",  # Orange clair (était CE2)
            "CE2": "#FFFACD",  # Jaune clair (LemonChiffon)
            "CM1": "#A5D6A7",  # Vert clair (était CP)
            "CM2": "#90CAF9"   # Bleu clair (était CE1)
        },
        "action_button_base_style_template": """
            QPushButton {{
                background-color: {bg_color}; color: white; font-weight: bold;
                font-size: 16px; padding: 8px 20px; border-radius: 8px;
            }}
            QPushButton:disabled {{ background-color: {disabled_bg_color}; color: {disabled_text_color}; }}
            QPushButton:pressed {{ background-color: {pressed_bg_color}; }}
        """,  # Garder la virgule ici si d'autres clés suivent au même niveau
        "pdf":            {"bg_color": "#FF7043", "pressed_bg_color": "#d84315"},  # Orange/Rouge
        # Bleu
        "word":           {"bg_color": "#1976D2", "pressed_bg_color": "#0d47a1"},
        # Vert pour "Choisir dossier"
        "select_folder":  {"bg_color": "#66BB6A", "pressed_bg_color": "#388E3C"},
        # Pastel Orange/Rouge
        "preview_pdf":    {"bg_color": "#FFAB91", "pressed_bg_color": "#FF8A65"},
        # Pastel Bleu
        "preview_word":   {"bg_color": "#90CAF9", "pressed_bg_color": "#64B5F6"},
        # Conservé au cas où, mais moins utilisé
        "preview_path":   {"bg_color": "#78909C", "pressed_bg_color": "#546E7A"},
        "disabled":     {"bg_color": "#cccccc", "text_color": "#888888"},
    },
    "separators": {
        "style": "border-top: 3px solid #505050;"
    },
    "scroll_bar": {
        "style_template": """
            QScrollBar:vertical {{
                border: none; background: {background_color}; width: {width}px; margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {handle_background_color}; min-height: {handle_min_height}px;
                border-radius: {handle_border_radius}px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none; background: none; height: 0px;
                subcontrol-position: top; subcontrol-origin: margin;
            }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{ background: none; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        """,
        "values": {
            "background_color": "#2E2E2E", "width": 12,
            "handle_background_color": "#555555", "handle_min_height": 20, "handle_border_radius": 6,
        }
    }
}