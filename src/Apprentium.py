from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QFrame, QTabWidget, QGroupBox, QSplitter, QFileDialog, QLayout, QGraphicsOpacityEffect, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtGui import QIcon
import json
import os 
import sys

# Import de la config
from gui.template import UI_STYLE_CONFIG 
# Import du header
from gui.header import AppHeader 
# Import du footer
from gui.footer import AppFooter 
# import des filtres
from gui.filter_widgets import create_input_row, create_generic_groupbox 
# import des colonnes
from gui.calcul_widgets import CalculsColumn
from gui.grammaire_widgets import GrammarColumn
from gui.orthographe_widgets import OrthographeColumn
from gui.anglais_widgets import AnglaisColumn
from gui.conjugaison_widgets import ConjugaisonColumn
from gui.mesures_widgets import MesuresColumn
from gui.settings_tab import SettingsTab
from gui.cours_widgets import CoursColumn

# Imports déplacés pour une meilleure organisation
from calculs_generator import generate_story_math_problems
from conjugation_generator import TENSES, VERBS
from grammar_generator import get_random_phrases, get_random_transformation
from mesures_generator import generate_measurement_story_problems, generate_conversion_exercises
from anglais_generator import PHRASES_SIMPLES, PHRASES_COMPLEXES, MOTS_A_RELIER
from exercise_data_builder import ExerciseDataBuilder
from pdf_generator import generate_workbook_pdf
from word_generator import generate_workbook_docx

class InvalidFieldError(Exception):
    def __init__(self, field_name, value):
        super().__init__(
            f"Champ '{field_name}' invalide : '{value}' n'est pas un nombre valide.")
        self.field_name = field_name
        self.value = value


__version__ = "0.25.6g"  # Version de l'application


