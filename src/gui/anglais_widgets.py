from PyQt6.QtWidgets import (QLabel, QCheckBox, QFrame, QGroupBox, QVBoxLayout, QGridLayout)
from gui.filter_widgets import create_generic_groupbox

class AnglaisColumn(QFrame):
    """
    A QFrame component representing the 'Anglais' column in the main UI.
    It encapsulates all the widgets for English-related exercises.
    """
    def __init__(self, parent_window, UI_STYLE_CONFIG, english_relier_themes):
        super().__init__()
        self.parent_window = parent_window # Reference to MainWindow
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG
        self.english_relier_themes = english_relier_themes

        self.all_line_edits = [] # Collect line edits for styling in MainWindow
        self.all_row_widgets_for_map = {} # Collect row widgets for exercise map

        # --- Widgets for this column ---
        self.english_title_label = None
        self.english_complete_group = None
        self.english_complete_count = None # QLineEdit
        self.english_type_simple = None
        self.english_type_complexe = None
        self.english_relier_group = None
        self.english_relier_count = None # QLineEdit
        self.relier_count = None # QLineEdit
        self.english_relier_theme_checkboxes = {} # Dict of theme checkboxes

        self._setup_ui()

    def _set_groupbox_style(self, groups, color):
        """Utility function to apply compact style to a list of QGroupBoxes."""
        style_template = self.UI_STYLE_CONFIG["group_boxes"]["base_style_template"]
        for group in groups:
            group.setStyleSheet(style_template.format(border_color=color))

    def _setup_ui(self):
        english_layout = QVBoxLayout(self)
        self.english_title_label = QLabel("Anglais")
        english_title_style = self.UI_STYLE_CONFIG["labels"]["column_title_base"] + \
            f"color: {self.UI_STYLE_CONFIG['labels']['column_title_colors']['english']};"
        self.english_title_label.setStyleSheet(english_title_style)
        english_layout.addWidget(self.english_title_label)
        english_layout.setContentsMargins(5, 5, 5, 5)
        english_layout.setSpacing(6)

        # Section 1 : Phrases à compléter
        english_complete_fields = [("Nombre d'exercices :", "english_complete_count", 60)]
        self.english_type_simple = QCheckBox("Phrase à compléter simple")
        self.english_type_complexe = QCheckBox("Phrase à compléter complexe")
        self.english_complete_group, english_complete_les, eng_comp_rows = create_generic_groupbox(self, "Phrases à compléter", english_complete_fields, extra_items=[self.english_type_simple, self.english_type_complexe])
        self.all_line_edits.extend(english_complete_les)
        self.all_row_widgets_for_map.update(eng_comp_rows)
        english_layout.addWidget(self.english_complete_group)

        # Section 2 : Jeux à relier
        english_relier_fields = [
            ("Nombre de jeux à relier :", "english_relier_count", 60),
            ("Nombre de mots par jeu :", "relier_count", 60)
        ]
        self.english_relier_group, english_relier_les, eng_rel_rows = create_generic_groupbox(self, "Jeux à relier", english_relier_fields)
        self.all_line_edits.extend(english_relier_les)
        self.all_row_widgets_for_map.update(eng_rel_rows)
        english_layout.addWidget(self.english_relier_group)

        # Ajout des checkboxes de thèmes directement dans le layout de english_relier_group
        english_relier_group_layout = self.english_relier_group.layout()
        if self.english_relier_themes:
            for theme_name in self.english_relier_themes.keys():
                cb = QCheckBox(theme_name.replace("_", " ").capitalize())
                self.english_relier_theme_checkboxes[theme_name] = cb
        themes_grid_layout = QGridLayout()
        themes_grid_layout.setContentsMargins(0, 10, 0, 0)
        themes_grid_layout.setVerticalSpacing(5)
        themes_grid_layout.setHorizontalSpacing(10)
        if self.english_relier_theme_checkboxes:
            checkbox_values = list(self.english_relier_theme_checkboxes.values())
            row, col = 0, 0
            for cb_widget in checkbox_values:
                themes_grid_layout.addWidget(cb_widget, row, col)
                col = (col + 1) % 2
                if col == 0: row += 1
            themes_grid_layout.setColumnStretch(2, 1)
        elif not self.english_relier_themes:
            no_themes_label = QLabel("Aucun thème défini dans mots_a_relier.json")
            themes_grid_layout.addWidget(no_themes_label, 0, 0, 1, 2)
        english_relier_group_layout.addLayout(themes_grid_layout)

        english_groups = [self.english_complete_group, self.english_relier_group]
        english_border_color = self.UI_STYLE_CONFIG["group_boxes"]["border_colors"]["english"]
        self._set_groupbox_style(english_groups, english_border_color)
        english_layout.addStretch()