from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QFrame, QGroupBox, QSplitter, QFileDialog, QLayout, QGraphicsOpacityEffect, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor
from calculs_generator import generate_story_math_problems
import json
import os # Added for path joining and os.startfile

import sys


class InvalidFieldError(Exception):
    def __init__(self, field_name, value):
        super().__init__(
            f"Champ '{field_name}' invalide : '{value}' n'est pas un nombre valide.")
        self.field_name = field_name
        self.value = value

__version__ = "0.25.6e" # Version de l'application


def get_resource_path(filename):
    """ Obtient le chemin absolu d'une ressource JSON, que ce soit en mode script ou compilé. """
    # base_path = os.path.dirname(__file__) # Chemin du script Apprentium.py
    if hasattr(sys, '_MEIPASS'):
        # Chemin pour l'exécutable PyInstaller (le dossier 'json' est au même niveau que l'exécutable)
        return os.path.join(sys._MEIPASS, "json", filename)
    # Chemin pour l'exécution en tant que script (le dossier 'json' est dans le même dossier que ce script)
    return os.path.join(os.path.dirname(__file__), "json", filename)


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apprentium")
        # Assurez-vous que le chemin est correct
        icon_path = os.path.join(os.path.dirname(__file__), "Apprentium.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumWidth(UI_STYLE_CONFIG["window"]["minimum_width"])
        self.setMinimumHeight(UI_STYLE_CONFIG["window"]["minimum_height"])

        # --- Constants for Level Selection ---
        # Récupère depuis la config
        self.LEVEL_COLORS = UI_STYLE_CONFIG["buttons"]["level_colors"]
        self.BASE_LEVEL_BUTTON_STYLE = UI_STYLE_CONFIG["buttons"]["level_button_base_style_template"]

        self.GITHUB_URL = "https://github.com/Gazz-yniere/Apprentium/releases" # MODIFIEZ CECI

        self.current_selected_level_button = None
        self.current_level = None  # To store the string name of the level

        self._all_row_widgets_for_map = {}  # Pour accumuler les widgets de ligne
        self.selected_output_path = None  # Pour stocker le chemin choisi par l'utilisateur
        self.all_line_edits = []  # Liste pour stocker tous les QLineEdit à styler

        # --- Chargement de la configuration des niveaux ---
        self.level_configuration_data = {}
        default_level_order = ["CP", "CE1", "CE2", "CM1", "CM2"]
        default_exercises_by_level = {}  # Fallback vide
        try:
            levels_config_path = get_resource_path('levels_config.json')
            with open(levels_config_path, 'r', encoding='utf-8') as f:
                self.level_configuration_data = json.load(f)
            # print(f"Configuration des niveaux chargée depuis : {levels_config_path}")
        except FileNotFoundError:
            print(
                f"ERREUR: Fichier de configuration des niveaux '{levels_config_path}' introuvable. Utilisation des valeurs par défaut.")
        except json.JSONDecodeError:
            print(
                f"ERREUR: Fichier de configuration des niveaux '{levels_config_path}' JSON invalide. Utilisation des valeurs par défaut.")

        self.LEVEL_ORDER = self.level_configuration_data.get(
            "level_order", default_level_order)
        self.EXERCISES_BY_LEVEL_INCREMENTAL = self.level_configuration_data.get(
            "exercises_by_level", default_exercises_by_level)

        # --- Chargement des thèmes pour l'anglais ---
        self.english_relier_themes = {}
        try:
            mots_relier_path = get_resource_path('mots_a_relier.json')
            with open(mots_relier_path, 'r', encoding='utf-8') as f:
                self.english_relier_themes = json.load(
                    f)  # Charge le dict des thèmes
        except Exception as e:
            print(
                f"ERREUR: Impossible de charger les thèmes depuis '{mots_relier_path}': {e}")
        # Fenêtre redimensionnable

        # --- Chargement des types de problèmes mathématiques ---
        self.math_problem_types_data = {}
        try:
            problemes_maths_path = get_resource_path('problemes_maths.json')
            with open(problemes_maths_path, 'r', encoding='utf-8') as f:
                self.math_problem_types_data = json.load(f)
        except Exception as e:
            print(
                f"ERREUR: Impossible de charger les types de problèmes mathématiques: {e}")

        # Mode dark
        dark_palette = QPalette()
        cfg_palette = UI_STYLE_CONFIG["palette"]
        dark_palette.setColor(QPalette.ColorRole.Window,
                              QColor(*cfg_palette["window"]))
        dark_palette.setColor(QPalette.ColorRole.WindowText,
                              QColor(*cfg_palette["window_text"]))
        dark_palette.setColor(QPalette.ColorRole.Base,
                              QColor(*cfg_palette["base"]))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(
            *cfg_palette["alternate_base"]))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase,
                              QColor(*cfg_palette["tooltip_base"]))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText,
                              QColor(*cfg_palette["tooltip_text"]))
        dark_palette.setColor(QPalette.ColorRole.Text,
                              QColor(*cfg_palette["text"]))
        dark_palette.setColor(QPalette.ColorRole.Button,
                              QColor(*cfg_palette["button"]))
        dark_palette.setColor(QPalette.ColorRole.ButtonText,
                              QColor(*cfg_palette["button_text"]))
        dark_palette.setColor(QPalette.ColorRole.BrightText,
                              QColor(*cfg_palette["bright_text"]))
        dark_palette.setColor(QPalette.ColorRole.Highlight,
                              QColor(*cfg_palette["highlight"]))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(
            *cfg_palette["highlighted_text"]))
        QApplication.instance().setPalette(dark_palette)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Partie supérieure : En-tête et Nombre de jours
        top_layout = QHBoxLayout()  # Layout principal pour cette ligne
        # Harmonisation avec level_selection_layout
        top_layout.setContentsMargins(10, 5, 10, 5)

        # Section En-tête (à gauche)
        header_section_layout = QHBoxLayout()
        self.header_label = QLabel("Titre :")
        self.header_label.setStyleSheet(
            UI_STYLE_CONFIG["labels"]["header_label"])
        self.header_entry = QLineEdit()
        self.all_line_edits.append(self.header_entry)
        self.header_entry.setPlaceholderText(
            UI_STYLE_CONFIG["line_edits"]["header_placeholder"])
        # Style appliqué globalement plus tard
        # Donner une largeur minimale pour la visibilité
        self.header_entry.setMinimumWidth(250)
        self.show_name_checkbox = QCheckBox("Afficher Nom")
        self.show_note_checkbox = QCheckBox("Afficher Note")

        header_section_layout.addWidget(self.header_label)
        header_section_layout.addWidget(self.header_entry)
        header_section_layout.addWidget(self.show_name_checkbox)
        header_section_layout.addWidget(self.show_note_checkbox)
        header_section_layout.setSpacing(10)

        top_layout.addLayout(header_section_layout)
        top_layout.addStretch()  # Pousse la section "jours" vers la droite

        # Section Nombre de jours (à droite)
        days_section_layout = QHBoxLayout()
        self.days_label = QLabel("Nombre de jours :")
        self.days_label.setStyleSheet(UI_STYLE_CONFIG["labels"]["days_label"])
        self.days_entry = QLineEdit()
        self.all_line_edits.append(self.days_entry)
        self.days_entry.setMaximumWidth(60)

        days_section_layout.addWidget(self.days_label)
        days_section_layout.addWidget(self.days_entry)
        # Ajouter un stretch *après* les widgets pour les garder compacts à gauche de ce layout
        days_section_layout.addStretch(1)
        days_section_layout.setSpacing(5)

        top_layout.addLayout(days_section_layout)
        main_layout.addLayout(top_layout)

        # Séparateur
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setFrameShadow(QFrame.Shadow.Sunken)
        sep1.setStyleSheet(UI_STYLE_CONFIG["separators"]["style"])
        main_layout.addWidget(sep1)

        # --- Level Selection ---
        level_selection_layout = QHBoxLayout()
        level_selection_layout.setContentsMargins(10, 5, 10, 5)
        level_selection_label = QLabel("Niveau :")
        level_selection_label.setStyleSheet(
            UI_STYLE_CONFIG["labels"]["level_selection"])
        level_selection_layout.addWidget(level_selection_label)

        self.level_buttons = {}
        # Utilise self.LEVEL_ORDER chargé depuis le JSON (ou la valeur par défaut)
        for level_name in self.LEVEL_ORDER:
            color_hex = self.LEVEL_COLORS[level_name]
            button = QPushButton(level_name)
            # Lighter hover for dark theme
            hover_color = self.darken_color(color_hex, 0.95)
            pressed_color = self.darken_color(color_hex, 0.85)
            # border_c = self.darken_color(color_hex, 0.7)

            button.setStyleSheet(self.BASE_LEVEL_BUTTON_STYLE.format(
                text_color=UI_STYLE_CONFIG["buttons"]["level_button_text_color"],
                bg_color=color_hex,
                hover_bg_color=hover_color,
                pressed_bg_color=pressed_color,
                # border_color=border_c # Plus utilisé car border: none
            ))
            button.setProperty("selected", False)
            button.clicked.connect(
                lambda checked, b=button, ln=level_name: self.select_level(ln, b))
            # Largeur fixe pour les boutons de niveau
            button.setFixedWidth(150)
            self.level_buttons[level_name] = button
            level_selection_layout.addWidget(button)

        level_selection_layout.addStretch()
        main_layout.addLayout(level_selection_layout)

        # Séparateur
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)
        sep2.setStyleSheet(UI_STYLE_CONFIG["separators"]["style"])
        main_layout.addWidget(sep2)

        # self.EXERCISES_BY_LEVEL_INCREMENTAL est maintenant chargé depuis le JSON
        # --- Colonne Calculs ---
        calc_layout = QVBoxLayout()
        self.calc_title_label = QLabel("Calculs")
        calc_title_style = UI_STYLE_CONFIG["labels"]["column_title_base"] + \
            f"color: {UI_STYLE_CONFIG['labels']['column_title_colors']['calc']};"
        self.calc_title_label.setStyleSheet(calc_title_style)
        calc_layout.addWidget(self.calc_title_label)
        calc_layout.setContentsMargins(5, 5, 5, 5)
        calc_layout.setSpacing(6)

        # Exercice : Enumérer un nombre
        enumerate_fields = [
            ("Nombre d'exercices :", "enumerate_count", 60),
            ("Chiffres par nombre :", "enumerate_digits", 60)
        ]
        self.enumerate_group, enumerate_les, enum_rows = self._create_generic_groupbox(
            "Enumérer un nombre", enumerate_fields)
        self.all_line_edits.extend(enumerate_les)
        self._all_row_widgets_for_map.update(enum_rows)

        # Addition
        addition_fields = [
            ("Nombre de calculs :", "addition_count", 60),
            # "opérande" au lieu de "nombre"
            ("Chiffres par opérande :", "addition_digits", 60),
            ("Nb décimales :", "addition_decimals", 60),
            ("Nombre d'opérandes :", "addition_num_operands", 60)  # Nouveau champ
        ]
        self.addition_group, addition_les, add_rows = self._create_generic_groupbox(
            "Addition", addition_fields)
        self.all_line_edits.extend(addition_les)
        self._all_row_widgets_for_map.update(add_rows)
        # Initialiser la valeur par défaut pour le nombre d'opérandes si le champ existe
        if hasattr(self, 'addition_num_operands'):
            self.addition_num_operands.setText("2")

        # Soustraction
        self.subtraction_negative_checkbox = QCheckBox(
            "Soustraction négative possible")
        subtraction_fields = [
            ("Nombre de calculs :", "subtraction_count", 60),
            ("Chiffres par opérande :", "subtraction_digits", 60),
            ("Nb décimales :", "subtraction_decimals", 60),
            ("Nombre d'opérandes :", "subtraction_num_operands", 60)  # Nouveau champ
        ]
        self.subtraction_group, subtraction_les, sub_rows = self._create_generic_groupbox(
            "Soustraction", subtraction_fields, extra_items=[self.subtraction_negative_checkbox]
        )
        self.all_line_edits.extend(subtraction_les)
        self._all_row_widgets_for_map.update(sub_rows)
        if hasattr(self, 'subtraction_num_operands'):
            self.subtraction_num_operands.setText("2")

        # Multiplication
        multiplication_fields = [
            # Clé: multiplication
            ("Nombre de calculs :", "multiplication_count", 60),
            ("Chiffres par opérande :", "multiplication_digits", 60),
            ("Nb décimales :", "multiplication_decimals", 60),
            ("Nombre d'opérandes :", "multiplication_num_operands", 60)  # Nouveau champ
        ]
        self.multiplication_group, multiplication_les, mult_rows = self._create_generic_groupbox(
            "Multiplication", multiplication_fields)
        self.all_line_edits.extend(multiplication_les)
        self._all_row_widgets_for_map.update(mult_rows)
        # Initialiser la valeur par défaut pour le nombre d'opérandes si le champ existe
        if hasattr(self, 'multiplication_num_operands'):
            self.multiplication_num_operands.setText("2")

        # Division
        self.division_reste_checkbox = QCheckBox("Division avec reste")
        division_fields = [
            ("Nombre de calculs :", "division_count", 60),  # Clé: division
            # Diviseur pour l'instant
            ("Chiffres par opérande :", "division_digits", 60),
            ("Nb décimales :", "division_decimals", 60)
        ]
        self.division_group, division_les, div_rows = self._create_generic_groupbox(
            "Division", division_fields, extra_items=[self.division_reste_checkbox]
        )
        self.all_line_edits.extend(division_les)
        self._all_row_widgets_for_map.update(div_rows)

        # Petits Problèmes Mathématiques
        self.math_problems_group = QGroupBox(
            "Petits Problèmes")  # Clé: math_problems_group
        math_problems_layout = QVBoxLayout()

        row_math_pb_count, self.math_problems_count = self._create_input_row(
            "Nombre de problèmes :", 60)
        self.all_line_edits.append(self.math_problems_count)
        self._all_row_widgets_for_map["math_problems_count_row"] = row_math_pb_count
        math_problems_layout.addWidget(row_math_pb_count)

        self.math_problem_type_checkboxes = {}  # Pour stocker les QCheckBox par type
        if self.math_problem_types_data:
            types_grid_layout = QGridLayout()  # Pour afficher les types 2 par 2
            types_grid_layout.setContentsMargins(0, 5, 0, 0)
            types_grid_layout.setVerticalSpacing(5)
            types_grid_layout.setHorizontalSpacing(10)
            row, col = 0, 0
            for type_key, _ in self.math_problem_types_data.items():
                type_name_display = type_key.replace("_", " ").capitalize()
                cb = QCheckBox(type_name_display)
                self.math_problem_type_checkboxes[type_key] = cb
                types_grid_layout.addWidget(cb, row, col)
                col = (col + 1) % 2
                if col == 0:
                    row += 1
            types_grid_layout.setColumnStretch(2, 1)  # Pousse à gauche
            math_problems_layout.addLayout(types_grid_layout)

        self.math_problems_group.setLayout(math_problems_layout)

        # Fonction utilitaire pour appliquer le style compact à une liste de QGroupBox
        def set_groupbox_style(groups, color):
            # Utiliser le template depuis UI_STYLE_CONFIG
            style_template = UI_STYLE_CONFIG["group_boxes"]["base_style_template"]
            for group in groups:
                group.setStyleSheet(style_template.format(border_color=color))

        # Harmonisation des couleurs des bordures des QGroupBox selon la couleur du titre de colonne
        calc_groups = [self.enumerate_group, self.addition_group, self.subtraction_group,
                       self.multiplication_group, self.division_group, self.math_problems_group]
        calc_border_color = UI_STYLE_CONFIG["group_boxes"]["border_colors"]["calc"]
        set_groupbox_style(calc_groups, calc_border_color)

        calc_layout.addWidget(self.enumerate_group)
        calc_layout.addWidget(self.addition_group)
        # ... (les autres addWidget pour calc_layout)
        calc_layout.addWidget(self.subtraction_group)
        calc_layout.addWidget(self.multiplication_group)
        calc_layout.addWidget(self.division_group)
        calc_layout.addWidget(self.math_problems_group)
        calc_layout.addStretch()

        # --- Colonne Géométrie/Mesures ---
        geo_layout = QVBoxLayout()
        self.geo_title_label = QLabel("Mesures")
        geo_title_style = UI_STYLE_CONFIG["labels"]["column_title_base"] + \
            f"color: {UI_STYLE_CONFIG['labels']['column_title_colors']['geo']};"
        self.geo_title_label.setStyleSheet(geo_title_style)
        geo_layout.addWidget(self.geo_title_label)
        geo_layout.setContentsMargins(5, 5, 5, 5)
        geo_layout.setSpacing(6)

        # Section conversions
        self.geo_conv_group = QGroupBox("Conversions")  # Clé: geo_conversion
        geo_conv_layout = QVBoxLayout()

        row_widget_geo_count, self.geo_ex_count = self._create_input_row(
            "Nombre d'exercices :", 60)
        self.all_line_edits.append(self.geo_ex_count)
        # Ajout manuel car pas via _create_generic_groupbox
        self._all_row_widgets_for_map["geo_ex_count_row"] = row_widget_geo_count
        geo_conv_layout.addWidget(row_widget_geo_count)

        self.conv_type_longueur = QCheckBox("Longueur")
        self.conv_type_masse = QCheckBox("Masse")
        self.conv_type_volume = QCheckBox("Volume")
        self.conv_type_temps = QCheckBox("Temps")
        self.conv_type_monnaie = QCheckBox("Monnaie")
        self.geo_conv_type_checkboxes = [
            self.conv_type_longueur, self.conv_type_masse, self.conv_type_volume, self.conv_type_temps, self.conv_type_monnaie
        ]
        for cb in self.geo_conv_type_checkboxes:
            geo_conv_layout.addWidget(cb)
        # Sens de conversion
        self.conv_sens_direct = QCheckBox("Aller (m → cm)")
        self.conv_sens_inverse = QCheckBox("Retour (cm → m)")
        self.conv_sens_direct.setChecked(True)
        self.conv_sens_inverse.setChecked(True)
        sens_layout = QHBoxLayout()
        sens_layout.addWidget(self.conv_sens_direct)
        sens_layout.addWidget(self.conv_sens_inverse)
        geo_conv_layout.addLayout(sens_layout)
        self.geo_conv_group.setLayout(geo_conv_layout)
        geo_layout.addWidget(self.geo_conv_group)

        # Section : Ranger les nombres (déplacée ici)
        self.sort_type_croissant = QCheckBox("Croissant")
        self.sort_type_decroissant = QCheckBox("Décroissant")
        self.sort_type_croissant.setChecked(True)

        # Utiliser un QGridLayout pour aligner sur deux colonnes
        sort_grid_type_layout = QGridLayout()
        # Pas de marges internes pour le layout de la grille
        sort_grid_type_layout.setContentsMargins(0, 0, 0, 0)
        sort_grid_type_layout.setVerticalSpacing(5)
        sort_grid_type_layout.setHorizontalSpacing(10)
        sort_grid_type_layout.addWidget(self.sort_type_croissant, 0, 0)
        sort_grid_type_layout.addWidget(self.sort_type_decroissant, 0, 1)
        # Étirer la colonne à droite des cases à cocher pour les pousser à gauche
        sort_grid_type_layout.setColumnStretch(2, 1)

        sort_fields = [
            ("Nombre d'exercices :", "sort_count", 60),
            ("Chiffres par nombre :", "sort_digits", 60),
            ("Nombres à ranger :", "sort_n_numbers", 60)
        ]
        self.sort_group, sort_les, sort_rows = self._create_generic_groupbox(
            # Utiliser le layout en grille
            "Ranger les nombres", sort_fields, extra_items=[sort_grid_type_layout]
        )
        self.all_line_edits.extend(sort_les)
        self._all_row_widgets_for_map.update(sort_rows)
        geo_layout.addWidget(self.sort_group)

        # Section : Encadrer un nombre
        encadrement_fields = [
            ("Nombre d'exercices :", "encadrement_count", 60),
            # Clé: geo_encadrement
            ("Chiffres par nombre :", "encadrement_digits", 60)
        ]

        # Types d'encadrement
        # type_label = QLabel("Type :") # Supprimé
        self.encadrement_unite = QCheckBox("Unité")
        self.encadrement_dizaine = QCheckBox("Dizaine")
        self.encadrement_centaine = QCheckBox("Centaine")
        self.encadrement_millier = QCheckBox("Millier")

        # Utiliser un QGridLayout pour aligner sur deux colonnes
        encadrement_grid_type_layout = QGridLayout()
        encadrement_grid_type_layout.setContentsMargins(0, 0, 0, 0)
        encadrement_grid_type_layout.setVerticalSpacing(5)
        encadrement_grid_type_layout.setHorizontalSpacing(10)

        encadrement_checkboxes_list = [
            self.encadrement_unite, self.encadrement_dizaine,
            self.encadrement_centaine, self.encadrement_millier
        ]
        row, col = 0, 0
        for cb in encadrement_checkboxes_list:
            encadrement_grid_type_layout.addWidget(cb, row, col)
            col = (col + 1) % 2
            if col == 0:
                row += 1
        encadrement_grid_type_layout.setColumnStretch(2, 1)  # Pousse à gauche

        self.encadrement_group, encadrement_les, enc_rows = self._create_generic_groupbox(
            # Utiliser le layout en grille
            "Encadrer un nombre", encadrement_fields, extra_items=[encadrement_grid_type_layout]
        )
        self.all_line_edits.extend(encadrement_les)
        self._all_row_widgets_for_map.update(enc_rows)
        geo_layout.addWidget(self.encadrement_group)

        # Section : Comparer des nombres
        compare_numbers_fields = [
            ("Nombre d'exercices :", "compare_numbers_count", 60),
            ("Chiffres par nombre :", "compare_numbers_digits", 60)
        ]
        self.compare_numbers_group, compare_numbers_les, cn_rows = self._create_generic_groupbox(
            "Comparer des nombres", compare_numbers_fields
        )
        self.all_line_edits.extend(compare_numbers_les)
        self._all_row_widgets_for_map.update(cn_rows)
        geo_layout.addWidget(self.compare_numbers_group)

        # Section : Suites Logiques
        logical_sequences_fields = [
            ("Nombre d'exercices :", "logical_sequences_count", 60),
            ("Nombre d'éléments (suite) :",
             "logical_sequences_length", 60)  # Nouveau champ
        ]
        # Types de suites
        self.logical_sequences_type_arithmetic_plus_cb = QCheckBox(
            "Suite arithmétique (+)")
        self.logical_sequences_type_arithmetic_minus_cb = QCheckBox(
            "Suite arithmétique (-)")
        self.logical_sequences_type_arithmetic_multiply_cb = QCheckBox(
            "Suite arithmétique (x)")
        self.logical_sequences_type_arithmetic_divide_cb = QCheckBox(
            "Suite arithmétique (÷)")

        self.logical_sequences_group, logical_sequences_les, ls_rows = self._create_generic_groupbox(
            "Suites Logiques", logical_sequences_fields,
            extra_items=[QLabel("Types de suites :"), self.logical_sequences_type_arithmetic_plus_cb,
                         self.logical_sequences_type_arithmetic_minus_cb,
                         self.logical_sequences_type_arithmetic_multiply_cb,  # Ajouté
                         self.logical_sequences_type_arithmetic_divide_cb]   # Ajouté
        )
        self.all_line_edits.extend(logical_sequences_les)
        self._all_row_widgets_for_map.update(ls_rows)
        # Initialiser la valeur par défaut pour la longueur des suites
        if hasattr(self, 'logical_sequences_length'):
            self.logical_sequences_length.setText("5")  # Valeur par défaut
        geo_layout.addWidget(self.logical_sequences_group)

        # Mesures : violet (#BA68C8) - Ajout des nouveaux groupes
        geo_groups = [self.geo_conv_group, self.sort_group, self.encadrement_group,
                      self.compare_numbers_group, self.logical_sequences_group]
        geo_border_color = UI_STYLE_CONFIG["group_boxes"]["border_colors"]["geo"]
        set_groupbox_style(geo_groups, geo_border_color)
        geo_layout.addStretch()

        # --- Colonne Conjugaison ---
        conj_layout = QVBoxLayout()
        self.conj_title_label = QLabel("Conjugaison")
        conj_title_style = UI_STYLE_CONFIG["labels"]["column_title_base"] + \
            f"color: {UI_STYLE_CONFIG['labels']['column_title_colors']['conj']};"
        self.conj_title_label.setStyleSheet(conj_title_style)
        conj_layout.addWidget(self.conj_title_label)
        conj_layout.setContentsMargins(5, 5, 5, 5)
        conj_layout.setSpacing(6)
        # Paramètres de conjugaison (d'abord)
        conj_param_fields = [
            ("Nombre de verbes par jour :", "verbs_per_day_entry", 60)]
        self.conj_number_group, conj_param_les, conj_param_rows = self._create_generic_groupbox(  # Clé: conj_params
            "Paramètres de conjugaison", conj_param_fields
        )
        self.all_line_edits.extend(conj_param_les)
        self._all_row_widgets_for_map.update(conj_param_rows)
        conj_layout.addWidget(self.conj_number_group)

        # Groupes de verbes
        self.conj_group_group = QGroupBox(
            "Groupes de verbes")  # Clé: conj_groups
        group_layout = QVBoxLayout()
        self.group_1_checkbox = QCheckBox("1er groupe")
        self.group_2_checkbox = QCheckBox("2ème groupe")
        self.group_3_checkbox = QCheckBox("3ème groupe")
        self.usual_verbs_checkbox = QCheckBox(
            "Verbes usuels (à connaître par cœur)")
        self.conj_group_group_checkboxes = [
            self.group_1_checkbox, self.group_2_checkbox, self.group_3_checkbox, self.usual_verbs_checkbox]
        for cb in self.conj_group_group_checkboxes:
            group_layout.addWidget(cb)
        self.conj_group_group.setLayout(group_layout)
        conj_layout.addWidget(self.conj_group_group)

        # Temps (dynamique depuis conjugation_generator.TENSES)
        from conjugation_generator import TENSES
        self.conj_tense_group = QGroupBox("Temps")  # Clé: conj_tenses
        tense_layout = QVBoxLayout()
        self.tense_checkboxes = []
        for tense in TENSES:
            cb = QCheckBox(tense.capitalize())
            tense_layout.addWidget(cb)
            self.tense_checkboxes.append(cb)
        self.conj_tense_group.setLayout(tense_layout)
        conj_layout.addWidget(self.conj_tense_group)
        # Conjugaison : vert (#81C784)
        conj_groups = [self.conj_number_group,
                       self.conj_group_group, self.conj_tense_group]
        conj_border_color = UI_STYLE_CONFIG["group_boxes"]["border_colors"]["conj"]
        set_groupbox_style(conj_groups, conj_border_color)
        conj_layout.addStretch()

        # --- Colonne Grammaire ---
        grammar_layout = QVBoxLayout()
        self.grammar_title_label = QLabel("Grammaire")
        grammar_title_style = UI_STYLE_CONFIG["labels"]["column_title_base"] + \
            f"color: {UI_STYLE_CONFIG['labels']['column_title_colors']['grammar']};"
        self.grammar_title_label.setStyleSheet(grammar_title_style)
        grammar_layout.addWidget(self.grammar_title_label)
        grammar_layout.setContentsMargins(5, 5, 5, 5)
        grammar_layout.setSpacing(6)

        grammar_param_fields = [
            ("Nombre de phrases :", "grammar_sentence_count", 60)]
        grammar_number_group, grammar_param_les, grammar_param_rows = self._create_generic_groupbox(
            "Paramètres de grammaire", grammar_param_fields
        )  # Clé: grammar_params (sera self.grammar_number_group)
        self.grammar_number_group = grammar_number_group  # Assign to self
        self.all_line_edits.extend(grammar_param_les)
        grammar_layout.addWidget(self.grammar_number_group)
        self._all_row_widgets_for_map.update(grammar_param_rows)

        self.grammar_type_group = QGroupBox(
            "Type de phrase")  # Clé: grammar_types
        grammar_type_layout = QVBoxLayout()
        self.intransitive_checkbox = QCheckBox("Sans complément d'objet")
        self.transitive_direct_checkbox = QCheckBox(
            "Avec complément d'objet direct")
        self.transitive_indirect_checkbox = QCheckBox(
            "Avec complément d'objet indirect")
        self.ditransitive_checkbox = QCheckBox("Avec deux compléments d'objet")
        self.grammar_type_checkboxes = [self.intransitive_checkbox, self.transitive_direct_checkbox,
                                        self.transitive_indirect_checkbox, self.ditransitive_checkbox]
        for cb in self.grammar_type_checkboxes:
            grammar_type_layout.addWidget(cb)
        self.grammar_type_group.setLayout(grammar_type_layout)
        grammar_layout.addWidget(self.grammar_type_group)

        from grammar_generator import TRANSFORMATIONS
        self.grammar_transfo_group = QGroupBox(
            "Transformations")  # Clé: grammar_transfo
        grammar_transfo_layout = QVBoxLayout()
        self.transfo_checkboxes = []
        for t in TRANSFORMATIONS:
            cb = QCheckBox(t)
            grammar_transfo_layout.addWidget(cb)
            self.transfo_checkboxes.append(cb)
        self.grammar_transfo_group.setLayout(grammar_transfo_layout)
        grammar_layout.addWidget(self.grammar_transfo_group)

        # Grammaire : jaune (#FFD54F)
        grammar_groups = [self.grammar_number_group,
                          self.grammar_type_group, self.grammar_transfo_group]
        grammar_border_color = UI_STYLE_CONFIG["group_boxes"]["border_colors"]["grammar"]
        set_groupbox_style(grammar_groups, grammar_border_color)
        grammar_layout.addStretch()

        # --- Colonne Orthographe ---
        orthographe_layout = QVBoxLayout()
        self.orthographe_title_label = QLabel("Orthographe")
        ortho_title_style = UI_STYLE_CONFIG["labels"]["column_title_base"] + \
            f"color: {UI_STYLE_CONFIG['labels']['column_title_colors']['ortho']};"
        self.orthographe_title_label.setStyleSheet(ortho_title_style)
        orthographe_layout.addWidget(self.orthographe_title_label)
        orthographe_layout.setContentsMargins(5, 5, 5, 5)
        orthographe_layout.setSpacing(6)
        # Paramètres orthographe
        ortho_param_fields = [
            ("Nombre d'exercices :", "orthographe_ex_count", 60)]
        self.orthographe_number_group, ortho_param_les, ortho_param_rows = self._create_generic_groupbox(  # Clé: ortho_params
            "Paramètres d'orthographe", ortho_param_fields
        )
        self.all_line_edits.extend(ortho_param_les)
        self._all_row_widgets_for_map.update(ortho_param_rows)
        orthographe_layout.addWidget(self.orthographe_number_group)

        # Section homophones
        self.orthographe_homophone_group = QGroupBox(
            "Homophones")  # Clé: ortho_homophones
        orthographe_homophone_layout = QVBoxLayout()
        # ... (checkboxes for homophones)
        self.homophone_a_checkbox = QCheckBox("a / à")
        self.homophone_et_checkbox = QCheckBox("et / est")
        self.homophone_on_checkbox = QCheckBox("on / ont")
        self.homophone_son_checkbox = QCheckBox("son / sont")
        self.homophone_ce_checkbox = QCheckBox("ce / se")
        self.homophone_ou_checkbox = QCheckBox("ou / où")
        self.homophone_ces_checkbox = QCheckBox("ces / ses")
        self.homophone_mes_checkbox = QCheckBox("mes / mais / met / mets")
        self.orthographe_homophone_checkboxes = [
            self.homophone_a_checkbox, self.homophone_et_checkbox, self.homophone_on_checkbox,
            self.homophone_son_checkbox, self.homophone_ce_checkbox, self.homophone_mes_checkbox,
            self.homophone_ou_checkbox, self.homophone_ces_checkbox
        ]
        for cb in self.orthographe_homophone_checkboxes:
            orthographe_homophone_layout.addWidget(cb)
        self.orthographe_homophone_group.setLayout(
            orthographe_homophone_layout)
        orthographe_layout.addWidget(self.orthographe_homophone_group)
        # Orthographe : orange foncé (#FFB300)
        ortho_groups = [self.orthographe_number_group,
                        self.orthographe_homophone_group]
        ortho_border_color = UI_STYLE_CONFIG["group_boxes"]["border_colors"]["ortho"]
        set_groupbox_style(ortho_groups, ortho_border_color)
        orthographe_layout.addStretch()

        # --- Colonne Anglais ---
        english_layout = QVBoxLayout()
        self.english_title_label = QLabel("Anglais")
        english_title_style = UI_STYLE_CONFIG["labels"]["column_title_base"] + \
            f"color: {UI_STYLE_CONFIG['labels']['column_title_colors']['english']};"
        self.english_title_label.setStyleSheet(english_title_style)
        english_layout.addWidget(self.english_title_label)
        english_layout.setContentsMargins(5, 5, 5, 5)
        english_layout.setSpacing(6)
        # Section 1 : Phrases à compléter
        english_complete_fields = [
            ("Nombre d'exercices :", "english_complete_count", 60)]
        self.english_type_simple = QCheckBox("Phrase à compléter simple")
        self.english_type_complexe = QCheckBox("Phrase à compléter complexe")
        self.english_complete_group, english_complete_les, eng_comp_rows = self._create_generic_groupbox(  # Clé: english_complete
            "Phrases à compléter",
            english_complete_fields,
            extra_items=[self.english_type_simple, self.english_type_complexe]
        )
        self.all_line_edits.extend(english_complete_les)
        self._all_row_widgets_for_map.update(eng_comp_rows)
        english_layout.addWidget(self.english_complete_group)

        # Section 2 : Jeux à relier
        english_relier_fields = [
            ("Nombre de jeux à relier :", "english_relier_count", 60),
            ("Nombre de mots par jeu :", "relier_count", 60)
        ]
        self.english_relier_group, english_relier_les, eng_rel_rows = self._create_generic_groupbox(  # Clé: english_relier
            "Jeux à relier", english_relier_fields
        )
        # Récupérer le layout existant du groupe "Jeux à relier"
        english_relier_group_layout = self.english_relier_group.layout()

        self.all_line_edits.extend(english_relier_les)
        self._all_row_widgets_for_map.update(eng_rel_rows)
        english_layout.addWidget(self.english_relier_group)

        # Ajout des checkboxes de thèmes directement dans le layout de english_relier_group
        # Dictionnaire pour stocker les checkboxes de thèmes
        self.english_relier_theme_checkboxes = {}

        if self.english_relier_themes:  # Si des thèmes ont été chargés
            for theme_name in self.english_relier_themes.keys():
                cb = QCheckBox(theme_name.replace("_", " ").capitalize())
                self.english_relier_theme_checkboxes[theme_name] = cb

        # Utiliser un QGridLayout pour afficher les checkboxes de thèmes
        themes_grid_layout = QGridLayout()
        themes_grid_layout.setContentsMargins(
            0, 10, 0, 0)  # Espace au-dessus des thèmes
        # Espacement vertical entre les lignes de checkboxes
        themes_grid_layout.setVerticalSpacing(5)
        # Espacement horizontal entre les checkboxes
        themes_grid_layout.setHorizontalSpacing(10)

        if self.english_relier_theme_checkboxes:
            checkbox_values = list(
                self.english_relier_theme_checkboxes.values())
            row, col = 0, 0
            for cb_widget in checkbox_values:
                themes_grid_layout.addWidget(cb_widget, row, col)
                col += 1
                if col == 2:  # Passer à la ligne suivante après 2 checkboxes
                    col = 0
                    row += 1
            # S'assurer que les colonnes ne s'étirent pas et que le contenu est poussé à gauche
            # Pas d'étirement pour la première colonne de checkboxes
            themes_grid_layout.setColumnStretch(0, 0)
            # Pas d'étirement pour la deuxième colonne de checkboxes
            themes_grid_layout.setColumnStretch(1, 0)
            # Étire tout l'espace restant à droite
            themes_grid_layout.setColumnStretch(2, 1)
        # S'il n'y a pas de thèmes du tout (fichier vide/erreur)
        elif not self.english_relier_themes:
            no_themes_label = QLabel(
                "Aucun thème défini dans mots_a_relier.json")
            themes_grid_layout.addWidget(
                no_themes_label, 0, 0, 1, 2)  # Span sur 2 colonnes

        english_relier_group_layout.addLayout(themes_grid_layout)

        # Anglais : bleu moyen (#64B5F6)
        # themes_group est maintenant stylé différemment et imbriqué
        english_groups = [self.english_complete_group,
                          self.english_relier_group]
        english_border_color = UI_STYLE_CONFIG["group_boxes"]["border_colors"]["english"]
        set_groupbox_style(english_groups, english_border_color)
        english_layout.addStretch()

        # --- Splitter pour 6 colonnes ---
        # Les colonnes sont maintenant des QWidget simples
        self.calc_column_widget = QWidget()
        self.calc_column_widget.setLayout(calc_layout)
        self.calc_column_widget.setMinimumWidth(
            270)  # Garder la largeur minimale

        self.geo_column_widget = QWidget()
        self.geo_column_widget.setLayout(geo_layout)
        self.geo_column_widget.setMinimumWidth(270)

        self.conj_column_widget = QWidget()
        self.conj_column_widget.setLayout(conj_layout)
        self.conj_column_widget.setMinimumWidth(270)

        self.grammar_column_widget = QWidget()
        self.grammar_column_widget.setLayout(grammar_layout)
        self.grammar_column_widget.setMinimumWidth(270)

        # Widgets pour les sections Orthographe et Anglais (contenus dans ortho_anglais_column_widget)
        self.orthographe_section_widget = QWidget()
        self.orthographe_section_widget.setLayout(orthographe_layout)

        self.english_section_widget = QWidget()
        self.english_section_widget.setLayout(english_layout)

        # Bloc vertical pour orthographe + anglais
        ortho_anglais_layout = QVBoxLayout()
        ortho_anglais_layout.setContentsMargins(0, 0, 0, 0)
        ortho_anglais_layout.setSpacing(0)
        ortho_anglais_layout.addWidget(self.orthographe_section_widget)
        ortho_anglais_layout.addWidget(self.english_section_widget)
        # Ajoute un ressort pour pousser les sections vers le haut
        ortho_anglais_layout.addStretch(1)
        # Ce widget contiendra le layout ortho_anglais
        self.ortho_anglais_column_widget = QWidget()
        self.ortho_anglais_column_widget.setLayout(ortho_anglais_layout)
        self.ortho_anglais_column_widget.setMinimumWidth(270)

        # Stocker la configuration initiale des colonnes du splitter pour la réorganisation
        self.splitter_column_configs_initial_order = [
            {'widget': self.calc_column_widget, 'stretch': 1, 'key': 'calc'},
            {'widget': self.geo_column_widget, 'stretch': 1, 'key': 'geo'},
            {'widget': self.conj_column_widget, 'stretch': 1, 'key': 'conj'},
            {'widget': self.ortho_anglais_column_widget,
                'stretch': 1, 'key': 'ortho_anglais'},
            {'widget': self.grammar_column_widget, 'stretch': 1, 'key': 'grammar'}
        ]

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.calc_column_widget)
        splitter.addWidget(self.geo_column_widget)
        splitter.addWidget(self.conj_column_widget)
        # Ortho/Anglais en 4ème
        splitter.addWidget(self.ortho_anglais_column_widget)
        # Grammaire en 5ème
        splitter.addWidget(self.grammar_column_widget)
        for i, config in enumerate(self.splitter_column_configs_initial_order):
            splitter.setStretchFactor(i, config['stretch'])

        # --- ScrollArea principal pour le QSplitter ---
        self.main_scroll_area = QScrollArea()
        self.main_scroll_area.setWidgetResizable(True)
        # Le splitter est maintenant le widget du scroll area
        self.main_scroll_area.setWidget(splitter)
        self.main_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Style pour la barre de défilement du QScrollArea principal (depuis la config)
        scrollbar_style = UI_STYLE_CONFIG["scroll_bar"]["style_template"].format(
            **UI_STYLE_CONFIG["scroll_bar"]["values"])
        self.main_scroll_area.setStyleSheet(scrollbar_style)

        # Ajoute le scroll area principal au layout
        main_layout.addWidget(self.main_scroll_area)
        self.splitter = splitter  # Garder une référence au splitter

        # --- Initialize exercise_widgets_map ---
        # This map will store all controllable widgets with unique keys.
        self.exercise_widgets_map = {
            # Calculs
            "enumerate_group": self.enumerate_group,
            "enumerate_count_input": self.enumerate_count, "enumerate_digits_input": self.enumerate_digits,
            "addition_group": self.addition_group,
            "addition_count_input": self.addition_count, "addition_digits_input": self.addition_digits,
            "addition_decimals_input": self.addition_decimals, "addition_num_operands_input": self.addition_num_operands,
            "subtraction_group": self.subtraction_group,
            "subtraction_count_input": self.subtraction_count, "subtraction_digits_input": self.subtraction_digits,
            "subtraction_decimals_input": self.subtraction_decimals, "subtraction_num_operands_input": self.subtraction_num_operands,
            "subtraction_negative_cb": self.subtraction_negative_checkbox,
            "multiplication_group": self.multiplication_group,
            "multiplication_count_input": self.multiplication_count, "multiplication_digits_input": self.multiplication_digits,
            "multiplication_decimals_input": self.multiplication_decimals, "multiplication_num_operands_input": self.multiplication_num_operands,
            "division_group": self.division_group,
            "division_count_input": self.division_count, "division_digits_input": self.division_digits, "division_decimals_input": self.division_decimals,
            "division_reste_cb": self.division_reste_checkbox,
            # Petits Problèmes
            "math_problems_group": self.math_problems_group,
            "math_problems_count_input": self.math_problems_count,

            # Mesures
            "geo_conv_group": self.geo_conv_group,
            "geo_ex_count_input": self.geo_ex_count,
            "conv_type_longueur_cb": self.conv_type_longueur, "conv_type_masse_cb": self.conv_type_masse, "conv_type_volume_cb": self.conv_type_volume, "conv_type_temps_cb": self.conv_type_temps, "conv_type_monnaie_cb": self.conv_type_monnaie,
            "conv_sens_direct_cb": self.conv_sens_direct, "conv_sens_inverse_cb": self.conv_sens_inverse,

            "geo_sort_group": self.sort_group,
            "sort_count_input": self.sort_count, "sort_digits_input": self.sort_digits, "sort_n_numbers_input": self.sort_n_numbers,
            "sort_type_croissant_cb": self.sort_type_croissant, "sort_type_decroissant_cb": self.sort_type_decroissant,

            "geo_encadrement_group": self.encadrement_group,
            "encadrement_count_input": self.encadrement_count, "encadrement_digits_input": self.encadrement_digits,
            "encadrement_unite_cb": self.encadrement_unite, "encadrement_dizaine_cb": self.encadrement_dizaine, "encadrement_centaine_cb": self.encadrement_centaine, "encadrement_millier_cb": self.encadrement_millier,

            "geo_compare_numbers_group": self.compare_numbers_group,
            "compare_numbers_count_input": self.compare_numbers_count, "compare_numbers_digits_input": self.compare_numbers_digits,

            "geo_logical_sequences_group": self.logical_sequences_group,
            "logical_sequences_count_input": self.logical_sequences_count,
            "logical_sequences_length_input": self.logical_sequences_length,  # Nouveau
            "logical_sequences_type_arithmetic_plus_cb": self.logical_sequences_type_arithmetic_plus_cb,
            "logical_sequences_type_arithmetic_minus_cb": self.logical_sequences_type_arithmetic_minus_cb,
            "logical_sequences_type_arithmetic_multiply_cb": self.logical_sequences_type_arithmetic_multiply_cb,
            "logical_sequences_type_arithmetic_divide_cb": self.logical_sequences_type_arithmetic_divide_cb,

            # Conjugaison
            # Renamed for clarity from conj_number_group
            "conj_params_group": self.conj_number_group,
            "verbs_per_day_entry_input": self.verbs_per_day_entry,
            "conj_groups_group": self.conj_group_group,  # Renamed for clarity
            "group_1_cb": self.group_1_checkbox, "group_2_cb": self.group_2_checkbox, "group_3_cb": self.group_3_checkbox, "usual_verbs_cb": self.usual_verbs_checkbox,
            "conj_tenses_group": self.conj_tense_group,  # Renamed for clarity
            # Individual tense checkboxes
            "tense_present_cb": self.tense_checkboxes[0] if len(self.tense_checkboxes) > 0 else None,
            "tense_imparfait_cb": self.tense_checkboxes[1] if len(self.tense_checkboxes) > 1 else None,
            "tense_passe_simple_cb": self.tense_checkboxes[2] if len(self.tense_checkboxes) > 2 else None,
            "tense_futur_simple_cb": self.tense_checkboxes[3] if len(self.tense_checkboxes) > 3 else None,
            "tense_passe_compose_cb": self.tense_checkboxes[4] if len(self.tense_checkboxes) > 4 else None,
            "tense_plus_que_parfait_cb": self.tense_checkboxes[5] if len(self.tense_checkboxes) > 5 else None,
            "tense_conditionnel_present_cb": self.tense_checkboxes[6] if len(self.tense_checkboxes) > 6 else None,
            "tense_imperatif_present_cb": self.tense_checkboxes[7] if len(self.tense_checkboxes) > 7 else None,
            # Add more if TENSES list grows, ensure TENSES order matches these keys in EXERCISES_BY_LEVEL_INCREMENTAL

            # Grammaire
            "grammar_params_group": self.grammar_number_group,  # Renamed for clarity
            "grammar_sentence_count_input": self.grammar_sentence_count,
            "grammar_types_group": self.grammar_type_group,
            "intransitive_cb": self.intransitive_checkbox, "transitive_direct_cb": self.transitive_direct_checkbox, "transitive_indirect_cb": self.transitive_indirect_checkbox, "ditransitive_cb": self.ditransitive_checkbox,
            "grammar_transfo_group": self.grammar_transfo_group,
            # Individual transformation checkboxes (key based on transformation text for simplicity, ensure no special chars or make them safe)
            "transfo_singulier_pluriel_cb": self.transfo_checkboxes[0] if len(self.transfo_checkboxes) > 0 else None,
            "transfo_masculin_feminin_cb": self.transfo_checkboxes[1] if len(self.transfo_checkboxes) > 1 else None,
            "transfo_present_passe_compose_cb": self.transfo_checkboxes[2] if len(self.transfo_checkboxes) > 2 else None,
            "transfo_present_imparfait_cb": self.transfo_checkboxes[3] if len(self.transfo_checkboxes) > 3 else None,
            "transfo_present_futur_simple_cb": self.transfo_checkboxes[4] if len(self.transfo_checkboxes) > 4 else None,
            "transfo_indicatif_imperatif_cb": self.transfo_checkboxes[5] if len(self.transfo_checkboxes) > 5 else None,
            "transfo_voix_active_passive_cb": self.transfo_checkboxes[6] if len(self.transfo_checkboxes) > 6 else None,
            "transfo_declarative_interrogative_cb": self.transfo_checkboxes[7] if len(self.transfo_checkboxes) > 7 else None,
            "transfo_declarative_exclamative_cb": self.transfo_checkboxes[8] if len(self.transfo_checkboxes) > 8 else None,
            "transfo_declarative_imperative_cb": self.transfo_checkboxes[9] if len(self.transfo_checkboxes) > 9 else None,
            "transfo_affirmative_negative_cb": self.transfo_checkboxes[10] if len(self.transfo_checkboxes) > 10 else None,

            # Orthographe
            "ortho_params_group": self.orthographe_number_group,  # Renamed for clarity
            "orthographe_ex_count_input": self.orthographe_ex_count,
            "ortho_homophones_group": self.orthographe_homophone_group,
            "homophone_a_cb": self.homophone_a_checkbox, "homophone_et_cb": self.homophone_et_checkbox, "homophone_on_cb": self.homophone_on_checkbox, "homophone_son_cb": self.homophone_son_checkbox,
            "homophone_ce_cb": self.homophone_ce_checkbox, "homophone_ou_cb": self.homophone_ou_checkbox, "homophone_ces_cb": self.homophone_ces_checkbox, "homophone_mes_cb": self.homophone_mes_checkbox,

            # Anglais
            "english_complete_group": self.english_complete_group,
            "english_complete_count_input": self.english_complete_count,
            "english_type_simple_cb": self.english_type_simple, "english_type_complexe_cb": self.english_type_complexe,
            "english_relier_group": self.english_relier_group,
            "english_relier_count_input": self.english_relier_count, "relier_count_input": self.relier_count,
            # "english_relier_themes_group": self.english_relier_themes_group, # Supprimé car plus de groupe dédié
        }
        # Remove None values from map (if checkboxes lists were shorter than expected)
        self.exercise_widgets_map = {
            k: v for k, v in self.exercise_widgets_map.items() if v is not None}
        # Ajouter les row_widgets stockés
        self.exercise_widgets_map.update(self._all_row_widgets_for_map)
        del self._all_row_widgets_for_map  # Nettoyer le dictionnaire temporaire

        # Ajouter dynamiquement les checkboxes de thèmes anglais à exercise_widgets_map
        if hasattr(self, 'english_relier_theme_checkboxes'):
            for theme_name, cb_widget in self.english_relier_theme_checkboxes.items():
                self.exercise_widgets_map[f"english_theme_{theme_name}_cb"] = cb_widget

        # Ajouter dynamiquement les checkboxes de types de problèmes mathématiques
        if hasattr(self, 'math_problem_type_checkboxes'):
            for type_key, cb_widget in self.math_problem_type_checkboxes.items():
                self.exercise_widgets_map[f"math_problem_type_{type_key}_cb"] = cb_widget

        # --- Column Titles and Sections Mapping (for hiding titles of empty columns) ---
        self.column_title_widgets = {
            "calc": self.calc_title_label,
            "geo": self.geo_title_label,
            "conj": self.conj_title_label,
            "grammar": self.grammar_title_label,
            "ortho": self.orthographe_title_label,
            "english": self.english_title_label,
        }
        self.column_section_keys = {  # Maps column key to list of its main section group keys
            # No change here
            "calc": ["enumerate_group", "addition_group", "subtraction_group", "multiplication_group", "division_group", "math_problems_group"],
            # Added new groups
            "geo": ["geo_conv_group", "geo_sort_group", "geo_encadrement_group", "geo_compare_numbers_group", "geo_logical_sequences_group"],
            "conj": ["conj_params_group", "conj_groups_group", "conj_tenses_group"],
            "grammar": ["grammar_params_group", "grammar_types_group", "grammar_transfo_group"],
            "ortho": ["ortho_params_group", "ortho_homophones_group"],
            # Les checkboxes de thèmes sont gérées individuellement
            "english": ["english_complete_group", "english_relier_group"],
        }

        # Séparateur avant les contrôles de fichier/génération
        sep_bottom = QFrame()
        sep_bottom.setFrameShape(QFrame.Shape.HLine)
        sep_bottom.setFrameShadow(QFrame.Shadow.Sunken)
        sep_bottom.setStyleSheet(UI_STYLE_CONFIG["separators"]["style"])
        main_layout.addWidget(sep_bottom)

        # Bandeau bas : boutons générer + nom du fichier sur la même ligne
        bottom_controls_layout = QHBoxLayout()  # Layout principal pour le bas
        bottom_controls_layout.setContentsMargins(
            10, 5, 10, 5)  # Mêmes marges que top_layout

        # Partie gauche pour chemin et nom de fichier
        left_file_controls_layout = QGridLayout()
        self.output_path_button = QPushButton("Choisir dossier...")
        # Style sera appliqué plus bas avec les autres boutons
        self.output_path_button.clicked.connect(self.select_output_directory)
        # Le texte sera défini par _update_output_path_display
        self.output_path_display_label = QLabel()
        self.output_path_display_label.setWordWrap(True)
        self.output_path_display_label.setMinimumWidth(
            200)  # Réduit un peu pour faire de la place
        # Style initial sera défini dans _update_output_path_display

        self.filename_label = QLabel("Nom du fichier :")
        self.filename_label.setStyleSheet(
            UI_STYLE_CONFIG["labels"]["filename_label"])
        self.filename_entry = QLineEdit()
        self.filename_entry.setMinimumWidth(150)  # Donne une largeur minimale
        self.filename_entry.setMaximumWidth(200)
        # Ajouter à la liste pour stylage
        self.all_line_edits.append(self.filename_entry)
        self.filename_entry.setText("workbook")

        # Initialiser l'affichage du chemin de sortie
        self._update_output_path_display(self.selected_output_path)

        # Layout horizontal pour tous les contrôles de fichier
        file_controls_line_layout = QHBoxLayout()
        file_controls_line_layout.addWidget(self.output_path_button)
        file_controls_line_layout.addWidget(self.output_path_display_label)
        file_controls_line_layout.addWidget(self.filename_label)
        file_controls_line_layout.addWidget(self.filename_entry)
        # Ajoute un peu d'espace extensible si nécessaire avant le stretch principal
        file_controls_line_layout.addStretch(0)

        bottom_controls_layout.addLayout(left_file_controls_layout)
        # Espace flexible pour pousser les boutons à droite
        bottom_controls_layout.addStretch(1)

        # Styles pour les boutons d'action (depuis la config)
        btn_cfg = UI_STYLE_CONFIG["buttons"]

        def get_action_button_style(type_key):
            return btn_cfg["action_button_base_style_template"].format(
                bg_color=btn_cfg[type_key]["bg_color"],
                disabled_bg_color=btn_cfg["disabled"]["bg_color"],
                disabled_text_color=btn_cfg["disabled"]["text_color"],
                pressed_bg_color=btn_cfg[type_key]["pressed_bg_color"]
            )

        self.output_path_button.setStyleSheet(
            get_action_button_style("select_folder"))
        # self.output_path_button.setFixedWidth(150) # Suppression de la largeur fixe

        left_file_controls_layout.addLayout(
            file_controls_line_layout, 0, 0, 1, 2)  # Ajout du layout de ligne
        # Partie droite pour les boutons
        action_buttons_layout = QHBoxLayout()
        self.generate_pdf_button = QPushButton("Générer PDF")
        self.generate_pdf_button.setStyleSheet(get_action_button_style("pdf"))
        self.generate_pdf_button.clicked.connect(self.generate_pdf)
        # self.generate_pdf_button.setFixedWidth(150) # Suppression de la largeur fixe
        action_buttons_layout.addWidget(self.generate_pdf_button)

        self.generate_word_button = QPushButton("Générer Word")
        self.generate_word_button.setStyleSheet(
            get_action_button_style("word"))
        self.generate_word_button.clicked.connect(self.generate_word)
        # self.generate_word_button.setFixedWidth(150) # Suppression de la largeur fixe
        action_buttons_layout.addWidget(self.generate_word_button)

        self.preview_pdf_button = QPushButton("Prévisualiser PDF")
        self.preview_pdf_button.setStyleSheet(
            get_action_button_style("preview_pdf"))
        self.preview_pdf_button.clicked.connect(self.preview_pdf)
        # self.preview_pdf_button.setFixedWidth(150) # Suppression de la largeur fixe
        action_buttons_layout.addWidget(self.preview_pdf_button)

        self.preview_word_button = QPushButton("Prévisualiser Word")
        self.preview_word_button.setStyleSheet(
            get_action_button_style("preview_word"))
        self.preview_word_button.clicked.connect(self.preview_word)
        # self.preview_word_button.setFixedWidth(150) # Suppression de la largeur fixe
        action_buttons_layout.addWidget(self.preview_word_button)

        action_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        bottom_controls_layout.addLayout(action_buttons_layout)
        main_layout.addLayout(bottom_controls_layout)

        # --- Footer ---
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(15, 5, 10, 5) # Marges pour le pied de page

        github_label_text = f"<a style='color: #90CAF9; text-decoration: none;' href='{self.GITHUB_URL}'>Code Source (GitHub)</a>"
        self.github_label = QLabel(github_label_text)
        self.github_label.setOpenExternalLinks(True)
        self.github_label.setStyleSheet(UI_STYLE_CONFIG["labels"]["footer_label"])
        footer_layout.addWidget(self.github_label)

        footer_layout.addStretch(1) # Pousse le label de version vers la droite

        self.version_label = QLabel(f"Apprentium v{__version__}")
        self.version_label.setStyleSheet(UI_STYLE_CONFIG["labels"]["version_label"])
        footer_layout.addWidget(self.version_label)
        main_layout.addLayout(footer_layout)

        # Correction du style pour les QLineEdit (texte noir sur fond sombre)
        lineedit_style = UI_STYLE_CONFIG["line_edits"]["default"]
        for le in self.all_line_edits:
            if le:  # S'assurer que le widget existe
                le.setStyleSheet(lineedit_style)

        # Le style des labels est maintenant appliqué dans _create_input_row
        # La boucle de style pour les labels est donc supprimée.

        # Chargement de la configuration si elle existe
        def get_config_path():
            if getattr(sys, 'frozen', False):
                # Exécutable PyInstaller : toujours à côté de l'exe
                return os.path.join(os.path.dirname(sys.executable), 'config.json')
            else:
                # Mode script : à côté du script
                return os.path.join(os.path.dirname(__file__), 'config.json')
        self.config_path = get_config_path()

        # Centralisation des champs pour la config (nom, widget, mode)
        self.config_fields = [
            ('days_entry', self.days_entry, 'text'),
            # Enumérer un nombre
            ('enumerate_count', self.enumerate_count, 'text'),
            ('enumerate_digits', self.enumerate_digits, 'text'),
            # Ranger les nombres
            ('sort_count', self.sort_count, 'text'),
            ('sort_digits', self.sort_digits, 'text'),
            ('sort_n_numbers', self.sort_n_numbers, 'text'),
            ('sort_type_croissant', self.sort_type_croissant, 'checked'),
            ('sort_type_decroissant', self.sort_type_decroissant, 'checked'),
            ('header_entry', self.header_entry, 'text'),
            ('addition_count', self.addition_count, 'text'),
            ('addition_digits', self.addition_digits, 'text'),
            ('addition_num_operands', self.addition_num_operands, 'text'),
            ('addition_decimals', self.addition_decimals, 'text'),
            ('subtraction_count', self.subtraction_count, 'text'),
            ('subtraction_digits', self.subtraction_digits, 'text'),
            ('subtraction_num_operands', self.subtraction_num_operands, 'text'),
            ('subtraction_decimals', self.subtraction_decimals, 'text'),
            ('subtraction_negative_checkbox',
             self.subtraction_negative_checkbox, 'checked'),
            ('multiplication_count', self.multiplication_count, 'text'),
            ('multiplication_digits', self.multiplication_digits, 'text'),
            ('multiplication_num_operands', self.multiplication_num_operands, 'text'),
            ('multiplication_decimals', self.multiplication_decimals, 'text'),
            ('division_count', self.division_count, 'text'),
            ('division_digits', self.division_digits, 'text'),
            ('division_decimals', self.division_decimals, 'text'),
            ('division_reste_checkbox', self.division_reste_checkbox, 'checked'),
            # Groupes de conjugaison
            ('group_1_checkbox', self.group_1_checkbox, 'checked'),
            ('group_2_checkbox', self.group_2_checkbox, 'checked'),
            ('group_3_checkbox', self.group_3_checkbox, 'checked'),
            ('verbs_per_day_entry', self.verbs_per_day_entry, 'text'),
            ('grammar_sentence_count', self.grammar_sentence_count, 'text'),
            ('intransitive_checkbox', self.intransitive_checkbox, 'checked'),
            ('transitive_direct_checkbox',
             self.transitive_direct_checkbox, 'checked'),
            ('transitive_indirect_checkbox',
             self.transitive_indirect_checkbox, 'checked'),
            ('ditransitive_checkbox', self.ditransitive_checkbox, 'checked'),
            ('transfo_checkboxes', self.transfo_checkboxes, 'checked_list'),
            # Orthographe
            ('orthographe_ex_count', self.orthographe_ex_count, 'text'),
            ('orthographe_homophone_checkboxes',
             self.orthographe_homophone_checkboxes, 'checked_list'),
            #
            ('show_name_checkbox', self.show_name_checkbox, 'checked'),
            ('show_note_checkbox', self.show_note_checkbox, 'checked'),
            ('filename_entry', self.filename_entry, 'text'),
            # Nouveau mode pour variable de chemin
            ('selected_output_path', self, 'path_variable'),
            ('usual_verbs_checkbox', self.usual_verbs_checkbox, 'checked'),
            ('tense_checkboxes', self.tense_checkboxes, 'checked_list'),
            ('geo_ex_count', self.geo_ex_count, 'text'),
            ('geo_conv_type_checkboxes', self.geo_conv_type_checkboxes, 'checked_list'),
            ('conv_sens_direct', self.conv_sens_direct, 'checked'),
            ('conv_sens_inverse', self.conv_sens_inverse, 'checked'),
            # Anglais - phrases à compléter
            ('english_complete_count', self.english_complete_count, 'text'),
            ('english_type_simple', self.english_type_simple, 'checked'),
            ('english_type_complexe', self.english_type_complexe, 'checked'),
            # Anglais - jeux à relier
            ('english_relier_count', self.english_relier_count, 'text'),
            ('relier_count', self.relier_count, 'text'),
            # Encadrement
            ('encadrement_count', self.encadrement_count, 'text'),
            ('encadrement_digits', self.encadrement_digits, 'text'),
            ('encadrement_unite', self.encadrement_unite, 'checked'),
            ('encadrement_dizaine', self.encadrement_dizaine, 'checked'),
            ('encadrement_centaine', self.encadrement_centaine, 'checked'),
            ('encadrement_millier', self.encadrement_millier, 'checked'),
            # Petits Problèmes
            ('math_problems_count', self.math_problems_count, 'text'),
            # Comparer des nombres
            ('compare_numbers_count', self.compare_numbers_count, 'text'),
            ('compare_numbers_digits', self.compare_numbers_digits, 'text'),
            # Suites Logiques
            ('logical_sequences_count', self.logical_sequences_count, 'text'),
            ('logical_sequences_length',
             self.logical_sequences_length, 'text'),  # Nouveau
            ('logical_sequences_type_arithmetic_plus_cb',
             self.logical_sequences_type_arithmetic_plus_cb, 'checked'),
            ('logical_sequences_type_arithmetic_minus_cb',
             self.logical_sequences_type_arithmetic_minus_cb, 'checked'),
            ('logical_sequences_type_arithmetic_multiply_cb',
             self.logical_sequences_type_arithmetic_multiply_cb, 'checked'),
            ('logical_sequences_type_arithmetic_divide_cb',
             self.logical_sequences_type_arithmetic_divide_cb, 'checked'),
            # Les checkboxes de types de problèmes seront ajoutées dynamiquement
            # Ajout pour sauvegarder le niveau
            ('current_level', self, 'level_variable'),
        ]
        # Ajouter dynamiquement les checkboxes de thèmes anglais à config_fields
        if hasattr(self, 'english_relier_theme_checkboxes'):
            for theme_name, cb_widget in self.english_relier_theme_checkboxes.items():
                # La clé de config doit correspondre à celle dans exercise_widgets_map
                self.config_fields.append(
                    (f"english_theme_{theme_name}_cb", cb_widget, 'checked'))

        # Ajouter dynamiquement les checkboxes de types de problèmes mathématiques à config_fields
        if hasattr(self, 'math_problem_type_checkboxes'):
            for type_key, cb_widget in self.math_problem_type_checkboxes.items():
                self.config_fields.append(
                    (f"math_problem_type_{type_key}_cb", cb_widget, 'checked'))

        self.load_config()
        # Set initial visibility based on loaded config (or default)
        self.update_exercise_visibility()

        # Charger la configuration des conversions
        self.conversion_config_data = {}
        try:
            # Les données de conversion sont maintenant dans mesures_generator
            from mesures_generator import CONVERSION_DATA as cg_conversion_data
            self.conversion_config_data = cg_conversion_data
        except ImportError:
            print(
                "Avertissement: Impossible de charger CONVERSION_DATA depuis conversion_generator.")
        except Exception as e:
            print(
                f"Erreur lors du chargement initial des données de conversion: {e}")

        self.days_entry.textChanged.connect(self.validate_days_entry)

    @staticmethod
    def darken_color(hex_color, factor=0.8):
        color = QColor(hex_color)
        r = max(0, min(255, int(color.red() * factor)))
        g = max(0, min(255, int(color.green() * factor)))
        b = max(0, min(255, int(color.blue() * factor)))
        return QColor(r, g, b).name()

        # --- Début des méthodes ---

    def _create_input_row(self, label_text, max_width=60):
        """Crée une ligne QHBoxLayout avec un QLabel et un QLineEdit."""
        # Le widget conteneur pour la ligne entière
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        # Pas de marges internes pour le layout de la ligne
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)  # Espacement entre label et line_edit

        label = QLabel(label_text)
        # Utilise la config
        label.setStyleSheet(UI_STYLE_CONFIG["labels"]["field_label"])
        row_layout.addWidget(label)

        line_edit = QLineEdit()
        # max_width est toujours un int ici
        line_edit.setMaximumWidth(max_width)
        # Le style des QLineEdit sera appliqué globalement via self.all_line_edits
        row_layout.addWidget(line_edit)
        return row_widget, line_edit  # Retourner le widget conteneur et le line_edit

    def _create_generic_groupbox(self, title, fields_config, extra_items=None):
        """
        Crée un QGroupBox avec des champs de saisie et des éléments supplémentaires optionnels.
        fields_config: liste de tuples (label_text, line_edit_attr_name, max_width)
        extra_items: liste de QWidget ou QLayout à ajouter à la fin.
        Retourne le QGroupBox, une liste des QLineEdit créés, et un dict des row_widgets créés.
        """
        group_box = QGroupBox(title)
        group_layout = QVBoxLayout()
        line_edits_created = []
        row_widgets_for_map_part = {}  # Spécifique à cet appel

        for label_text, line_edit_attr_name, max_width_val in fields_config:
            row_widget, line_edit = self._create_input_row(
                label_text, max_width_val)  # row_widget est le QWidget de la ligne
            group_layout.addWidget(row_widget)
            setattr(self, line_edit_attr_name, line_edit)
            line_edits_created.append(line_edit)
            # Stocker le row_widget pour l'ajouter plus tard à exercise_widgets_map
            # Clé pour le QLineEdit dans exercise_widgets_map: "{line_edit_attr_name}_input"
            # Clé pour le row_widget dans exercise_widgets_map: "{line_edit_attr_name}_row"
            row_widgets_for_map_part[f"{line_edit_attr_name}_row"] = row_widget

        if extra_items:
            for item in extra_items:
                if isinstance(item, QLayout):
                    group_layout.addLayout(item)
                elif isinstance(item, QWidget):
                    group_layout.addWidget(item)
        group_box.setLayout(group_layout)
        return group_box, line_edits_created, row_widgets_for_map_part

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Choisir le dossier de sortie", self.selected_output_path or os.getcwd())
        if directory:
            self.selected_output_path = os.path.normpath(
                directory)  # Normaliser le chemin
        self._update_output_path_display(self.selected_output_path)

    def select_level(self, level_name, clicked_button):
        # 1. Gérer la sélection/désélection de self.current_level et self.current_selected_level_button
        if self.current_level == level_name:  # Clicked on already selected level
            self.current_level = None  # Deselect
            self.current_selected_level_button = None
        else:
            self.current_level = level_name
            self.current_selected_level_button = clicked_button

        # 2. Mettre à jour les styles et l'opacité de TOUS les boutons de niveau
        for ln_iter, btn_iter in self.level_buttons.items():
            original_color_hex = self.LEVEL_COLORS[ln_iter]
            hover_color = self.darken_color(original_color_hex, 0.95)
            pressed_color = self.darken_color(original_color_hex, 0.85)
            border_c = self.darken_color(original_color_hex, 0.7)

            is_currently_iter_selected_button = (
                btn_iter == self.current_selected_level_button)
            # Propriété pour le style
            btn_iter.setProperty("selected", is_currently_iter_selected_button)

            # Appliquer le style de base (qui réagit à la propriété "selected")
            style_str = self.BASE_LEVEL_BUTTON_STYLE.format(
                text_color=UI_STYLE_CONFIG["buttons"]["level_button_text_color"],
                bg_color=original_color_hex,
                hover_bg_color=hover_color,
                pressed_bg_color=pressed_color,
                border_color=border_c
            )
            btn_iter.setStyleSheet(style_str)
            # Forcer la réévaluation du style pour que la propriété "selected" soit prise en compte
            btn_iter.style().unpolish(btn_iter)
            btn_iter.style().polish(btn_iter)
            btn_iter.update()  # Forcer un rafraîchissement visuel immédiat

            # Gérer l'opacité
            opacity_effect = btn_iter.graphicsEffect()
            # S'il n'y a pas d'effet ou si ce n'est pas le bon type
            if not isinstance(opacity_effect, QGraphicsOpacityEffect):
                if opacity_effect:  # Supprimer un ancien effet d'un autre type si existant
                    opacity_effect.deleteLater()
                opacity_effect = QGraphicsOpacityEffect(btn_iter)
                btn_iter.setGraphicsEffect(opacity_effect)

            if is_currently_iter_selected_button or not self.current_selected_level_button:
                # Si c'est le bouton sélectionné OU si aucun bouton n'est sélectionné (tout est actif)
                opacity_effect.setOpacity(1.0)  # Pleinement opaque
            else:
                # Ce n'est pas le bouton sélectionné, ET un autre bouton EST sélectionné -> griser celui-ci
                opacity_effect.setOpacity(0.55)  # Valeur pour griser

        # QTimer pour s'assurer que les mises à jour de style sont appliquées après le traitement des événements
        QTimer.singleShot(0, self._refresh_level_button_styles)

        # print(f"Niveau sélectionné : {self.current_level}")
        self.update_exercise_visibility()

    def _refresh_level_button_styles(self):
        for btn_iter in self.level_buttons.values():
            btn_iter.style().unpolish(btn_iter)
            btn_iter.style().polish(btn_iter)
            btn_iter.update()

    def get_int(self, lineedit, default=0, field_name=None):
        value = lineedit.text().strip()
        if value == '':
            return default
        if value.isdigit():
            return int(value)
        else:
            raise InvalidFieldError(field_name or lineedit.objectName(), value)

    def validate_days_entry(self):
        value = self.days_entry.text().strip()
        is_valid = value.isdigit() and int(value) > 0
        style = UI_STYLE_CONFIG["line_edits"]["default"]
        if not is_valid:
            # Ajouter la bordure rouge spécifique pour l'invalidité
            style += UI_STYLE_CONFIG["line_edits"]["days_invalid_border"]
        self.days_entry.setStyleSheet(style)
        self.generate_pdf_button.setEnabled(is_valid)
        self.generate_word_button.setEnabled(is_valid)
        self.preview_pdf_button.setEnabled(is_valid)
        self.preview_word_button.setEnabled(is_valid)

    def build_exercise_data(self):
        try:
            from exercise_data_builder import ExerciseDataBuilder
            from conjugation_generator import TENSES, VERBS  # OK
            from grammar_generator import get_random_phrases, get_random_transformation
            from mesures_generator import generate_conversion_exercises  # Modifié
            from anglais_generator import PHRASES_SIMPLES, PHRASES_COMPLEXES, MOTS_A_RELIER
            # print(f"Apprentium.build_exercise_data: self.current_level is {self.current_level} at start.") # Debug print

            # Get allowed keys for the current level
            allowed_keys = self.get_exercises_for_level(self.current_level)

            # Génération des exercices d'encadrement
            # Les paramètres pour l'encadrement sont collectés ici et passés à ExerciseDataBuilder
            # ExerciseDataBuilder appellera ensuite une fonction de mesures_generator.py par jour.
            encadrement_params_for_builder = {
                'count': self.get_int(self.encadrement_count, field_name="Encadrement - nombre d'exercices") if "geo_encadrement_group" in allowed_keys else 0,
                'digits': self.get_int(self.encadrement_digits, field_name="Encadrement - chiffres par nombre") if "geo_encadrement_group" in allowed_keys else 0,
                'types': [name for cb, name, key in zip(
                    [self.encadrement_unite, self.encadrement_dizaine,
                        self.encadrement_centaine, self.encadrement_millier],
                    ["unité", "dizaine", "centaine", "millier"],
                    ["encadrement_unite_cb", "encadrement_dizaine_cb",
                        "encadrement_centaine_cb", "encadrement_millier_cb"]
                ) if key in allowed_keys and cb.isChecked()]
            }

            # Génération des exercices anglais (phrases à compléter + jeux à relier)
            from anglais_generator import generate_english_full_exercises
            # english_types = self.get_selected_english_types()
            n_complete = self.get_int(
                self.english_complete_count) if "english_complete_group" in allowed_keys else 0
            n_relier = self.get_int(
                self.english_relier_count) if "english_relier_group" in allowed_keys else 0
            n_mots_reliés = self.get_int(
                self.relier_count) if "english_relier_group" in allowed_keys else 0  # Garder pour params
            # La génération effective des english_exercises se fera dans ExerciseDataBuilder

            # Ranger les nombres - Logique améliorée
            # Thèmes anglais sélectionnés
            # print(f"DEBUG Apprentium: allowed_keys pour le niveau '{self.current_level}': {allowed_keys}")
            selected_english_themes = []
            # Vérifier si la section "jeux à relier" est active
            if hasattr(self, 'english_relier_theme_checkboxes') and "english_relier_group" in allowed_keys:
                for theme_name, cb in self.english_relier_theme_checkboxes.items():
                    theme_cb_key = f"english_theme_{theme_name}_cb"
                    # Vérifier si la checkbox de thème elle-même est autorisée par le niveau actuel ET cochée
                    if theme_cb_key in allowed_keys and cb.isChecked():
                        selected_english_themes.append(theme_name)
            # print(f"DEBUG Apprentium: Thèmes anglais sélectionnés: {selected_english_themes}")

            sort_count_val = self.get_int(
                self.sort_count, field_name="Ranger - nombre d'exercices") if "geo_sort_group" in allowed_keys else 0
            is_croissant_selected = self.sort_type_croissant.isChecked(
            ) if "sort_type_croissant_cb" in allowed_keys else False
            is_decroissant_selected = self.sort_type_decroissant.isChecked(
            ) if "sort_type_decroissant_cb" in allowed_keys else False

            # Petits Problèmes Mathématiques
            math_problems_count_val = self.get_int(
                self.math_problems_count, field_name="Nombre de problèmes") if "math_problems_group" in allowed_keys else 0
            selected_math_problem_types = []
            if hasattr(self, 'math_problem_type_checkboxes') and "math_problems_group" in allowed_keys:
                for type_key, cb_widget in self.math_problem_type_checkboxes.items():
                    # Clé dans exercise_widgets_map
                    type_cb_key_map = f"math_problem_type_{type_key}_cb"
                    if type_cb_key_map in allowed_keys and cb_widget.isChecked():
                        # Utiliser la clé JSON (ex: "addition_simple")
                        selected_math_problem_types.append(type_key)

            # Suites Logiques
            logical_sequences_count_val = self.get_int(
                self.logical_sequences_count, field_name="Suites Logiques - nombre d'exercices") if "geo_logical_sequences_group" in allowed_keys else 0
            logical_sequences_length_val = self.get_int(
                self.logical_sequences_length, default=5, field_name="Suites Logiques - nombre d'éléments") if "logical_sequences_length_input" in allowed_keys else 5
            logical_sequences_params_for_builder = {
                'count': logical_sequences_count_val,
                'length': logical_sequences_length_val,
                'types': [],
                # Le 'step' n'est plus récupéré de l'UI
            }
            if "logical_sequences_type_arithmetic_plus_cb" in allowed_keys and self.logical_sequences_type_arithmetic_plus_cb.isChecked():
                logical_sequences_params_for_builder['types'].append(
                    'arithmetic_plus')
            if "logical_sequences_type_arithmetic_minus_cb" in allowed_keys and self.logical_sequences_type_arithmetic_minus_cb.isChecked():
                logical_sequences_params_for_builder['types'].append(
                    'arithmetic_minus')
            if "logical_sequences_type_arithmetic_multiply_cb" in allowed_keys and self.logical_sequences_type_arithmetic_multiply_cb.isChecked():
                logical_sequences_params_for_builder['types'].append(
                    'arithmetic_multiply')
            if "logical_sequences_type_arithmetic_divide_cb" in allowed_keys and self.logical_sequences_type_arithmetic_divide_cb.isChecked():
                logical_sequences_params_for_builder['types'].append(
                    'arithmetic_divide')

            # Si aucun type de suite n'est coché
            if not logical_sequences_params_for_builder['types']:
                # Ne pas générer d'exercices de suite
                logical_sequences_params_for_builder['count'] = 0

            if not is_croissant_selected and not is_decroissant_selected:  # Si aucun type de tri n'est sélectionné
                sort_count_val = 0

            params = {
                # Enumérer un nombre
                'enumerate_count': self.get_int(self.enumerate_count, field_name="Enumérer - nombre d'exercices") if "enumerate_group" in allowed_keys else 0,
                'enumerate_digits': self.get_int(self.enumerate_digits, field_name="Enumérer - chiffres par nombre") if "enumerate_group" in allowed_keys else 0,
                # Ranger les nombres
                'sort_count': sort_count_val,
                'sort_digits': self.get_int(self.sort_digits, field_name="Ranger - chiffres par nombre") if "geo_sort_group" in allowed_keys and sort_count_val > 0 else 0,
                'sort_n_numbers': self.get_int(self.sort_n_numbers, field_name="Ranger - nombres à ranger") if "geo_sort_group" in allowed_keys and sort_count_val > 0 else 0,
                'sort_type_croissant': is_croissant_selected,
                'sort_type_decroissant': is_decroissant_selected,
                'days': self.get_int(self.days_entry, field_name="Nombre de jours"),
                'relier_count': n_mots_reliés,  # Already filtered based on english_relier_group
                'addition_count': self.get_int(self.addition_count, field_name="Addition - nombre de calculs") if "addition_group" in allowed_keys else 0,
                'addition_num_operands': self.get_int(self.addition_num_operands, default=2, field_name="Addition - nombre d'opérandes") if "addition_num_operands_input" in allowed_keys else 2,
                'addition_digits': self.get_int(self.addition_digits, field_name="Addition - chiffres") if "addition_group" in allowed_keys else 0,
                'addition_decimals': self.get_int(self.addition_decimals, field_name="Addition - décimales") if "addition_decimals_input" in allowed_keys else 0,
                'subtraction_count': self.get_int(self.subtraction_count, field_name="Soustraction - nombre de calculs") if "subtraction_group" in allowed_keys else 0,
                'subtraction_num_operands': self.get_int(self.subtraction_num_operands, default=2, field_name="Soustraction - nombre d'opérandes") if "subtraction_num_operands_input" in allowed_keys else 2,
                'subtraction_digits': self.get_int(self.subtraction_digits, field_name="Soustraction - chiffres") if "subtraction_group" in allowed_keys else 0,
                'subtraction_decimals': self.get_int(self.subtraction_decimals, field_name="Soustraction - décimales") if "subtraction_decimals_input" in allowed_keys else 0,
                'subtraction_negative': self.subtraction_negative_checkbox.isChecked() if "subtraction_negative_cb" in allowed_keys else False,
                'multiplication_count': self.get_int(self.multiplication_count, field_name="Multiplication - nombre de calculs") if "multiplication_group" in allowed_keys else 0,
                'multiplication_num_operands': self.get_int(self.multiplication_num_operands, default=2, field_name="Multiplication - nombre d'opérandes") if "multiplication_num_operands_input" in allowed_keys else 2,
                'multiplication_digits': self.get_int(self.multiplication_digits, field_name="Multiplication - chiffres") if "multiplication_group" in allowed_keys else 0,
                'multiplication_decimals': self.get_int(self.multiplication_decimals, field_name="Multiplication - décimales") if "multiplication_decimals_input" in allowed_keys else 0,
                'division_count': self.get_int(self.division_count, field_name="Division - nombre de calculs") if "division_group" in allowed_keys else 0,
                'division_digits': self.get_int(self.division_digits, field_name="Division - chiffres") if "division_group" in allowed_keys else 0,
                'division_decimals': self.get_int(self.division_decimals, field_name="Division - décimales") if "division_decimals_input" in allowed_keys else 0,
                'division_reste': self.division_reste_checkbox.isChecked() if "division_reste_cb" in allowed_keys else False,
                'TENSES': TENSES,
                'VERBS': VERBS,
                'grammar_sentence_count': self.get_int(self.grammar_sentence_count, field_name="Grammaire - nombre de phrases") if "grammar_params_group" in allowed_keys else 0,
                'grammar_types': [t_name for t_name, cb_key, cb_widget in zip(['intransitive', 'transitive_direct', 'transitive_indirect', 'ditransitive'], ["intransitive_cb", "transitive_direct_cb", "transitive_indirect_cb", "ditransitive_cb"], [self.intransitive_checkbox, self.transitive_direct_checkbox, self.transitive_indirect_checkbox, self.ditransitive_checkbox]) if cb_key in allowed_keys and cb_widget.isChecked()],
                'get_random_phrases': get_random_phrases,
                'get_random_transformation': get_random_transformation,
                'generate_conversion_exercises': generate_conversion_exercises,
                'geo_ex_count': self.get_int(self.geo_ex_count, field_name="Géométrie/mesures - nombre d'exercices") if "geo_conv_group" in allowed_keys else 0,
                'geo_types': [label for cb, label, cb_key in zip(self.geo_conv_type_checkboxes, ['longueur', 'masse', 'volume', 'temps', 'monnaie'], ["conv_type_longueur_cb", "conv_type_masse_cb", "conv_type_volume_cb", "conv_type_temps_cb", "conv_type_monnaie_cb"]) if cb_key in allowed_keys and cb.isChecked()],
                'geo_senses': [sense for sense, cb_key, cb_widget in zip(['direct', 'inverse'], ["conv_sens_direct_cb", "conv_sens_inverse_cb"], [self.conv_sens_direct, self.conv_sens_inverse]) if cb_key in allowed_keys and cb_widget.isChecked()],
                'english_types': [etype for etype, cb_key, cb_widget in zip(['simple', 'complexe'], ["english_type_simple_cb", "english_type_complexe_cb"], [self.english_type_simple, self.english_type_complexe]) if cb_key in allowed_keys and cb_widget.isChecked()],
                'PHRASES_SIMPLES': PHRASES_SIMPLES,
                'PHRASES_COMPLEXES': PHRASES_COMPLEXES,
                'MOTS_A_RELIER': MOTS_A_RELIER,
                # Anglais
                'english_complete_count': n_complete,  # Already filtered
                'english_relier_count': n_relier,     # Already filtered
                # Orthographe
                # AJOUT DE CETTE LIGNE
                'generate_english_full_exercises_func': generate_english_full_exercises,
                'orthographe_ex_count': self.get_int(self.orthographe_ex_count, field_name="Orthographe - nombre d'exercices") if "ortho_params_group" in allowed_keys else 0,
                # Encadrement
                'encadrement_params': encadrement_params_for_builder,
                # Comparer des nombres
                'compare_numbers_count': self.get_int(self.compare_numbers_count, field_name="Comparer - nombre d'exercices") if "geo_compare_numbers_group" in allowed_keys else 0,
                'compare_numbers_digits': self.get_int(self.compare_numbers_digits, field_name="Comparer - chiffres par nombre") if "geo_compare_numbers_group" in allowed_keys else 0,
                # Suites Logiques
                'logical_sequences_params': logical_sequences_params_for_builder,
                # Petits Problèmes
                'math_problems_count': math_problems_count_val,
                'selected_math_problem_types': selected_math_problem_types,
                # Pour filtrer les problèmes par niveau dans le générateur
                'current_level_for_problems': self.current_level,
                'selected_english_themes': selected_english_themes,
                'current_level_for_conversions': self.current_level
            }

            verbs_per_day_val = self.get_int(
                self.verbs_per_day_entry, field_name="Verbes par jour") if "conj_params_group" in allowed_keys else 0

            # Modifié
            params['generate_math_problems_func'] = generate_story_math_problems
            # Construction corrigée pour conjugation_tenses
            conjugation_tenses_list = []
            for i, tense_cb_widget in enumerate(self.tense_checkboxes):
                tense_cb_key = None
                for map_key, map_widget in self.exercise_widgets_map.items():
                    if map_widget == tense_cb_widget:
                        tense_cb_key = map_key
                        break
                if tense_cb_key and tense_cb_key in allowed_keys and tense_cb_widget.isChecked():
                    conjugation_tenses_list.append(TENSES[i])
            params['conjugation_tenses'] = conjugation_tenses_list

            # Groupes de conjugaison et verbes usuels
            conjugation_groups_selected = [g for g, cb_key, cb_widget in zip([1, 2, 3], ["group_1_cb", "group_2_cb", "group_3_cb"], [
                                                                             self.group_1_checkbox, self.group_2_checkbox, self.group_3_checkbox]) if cb_key in allowed_keys and cb_widget.isChecked()]
            is_usual_verbs_selected = self.usual_verbs_checkbox.isChecked(
            ) if "usual_verbs_cb" in allowed_keys else False
            params['conjugation_groups'] = conjugation_groups_selected
            params['conjugation_usual'] = is_usual_verbs_selected

            if not conjugation_tenses_list or (not conjugation_groups_selected and not is_usual_verbs_selected):
                # Ne pas générer si pas de temps OU (pas de groupe ET pas d'usuels)
                verbs_per_day_val = 0
            params['verbs_per_day'] = verbs_per_day_val
            # Construction corrigée pour grammar_transformations
            grammar_transformations_list = []
            for transfo_cb_widget in self.transfo_checkboxes:
                transfo_cb_key = None
                for map_key, map_widget in self.exercise_widgets_map.items():
                    if map_widget == transfo_cb_widget:
                        transfo_cb_key = map_key
                        break
                if transfo_cb_key and transfo_cb_key in allowed_keys and transfo_cb_widget.isChecked():
                    grammar_transformations_list.append(
                        transfo_cb_widget.text())
            params['grammar_transformations'] = grammar_transformations_list

            # Construction corrigée pour orthographe_homophones
            orthographe_homophones_list = []
            for ortho_cb_widget in self.orthographe_homophone_checkboxes:
                ortho_cb_key = None
                for map_key, map_widget in self.exercise_widgets_map.items():
                    if map_widget == ortho_cb_widget:
                        ortho_cb_key = map_key
                        break
                if ortho_cb_key and ortho_cb_key in allowed_keys and ortho_cb_widget.isChecked():
                    orthographe_homophones_list.append(ortho_cb_widget.text())
            params['orthographe_homophones'] = orthographe_homophones_list

            # print(f"Apprentium.build_exercise_data: Calling ExerciseDataBuilder.build with params['current_level_for_conversions'] = {params.get('current_level_for_conversions')}") # Debug print
            result = ExerciseDataBuilder.build(params)
            if result is None:
                # Si ExerciseDataBuilder.build retourne None, on ne peut pas continuer.
                print(
                    "Erreur critique : ExerciseDataBuilder.build n'a pas pu construire les données d'exercices.")
                # result['encadrement_exercises'] n'est plus nécessaire ici, géré par le builder
                return None
            # result['english_exercises'] est maintenant rempli par ExerciseDataBuilder
            return result
        except InvalidFieldError as e:
            print(
                f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite : {type(e).__name__} : {e}")
            traceback.print_exc()

    def generate_pdf(self):
        try:
            data = self.build_exercise_data()
            if data is None:
                return
            from pdf_generator import generate_workbook_pdf
            header_text = self.header_entry.text().strip()
            show_name = self.show_name_checkbox.isChecked()
            show_note = self.show_note_checkbox.isChecked()
            filename = self.filename_entry.text().strip() or "workbook"
            output_directory = self.selected_output_path  # Utilise le chemin stocké
            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"
            output_path = generate_workbook_pdf(
                data['days'], data['operations'], data['counts'], data['max_digits'],
                data['conjugations'], data['params_list'], data['grammar_exercises'],
                data['orthographe_exercises'],
                data['enumerate_exercises'], data['sort_exercises'],
                geo_exercises=data['geo_exercises'], english_exercises=data['english_exercises'],
                encadrement_exercises_list=data.get(
                    'encadrement_exercises_list'),
                compare_numbers_exercises_list=data.get(
                    'compare_numbers_exercises_list'),  # Nouveau
                logical_sequences_exercises_list=data.get(
                    'logical_sequences_exercises_list'),  # Nouveau
                story_math_problems_by_day=data.get('math_problems'),
                header_text=header_text, show_name=show_name, show_note=show_note, filename=filename,
                output_dir_override=output_directory
            )
            if output_path and os.path.exists(output_path):
                print(f"PDF généré avec succès : {output_path}")
        except InvalidFieldError as e:
            print(
                f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite : {type(e).__name__} : {e}")
            traceback.print_exc()

    def generate_word(self):
        try:
            data = self.build_exercise_data()
            if data is None:
                return
            from word_generator import generate_workbook_docx
            header_text = self.header_entry.text().strip()
            show_name = self.show_name_checkbox.isChecked()
            show_note = self.show_note_checkbox.isChecked()
            filename = self.filename_entry.text().strip() or "workbook"
            output_directory = self.selected_output_path  # Utilise le chemin stocké
            if not filename.lower().endswith(".docx"):
                filename += ".docx"
            output_path = generate_workbook_docx(
                data['days'], data['operations'], data['counts'], data['max_digits'],
                data['conjugations'], data['params_list'], data['grammar_exercises'],
                # Passer toutes les données d'exercices comme pour le PDF
                orthographe_exercises=data['orthographe_exercises'],
                enumerate_exercises=data['enumerate_exercises'],
                sort_exercises=data['sort_exercises'],
                geo_exercises=data['geo_exercises'],
                english_exercises=data['english_exercises'],
                encadrement_exercises_list=data.get(
                    'encadrement_exercises_list'),
                compare_numbers_exercises_list=data.get(
                    'compare_numbers_exercises_list'),  # Nouveau
                logical_sequences_exercises_list=data.get(
                    'logical_sequences_exercises_list'),  # Nouveau
                story_math_problems_by_day=data.get('math_problems'),
                header_text=header_text, show_name=show_name, show_note=show_note, filename=filename,
                output_dir_override=output_directory
            )
            if output_path and os.path.exists(output_path):
                print(f"Word généré avec succès : {output_path}")
        except InvalidFieldError as e:
            print(
                f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite : {type(e).__name__} : {e}")
            traceback.print_exc()

    def preview_pdf(self):
        try:
            data = self.build_exercise_data()
            if data is None:
                return

            from pdf_generator import generate_workbook_pdf
            header_text = self.header_entry.text().strip()
            show_name = self.show_name_checkbox.isChecked()
            show_note = self.show_note_checkbox.isChecked()
            filename = self.filename_entry.text().strip() or "Apprentium"
            # Utiliser le chemin pour l'aperçu aussi
            output_directory = self.selected_output_path
            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"

            output_path = generate_workbook_pdf(
                data['days'], data['operations'], data['counts'], data['max_digits'],
                data['conjugations'], data['params_list'], data['grammar_exercises'],
                data['orthographe_exercises'], data['enumerate_exercises'], data['sort_exercises'],
                # Modifié
                geo_exercises=data['geo_exercises'], english_exercises=data['english_exercises'],
                encadrement_exercises_list=data.get(
                    'encadrement_exercises_list'),
                compare_numbers_exercises_list=data.get(
                    'compare_numbers_exercises_list'),  # Nouveau
                logical_sequences_exercises_list=data.get(
                    'logical_sequences_exercises_list'),  # Nouveau
                story_math_problems_by_day=data.get('math_problems'),
                header_text=header_text, show_name=show_name, show_note=show_note, filename=filename,
                output_dir_override=output_directory
            )

            if output_path and os.path.exists(output_path):
                # Ouvre le fichier avec l'application par défaut (Windows)
                os.startfile(output_path)
            else:
                print(
                    f"Erreur : Fichier PDF non trouvé à {output_path} après la génération pour l'aperçu.")
        except InvalidFieldError as e:
            print(
                f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(
                f"Une erreur s'est produite lors de la prévisualisation PDF : {type(e).__name__} : {e}")
            traceback.print_exc()

    def preview_word(self):
        try:
            data = self.build_exercise_data()
            if data is None:
                return
            from word_generator import generate_workbook_docx
            header_text = self.header_entry.text().strip()
            show_name = self.show_name_checkbox.isChecked()
            show_note = self.show_note_checkbox.isChecked()
            filename = self.filename_entry.text().strip() or "apercu_Apprentium"
            # Utiliser le chemin pour l'aperçu aussi
            output_directory = self.selected_output_path
            if not filename.lower().endswith(".docx"):
                filename += ".docx"
            output_path = generate_workbook_docx(
                data['days'], data['operations'], data['counts'], data['max_digits'],
                data['conjugations'], data['params_list'], data['grammar_exercises'],
                orthographe_exercises=data['orthographe_exercises'],
                enumerate_exercises=data['enumerate_exercises'],
                sort_exercises=data['sort_exercises'],
                geo_exercises=data['geo_exercises'],  # Modifié
                english_exercises=data['english_exercises'],
                encadrement_exercises_list=data.get(
                    'encadrement_exercises_list'),  # Nouveau
                compare_numbers_exercises_list=data.get(
                    'compare_numbers_exercises_list'),  # Nouveau
                logical_sequences_exercises_list=data.get(
                    'logical_sequences_exercises_list'),
                story_math_problems_by_day=data.get('math_problems'),
                header_text=header_text, show_name=show_name, show_note=show_note, filename=filename,
                output_dir_override=output_directory)
            if output_path and os.path.exists(output_path):
                # Ouvre le fichier avec l'application par défaut (Windows)
                os.startfile(output_path)
            else:
                print(
                    f"Erreur : Fichier Word non trouvé à {output_path} après la génération pour l'aperçu.")
        except InvalidFieldError as e:
            print(
                f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(
                f"Une erreur s'est produite lors de la prévisualisation Word : {type(e).__name__} : {e}")
            traceback.print_exc()

    def save_config(self):
        config = {}
        for name, widget, mode in self.config_fields:
            if mode == 'text':
                config[name] = widget.text()
            elif mode == 'checked':
                config[name] = widget.isChecked()
            elif mode == 'checked_list':
                config[name] = [cb.isChecked() for cb in widget]
            # 'widget' est self (MainWindow) ici
            elif mode == 'level_variable':
                # Sauvegarde le nom du niveau actuel
                config[name] = widget.current_level
            elif mode == 'path_variable':
                # Sauvegarde la variable directement
                config[name] = self.selected_output_path
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration : {e}")

    def load_config(self):
        if not os.path.exists(self.config_path):
            # Crée un fichier config.json vide si absent (pour PyInstaller)
            try:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
            except Exception as e:
                print(f"Erreur lors de la création de la configuration : {e}")
            return
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # widget_ref est le widget/objet stocké dans config_fields
            for name, widget_ref, mode in self.config_fields:
                if name not in config:
                    continue
                if mode == 'text':
                    widget_ref.setText(config.get(name, ''))
                elif mode == 'checked':
                    widget_ref.setChecked(config.get(name, False))
                elif mode == 'checked_list':
                    states = config.get(name, [False]*len(widget_ref))
                    for cb, state in zip(widget_ref, states):
                        cb.setChecked(state)
                elif mode == 'path_variable':
                    # Pour 'path_variable', widget_ref est 'self' (MainWindow)
                    self.selected_output_path = config.get(name, None)
                    self._update_output_path_display(
                        self.selected_output_path)  # Mettre à jour l'affichage
                elif mode == 'level_variable':
                    # Pour 'level_variable', widget_ref est 'self' (MainWindow)
                    # 'name' est 'current_level'
                    loaded_level_name = config.get(name, None)
                    if loaded_level_name and loaded_level_name in self.level_buttons:  # Accéder à self.level_buttons
                        button_to_select = self.level_buttons[loaded_level_name]
                        # Appeler select_level pour restaurer l'état du niveau
                        # Cela mettra à jour self.current_level et l'UI
                        self.select_level(loaded_level_name, button_to_select)
        except FileNotFoundError:
            print(
                f"Fichier de configuration non trouvé : {self.config_path}. Un nouveau sera créé à la fermeture si nécessaire.")
        except json.JSONDecodeError:
            print(
                f"Erreur de décodage JSON dans {self.config_path}. Le fichier est peut-être corrompu.")
        except Exception as e:
            print(
                f"Erreur inattendue lors du chargement de la configuration : {type(e).__name__} - {e}")
            # import traceback; traceback.print_exc() # Décommenter pour un débogage plus détaillé

    def closeEvent(self, event):
        self.save_config()
        super().closeEvent(event)

    def get_exercises_for_level(self, target_level):
        if not target_level:  # If None or empty string, show all exercises
            return list(self.exercise_widgets_map.keys())

        allowed_exercises = set()
        # Iterate through LEVEL_ORDER up to and including target_level
        for level_in_order in self.LEVEL_ORDER:
            allowed_exercises.update(
                self.EXERCISES_BY_LEVEL_INCREMENTAL.get(level_in_order, []))
            if level_in_order == target_level:
                break
        return list(allowed_exercises)

    def update_exercise_visibility(self):
        allowed_exercise_keys = self.get_exercises_for_level(
            self.current_level)

        # 1. Mettre à jour la visibilité des composants d'exercice individuels (QGroupBox, QLineEdit, etc.)
        for key, widget in self.exercise_widgets_map.items():
            if widget:  # Ensure widget exists
                if key in allowed_exercise_keys:
                    widget.show()
                else:
                    widget.hide()

        # 2. Déterminer l'activité de chaque colonne principale et la visibilité de son titre
        #    et des conteneurs de section (pour Ortho/Anglais).
        #    Une colonne est active si au moins un de ses QGroupBoxes est autorisé pour le niveau.

        is_calc_column_active = False
        for section_key in self.column_section_keys.get("calc", []):
            if section_key in allowed_exercise_keys:  # Vérifier si le QGroupBox lui-même est autorisé
                is_calc_column_active = True
                break
        self.calc_title_label.setVisible(is_calc_column_active)

        is_geo_column_active = False
        for section_key in self.column_section_keys.get("geo", []):
            if section_key in allowed_exercise_keys:
                is_geo_column_active = True
                break
        self.geo_title_label.setVisible(is_geo_column_active)

        is_conj_column_active = False
        for section_key in self.column_section_keys.get("conj", []):
            if section_key in allowed_exercise_keys:
                is_conj_column_active = True
                break
        self.conj_title_label.setVisible(is_conj_column_active)

        is_grammar_column_active = False
        for section_key in self.column_section_keys.get("grammar", []):
            if section_key in allowed_exercise_keys:
                is_grammar_column_active = True
                break
        self.grammar_title_label.setVisible(is_grammar_column_active)

        # Pour la colonne combinée Orthographe/Anglais
        is_ortho_section_active = False
        for section_key in self.column_section_keys.get("ortho", []):
            if section_key in allowed_exercise_keys:
                is_ortho_section_active = True
                break
        self.orthographe_title_label.setVisible(is_ortho_section_active)
        self.orthographe_section_widget.setVisible(
            is_ortho_section_active)  # Important pour le contenu

        is_english_section_active = False
        for section_key in self.column_section_keys.get("english", []):
            if section_key in allowed_exercise_keys:
                is_english_section_active = True
                break
        self.english_title_label.setVisible(is_english_section_active)
        self.english_section_widget.setVisible(
            is_english_section_active)  # Important pour le contenu
        is_ortho_anglais_column_active = is_ortho_section_active or is_english_section_active

        # 3. Préparer les listes pour la réorganisation du QSplitter
        column_activity_map = {
            'calc': is_calc_column_active,
            'geo': is_geo_column_active,
            'conj': is_conj_column_active,
            'ortho_anglais': is_ortho_anglais_column_active,
            'grammar': is_grammar_column_active
        }

        active_column_configs = []
        inactive_column_configs = []

        for config in self.splitter_column_configs_initial_order:
            if column_activity_map.get(config['key'], False):
                active_column_configs.append(config)
            else:
                inactive_column_configs.append(config)

        final_ordered_configs = active_column_configs + inactive_column_configs

        # 4. Réorganiser les widgets dans le QSplitter
        # Détacher tous les widgets actuels du splitter pour éviter les problèmes de ré-ajout
        # et pour s'assurer que l'ordre est correctement appliqué.
        widgets_in_splitter_before_reorder = []
        for i in range(self.splitter.count()):
            widgets_in_splitter_before_reorder.append(self.splitter.widget(i))

        for w_to_detach in widgets_in_splitter_before_reorder:
            w_to_detach.setParent(None)  # Détache le widget du splitter

        # Ajouter les widgets dans le nouvel ordre et réappliquer les stretch factors
        for i, config_to_add in enumerate(final_ordered_configs):
            self.splitter.addWidget(config_to_add['widget'])
            self.splitter.setStretchFactor(i, config_to_add['stretch'])
            # S'assurer que le widget de colonne est visible
            config_to_add['widget'].show()

        # Forcer la réinitialisation de la distribution des tailles pour que les stretch factors s'appliquent correctement
        if self.splitter.count() > 0:
            # Petites tailles initiales égales
            sizes = [1] * self.splitter.count()
            self.splitter.setSizes(sizes)

    def get_selected_conversion_types(self):
        types = []
        labels = ['longueur', 'masse', 'volume', 'temps', 'monnaie']
        for cb, label in zip(self.geo_conv_type_checkboxes, labels):
            if cb.isChecked():
                types.append(label)
        return types

    def get_selected_conversion_senses(self):
        senses = []
        if self.conv_sens_direct.isChecked():
            senses.append('direct')
        if self.conv_sens_inverse.isChecked():
            senses.append('inverse')
        return senses

    def get_selected_english_types(self):
        types = []
        if self.english_type_simple.isChecked():
            types.append('simple')
        if self.english_type_complexe.isChecked():
            types.append('complexe')
        return types

    def toggle_relier_count(self):
        if self.english_type_relier.isChecked():
            self.relier_count_label.show()
            self.relier_count.show()
        else:
            self.relier_count_label.hide()
            self.relier_count.hide()
# Note : Pour PyInstaller, les fichiers JSON (phrases_grammaire.json, verbes.json, config.json) doivent être à côté de l'exe pour être modifiables après compilation.

    def _update_output_path_display(self, full_path):
        """Met à jour le label affichant le chemin de sortie, en le raccourcissant si nécessaire."""
        prefix = "Dossier : "
        # Ce qui est affiché si aucun chemin absolu n'est défini
        default_relative_path = "output/"
        # Longueur maximale approximative du chemin affiché (sans le préfixe)
        max_display_len = 40

        cfg_labels = UI_STYLE_CONFIG["labels"]
        if not full_path:
            self.output_path_display_label.setText(
                prefix + default_relative_path)
            self.output_path_display_label.setStyleSheet(
                cfg_labels["output_path_display_default"])
        else:
            display_path = full_path
            if len(full_path) > max_display_len:
                parts = full_path.split(os.sep)
                if len(parts) > 4:  # Assez de parties pour raccourcir (lecteur + ... + 3 dossiers)
                    display_path = parts[0] + os.sep + "..." + os.sep + \
                        os.path.join(parts[-3], parts[-2], parts[-1])

            self.output_path_display_label.setText(prefix + display_path)
            self.output_path_display_label.setStyleSheet(
                cfg_labels["output_path_display_set"])


if __name__ == "__main__":
    from PyQt6.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), "Apprentium.ico")
    app = QApplication([])
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    app.exec()