def get_resource_path(filename):
    """ Obtient le chemin absolu d'une ressource JSON, que ce soit en mode script ou compilé. """
    # base_path = os.path.dirname(__file__) # Chemin du script Apprentium.py
    if hasattr(sys, '_MEIPASS'):
        # Chemin pour l'exécutable PyInstaller (le dossier 'json' est au même niveau que l'exécutable)
        return os.path.join(sys._MEIPASS, "json", filename)
    # Chemin pour l'exécution en tant que script (le dossier 'json' est dans le même dossier que ce script)
    return os.path.join(os.path.dirname(__file__), "json", filename)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apprentium")
        # Assurez-vous que le chemin est correct
        icon_path = os.path.join(os.path.dirname(__file__), "Apprentium.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumWidth(UI_STYLE_CONFIG["window"]["minimum_width"])
        self.setMinimumHeight(UI_STYLE_CONFIG["window"]["minimum_height"])

        self.GITHUB_URL = "https://github.com/Gazz-yniere/Apprentium/releases"  # MODIFIEZ CECI

        self.current_selected_level_button = None
        self.current_level = None  # To store the string name of the level

        self._all_row_widgets_for_map = {}  # Pour accumuler les widgets de ligne
        self.selected_output_path = None  # Pour stocker le chemin choisi par l'utilisateur
        self.all_line_edits = [] # Liste pour stocker tous les QLineEdit à styler

        # --- Constants for Level Selection ---
        # Récupère depuis la config
        self.LEVEL_COLORS = UI_STYLE_CONFIG["buttons"]["level_colors"]

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

        # --- Chargement des données de cours ---
        self.cours_calcul_data = {}
        try:
            cours_calcul_path = get_resource_path('cours_calcul.json')
            with open(cours_calcul_path, 'r', encoding='utf-8') as f:
                self.cours_calcul_data = json.load(f)
        except Exception as e:
            print(f"ERREUR: Impossible de charger les cours de calcul: {e}")

        self.cours_grammaire_data = {}
        try:
            cours_grammaire_path = get_resource_path('cours_grammaire.json')
            with open(cours_grammaire_path, 'r', encoding='utf-8') as f:
                self.cours_grammaire_data = json.load(f)
        except Exception as e:
            print(f"ERREUR: Impossible de charger les cours de grammaire: {e}")

        self.cours_mesures_data = {}
        try:
            cours_mesures_path = get_resource_path('cours_mesures.json')
            with open(cours_mesures_path, 'r', encoding='utf-8') as f:
                self.cours_mesures_data = json.load(f)
        except Exception as e:
            print(f"ERREUR: Impossible de charger les cours de mesures: {e}")

        self.cours_conjugaison_data = {}
        try:
            cours_conjugaison_path = get_resource_path('cours_conjugaison.json')
            with open(cours_conjugaison_path, 'r', encoding='utf-8') as f:
                self.cours_conjugaison_data = json.load(f)
        except Exception as e:
            print(f"ERREUR: Impossible de charger les cours de conjugaison: {e}")

        self.cours_orthographe_data = {}
        try:
            cours_orthographe_path = get_resource_path('cours_orthographe.json')
            with open(cours_orthographe_path, 'r', encoding='utf-8') as f:
                self.cours_orthographe_data = json.load(f)
        except Exception as e:
            print(f"ERREUR: Impossible de charger les cours d'orthographe: {e}")

        self.cours_anglais_data = {}
        try:
            cours_anglais_path = get_resource_path('cours_anglais.json')
            with open(cours_anglais_path, 'r', encoding='utf-8') as f:
                self.cours_anglais_data = json.load(f)
        except Exception as e:
            print(f"ERREUR: Impossible de charger les cours d'anglais: {e}")

        # Mode dark
        dark_palette = QPalette()
        cfg_palette = UI_STYLE_CONFIG["palette"]
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(*cfg_palette["window"]))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(*cfg_palette["window_text"]))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(*cfg_palette["base"]))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(*cfg_palette["alternate_base"]))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(*cfg_palette["tooltip_base"]))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(*cfg_palette["tooltip_text"]))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(*cfg_palette["text"]))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(*cfg_palette["button"]))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(*cfg_palette["button_text"]))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(*cfg_palette["bright_text"]))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(*cfg_palette["highlight"]))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(*cfg_palette["highlighted_text"]))
        QApplication.instance().setPalette(dark_palette)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # --- Header Component ---
        # AppHeader will manage its own UI elements and internal state
        self.header_component = AppHeader(self, UI_STYLE_CONFIG, self.LEVEL_COLORS, self.LEVEL_ORDER)
        main_layout.addWidget(self.header_component)
        # Connect the days_entry from the header component to MainWindow's validation

        self.header_component.days_entry.textChanged.connect(self.validate_days_entry)
        self.level_buttons = self.header_component.level_buttons

        # --- Colonne Calculs ---
        self.calculs_column_component = CalculsColumn(self, UI_STYLE_CONFIG, self.math_problem_types_data)
        self.all_line_edits.extend(self.calculs_column_component.all_line_edits)
        self._all_row_widgets_for_map.update(self.calculs_column_component.all_row_widgets_for_map)

        # --- Colonne Mesures ---
        self.mesures_column_component = MesuresColumn(self, UI_STYLE_CONFIG)
        self.all_line_edits.extend(self.mesures_column_component.all_line_edits)
        self._all_row_widgets_for_map.update(self.mesures_column_component.all_row_widgets_for_map)
        
        # --- Colonne Conjugaison ---
        self.conjugaison_column_component = ConjugaisonColumn(self, UI_STYLE_CONFIG)
        self.all_line_edits.extend(self.conjugaison_column_component.all_line_edits)
        self._all_row_widgets_for_map.update(self.conjugaison_column_component.all_row_widgets_for_map)

        # --- Colonne Grammaire ---
        self.grammar_column_component = GrammarColumn(self, UI_STYLE_CONFIG)
        self.all_line_edits.extend(self.grammar_column_component.all_line_edits)
        self._all_row_widgets_for_map.update(self.grammar_column_component.all_row_widgets_for_map)

        # --- Colonne Orthographe ---
        self.orthographe_column_component = OrthographeColumn(self, UI_STYLE_CONFIG)
        self.all_line_edits.extend(self.orthographe_column_component.all_line_edits)
        self._all_row_widgets_for_map.update(self.orthographe_column_component.all_row_widgets_for_map)

        # --- Colonne Anglais ---
        self.anglais_column_component = AnglaisColumn(self, UI_STYLE_CONFIG, self.english_relier_themes)
        self.all_line_edits.extend(self.anglais_column_component.all_line_edits)
        self._all_row_widgets_for_map.update(self.anglais_column_component.all_row_widgets_for_map)

        # --- Splitter pour 6 colonnes ---
        self.calculs_column_component.setMinimumWidth(270)
        self.mesures_column_component.setMinimumWidth(270)
        self.conjugaison_column_component.setMinimumWidth(270)
        self.grammar_column_component.setMinimumWidth(270)
        
        ortho_anglais_layout = QVBoxLayout()
        ortho_anglais_layout.setContentsMargins(0, 0, 0, 0)
        ortho_anglais_layout.setSpacing(0)
        ortho_anglais_layout.addWidget(self.orthographe_column_component)
        ortho_anglais_layout.addWidget(self.anglais_column_component)
        # Ajoute un ressort pour pousser les sections vers le haut
        ortho_anglais_layout.addStretch(1)
        # Ce widget contiendra le layout ortho_anglais
        self.ortho_anglais_column_widget = QWidget()
        self.ortho_anglais_column_widget.setLayout(ortho_anglais_layout)
        self.ortho_anglais_column_widget.setMinimumWidth(270)

        # Stocker la configuration initiale des colonnes du splitter pour la réorganisation
        self.splitter_column_configs_initial_order = [
            {'widget': self.calculs_column_component, 'stretch': 1, 'key': 'calc'},
            {'widget': self.mesures_column_component, 'stretch': 1, 'key': 'geo'}, # Use the new component
            {'widget': self.conjugaison_column_component, 'stretch': 1, 'key': 'conj'},
            {'widget': self.ortho_anglais_column_widget,'stretch': 1, 'key': 'ortho_anglais'},
            {'widget': self.grammar_column_component, 'stretch': 1, 'key': 'grammar'}
        ]

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.calculs_column_component)
        splitter.addWidget(self.mesures_column_component)
        splitter.addWidget(self.conjugaison_column_component)
        # Ortho/Anglais en 4ème
        splitter.addWidget(self.ortho_anglais_column_widget)
        # Grammaire en 5ème
        splitter.addWidget(self.grammar_column_component)
        for i, config in enumerate(self.splitter_column_configs_initial_order):
            splitter.setStretchFactor(i, config['stretch'])

        # --- Create Tab Widget ---
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(UI_STYLE_CONFIG["tab_widget"]["style"])

        # --- Exercices Tab ---
        exercices_tab = QWidget()
        exercices_layout = QVBoxLayout(exercices_tab)
        exercices_layout.setContentsMargins(0, 0, 0, 0)

        # ScrollArea for the exercise columns splitter
        self.exercices_scroll_area = QScrollArea()
        self.exercices_scroll_area.setWidgetResizable(True)
        self.exercices_scroll_area.setWidget(splitter)
        self.exercices_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.exercices_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.exercices_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        exercices_layout.addWidget(self.exercices_scroll_area)
        self.tab_widget.addTab(exercices_tab, "Exercices")

        # --- Cours Tab ---
        # Rassembler toutes les données de cours dans un dictionnaire
        all_cours_data = {
            'calc': self.cours_calcul_data,
            'grammar': self.cours_grammaire_data,
            'geo': self.cours_mesures_data,
            'conj': self.cours_conjugaison_data,
            'ortho': self.cours_orthographe_data,
            'english': self.cours_anglais_data,
        }

        # Créer le composant de l'onglet Cours
        self.cours_tab_component = CoursColumn(self, UI_STYLE_CONFIG, "Cours", all_cours_data, "blue")
        self.tab_widget.addTab(self.cours_tab_component, "Cours")

        # --- Paramètres Tab ---
        # (Instantiated after exercise_widgets_map is fully populated)
        # Add the tab widget to the main layout
        main_layout.addWidget(self.tab_widget)
        
        self.splitter = splitter  # Garder une référence au splitter
        
        # Apply scrollbar style to the exercise scroll area
        scrollbar_style = UI_STYLE_CONFIG["scroll_bar"]["style_template"].format(
            **UI_STYLE_CONFIG["scroll_bar"]["values"])
        self.exercices_scroll_area.setStyleSheet(scrollbar_style)
        
        # --- Footer Component ---
        self.footer_component = AppFooter(self, UI_STYLE_CONFIG, __version__, self.GITHUB_URL)
        main_layout.addWidget(self.footer_component)

        # Collect all line edits from components and apply styling
        self.all_line_edits.extend(self.header_component.all_line_edits)
        self.all_line_edits.extend(self.footer_component.all_line_edits)

        # --- Initialize exercise_widgets_map ---
        # This map will store all controllable widgets with unique keys.
        self.exercise_widgets_map = {
            # Calculs
            "enumerate_group": self.calculs_column_component.enumerate_group,
            "enumerate_count_input": self.calculs_column_component.enumerate_count, "enumerate_digits_input": self.calculs_column_component.enumerate_digits,
            "addition_group": self.calculs_column_component.addition_group,
            "addition_count_input": self.calculs_column_component.addition_count, "addition_digits_input": self.calculs_column_component.addition_digits,
            "addition_decimals_input": self.calculs_column_component.addition_decimals, "addition_num_operands_input": self.calculs_column_component.addition_num_operands,
            "subtraction_group": self.calculs_column_component.subtraction_group,
            "subtraction_count_input": self.calculs_column_component.subtraction_count, "subtraction_digits_input": self.calculs_column_component.subtraction_digits,
            "subtraction_decimals_input": self.calculs_column_component.subtraction_decimals, "subtraction_num_operands_input": self.calculs_column_component.subtraction_num_operands,
            "subtraction_negative_cb": self.calculs_column_component.subtraction_negative_checkbox,
            "multiplication_group": self.calculs_column_component.multiplication_group,
            "multiplication_count_input": self.calculs_column_component.multiplication_count, "multiplication_digits_input": self.calculs_column_component.multiplication_digits,
            "multiplication_decimals_input": self.calculs_column_component.multiplication_decimals, "multiplication_num_operands_input": self.calculs_column_component.multiplication_num_operands,
            "division_group": self.calculs_column_component.division_group,
            "division_count_input": self.calculs_column_component.division_count, "division_digits_input": self.calculs_column_component.division_digits, "division_decimals_input": self.calculs_column_component.division_decimals,
            "division_reste_cb": self.calculs_column_component.division_reste_checkbox,
            # Petits Problèmes
            "math_problems_group": self.calculs_column_component.math_problems_group,
            "math_problems_count_input": self.calculs_column_component.math_problems_count,

            # Mesures
            "geo_conv_group": self.mesures_column_component.geo_conv_group,
            "geo_ex_count_input": self.mesures_column_component.geo_ex_count,
            "conv_type_longueur_cb": self.mesures_column_component.conv_type_longueur, "conv_type_masse_cb": self.mesures_column_component.conv_type_masse, "conv_type_volume_cb": self.mesures_column_component.conv_type_volume, "conv_type_temps_cb": self.mesures_column_component.conv_type_temps, "conv_type_monnaie_cb": self.mesures_column_component.conv_type_monnaie,
            "conv_sens_direct_cb": self.mesures_column_component.conv_sens_direct, "conv_sens_inverse_cb": self.mesures_column_component.conv_sens_inverse,
            # --- NEW: Problèmes de Mesures ---
            "measurement_problems_group": self.mesures_column_component.measurement_problems_group,
            "measurement_problems_count_input": self.mesures_column_component.measurement_problems_count,
            "measurement_problem_longueur_cb": self.mesures_column_component.measurement_problem_longueur_cb,
            "measurement_problem_masse_cb": self.mesures_column_component.measurement_problem_masse_cb,
            "measurement_problem_volume_cb": self.mesures_column_component.measurement_problem_volume_cb,
            "measurement_problem_temps_cb": self.mesures_column_component.measurement_problem_temps_cb,
            "measurement_problem_monnaie_cb": self.mesures_column_component.measurement_problem_monnaie_cb,
            "geo_sort_group": self.mesures_column_component.sort_group,
            "sort_count_input": self.mesures_column_component.sort_count, "sort_digits_input": self.mesures_column_component.sort_digits, "sort_n_numbers_input": self.mesures_column_component.sort_n_numbers,
            "sort_type_croissant_cb": self.mesures_column_component.sort_type_croissant, "sort_type_decroissant_cb": self.mesures_column_component.sort_type_decroissant,

            "geo_encadrement_group": self.mesures_column_component.encadrement_group,
            "encadrement_count_input": self.mesures_column_component.encadrement_count, "encadrement_digits_input": self.mesures_column_component.encadrement_digits,
            "encadrement_unite_cb": self.mesures_column_component.encadrement_unite, "encadrement_dizaine_cb": self.mesures_column_component.encadrement_dizaine, "encadrement_centaine_cb": self.mesures_column_component.encadrement_centaine, "encadrement_millier_cb": self.mesures_column_component.encadrement_millier,

            "geo_compare_numbers_group": self.mesures_column_component.compare_numbers_group,
            "compare_numbers_count_input": self.mesures_column_component.compare_numbers_count, "compare_numbers_digits_input": self.mesures_column_component.compare_numbers_digits,

            "geo_logical_sequences_group": self.mesures_column_component.logical_sequences_group,
            "logical_sequences_count_input": self.mesures_column_component.logical_sequences_count,
            "logical_sequences_length_input": self.mesures_column_component.logical_sequences_length,  # Nouveau
            "logical_sequences_type_arithmetic_plus_cb": self.mesures_column_component.logical_sequences_type_arithmetic_plus_cb,
            "logical_sequences_type_arithmetic_minus_cb": self.mesures_column_component.logical_sequences_type_arithmetic_minus_cb,
            "logical_sequences_type_arithmetic_multiply_cb": self.mesures_column_component.logical_sequences_type_arithmetic_multiply_cb,
            "logical_sequences_type_arithmetic_divide_cb": self.mesures_column_component.logical_sequences_type_arithmetic_divide_cb,

            # Conjugaison
            "verbs_per_day_entry_input": self.conjugaison_column_component.verbs_per_day_entry,
            "conj_groups_group": self.conjugaison_column_component.conj_group_group,
            "group_1_cb": self.conjugaison_column_component.group_1_checkbox, "group_2_cb": self.conjugaison_column_component.group_2_checkbox, "group_3_cb": self.conjugaison_column_component.group_3_checkbox, "usual_verbs_cb": self.conjugaison_column_component.usual_verbs_checkbox,
            "conj_tenses_group": self.conjugaison_column_component.conj_tense_group,
            # Individual tense checkboxes
            "tense_present_cb": self.conjugaison_column_component.tense_checkboxes[0] if len(self.conjugaison_column_component.tense_checkboxes) > 0 else None,
            "tense_imparfait_cb": self.conjugaison_column_component.tense_checkboxes[1] if len(self.conjugaison_column_component.tense_checkboxes) > 1 else None,
            "tense_passe_simple_cb": self.conjugaison_column_component.tense_checkboxes[2] if len(self.conjugaison_column_component.tense_checkboxes) > 2 else None,
            "tense_futur_simple_cb": self.conjugaison_column_component.tense_checkboxes[3] if len(self.conjugaison_column_component.tense_checkboxes) > 3 else None,
            "tense_passe_compose_cb": self.conjugaison_column_component.tense_checkboxes[4] if len(self.conjugaison_column_component.tense_checkboxes) > 4 else None,
            "tense_plus_que_parfait_cb": self.conjugaison_column_component.tense_checkboxes[5] if len(self.conjugaison_column_component.tense_checkboxes) > 5 else None,
            "tense_conditionnel_present_cb": self.conjugaison_column_component.tense_checkboxes[6] if len(self.conjugaison_column_component.tense_checkboxes) > 6 else None,
            "tense_imperatif_present_cb": self.conjugaison_column_component.tense_checkboxes[7] if len(self.conjugaison_column_component.tense_checkboxes) > 7 else None,
            # Nouveaux exercices de conjugaison
            "conj_complete_sentence_group": self.conjugaison_column_component.conj_complete_sentence_group,
            "conj_complete_sentence_count_input": self.conjugaison_column_component.conj_complete_sentence_count,
            "conj_complete_pronoun_group": self.conjugaison_column_component.conj_complete_pronoun_group,
            "conj_complete_pronoun_count_input": self.conjugaison_column_component.conj_complete_pronoun_count,
            # Add more if TENSES list grows, ensure TENSES order matches these keys in EXERCISES_BY_LEVEL_INCREMENTAL

            # Grammaire
            "grammar_params_group": self.grammar_column_component.grammar_number_group,
            "grammar_sentence_count_input": self.grammar_column_component.grammar_sentence_count,
            "grammar_types_group": self.grammar_column_component.grammar_type_group,
            "intransitive_cb": self.grammar_column_component.intransitive_checkbox, "transitive_direct_cb": self.grammar_column_component.transitive_direct_checkbox, "transitive_indirect_cb": self.grammar_column_component.transitive_indirect_checkbox, "ditransitive_cb": self.grammar_column_component.ditransitive_checkbox,
            "grammar_transfo_group": self.grammar_column_component.grammar_transfo_group,
            # Individual transformation checkboxes (key based on transformation text for simplicity, ensure no special chars or make them safe)
            "transfo_singulier_pluriel_cb": self.grammar_column_component.transfo_checkboxes[0] if len(self.grammar_column_component.transfo_checkboxes) > 0 else None,
            "transfo_masculin_feminin_cb": self.grammar_column_component.transfo_checkboxes[1] if len(self.grammar_column_component.transfo_checkboxes) > 1 else None,
            "transfo_present_passe_compose_cb": self.grammar_column_component.transfo_checkboxes[2] if len(self.grammar_column_component.transfo_checkboxes) > 2 else None,
            "transfo_present_imparfait_cb": self.grammar_column_component.transfo_checkboxes[3] if len(self.grammar_column_component.transfo_checkboxes) > 3 else None,
            "transfo_present_futur_simple_cb": self.grammar_column_component.transfo_checkboxes[4] if len(self.grammar_column_component.transfo_checkboxes) > 4 else None,
            "transfo_indicatif_imperatif_cb": self.grammar_column_component.transfo_checkboxes[5] if len(self.grammar_column_component.transfo_checkboxes) > 5 else None,
            "transfo_voix_active_passive_cb": self.grammar_column_component.transfo_checkboxes[6] if len(self.grammar_column_component.transfo_checkboxes) > 6 else None,
            "transfo_declarative_interrogative_cb": self.grammar_column_component.transfo_checkboxes[7] if len(self.grammar_column_component.transfo_checkboxes) > 7 else None,
            "transfo_declarative_exclamative_cb": self.grammar_column_component.transfo_checkboxes[8] if len(self.grammar_column_component.transfo_checkboxes) > 8 else None,
            "transfo_declarative_imperative_cb": self.grammar_column_component.transfo_checkboxes[9] if len(self.grammar_column_component.transfo_checkboxes) > 9 else None,
            "transfo_affirmative_negative_cb": self.grammar_column_component.transfo_checkboxes[10] if len(self.grammar_column_component.transfo_checkboxes) > 10 else None,

            # Orthographe
            "ortho_params_group": self.orthographe_column_component.orthographe_number_group,
            "orthographe_ex_count_input": self.orthographe_column_component.orthographe_ex_count,
            "ortho_homophones_group": self.orthographe_column_component.orthographe_homophone_group,
            "homophone_a_cb": self.orthographe_column_component.homophone_a_checkbox, "homophone_et_cb": self.orthographe_column_component.homophone_et_checkbox, "homophone_on_cb": self.orthographe_column_component.homophone_on_checkbox, "homophone_son_cb": self.orthographe_column_component.homophone_son_checkbox,
            "homophone_ce_cb": self.orthographe_column_component.homophone_ce_checkbox, "homophone_ou_cb": self.orthographe_column_component.homophone_ou_checkbox, "homophone_ces_cb": self.orthographe_column_component.homophone_ces_checkbox, "homophone_mes_cb": self.orthographe_column_component.homophone_mes_checkbox,

            # Anglais
            "english_complete_group": self.anglais_column_component.english_complete_group,
            "english_complete_count_input": self.anglais_column_component.english_complete_count,
            "english_type_simple_cb": self.anglais_column_component.english_type_simple, "english_type_complexe_cb": self.anglais_column_component.english_type_complexe,
            "english_relier_group": self.anglais_column_component.english_relier_group,
            "english_relier_count_input": self.anglais_column_component.english_relier_count, "relier_count_input": self.anglais_column_component.relier_count,
            # "english_relier_themes_group": self.english_relier_themes_group, # Supprimé car plus de groupe dédié
            # Header components (for config saving/loading)
            "header_entry_input": self.header_component.header_entry,
            "show_name_checkbox_cb": self.header_component.show_name_checkbox,
            "show_note_checkbox_cb": self.header_component.show_note_checkbox,
            "days_entry_input": self.header_component.days_entry,
            # Footer components (for config saving/loading)
            "filename_entry_input": self.footer_component.filename_entry,
        }
        # Remove None values from map (if checkboxes lists were shorter than expected)
        self.exercise_widgets_map = {
            k: v for k, v in self.exercise_widgets_map.items() if v is not None}
        # Ajouter les row_widgets stockés
        self.exercise_widgets_map.update(self._all_row_widgets_for_map)
        del self._all_row_widgets_for_map # Nettoyer le dictionnaire temporaire

        # Ajouter dynamiquement les checkboxes de thèmes anglais à exercise_widgets_map
        if hasattr(self.anglais_column_component, 'english_relier_theme_checkboxes'): # Access via anglais_column_component
            for theme_name, cb_widget in self.anglais_column_component.english_relier_theme_checkboxes.items():
                self.exercise_widgets_map[f"english_theme_{theme_name}_cb"] = cb_widget

        # Ajouter dynamiquement les checkboxes de types de problèmes mathématiques
        if hasattr(self.calculs_column_component, 'math_problem_type_checkboxes'):
            for type_key, cb_widget in self.calculs_column_component.math_problem_type_checkboxes.items():
                self.exercise_widgets_map[f"math_problem_type_{type_key}_cb"] = cb_widget

        # --- Paramètres Tab (instantiate after exercise_widgets_map is complete) ---
        # Path to levels_config.json
        levels_config_json_path = get_resource_path('levels_config.json')
        self.parametres_tab_component = SettingsTab(
            self, UI_STYLE_CONFIG, self.LEVEL_ORDER,
            self.EXERCISES_BY_LEVEL_INCREMENTAL, self.exercise_widgets_map,
            levels_config_json_path
        )
        self.tab_widget.addTab(self.parametres_tab_component, "Paramètres")
        
        # --- Column Titles and Sections Mapping (for hiding titles of empty columns) ---
        self.column_title_widgets = {
            "calc": self.calculs_column_component.calc_title_label,
            "geo": self.mesures_column_component.geo_title_label,
            "conj": self.conjugaison_column_component.conj_title_label,
            "grammar": self.grammar_column_component.grammar_title_label,
            "ortho": self.orthographe_column_component.orthographe_title_label,
            "english": self.anglais_column_component.english_title_label,
        }
        self.column_section_keys = {  # Maps column key to list of its main section group keys
            # No change here
            "calc": ["enumerate_group", "addition_group", "subtraction_group", "multiplication_group", "division_group", "math_problems_group"],
            # Updated groups
            "geo": ["geo_conv_group", "geo_sort_group", "geo_encadrement_group", "geo_compare_numbers_group", "geo_logical_sequences_group"],
            "conj": ["conj_groups_group", "conj_tenses_group","conj_complete_sentence_group", "conj_complete_pronoun_group"],
            "grammar": ["grammar_params_group", "grammar_types_group", "grammar_transfo_group"], # No change here
            "ortho": ["ortho_params_group", "ortho_homophones_group"], # No change here
            # Les checkboxes de thèmes sont gérées individuellement
            "english": ["english_complete_group", "english_relier_group"],
        }
        
        lineedit_style = UI_STYLE_CONFIG["line_edits"]["default"]
        for le in self.all_line_edits: # Apply style to all collected line edits
            if le: le.setStyleSheet(lineedit_style)
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
            ('days_entry', self.header_component.days_entry, 'text'),
            ('header_entry', self.header_component.header_entry, 'text'), # Access via component
            # Enumérer un nombre
            ('enumerate_count', self.calculs_column_component.enumerate_count, 'text'),
            ('enumerate_digits', self.calculs_column_component.enumerate_digits, 'text'),
            ('sort_count', self.mesures_column_component.sort_count, 'text'),
            ('sort_digits', self.mesures_column_component.sort_digits, 'text'),
            ('sort_n_numbers', self.mesures_column_component.sort_n_numbers, 'text'),
            ('sort_type_croissant', self.mesures_column_component.sort_type_croissant, 'checked'),
            ('sort_type_decroissant', self.mesures_column_component.sort_type_decroissant, 'checked'),
            ('addition_count', self.calculs_column_component.addition_count, 'text'), # Kept for value, not level config
            ('addition_digits', self.calculs_column_component.addition_digits, 'text'),
            ('addition_num_operands', self.calculs_column_component.addition_num_operands, 'text'), # Kept for value, not level config
            ('addition_decimals', self.calculs_column_component.addition_decimals, 'text'), # Kept for value, not level config
            ('subtraction_count', self.calculs_column_component.subtraction_count, 'text'), # Kept for value, not level config
            ('subtraction_digits', self.calculs_column_component.subtraction_digits, 'text'), # Kept for value, not level config
            ('subtraction_num_operands', self.calculs_column_component.subtraction_num_operands, 'text'), # Kept for value, not level config
            ('subtraction_decimals', self.calculs_column_component.subtraction_decimals, 'text'), # Kept for value, not level config
            ('subtraction_negative_checkbox',self.calculs_column_component.subtraction_negative_checkbox, 'checked'), # Kept for value, not level config
            ('multiplication_count', self.calculs_column_component.multiplication_count, 'text'), # Kept for value, not level config
            ('multiplication_digits', self.calculs_column_component.multiplication_digits, 'text'), # Kept for value, not level config
            ('multiplication_num_operands', self.calculs_column_component.multiplication_num_operands, 'text'), # Kept for value, not level config
            ('multiplication_decimals', self.calculs_column_component.multiplication_decimals, 'text'), # Kept for value, not level config
            ('division_count', self.calculs_column_component.division_count, 'text'), # Kept for value, not level config
            ('division_digits', self.calculs_column_component.division_digits, 'text'), # Kept for value, not level config
            ('division_decimals', self.calculs_column_component.division_decimals, 'text'), # Kept for value, not level config
            ('division_reste_checkbox', self.calculs_column_component.division_reste_checkbox, 'checked'), # Kept for value, not level config
            ('conj_complete_sentence_count', self.conjugaison_column_component.conj_complete_sentence_count, 'text'), # Kept for value, not level config
            ('conj_complete_pronoun_count', self.conjugaison_column_component.conj_complete_pronoun_count, 'text'), # Kept for value, not level config 
            # Groupes de conjugaison
            ('verbs_per_day_entry', self.conjugaison_column_component.verbs_per_day_entry, 'text'),
            ('grammar_sentence_count', self.grammar_column_component.grammar_sentence_count, 'text'),
            ('intransitive_checkbox', self.grammar_column_component.intransitive_checkbox, 'checked'),
            ('transitive_direct_checkbox',self.grammar_column_component.transitive_direct_checkbox, 'checked'),
            ('transitive_indirect_checkbox',self.grammar_column_component.transitive_indirect_checkbox, 'checked'),
            ('ditransitive_checkbox', self.grammar_column_component.ditransitive_checkbox, 'checked'),
            ('transfo_checkboxes', self.grammar_column_component.transfo_checkboxes, 'checked_list'),
            # Orthographe
            ('orthographe_ex_count', self.orthographe_column_component.orthographe_ex_count, 'text'), # Kept for value, not level config
            ('orthographe_homophone_checkboxes',self.orthographe_column_component.orthographe_homophone_checkboxes, 'checked_list'), # Kept for value, not level config
            # Header checkboxes
            ('show_name_checkbox', self.header_component.show_name_checkbox, 'checked'),
            ('show_note_checkbox', self.header_component.show_note_checkbox, 'checked'),
            ('filename_entry', self.footer_component.filename_entry, 'text'),
            # Nouveau mode pour variable de chemin (No change here)
            ('selected_output_path', self, 'path_variable'),
            ('group_1_checkbox', self.conjugaison_column_component.group_1_checkbox, 'checked'),
            ('group_2_checkbox', self.conjugaison_column_component.group_2_checkbox, 'checked'),
            ('group_3_checkbox', self.conjugaison_column_component.group_3_checkbox, 'checked'),
            ('usual_verbs_checkbox', self.conjugaison_column_component.usual_verbs_checkbox, 'checked'),
            ('tense_checkboxes', self.conjugaison_column_component.tense_checkboxes, 'checked_list'),
            ('geo_ex_count', self.mesures_column_component.geo_ex_count, 'text'), # Kept for value, not level config
            ('geo_conv_type_checkboxes', self.mesures_column_component.geo_conv_type_checkboxes, 'checked_list'), # Kept for value, not level config
            ('conv_sens_direct', self.mesures_column_component.conv_sens_direct, 'checked'), # Kept for value, not level config
            ('conv_sens_inverse', self.mesures_column_component.conv_sens_inverse, 'checked'), # Kept for value, not level config
            ('english_complete_count', self.anglais_column_component.english_complete_count, 'text'), # Kept for value, not level config
            ('english_type_simple', self.anglais_column_component.english_type_simple, 'checked'), # Kept for value, not level config
            ('english_type_complexe', self.anglais_column_component.english_type_complexe, 'checked'), # Kept for value, not level config
            ('english_relier_count', self.anglais_column_component.english_relier_count, 'text'), # Kept for value, not level config
            ('relier_count', self.anglais_column_component.relier_count, 'text'), # Kept for value, not level config
            ('encadrement_count', self.mesures_column_component.encadrement_count, 'text'), # Kept for value, not level config
            ('encadrement_digits', self.mesures_column_component.encadrement_digits, 'text'), # Kept for value, not level config
            ('encadrement_unite', self.mesures_column_component.encadrement_unite, 'checked'), # Kept for value, not level config
            ('encadrement_dizaine', self.mesures_column_component.encadrement_dizaine, 'checked'), # Kept for value, not level config
            ('encadrement_centaine', self.mesures_column_component.encadrement_centaine, 'checked'), # Kept for value, not level config
            ('encadrement_millier', self.mesures_column_component.encadrement_millier, 'checked'), # Kept for value, not level config
            ('measurement_problems_count', self.mesures_column_component.measurement_problems_count, 'text'), # Kept for value, not level config
            ('measurement_problem_longueur_cb', self.mesures_column_component.measurement_problem_longueur_cb, 'checked'), # Kept for value, not level config
            ('measurement_problem_masse_cb', self.mesures_column_component.measurement_problem_masse_cb, 'checked'), # Kept for value, not level config
            ('measurement_problem_volume_cb', self.mesures_column_component.measurement_problem_volume_cb, 'checked'), # Kept for value, not level config
            ('measurement_problem_temps_cb', self.mesures_column_component.measurement_problem_temps_cb, 'checked'), # Kept for value, not level config
            ('measurement_problem_monnaie_cb', self.mesures_column_component.measurement_problem_monnaie_cb, 'checked'), # Kept for value, not level config
            ('math_problems_count', self.calculs_column_component.math_problems_count, 'text'), # Kept for value, not level config
            ('compare_numbers_count', self.mesures_column_component.compare_numbers_count, 'text'), # Kept for value, not level config
            ('compare_numbers_digits', self.mesures_column_component.compare_numbers_digits, 'text'), # Kept for value, not level config
            ('logical_sequences_count', self.mesures_column_component.logical_sequences_count, 'text'), # Kept for value, not level config
            ('logical_sequences_length', self.mesures_column_component.logical_sequences_length, 'text'), # Kept for value, not level config
            ('logical_sequences_type_arithmetic_plus_cb', self.mesures_column_component.logical_sequences_type_arithmetic_plus_cb, 'checked'), # Kept for value, not level config
            ('logical_sequences_type_arithmetic_minus_cb', self.mesures_column_component.logical_sequences_type_arithmetic_minus_cb, 'checked'), # Kept for value, not level config
            ('logical_sequences_type_arithmetic_multiply_cb', self.mesures_column_component.logical_sequences_type_arithmetic_multiply_cb, 'checked'), # Kept for value, not level config
            ('logical_sequences_type_arithmetic_divide_cb', self.mesures_column_component.logical_sequences_type_arithmetic_divide_cb, 'checked'), # Kept for value, not level config

            # Les checkboxes de types de problèmes seront ajoutées dynamiquement
            # Ajout pour sauvegarder le niveau
            ('current_level', self, 'level_variable'),
        ] # End of config_fields
        
        # --- NEW: Add window settings to config fields ---
        if hasattr(self, 'parametres_tab_component'):
            self.config_fields.extend([
                ('window_fullscreen', self.parametres_tab_component.fullscreen_checkbox, 'checked'),
                ('window_width', self.parametres_tab_component.width_input, 'text'),
                ('window_height', self.parametres_tab_component.height_input, 'text'),
            ])
            
        # Dynamically add checkboxes from components to config_fields
        if hasattr(self.anglais_column_component, 'english_relier_theme_checkboxes'): # Access via anglais_column_component
            for theme_name, cb_widget in self.anglais_column_component.english_relier_theme_checkboxes.items():
                self.config_fields.append((f"english_theme_{theme_name}_cb", cb_widget, 'checked'))
        if hasattr(self.calculs_column_component, 'math_problem_type_checkboxes'):
            for type_key, cb_widget in self.calculs_column_component.math_problem_type_checkboxes.items():
                self.config_fields.append(
                    (f"math_problem_type_{type_key}_cb", cb_widget, 'checked'))

        self.load_config()
        self._apply_window_size_from_config() # Apply size after loading
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

    def set_current_level(self, level_name):
        """
        Called by AppHeader to update the main window's current level.
        """
        self.current_level = level_name
        # The AppHeader component manages its own current_selected_level_button
        # and its visual state.
        self.update_exercise_visibility()
        # Mettre à jour le contenu de l'onglet Cours
        if hasattr(self, 'cours_tab_component'):
            self.cours_tab_component.update_content(level_name)
    
    def _apply_window_size_from_config(self):
        """Applies window size settings after the configuration is loaded."""
        if not hasattr(self, 'parametres_tab_component'):
            return # Component not ready yet

        try:
            # The state of the widgets has been set by load_config()
            is_fullscreen = self.parametres_tab_component.fullscreen_checkbox.isChecked()
            
            if is_fullscreen:
                self.showMaximized()
            else:
                width_str = self.parametres_tab_component.width_input.text()
                height_str = self.parametres_tab_component.height_input.text()
                
                if width_str and height_str:
                    width = int(width_str)
                    height = int(height_str)
                    if width >= self.minimumWidth() and height >= self.minimumHeight():
                        self.resize(width, height)
        except (ValueError, TypeError):
            # If values are invalid or empty, do nothing, keep default size.
            pass
        
    def set_selected_output_path(self, path):
        """
        Called by AppFooter to update the main window's selected output path.
        """
        self.selected_output_path = path

    def get_int(self, lineedit, default=0, field_name=None):
        value = lineedit.text().strip()
        if value == '':
            return default
        if value.isdigit():
            # Ensure positive integer for days_entry
            if lineedit == self.header_component.days_entry and int(value) <= 0:
                raise InvalidFieldError(field_name or lineedit.objectName(), value)
            return int(value) 
        else:
            raise InvalidFieldError(field_name or lineedit.objectName(), value)

    def validate_days_entry(self):
        value = self.header_component.days_entry.text().strip()
        is_valid = value.isdigit() and int(value) > 0
        style = UI_STYLE_CONFIG["line_edits"]["default"]
        if not is_valid:
            # Ajouter la bordure rouge spécifique pour l'invalidité
            style += UI_STYLE_CONFIG["line_edits"]["days_invalid_border"]
        self.header_component.days_entry.setStyleSheet(style)
        self.footer_component.generate_pdf_button.setEnabled(is_valid)
        self.footer_component.generate_word_button.setEnabled(is_valid)
        self.footer_component.preview_pdf_button.setEnabled(is_valid)
        self.footer_component.preview_word_button.setEnabled(is_valid)

    def _get_param_value_if_allowed(self, widget_map_key, field_name_for_error, default_value, allowed_keys, value_type='int'):
        """
        Retrieves a parameter value from a widget if its key is in allowed_keys.
        Handles different widget types and value conversions.
        """
        if widget_map_key not in allowed_keys:
            return default_value

        widget = self.exercise_widgets_map.get(widget_map_key)
        if widget is None:
            print(f"Warning: Widget not found for key '{widget_map_key}'. Returning default value.")
            return default_value

        try:
            if value_type == 'int':
                return self.get_int(widget, default=default_value, field_name=field_name_for_error)
            elif value_type == 'bool':
                return widget.isChecked()
            elif value_type == 'text':
                return widget.text().strip()
            else:
                raise ValueError(f"Unknown value_type '{value_type}' for key '{widget_map_key}'.")
        except InvalidFieldError:
            raise # Re-raise to be caught by the main build_exercise_data try-except
        except Exception as e:
            print(f"Error retrieving value for '{widget_map_key}': {e}. Returning default.")
            return default_value

    def _execute_workbook_generation(self, generator_func, file_extension, is_preview):
        """
        Helper method to encapsulate common logic for generating/previewing workbooks.
        """
        try:
            data = self.build_exercise_data()
            if data is None:
                return

            header_text = self.header_component.header_entry.text().strip()
            show_name = self.header_component.show_name_checkbox.isChecked()
            show_note = self.header_component.show_note_checkbox.isChecked()
            filename = self.footer_component.filename_entry.text().strip() or "workbook"
            output_directory = self.selected_output_path

            if not filename.lower().endswith(file_extension):
                filename += file_extension

            # Common parameters for both PDF and DOCX generators
            common_params = {
                'days': data['days'],
                'operations': data['operations'],
                'counts': data['counts'],
                'max_digits': data['max_digits'],
                'conjugations': data['conjugations'],
                'params_list': data['params_list'],
                'grammar_exercises': data['grammar_exercises'],
                'orthographe_exercises': data['orthographe_exercises'],
                'enumerate_exercises': data['enumerate_exercises'],
                'sort_exercises': data['sort_exercises'],
                'geo_exercises': data['geo_exercises'],
                'english_exercises': data['english_exercises'],
                'measurement_problems': data.get('measurement_problems'),
                'encadrement_exercises_list': data.get('encadrement_exercises_list'),
                'compare_numbers_exercises_list': data.get('compare_numbers_exercises_list'),
                'logical_sequences_exercises_list': data.get('logical_sequences_exercises_list'),
                'story_math_problems_by_day': data.get('math_problems'),
                'conj_complete_sentence_exercises': data.get('conj_complete_sentence_exercises'),
                'conj_complete_pronoun_exercises': data.get('conj_complete_pronoun_exercises'),
                'header_text': header_text,
                'show_name': show_name,
                'show_note': show_note,
                'filename': filename,
                'output_dir_override': output_directory
            }

            output_path = generator_func(**common_params)

            if output_path and os.path.exists(output_path):
                if is_preview:
                    os.startfile(output_path)
                else:
                    print(f"{file_extension.upper()} généré avec succès : {output_path}")
            else:
                print(f"Erreur : Fichier {file_extension.upper()} non trouvé à {output_path} après la génération.")

        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite lors de la génération/prévisualisation {file_extension.upper()} : {type(e).__name__} : {e}")
            traceback.print_exc()

    def build_exercise_data(self):
        try:
            # Get allowed keys for the current level
            allowed_keys = self.get_exercises_for_level(self.current_level)

            # Génération des exercices d'encadrement
            # Les paramètres pour l'encadrement sont collectés ici et passés à ExerciseDataBuilder
            # ExerciseDataBuilder appellera ensuite une fonction de mesures_generator.py par jour.
            encadrement_params_for_builder = {
                'count': self._get_param_value_if_allowed("encadrement_count_input", "Encadrement - nombre d'exercices", 0, allowed_keys),
                'digits': self._get_param_value_if_allowed("encadrement_digits_input", "Encadrement - chiffres par nombre", 0, allowed_keys),
                'types': [name for cb, name, key in zip(
                    [self.mesures_column_component.encadrement_unite, self.mesures_column_component.encadrement_dizaine,
                        self.mesures_column_component.encadrement_centaine, self.mesures_column_component.encadrement_millier],
                    ["unité", "dizaine", "centaine", "millier"],
                    ["encadrement_unite_cb", "encadrement_dizaine_cb",
                        "encadrement_centaine_cb", "encadrement_millier_cb"]
                ) if key in allowed_keys and cb.isChecked()]
            }

            # Génération des exercices anglais (phrases à compléter + jeux à relier)
            from anglais_generator import generate_english_full_exercises
            # english_types = self.get_selected_english_types()
            n_complete = self._get_param_value_if_allowed("english_complete_count_input", "Anglais - phrases à compléter", 0, allowed_keys)
            n_relier = self._get_param_value_if_allowed("english_relier_count_input", "Anglais - jeux à relier", 0, allowed_keys)
            n_mots_reliés = self._get_param_value_if_allowed("relier_count_input", "Anglais - mots par jeu", 0, allowed_keys) # Garder pour params
            
            # La génération effective des english_exercises se fera dans ExerciseDataBuilder

            # Ranger les nombres - Logique améliorée
            # Thèmes anglais sélectionnés (déplacé ici pour être après l'initialisation de self.anglais_column_component)
            selected_english_themes = []
            # Vérifier si la section "jeux à relier" est active
            if hasattr(self.anglais_column_component, 'english_relier_theme_checkboxes') and "english_relier_group" in allowed_keys:
                for theme_name, cb in self.anglais_column_component.english_relier_theme_checkboxes.items():
                    theme_cb_key = f"english_theme_{theme_name}_cb"
                    # Vérifier si la checkbox de thème elle-même est autorisée par le niveau actuel ET cochée
                    if theme_cb_key in allowed_keys and cb.isChecked():
                        selected_english_themes.append(theme_name)
            # print(f"DEBUG Apprentium: Thèmes anglais sélectionnés: {selected_english_themes}")

            sort_count_val = self._get_param_value_if_allowed("sort_count_input", "Ranger - nombre d'exercices", 0, allowed_keys) # Access via component
            is_croissant_selected = self.mesures_column_component.sort_type_croissant.isChecked(
            ) if "sort_type_croissant_cb" in allowed_keys else False
            is_decroissant_selected = self.mesures_column_component.sort_type_decroissant.isChecked(
            ) if "sort_type_decroissant_cb" in allowed_keys else False

            # Petits Problèmes Mathématiques
            math_problems_count_val = self._get_param_value_if_allowed("math_problems_count_input", "Nombre de problèmes", 0, allowed_keys)
            selected_math_problem_types = []
            if hasattr(self.calculs_column_component, 'math_problem_type_checkboxes') and "math_problems_group" in allowed_keys:
                for type_key, cb_widget in self.calculs_column_component.math_problem_type_checkboxes.items():
                    # Clé dans exercise_widgets_map
                    type_cb_key_map = f"math_problem_type_{type_key}_cb"
                    if type_cb_key_map in allowed_keys and cb_widget.isChecked():
                        # Utiliser la clé JSON (ex: "addition_simple")
                        selected_math_problem_types.append(type_key)
            
            # --- NEW: Measurement Story Problems ---
            measurement_problems_count_val = self._get_param_value_if_allowed("measurement_problems_count_input", "Problèmes de mesures - nombre", 0, allowed_keys)
            selected_measurement_problem_types = []
            if "measurement_problems_group" in allowed_keys: # Access via component
                for ptype, cb in zip(
                    ['longueur', 'masse', 'volume', 'temps', 'monnaie'],
                    self.mesures_column_component.measurement_problem_type_checkboxes
                ):
                    # Check if the checkbox itself is allowed by the current level AND is checked
                    if f"measurement_problem_{ptype}_cb" in allowed_keys and cb.isChecked():
                        selected_measurement_problem_types.append(ptype)
            # --- END NEW ---
            
            # Suites Logiques
            logical_sequences_count_val = self._get_param_value_if_allowed("logical_sequences_count_input", "Suites Logiques - nombre d'exercices", 0, allowed_keys) # Access via component
            logical_sequences_length_val = self._get_param_value_if_allowed("logical_sequences_length_input", "Suites Logiques - nombre d'éléments", 5, allowed_keys) # Access via component
            logical_sequences_params_for_builder = {
                'count': logical_sequences_count_val,
                'length': logical_sequences_length_val,
                'types': [],
                # Le 'step' n'est plus récupéré de l'UI
            }
            if "logical_sequences_type_arithmetic_plus_cb" in allowed_keys and self.mesures_column_component.logical_sequences_type_arithmetic_plus_cb.isChecked():
                logical_sequences_params_for_builder['types'].append(
                    'arithmetic_plus')
            if "logical_sequences_type_arithmetic_minus_cb" in allowed_keys and self.mesures_column_component.logical_sequences_type_arithmetic_minus_cb.isChecked():
                logical_sequences_params_for_builder['types'].append(
                    'arithmetic_minus')
            if "logical_sequences_type_arithmetic_multiply_cb" in allowed_keys and self.mesures_column_component.logical_sequences_type_arithmetic_multiply_cb.isChecked():
                logical_sequences_params_for_builder['types'].append(
                    'arithmetic_multiply')
            if "logical_sequences_type_arithmetic_divide_cb" in allowed_keys and self.mesures_column_component.logical_sequences_type_arithmetic_divide_cb.isChecked():
                logical_sequences_params_for_builder['types'].append(
                    'arithmetic_divide')

            # Si aucun type de suite n'est coché
            if not logical_sequences_params_for_builder['types']:
                # Ne pas générer d'exercices de suite
                logical_sequences_params_for_builder['count'] = 0

            if not is_croissant_selected and not is_decroissant_selected:  # Si aucun type de tri n'est sélectionné
                sort_count_val = 0

            params = { # All these parameters are now accessed via self.header_component or other specific widgets
                # Enumérer un nombre
                'enumerate_count': self._get_param_value_if_allowed("enumerate_count_input", "Enumérer - nombre d'exercices", 0, allowed_keys), # Access via component
                'enumerate_digits': self._get_param_value_if_allowed("enumerate_digits_input", "Enumérer - chiffres par nombre", 0, allowed_keys), # Access via component
                # Ranger les nombres
                'sort_count': sort_count_val,
                'sort_digits': self._get_param_value_if_allowed("sort_digits_input", "Ranger - chiffres par nombre", 0, allowed_keys), # Access via component
                'sort_n_numbers': self._get_param_value_if_allowed("sort_n_numbers_input", "Ranger - nombres à ranger", 0, allowed_keys), # Access via component
                'sort_type_croissant': is_croissant_selected,
                'sort_type_decroissant': is_decroissant_selected,
                'days': self.get_int(self.header_component.days_entry, field_name="Nombre de jours"), # Access via component
                'relier_count': n_mots_reliés,  # Already filtered based on english_relier_group
                'addition_count': self._get_param_value_if_allowed("addition_count_input", "Addition - nombre de calculs", 0, allowed_keys),
                'addition_num_operands': self._get_param_value_if_allowed("addition_num_operands_input", "Addition - nombre d'opérandes", 2, allowed_keys),
                'addition_digits': self._get_param_value_if_allowed("addition_digits_input", "Addition - chiffres", 0, allowed_keys),
                'addition_decimals': self._get_param_value_if_allowed("addition_decimals_input", "Addition - décimales", 0, allowed_keys),
                'subtraction_count': self._get_param_value_if_allowed("subtraction_count_input", "Soustraction - nombre de calculs", 0, allowed_keys),
                'subtraction_num_operands': self._get_param_value_if_allowed("subtraction_num_operands_input", "Soustraction - nombre d'opérandes", 2, allowed_keys),
                'subtraction_digits': self._get_param_value_if_allowed("subtraction_digits_input", "Soustraction - chiffres", 0, allowed_keys),
                'subtraction_decimals': self._get_param_value_if_allowed("subtraction_decimals_input", "Soustraction - décimales", 0, allowed_keys),
                'subtraction_negative': self._get_param_value_if_allowed("subtraction_negative_cb", "Soustraction négative possible", False, allowed_keys, value_type='bool'),
                'multiplication_count': self._get_param_value_if_allowed("multiplication_count_input", "Multiplication - nombre de calculs", 0, allowed_keys),
                'multiplication_num_operands': self._get_param_value_if_allowed("multiplication_num_operands_input", "Multiplication - nombre d'opérandes", 2, allowed_keys),
                'multiplication_digits': self._get_param_value_if_allowed("multiplication_digits_input", "Multiplication - chiffres", 0, allowed_keys),
                'multiplication_decimals': self._get_param_value_if_allowed("multiplication_decimals_input", "Multiplication - décimales", 0, allowed_keys),
                'division_count': self._get_param_value_if_allowed("division_count_input", "Division - nombre de calculs", 0, allowed_keys),
                'division_digits': self._get_param_value_if_allowed("division_digits_input", "Division - chiffres", 0, allowed_keys),
                'division_decimals': self._get_param_value_if_allowed("division_decimals_input", "Division - décimales", 0, allowed_keys),
                'division_reste': self._get_param_value_if_allowed("division_reste_cb", "Division avec reste", False, allowed_keys, value_type='bool'),
                'TENSES': TENSES,
                'VERBS': VERBS, # This is a constant, not a UI element
                'grammar_sentence_count': self._get_param_value_if_allowed("grammar_sentence_count_input", "Grammaire - nombre de phrases", 0, allowed_keys),
                'grammar_types': [t_name for t_name, cb_key, cb_widget in zip(['intransitive', 'transitive_direct', 'transitive_indirect', 'ditransitive'], ["intransitive_cb", "transitive_direct_cb", "transitive_indirect_cb", "ditransitive_cb"], [self.grammar_column_component.intransitive_checkbox, self.grammar_column_component.transitive_direct_checkbox, self.grammar_column_component.transitive_indirect_checkbox, self.grammar_column_component.ditransitive_checkbox]) if cb_key in allowed_keys and cb_widget.isChecked()],
                'get_random_phrases': get_random_phrases,
                'get_random_transformation': get_random_transformation,
                'generate_conversion_exercises': generate_conversion_exercises,
                'geo_ex_count': self._get_param_value_if_allowed("geo_ex_count_input", "Géométrie/mesures - nombre d'exercices", 0, allowed_keys), # Access via component
                'geo_types': [label for cb, label, cb_key in zip(self.mesures_column_component.geo_conv_type_checkboxes, ['longueur', 'masse', 'volume', 'temps', 'monnaie'], ["conv_type_longueur_cb", "conv_type_masse_cb", "conv_type_volume_cb", "conv_type_temps_cb", "conv_type_monnaie_cb"]) if cb_key in allowed_keys and cb.isChecked()],
                'geo_senses': [sense for sense, cb_key, cb_widget in zip(['direct', 'inverse'], ["conv_sens_direct_cb", "conv_sens_inverse_cb"], [self.mesures_column_component.conv_sens_direct, self.mesures_column_component.conv_sens_inverse]) if cb_key in allowed_keys and cb_widget.isChecked()], # Access via component
                'english_types': [etype for etype, cb_key, cb_widget in zip(['simple', 'complexe'], ["english_type_simple_cb", "english_type_complexe_cb"], [self.anglais_column_component.english_type_simple, self.anglais_column_component.english_type_complexe]) if cb_key in allowed_keys and cb_widget.isChecked()],
                'PHRASES_SIMPLES': PHRASES_SIMPLES, # This is a constant
                'PHRASES_COMPLEXES': PHRASES_COMPLEXES,
                'MOTS_A_RELIER': MOTS_A_RELIER,
                # Anglais
                'english_complete_count': n_complete,  # Already filtered
                'english_relier_count': n_relier,     # Already filtered
                # Orthographe
                # AJOUT DE CETTE LIGNE
                'generate_english_full_exercises_func': generate_english_full_exercises,
                'orthographe_ex_count': self._get_param_value_if_allowed("orthographe_ex_count_input", "Orthographe - nombre d'exercices", 0, allowed_keys), # Access via component
                # Encadrement
                'encadrement_params': encadrement_params_for_builder,
                # Comparer des nombres (Access via component)
                'compare_numbers_count': self._get_param_value_if_allowed("compare_numbers_count_input", "Comparer - nombre d'exercices", 0, allowed_keys),
                'compare_numbers_digits': self._get_param_value_if_allowed("compare_numbers_digits_input", "Comparer - chiffres par nombre", 0, allowed_keys),
                # Suites Logiques
                'logical_sequences_params': logical_sequences_params_for_builder,
                # Petits Problèmes
                'math_problems_count': math_problems_count_val,
                # --- NEW ---
                'measurement_problems_count': measurement_problems_count_val,
                'selected_measurement_problem_types': selected_measurement_problem_types,
                'selected_math_problem_types': selected_math_problem_types,
                # Nouveaux exercices de conjugaison
                'conj_complete_sentence_count': self._get_param_value_if_allowed("conj_complete_sentence_count_input", "Compléter phrases - nombre d'exercices", 0, allowed_keys),
                'conj_complete_pronoun_count': self._get_param_value_if_allowed("conj_complete_pronoun_count_input", "Compléter pronoms - nombre d'exercices", 0, allowed_keys),
                # Pour filtrer les problèmes par niveau dans le générateur
                'current_level_for_problems': self.current_level,
                'selected_english_themes': selected_english_themes,
                'current_level_for_conversions': self.current_level,
                'level_order_for_conversions': self.LEVEL_ORDER,
            }

            verbs_per_day_val = self._get_param_value_if_allowed("verbs_per_day_entry_input", "Verbes par jour", 0, allowed_keys)

            # Modifié
            params['generate_math_problems_func'] = generate_story_math_problems
            params['generate_measurement_story_problems_func'] = generate_measurement_story_problems # NEW
            # Construction corrigée pour conjugation_tenses
            conjugation_tenses_list = []
            for i, tense_cb_widget in enumerate(self.conjugaison_column_component.tense_checkboxes):
                tense_cb_key = None
                for map_key, map_widget in self.exercise_widgets_map.items():
                    if map_widget == tense_cb_widget:
                        tense_cb_key = map_key
                        break
                if tense_cb_key and tense_cb_key in allowed_keys and tense_cb_widget.isChecked():
                    conjugation_tenses_list.append(TENSES[i])
            params['conjugation_tenses'] = conjugation_tenses_list

            # Groupes de conjugaison et verbes usuels
            conjugation_groups_selected = [g for g, cb_key, cb_widget in zip([1, 2, 3], ["group_1_cb", "group_2_cb", "group_3_cb"], [self.conjugaison_column_component.group_1_checkbox, self.conjugaison_column_component.group_2_checkbox, self.conjugaison_column_component.group_3_checkbox]) if cb_key in allowed_keys and cb_widget.isChecked()]
            is_usual_verbs_selected = self.conjugaison_column_component.usual_verbs_checkbox.isChecked() if "usual_verbs_cb" in allowed_keys else False
            params['conjugation_groups'] = conjugation_groups_selected
            params['conjugation_usual'] = is_usual_verbs_selected

            if not conjugation_tenses_list or (not conjugation_groups_selected and not is_usual_verbs_selected):
                # Ne pas générer si pas de temps OU (pas de groupe ET pas d'usuels)
                verbs_per_day_val = 0 # No change here
            params['verbs_per_day'] = verbs_per_day_val
            # Construction corrigée pour grammar_transformations
            grammar_transformations_list = []
            for transfo_cb_widget in self.grammar_column_component.transfo_checkboxes:
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
            for ortho_cb_widget in self.orthographe_column_component.orthographe_homophone_checkboxes:
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
        self._execute_workbook_generation(generate_workbook_pdf, ".pdf", False)

    def generate_word(self):
        self._execute_workbook_generation(generate_workbook_docx, ".docx", False)

    def preview_pdf(self):
        self._execute_workbook_generation(generate_workbook_pdf, ".pdf", True)

    def preview_word(self):
        self._execute_workbook_generation(generate_workbook_docx, ".docx", True)

    def save_config(self):
        config = {}
        for name, widget, mode in self.config_fields:
            if mode == 'text':
                config[name] = widget.text() # Widget is now the actual QLineEdit instance
            elif mode == 'checked':
                config[name] = widget.isChecked() # Widget is now the actual QCheckBox instance
            elif mode == 'checked_list':
                config[name] = [cb.isChecked() for cb in widget] # Widget is the list of QCheckBoxes
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
                    widget_ref.setText(config.get(name, '')) # widget_ref is the QLineEdit
                elif mode == 'checked':
                    widget_ref.setChecked(config.get(name, False)) # widget_ref is the QCheckBox
                elif mode == 'checked_list':
                    states = config.get(name, [False]*len(widget_ref)) # widget_ref is the list of QCheckBoxes
                    for cb, state in zip(widget_ref, states):
                        cb.setChecked(state)
                elif mode == 'path_variable':
                    # Pour 'path_variable', widget_ref est 'self' (MainWindow)
                    self.selected_output_path = config.get(name, None)
                    # Notify the footer component to update its display
                    if self.footer_component:
                        self.footer_component.set_output_path_from_config(self.selected_output_path)

                elif mode == 'level_variable':
                    # Pour 'level_variable', widget_ref est 'self' (MainWindow)
                    # 'name' est 'current_level'
                    loaded_level_name = config.get(name, None)
                    if loaded_level_name and loaded_level_name in self.level_buttons:  # Accéder à self.level_buttons
                        button_to_select = self.level_buttons[loaded_level_name]
                        # Appeler select_level pour restaurer l'état du niveau
                        # This will call set_current_level on MainWindow
                        self.header_component._select_level_internal(loaded_level_name, button_to_select)
        except FileNotFoundError: # This is a common case for first run
            print(
                f"Fichier de configuration non trouvé : {self.config_path}. Un nouveau sera créé à la fermeture si nécessaire.")
        except json.JSONDecodeError:
            print(
                f"Erreur de décodage JSON dans {self.config_path}. Le fichier est peut-être corrompu.")
        except Exception as e:
            print(
                f"Erreur inattendue lors du chargement de la configuration : {type(e).__name__} - {e}")
            # import traceback; traceback.print_exc() # Décommenter pour un débogage plus détaillé
        
        # Update the SettingsTab component with the latest data if it exists
        if hasattr(self, 'parametres_tab_component'):
            self.parametres_tab_component.update_data(self.EXERCISES_BY_LEVEL_INCREMENTAL)
            
    def closeEvent(self, event):
        self.save_config()
        super().closeEvent(event)

    def reload_level_config_and_update_ui(self):
        """
        Recharge le fichier levels_config.json et met à jour toutes les parties pertinentes de l'interface.
        Cette méthode est appelée depuis l'onglet Paramètres après la sauvegarde d'une modification.
        """
        # --- 1. Recharger la configuration des niveaux ---
        self.level_configuration_data = {}
        default_level_order = ["CP", "CE1", "CE2", "CM1", "CM2"]
        default_exercises_by_level = {}  # Fallback vide
        try:
            levels_config_path = get_resource_path('levels_config.json')
            with open(levels_config_path, 'r', encoding='utf-8') as f:
                self.level_configuration_data = json.load(f)
        except FileNotFoundError:
            print(f"ERREUR: Fichier de configuration des niveaux '{levels_config_path}' introuvable. Utilisation des valeurs par défaut.")
        except json.JSONDecodeError:
            print(f"ERREUR: Fichier de configuration des niveaux '{levels_config_path}' JSON invalide. Utilisation des valeurs par défaut.")

        # Mettre à jour les attributs de la fenêtre principale avec la configuration rechargée
        self.LEVEL_ORDER = self.level_configuration_data.get("level_order", default_level_order)
        self.EXERCISES_BY_LEVEL_INCREMENTAL = self.level_configuration_data.get("exercises_by_level", default_exercises_by_level)

        # --- 2. Mettre à jour les composants de l'interface ---
        if hasattr(self, 'parametres_tab_component'):
            self.parametres_tab_component.update_data(self.EXERCISES_BY_LEVEL_INCREMENTAL)

        self.update_exercise_visibility()

    def get_exercises_for_level(self, target_level):
        ALWAYS_VISIBLE_KEYS = {
            "header_entry_input",
            "show_name_checkbox_cb",
            "show_note_checkbox_cb",
            "days_entry_input",
            "filename_entry_input",
        }
        if not target_level:  # If None or empty string, show all exercises
            return list(self.exercise_widgets_map.keys())

        allowed_exercises = set()
        # Iterate through LEVEL_ORDER up to and including target_level
        for level_in_order in self.LEVEL_ORDER:
            exercises_for_this_level = self.EXERCISES_BY_LEVEL_INCREMENTAL.get(level_in_order, [])
            allowed_exercises.update(exercises_for_this_level)
            if level_in_order == target_level:
                break

        # Ensure header and footer controls are always visible
        allowed_exercises.update(ALWAYS_VISIBLE_KEYS)
        return list(allowed_exercises)

    def update_exercise_visibility(self):
        # This method is called by set_current_level in MainWindow
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
        self.calculs_column_component.calc_title_label.setVisible(is_calc_column_active)

        is_geo_column_active = False
        for section_key in self.column_section_keys.get("geo", []): # Access via component
            if section_key in allowed_exercise_keys:
                is_geo_column_active = True
                break
        self.mesures_column_component.geo_title_label.setVisible(is_geo_column_active)

        is_conj_column_active = False
        for section_key in self.column_section_keys.get("conj", []):
            if section_key in allowed_exercise_keys:
                is_conj_column_active = True
                break
        self.conjugaison_column_component.conj_title_label.setVisible(is_conj_column_active)

        is_grammar_column_active = False
        for section_key in self.column_section_keys.get("grammar", []): # This line was not changed, but it's part of the context.
            if section_key in allowed_exercise_keys:
                is_grammar_column_active = True
                break
        self.grammar_column_component.grammar_title_label.setVisible(is_grammar_column_active)

        # Pour la colonne combinée Orthographe/Anglais
        # Orthographe
        is_ortho_section_active = False
        for section_key in self.column_section_keys.get("ortho", []):
            if section_key in allowed_exercise_keys:
                is_ortho_section_active = True
                break
        self.orthographe_column_component.orthographe_title_label.setVisible(is_ortho_section_active)
        self.orthographe_column_component.setVisible(is_ortho_section_active)
        # Anglais
        is_english_section_active = False
        for section_key in self.column_section_keys.get("english", []):
            if section_key in allowed_exercise_keys:
                is_english_section_active = True
                break
        self.anglais_column_component.english_title_label.setVisible(is_english_section_active)
        self.anglais_column_component.setVisible(is_english_section_active)
        is_ortho_anglais_column_active = is_ortho_section_active or is_english_section_active

        # 3. Préparer les listes pour la réorganisation du QSplitter
        column_activity_map = {
            'calc': is_calc_column_active,
            'geo': is_geo_column_active,
            'conj': is_conj_column_active,
            'ortho_anglais': is_ortho_anglais_column_active,
            'grammar': is_grammar_column_active,
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
        return self.header_component.get_selected_conversion_types() # This method is no longer needed in MainWindow

    def get_selected_conversion_senses(self):
        return self.header_component.get_selected_conversion_senses() # This method is no longer needed in MainWindow


if __name__ == "__main__":
    from PyQt6.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), "Apprentium.ico")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    app.exec()
