from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QCheckBox, QPushButton, QComboBox, QSplitter,
                             QHeaderView, QLabel, QMessageBox, QScrollArea, QFrame, QSizePolicy,
                             QGroupBox, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt, QTimer # Import QTimer for feedback
from PyQt6.QtGui import QColor # Import QColor for styling
import json
import os
import sys

class SettingsTab(QWidget):
    def __init__(self, parent_window, UI_STYLE_CONFIG, level_order, exercises_by_level_incremental, exercise_widgets_map, config_path):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0) # Remove default margins
        self.parent_window = parent_window
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG
        self.level_order = level_order
        self.exercise_widgets_map = exercise_widgets_map
        self.config_path = config_path # Path to levels_config.json
        self.is_dirty = False # To track unsaved changes

        self._exercise_display_names = self._build_exercise_display_names()
        self._exercise_min_levels = self._determine_initial_min_levels(exercises_by_level_incremental)
        self._categorized_exercise_keys = self._build_categorized_exercise_keys()

        self._setup_ui()
        self._populate_table()
        self._connect_general_settings_signals()

    def _get_predefined_exercise_names(self):
        """
        Returns a dictionary mapping internal exercise_widgets_map keys
        to user-friendly display names for the settings table.
        This should cover all relevant QGroupBoxes, QLineEdits, and QCheckBoxes.
        """
        return {
            # Calculs
            "enumerate_group": "Enumérer un nombre (Groupe)",
            "enumerate_count_input": "Enumérer - Nombre d'exercices",
            "enumerate_digits_input": "Enumérer - Chiffres par nombre",
            "addition_group": "Addition (Groupe)",
            "addition_count_input": "Addition - Nombre de calculs",
            "addition_digits_input": "Addition - Chiffres par opérande",
            "addition_decimals_input": "Addition - Nombre de décimales",
            "addition_num_operands_input": "Addition - Nombre d'opérandes",
            "subtraction_group": "Soustraction (Groupe)",
            "subtraction_count_input": "Soustraction - Nombre de calculs",
            "subtraction_digits_input": "Soustraction - Chiffres par opérande",
            "subtraction_decimals_input": "Soustraction - Nombre de décimales",
            "subtraction_num_operands_input": "Soustraction - Nombre d'opérandes",
            "subtraction_negative_cb": "Soustraction - Négative possible",
            "multiplication_group": "Multiplication (Groupe)",
            "multiplication_count_input": "Multiplication - Nombre de calculs",
            "multiplication_digits_input": "Multiplication - Chiffres par opérande",
            "multiplication_decimals_input": "Multiplication - Nombre de décimales",
            "multiplication_num_operands_input": "Multiplication - Nombre d'opérandes",
            "division_group": "Division (Groupe)",
            "division_count_input": "Division - Nombre de calculs",
            "division_digits_input": "Division - Chiffres par opérande",
            "division_decimals_input": "Division - Nombre de décimales",
            "division_reste_cb": "Division - Avec reste",
            "math_problems_group": "Petits Problèmes (Groupe)",
            "math_problems_count_input": "Petits Problèmes - Nombre de problèmes",

            # Mesures
            "geo_conv_group": "Conversions (Groupe)",
            "geo_ex_count_input": "Conversions - Nombre d'exercices",
            "conv_type_longueur_cb": "Conversion - Longueur",
            "conv_type_masse_cb": "Conversion - Masse",
            "conv_type_volume_cb": "Conversion - Volume",
            "conv_type_temps_cb": "Conversion - Temps",
            "conv_type_monnaie_cb": "Conversion - Monnaie",
            "conv_sens_direct_cb": "Conversion - Sens direct",
            "conv_sens_inverse_cb": "Conversion - Sens inverse",
            "measurement_problems_group": "Problèmes de mesures (Groupe)",
            "measurement_problems_count_input": "Problèmes de mesures - Nombre",
            "measurement_problem_longueur_cb": "Problème Mesures - Longueur",
            "measurement_problem_masse_cb": "Problème Mesures - Masse",
            "measurement_problem_volume_cb": "Problème Mesures - Volume",
            "measurement_problem_temps_cb": "Problème Mesures - Temps",
            "measurement_problem_monnaie_cb": "Problème Mesures - Monnaie",
            "geo_sort_group": "Ranger les nombres (Groupe)",
            "sort_count_input": "Ranger - Nombre d'exercices",
            "sort_digits_input": "Ranger - Chiffres par nombre",
            "sort_n_numbers_input": "Ranger - Nombres à ranger",
            "sort_type_croissant_cb": "Ranger - Croissant",
            "sort_type_decroissant_cb": "Ranger - Décroissant",
            "geo_encadrement_group": "Encadrer un nombre (Groupe)",
            "encadrement_count_input": "Encadrer - Nombre d'exercices",
            "encadrement_digits_input": "Encadrer - Chiffres par nombre",
            "encadrement_unite_cb": "Encadrer - Unité",
            "encadrement_dizaine_cb": "Encadrer - Dizaine",
            "encadrement_centaine_cb": "Encadrer - Centaine",
            "encadrement_millier_cb": "Encadrer - Millier",
            "geo_compare_numbers_group": "Comparer des nombres (Groupe)",
            "compare_numbers_count_input": "Comparer - Nombre d'exercices",
            "compare_numbers_digits_input": "Comparer - Chiffres par nombre",
            "geo_logical_sequences_group": "Suites Logiques (Groupe)",
            "logical_sequences_count_input": "Suites Logiques - Nombre d'exercices",
            "logical_sequences_length_input": "Suites Logiques - Longueur de la suite",
            "logical_sequences_type_arithmetic_plus_cb": "Suites Logiques - Arithmétique (+)",
            "logical_sequences_type_arithmetic_minus_cb": "Suites Logiques - Arithmétique (-)",
            "logical_sequences_type_arithmetic_multiply_cb": "Suites Logiques - Arithmétique (x)",
            "logical_sequences_type_arithmetic_divide_cb": "Suites Logiques - Arithmétique (÷)",

            # Conjugaison
            "conj_groups_group": "Groupes de verbes (Groupe)",
            "verbs_per_day_entry_input": "Conjugaison - Nombre de verbes",
            "group_1_cb": "Conjugaison - 1er groupe",
            "group_2_cb": "Conjugaison - 2ème groupe",
            "group_3_cb": "Conjugaison - 3ème groupe",
            "usual_verbs_cb": "Conjugaison - Verbes usuels",
            "conj_tenses_group": "Temps de conjugaison (Groupe)",
            "tense_present_cb": "Conjugaison - Temps Présent",
            "tense_imparfait_cb": "Conjugaison - Temps Imparfait",
            "tense_passe_simple_cb": "Conjugaison - Temps Passé Simple",
            "tense_futur_simple_cb": "Conjugaison - Temps Futur Simple",
            "tense_passe_compose_cb": "Conjugaison - Temps Passé Composé",
            "tense_plus_que_parfait_cb": "Conjugaison - Temps Plus-que-parfait",
            "tense_conditionnel_present_cb": "Conjugaison - Temps Conditionnel Présent",
            "tense_imperatif_present_cb": "Conjugaison - Temps Impératif Présent",
            "conj_complete_sentence_group": "Phrases à compléter (Conjugaison) (Groupe)",
            "conj_complete_sentence_count_input": "Conjugaison - Phrases à compléter (Nb)",
            "conj_complete_pronoun_group": "Pronoms à compléter (Conjugaison) (Groupe)",
            "conj_complete_pronoun_count_input": "Conjugaison - Pronoms à compléter (Nb)",

            # Grammaire
            "grammar_params_group": "Paramètres de grammaire (Groupe)",
            "grammar_sentence_count_input": "Grammaire - Nombre de phrases",
            "grammar_types_group": "Type de phrase (Grammaire) (Groupe)",
            "intransitive_cb": "Grammaire - Intransitive",
            "transitive_direct_cb": "Grammaire - Transitive directe",
            "transitive_indirect_cb": "Grammaire - Transitive indirecte",
            "ditransitive_cb": "Grammaire - Ditransitive",
            "grammar_transfo_group": "Transformations (Grammaire) (Groupe)",
            "transfo_singulier_pluriel_cb": "Grammaire - Singulier/Pluriel",
            "transfo_masculin_feminin_cb": "Grammaire - Masculin/Féminin",
            "transfo_present_passe_compose_cb": "Grammaire - Présent/Passé Composé",
            "transfo_present_imparfait_cb": "Grammaire - Présent/Imparfait",
            "transfo_present_futur_simple_cb": "Grammaire - Présent/Futur Simple",
            "transfo_indicatif_imperatif_cb": "Grammaire - Indicatif/Impératif",
            "transfo_voix_active_passive_cb": "Grammaire - Voix Active/Passive",
            "transfo_declarative_interrogative_cb": "Grammaire - Déclarative/Interrogative",
            "transfo_declarative_exclamative_cb": "Grammaire - Déclarative/Exclamative",
            "transfo_declarative_imperative_cb": "Grammaire - Déclarative/Impérative",
            "transfo_affirmative_negative_cb": "Grammaire - Affirmative/Négative",

            # Orthographe
            "ortho_params_group": "Paramètres d'orthographe (Groupe)",
            "orthographe_ex_count_input": "Orthographe - Nombre d'exercices",
            "ortho_homophones_group": "Homophones (Orthographe) (Groupe)",
            "homophone_a_cb": "Homophone - a / à",
            "homophone_et_cb": "Homophone - et / est",
            "homophone_on_cb": "Homophone - on / ont",
            "homophone_son_cb": "Homophone - son / sont",
            "homophone_ce_cb": "Homophone - ce / se",
            "homophone_ou_cb": "Homophone - ou / où",
            "homophone_ces_cb": "Homophone - ces / ses",
            "homophone_mes_cb": "Homophone - mes / mais / met / mets",

            # Anglais
            "english_complete_group": "Phrases à compléter (Anglais) (Groupe)",
            "english_complete_count_input": "Anglais - Phrases à compléter (Nb)",
            "english_type_simple_cb": "Anglais - Phrases simples",
            "english_type_complexe_cb": "Anglais - Phrases complexes",
            "english_relier_group": "Jeux à relier (Anglais) (Groupe)",
            "english_relier_count_input": "Anglais - Jeux à relier (Nb)",
            "relier_count_input": "Anglais - Mots par jeu à relier",
        }

    def _build_exercise_display_names(self):
        """
        Builds the final mapping using predefined names and dynamic ones.
        Filters out keys not present in exercise_widgets_map.
        """
        final_display_names = {}
        # Add predefined names first
        for key, display_name in self._get_predefined_exercise_names().items():
            if key in self.exercise_widgets_map: # Only include if the widget actually exists
                final_display_names[key] = display_name

        # Add dynamically generated checkboxes (English themes, Math problem types)
        for key in self.exercise_widgets_map.keys():
            if key.startswith("english_theme_") and key not in final_display_names:
                theme_name = key.replace("english_theme_", "").replace("_cb", "").replace("_", " ").capitalize()
                final_display_names[key] = f"Anglais - Thème {theme_name}"
            elif key.startswith("math_problem_type_") and key not in final_display_names:
                type_name = key.replace("math_problem_type_", "").replace("_cb", "").replace("_", " ").capitalize()
                final_display_names[key] = f"Problème Maths - {type_name}"

        return final_display_names

    def _build_categorized_exercise_keys(self):
        """
        Organizes exercise keys into categories for display in the table.
        Filters out keys that do not have a corresponding widget in exercise_widgets_map.
        """
        categorized_keys = {
            "Calculs": [
                "enumerate_group", "enumerate_count_input", "enumerate_digits_input",
                "addition_group", "addition_count_input", "addition_digits_input", "addition_decimals_input", "addition_num_operands_input",
                "subtraction_group", "subtraction_count_input", "subtraction_digits_input", "subtraction_decimals_input", "subtraction_num_operands_input", "subtraction_negative_cb",
                "multiplication_group", "multiplication_count_input", "multiplication_digits_input", "multiplication_decimals_input", "multiplication_num_operands_input",
                "division_group", "division_count_input", "division_digits_input", "division_decimals_input", "division_reste_cb",
                "math_problems_group", "math_problems_count_input",
            ],
            "Mesures": [
                "geo_conv_group", "geo_ex_count_input", "conv_type_longueur_cb", "conv_type_masse_cb", "conv_type_volume_cb", "conv_type_temps_cb", "conv_type_monnaie_cb", "conv_sens_direct_cb", "conv_sens_inverse_cb",
                "measurement_problems_group", "measurement_problems_count_input", "measurement_problem_longueur_cb", "measurement_problem_masse_cb", "measurement_problem_volume_cb", "measurement_problem_temps_cb", "measurement_problem_monnaie_cb",
                "geo_sort_group", "sort_count_input", "sort_digits_input", "sort_n_numbers_input", "sort_type_croissant_cb", "sort_type_decroissant_cb",
                "geo_encadrement_group", "encadrement_count_input", "encadrement_digits_input", "encadrement_unite_cb", "encadrement_dizaine_cb", "encadrement_centaine_cb", "encadrement_millier_cb",
                "geo_compare_numbers_group", "compare_numbers_count_input", "compare_numbers_digits_input",
                "geo_logical_sequences_group", "logical_sequences_count_input", "logical_sequences_length_input", "logical_sequences_type_arithmetic_plus_cb", "logical_sequences_type_arithmetic_minus_cb", "logical_sequences_type_arithmetic_multiply_cb", "logical_sequences_type_arithmetic_divide_cb",
            ],
            "Conjugaison": [
                "conj_groups_group", "verbs_per_day_entry_input", "group_1_cb", "group_2_cb", "group_3_cb", "usual_verbs_cb",
                "conj_tenses_group", "tense_present_cb", "tense_imparfait_cb", "tense_passe_simple_cb", "tense_futur_simple_cb", "tense_passe_compose_cb", "tense_plus_que_parfait_cb", "tense_conditionnel_present_cb", "tense_imperatif_present_cb",
                "conj_complete_sentence_group", "conj_complete_sentence_count_input",
                "conj_complete_pronoun_group", "conj_complete_pronoun_count_input",
            ],
            "Grammaire": [
                "grammar_params_group", "grammar_sentence_count_input",
                "grammar_types_group", "intransitive_cb", "transitive_direct_cb", "transitive_indirect_cb", "ditransitive_cb",
                "grammar_transfo_group", "transfo_singulier_pluriel_cb", "transfo_masculin_feminin_cb", "transfo_present_passe_compose_cb", "transfo_present_imparfait_cb", "transfo_present_futur_simple_cb", "transfo_indicatif_imperatif_cb", "transfo_voix_active_passive_cb", "transfo_declarative_interrogative_cb", "transfo_declarative_exclamative_cb", "transfo_declarative_imperative_cb", "transfo_affirmative_negative_cb",
            ],
            "Orthographe": [
                "ortho_params_group", "orthographe_ex_count_input",
                "ortho_homophones_group", "homophone_a_cb", "homophone_et_cb", "homophone_on_cb", "homophone_son_cb", "homophone_ce_cb", "homophone_ou_cb", "homophone_ces_cb", "homophone_mes_cb",
            ],
            "Anglais": [
                "english_complete_group", "english_complete_count_input", "english_type_simple_cb", "english_type_complexe_cb",
                "english_relier_group", "english_relier_count_input", "relier_count_input",
            ]
        }

        # Add dynamic keys to their categories
        for key in self.exercise_widgets_map.keys():
            if key.startswith("english_theme_") and key not in categorized_keys["Anglais"]:
                categorized_keys["Anglais"].append(key)
            elif key.startswith("math_problem_type_") and key not in categorized_keys["Calculs"]:
                categorized_keys["Calculs"].append(key)

        # Filter out keys that don't exist in _exercise_display_names (which itself is filtered by exercise_widgets_map)
        filtered_categorized_keys = {}
        for category, keys in categorized_keys.items():
            filtered_keys = [k for k in keys if k in self._exercise_display_names]
            if filtered_keys: # Only include category if it has active exercises
                filtered_categorized_keys[category] = filtered_keys
        return filtered_categorized_keys

    def _determine_initial_min_levels(self, exercises_by_level_incremental):
        min_levels = {}
        all_exercise_keys = set(self.exercise_widgets_map.keys()) # All possible keys

        for ex_key in all_exercise_keys:
            found_min_level = "Désactivé" # Default if not found in any level
            for level in self.level_order:
                if ex_key in exercises_by_level_incremental.get(level, set()):
                    found_min_level = level
                    break # Found the first level this exercise appears in
            min_levels[ex_key] = found_min_level
        return min_levels

    def _setup_ui(self):
        # Main layout for the whole tab is horizontal, to hold the splitter
        main_h_layout = QHBoxLayout(self)
        main_h_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_h_layout.addWidget(splitter)

        # --- Left Panel (Table for exercise levels) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 10, 10, 10) # Left, Top, Right, Bottom
        left_layout.setSpacing(10)

        # Top layout for title and save button
        top_layout = QHBoxLayout()
        title_label = QLabel("Configuration des Niveaux d'Exercice")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #E0E0E0;")
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        self.save_button = QPushButton()
        self.save_button.clicked.connect(self._save_and_refresh)
        self._update_save_button_style() # Set initial style
        top_layout.addWidget(self.save_button)

        left_layout.addLayout(top_layout)

        description_label = QLabel("Définissez le niveau minimum pour chaque exercice. Les exercices seront disponibles à ce niveau et à tous les niveaux supérieurs. Cliquez sur 'Sauvegarder' pour appliquer les changements.")
        description_label.setStyleSheet("font-size: 14px; color: #B0BEC5;")
        description_label.setWordWrap(True)
        left_layout.addWidget(description_label, alignment=Qt.AlignmentFlag.AlignTop)

        # Table Widget setup
        self.table_widget = QTableWidget()
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Laisser QScrollArea gérer le défilement vertical
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Laisser QScrollArea gérer le défilement horizontal
        self.table_widget.verticalHeader().setVisible(False) # Hide default row headers
        self.table_widget.setStyleSheet(self.UI_STYLE_CONFIG["table_widget"]["style"]) # Apply style

        # Scroll area for the table, now inside the left panel
        table_scroll_area = QScrollArea()
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setWidget(self.table_widget)
        table_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        left_layout.addWidget(table_scroll_area)
        self.table_scroll_area = table_scroll_area # Keep a reference for scroll management

        scrollbar_style = self.UI_STYLE_CONFIG["scroll_bar"]["style_template"].format(
            **self.UI_STYLE_CONFIG["scroll_bar"]["values"]
        )
        table_scroll_area.setStyleSheet(scrollbar_style)

        # --- Right Panel (for future General Settings) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 20, 10) # Left, Top, Right, Bottom
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        general_title_label = QLabel("Paramètres Généraux")
        general_title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #E0E0E0;")
        right_layout.addWidget(general_title_label)

        # --- Window Size Settings ---
        window_group = QGroupBox("Taille de la fenêtre au démarrage")
        window_group.setStyleSheet(self.UI_STYLE_CONFIG["group_boxes"]["base_style_template"].format(border_color="#7F8C8D"))
        window_layout = QVBoxLayout(window_group)

        self.fullscreen_checkbox = QCheckBox("Lancer en plein écran (maximisé)")
        self.fullscreen_checkbox.setStyleSheet("QCheckBox { color: #ECF0F1; }")
        window_layout.addWidget(self.fullscreen_checkbox)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Taille personnalisée :"))
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Largeur")
        self.width_input.setMaximumWidth(80)
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Hauteur")
        self.height_input.setMaximumWidth(80)
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(QLabel("x"))
        size_layout.addWidget(self.height_input)
        size_layout.addWidget(QLabel("px"))
        size_layout.addStretch()

        # Apply line edit style
        lineedit_style = self.UI_STYLE_CONFIG["line_edits"]["default"]
        self.width_input.setStyleSheet(lineedit_style)
        self.height_input.setStyleSheet(lineedit_style)

        window_layout.addLayout(size_layout)
        right_layout.addWidget(window_group)

        # --- Output Folder Settings ---
        output_group = QGroupBox("Dossier de sortie des fichiers générés")
        output_group.setStyleSheet(self.UI_STYLE_CONFIG["group_boxes"]["base_style_template"].format(border_color="#7F8C8D"))
        output_layout = QVBoxLayout(output_group)
        self.choose_output_folder_btn = QPushButton("Définir le dossier de sortie…")
        self.choose_output_folder_btn.setStyleSheet(self.UI_STYLE_CONFIG["buttons"]["action_button_base_style_template"].format(
            bg_color=self.UI_STYLE_CONFIG["buttons"]["select_folder"]["bg_color"],
            disabled_bg_color=self.UI_STYLE_CONFIG["buttons"]["disabled"]["bg_color"],
            disabled_text_color=self.UI_STYLE_CONFIG["buttons"]["disabled"]["text_color"],
            pressed_bg_color=self.UI_STYLE_CONFIG["buttons"]["select_folder"]["pressed_bg_color"]
        ))
        self.choose_output_folder_btn.clicked.connect(self.choose_output_folder)
        self.choose_output_folder_btn.setFixedWidth(300) # Définir une largeur fixe
        output_layout.addWidget(self.choose_output_folder_btn)
        self.output_path_label = QLabel()
        self.output_path_label.setStyleSheet("color: #E0E0E0; font-size: 13px; margin-top: 4px;")
        output_layout.addWidget(self.output_path_label)
        right_layout.addWidget(output_group)
        # Afficher le chemin actuel au démarrage
        config_path = os.path.join(os.path.dirname(__file__), '../config.json')
        config_path = os.path.abspath(config_path)
        try:
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            folder = config.get('selected_output_path', '')
            if folder:
                self.output_path_label.setText(f"Dossier de sortie actuel : {folder}")
            else:
                # Par défaut : dossier output/ à côté de l'exécutable
                default_output = os.path.abspath(os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(__file__)), 'output'))
                self.output_path_label.setText(f"Dossier de sortie actuel : {default_output} (par défaut)")
        except Exception:
            default_output = os.path.abspath(os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(__file__)), 'output'))
            self.output_path_label.setText(f"Dossier de sortie actuel : {default_output} (par défaut)")

        right_layout.addStretch()

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        # Set initial sizes to be 50/50
        QTimer.singleShot(0, lambda: splitter.setSizes([self.width() // 2, self.width() // 2]))

    def _connect_general_settings_signals(self):
        """Connects signals for the general settings widgets."""
        self.fullscreen_checkbox.stateChanged.connect(self._on_fullscreen_changed)
        self.fullscreen_checkbox.stateChanged.connect(self._mark_as_dirty)
        self.width_input.textChanged.connect(self._mark_as_dirty)
        self.height_input.textChanged.connect(self._mark_as_dirty)
        # Set initial state for enabled/disabled inputs based on checkbox
        self._on_fullscreen_changed(self.fullscreen_checkbox.checkState())

    def _populate_table(self):
        self.table_widget.setRowCount(0) # Clear existing rows
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Exercice", "Niveau Minimum"])
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        # Définir une largeur fixe pour la colonne de sélection du niveau pour la rapprocher du texte.
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table_widget.horizontalHeader().resizeSection(1, 180) # Ajustez cette valeur si nécessaire

        # Disable signals during population to avoid re-entry issues
        self.table_widget.blockSignals(True)

        # Map pour associer les catégories aux couleurs des titres de colonnes
        category_color_map = {
            "Calculs": self.UI_STYLE_CONFIG["labels"]["column_title_colors"]["calc"],
            "Mesures": self.UI_STYLE_CONFIG["labels"]["column_title_colors"]["geo"],
            "Conjugaison": self.UI_STYLE_CONFIG["labels"]["column_title_colors"]["conj"],
            "Grammaire": self.UI_STYLE_CONFIG["labels"]["column_title_colors"]["grammar"],
            "Orthographe": self.UI_STYLE_CONFIG["labels"]["column_title_colors"]["ortho"],
            "Anglais": self.UI_STYLE_CONFIG["labels"]["column_title_colors"]["english"],
            # "Général" category removed from table
        }

        row = 0
        for category_name, exercise_keys_in_category in self._categorized_exercise_keys.items():
            # Category Header Row
            self.table_widget.insertRow(row)
            header_item = QTableWidgetItem(category_name)
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            header_item.setFlags(Qt.ItemFlag.NoItemFlags) # Make it non-selectable

            # Appliquer la couleur de fond spécifique à la catégorie
            category_color_hex = category_color_map.get(category_name, "#4A4A4A")
            header_item.setBackground(QColor(category_color_hex))
            # Texte en noir pour un meilleur contraste sur les couleurs vives
            header_item.setForeground(QColor("black"))

            font = header_item.font()
            font.setBold(True)
            font.setPointSize(14)
            header_item.setFont(font)

            self.table_widget.setSpan(row, 0, 1, 2) # Span across both columns
            self.table_widget.setItem(row, 0, header_item)
            row += 1

            for exercise_key in exercise_keys_in_category:
                # Ensure the exercise key actually has a display name (i.e., it's a valid widget)
                if exercise_key not in self._exercise_display_names:
                    continue

                self.table_widget.insertRow(row)
                display_name = self._exercise_display_names[exercise_key]
                name_item = QTableWidgetItem()
                font = name_item.font()

                if "(Groupe)" in display_name:
                    name_item.setText(display_name)
                    font.setBold(True)
                else:
                    name_item.setText("    " + display_name) # Ajout de l'indentation
                name_item.setFont(font)
                name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable) # Make name selectable but not editable
                self.table_widget.setItem(row, 0, name_item)

                level_combo = QComboBox()
                level_combo.addItems(["Désactivé"] + self.level_order)
                level_combo.setStyleSheet("QComboBox { color: white; background-color: #3C3C3C; border: 1px solid #555555; border-radius: 4px; padding: 2px; } QComboBox::drop-down { border: 0px; } QComboBox::down-arrow { image: url(no_arrow.png); } QComboBox QAbstractItemView { color: white; background-color: #3C3C3C; selection-background-color: #0078D7; }")
                level_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                
                current_min_level = self._exercise_min_levels.get(exercise_key, "Désactivé")
                index = level_combo.findText(current_min_level)
                if index != -1:
                    level_combo.setCurrentIndex(index)

                level_combo.setProperty("exercise_key", exercise_key)
                level_combo.currentIndexChanged.connect(self._on_level_selected)

                cell_widget = QWidget()
                cell_layout = QHBoxLayout(cell_widget)
                cell_layout.addWidget(level_combo)
                cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                self.table_widget.setCellWidget(row, 1, cell_widget)
                row += 1

        self.table_widget.setRowCount(row) # Adjust total row count
        self.table_widget.blockSignals(False)

    def _update_save_button_style(self):
        """Applies a style to the save button based on the dirty state."""
        btn_cfg = self.UI_STYLE_CONFIG["buttons"]
        if self.is_dirty:
            # Style for "needs saving" - using a visible color like orange/red
            style = btn_cfg["action_button_base_style_template"].format(
                bg_color=btn_cfg["pdf"]["bg_color"],
                disabled_bg_color=btn_cfg["disabled"]["bg_color"],
                disabled_text_color=btn_cfg["disabled"]["text_color"],
                pressed_bg_color=btn_cfg["pdf"]["pressed_bg_color"]
            )
            self.save_button.setText("Sauvegarder*")
        else:
            # Style for "saved" - using a neutral/positive color like green
            style = btn_cfg["action_button_base_style_template"].format(
                bg_color=btn_cfg["select_folder"]["bg_color"],
                disabled_bg_color=btn_cfg["disabled"]["bg_color"],
                disabled_text_color=btn_cfg["disabled"]["text_color"],
                pressed_bg_color=btn_cfg["select_folder"]["pressed_bg_color"]
            )
            self.save_button.setText("Sauvegardé")
        self.save_button.setStyleSheet(style)

    def _on_fullscreen_changed(self, state):
        """Enables or disables the custom size inputs based on the fullscreen checkbox."""
        is_fullscreen = (state == Qt.CheckState.Checked)
        self.width_input.setEnabled(not is_fullscreen)
        self.height_input.setEnabled(not is_fullscreen)

    def _on_level_selected(self, index):
        """Called when a level is changed in a ComboBox. Does not save automatically."""
        combo_box = self.sender()
        exercise_key = combo_box.property("exercise_key")
        selected_level = combo_box.currentText()

        # Mettre à jour le modèle interne pour la clé principale
        self._exercise_min_levels[exercise_key] = selected_level
        
        # Mettre également à jour la clé de la ligne associée, si elle existe, pour les garder synchronisées.
        # Cela garantit que le masquage d'une entrée masque également la ligne de son étiquette.
        row_key = None
        if exercise_key.endswith("_input"):
            row_key = exercise_key.replace("_input", "_row")
        elif exercise_key.endswith("_cb"):
            # Les cases à cocher n'ont pas toujours de lignes, mais nous gérons le cas si elles en ont.
            row_key = exercise_key.replace("_cb", "_row")

        if row_key and row_key in self._exercise_min_levels:
            self._exercise_min_levels[row_key] = selected_level

        self._mark_as_dirty()

    def _mark_as_dirty(self, *args):
        """Marks the settings as changed and updates the save button."""
        if not self.is_dirty:
            self.is_dirty = True
            self.save_button.setText("Sauvegarder*") # Set text immediately
            self._update_save_button_style() # Apply style

    def _save_configuration(self):
        try:
            # Load existing levels_config.json to preserve other keys if any
            levels_config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    levels_config = json.load(f)

            exercises_by_level_output = {level: [] for level in self.level_order}
            for exercise_key, min_level in self._exercise_min_levels.items():
                if min_level == "Désactivé":
                    continue
                
                try:
                    min_level_idx = self.level_order.index(min_level)
                except ValueError:
                    print(f"Warning: Invalid min_level '{min_level}' for exercise '{exercise_key}'. Skipping.")
                    continue

                for i in range(min_level_idx, len(self.level_order)):
                    level_name = self.level_order[i]
                    exercises_by_level_output[level_name].append(exercise_key)

            # Sort lists for consistency
            for level in exercises_by_level_output:
                exercises_by_level_output[level].sort()

            levels_config["exercises_by_level"] = exercises_by_level_output
            levels_config["level_order"] = self.level_order # Ensure level_order is also saved

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(levels_config, f, ensure_ascii=False, indent=2)

            # Notifier MainWindow de recharger la configuration des niveaux et de mettre à jour la visibilité
            self.parent_window.reload_level_config_and_update_ui()
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Sauvegarde", f"Une erreur est survenue lors de la sauvegarde : {e}")
            print(f"Error saving levels_config.json: {e}")

    def _save_and_refresh(self):
        """Saves the configuration and refreshes the main window UI."""
        if not self.is_dirty:
            return # Nothing to save

        # Save the level configuration
        self._save_configuration()

        # Also trigger the save of the main application configuration (window size, etc.)
        if hasattr(self.parent_window, 'save_config'):
            self.parent_window.save_config()

        # Reset dirty state and update button style
        self.is_dirty = False
        self._update_save_button_style()

    def update_data(self, new_exercises_by_level_incremental):
        """
        Updates the internal data model and repopulates the table.
        Called by MainWindow after loading a new configuration.
        """
        self._exercise_min_levels = self._determine_initial_min_levels(new_exercises_by_level_incremental)
        self._populate_table() # Repopulate the table with the new data
        
        # After loading new data, the state is no longer dirty
        self.is_dirty = False
        if hasattr(self, 'save_button'): # Check if button exists yet
            self._update_save_button_style()

    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Définir le dossier de sortie des fichiers générés")
        if folder:
            # Enregistrer dans config.json (création si besoin)
            config_path = os.path.join(os.path.dirname(__file__), '../config.json')
            config_path = os.path.abspath(config_path)
            import json
            config = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except Exception:
                    config = {}
            config['selected_output_path'] = folder
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Erreur lors de l'enregistrement du dossier de sortie : {e}")
            # Notifier la fenêtre principale pour mettre à jour la variable ET sauvegarder
            if hasattr(self.parent_window, 'set_selected_output_path'):
                self.parent_window.set_selected_output_path(folder)
            if hasattr(self.parent_window, 'save_config'):
                self.parent_window.save_config()
            # Afficher le chemin sous le bouton
            if hasattr(self, 'output_path_label'):
                self.output_path_label.setText(f"Dossier de sortie actuel : {folder}")
        elif hasattr(self, 'output_path_label'):
            self.output_path_label.setText("Aucun dossier sélectionné.")