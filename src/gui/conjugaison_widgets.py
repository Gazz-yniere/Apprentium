from PyQt6.QtWidgets import (QLabel, QCheckBox, QFrame, QGroupBox, QVBoxLayout)
from gui.filter_widgets import create_input_row, create_generic_groupbox, set_groupbox_style
from conjugation_generator import TENSES

class ConjugaisonColumn(QFrame):
    """
    A QFrame component representing the 'Conjugaison' column in the main UI.
    It encapsulates all the widgets for conjugation-related exercises.
    """
    def __init__(self, parent_window, UI_STYLE_CONFIG):
        super().__init__()
        self.parent_window = parent_window # Reference to MainWindow
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG

        self.all_line_edits = [] # Collect line edits for styling in MainWindow
        self.all_row_widgets_for_map = {} # Collect row widgets for exercise map

        # --- Widgets for this column ---
        self.conj_title_label = None
        self.conj_group_group = None
        self.verbs_per_day_entry = None # QLineEdit
        self.group_1_checkbox = None
        self.group_2_checkbox = None
        self.group_3_checkbox = None
        self.usual_verbs_checkbox = None
        self.conj_group_group_checkboxes = []
        self.conj_tense_group = None
        self.tense_checkboxes = []
        self.conj_complete_sentence_group = None
        self.conj_complete_sentence_count = None # QLineEdit
        self.conj_complete_pronoun_group = None
        self.conj_complete_pronoun_count = None # QLineEdit

        self._setup_ui()

    def _setup_ui(self):
        conj_layout = QVBoxLayout(self)
        self.conj_title_label = QLabel("Conjugaison")
        conj_title_style = self.UI_STYLE_CONFIG["labels"]["column_title_base"] + f"color: {self.UI_STYLE_CONFIG['labels']['column_title_colors']['conj']};"
        self.conj_title_label.setStyleSheet(conj_title_style)
        conj_layout.addWidget(self.conj_title_label)
        conj_layout.setContentsMargins(5, 5, 5, 5)
        conj_layout.setSpacing(6)

        # Groupes de verbes
        self.conj_group_group = QGroupBox("Groupes de verbes")
        group_layout = QVBoxLayout()

        row_widget_verbs_per_day, self.verbs_per_day_entry = create_input_row("Nombre de verbes :", 60)
        self.all_line_edits.append(self.verbs_per_day_entry)
        self.all_row_widgets_for_map["verbs_per_day_entry_row"] = row_widget_verbs_per_day
        group_layout.addWidget(row_widget_verbs_per_day)

        self.group_1_checkbox = QCheckBox("1er groupe")
        self.group_2_checkbox = QCheckBox("2ème groupe")
        self.group_3_checkbox = QCheckBox("3ème groupe")
        self.usual_verbs_checkbox = QCheckBox("Verbes usuels (à connaître par \u2665)")
        self.conj_group_group_checkboxes = [self.group_1_checkbox, self.group_2_checkbox, self.group_3_checkbox, self.usual_verbs_checkbox]
        for cb in self.conj_group_group_checkboxes:
            group_layout.addWidget(cb)
        self.conj_group_group.setLayout(group_layout)
        conj_layout.addWidget(self.conj_group_group)

        # Temps (dynamique depuis conjugation_generator.TENSES)
        self.conj_tense_group = QGroupBox("Temps")
        tense_layout = QVBoxLayout()
        self.tense_checkboxes = []
        for tense in TENSES:
            cb = QCheckBox(tense.capitalize())
            tense_layout.addWidget(cb)
            self.tense_checkboxes.append(cb)
        self.conj_tense_group.setLayout(tense_layout)
        conj_layout.addWidget(self.conj_tense_group)

        # Section: Compléter les phrases
        conj_complete_sentence_fields = [("Nombre de phrases :", "conj_complete_sentence_count", 60)]
        self.conj_complete_sentence_group, conj_cs_les, conj_cs_rows = create_generic_groupbox(self, "Phrases à complèter", conj_complete_sentence_fields)
        self.all_line_edits.extend(conj_cs_les)
        self.all_row_widgets_for_map.update(conj_cs_rows)
        conj_layout.addWidget(self.conj_complete_sentence_group)

        # Section: Compléter les pronoms
        conj_complete_pronoun_fields = [("Nombre de phrases :", "conj_complete_pronoun_count", 60)]
        self.conj_complete_pronoun_group, conj_cp_les, conj_cp_rows = create_generic_groupbox(self, "Pronoms à complèter", conj_complete_pronoun_fields)
        self.all_line_edits.extend(conj_cp_les)
        self.all_row_widgets_for_map.update(conj_cp_rows)
        conj_layout.addWidget(self.conj_complete_pronoun_group)

        conj_groups = [self.conj_group_group, self.conj_tense_group, self.conj_complete_sentence_group, self.conj_complete_pronoun_group]
        conj_border_color = self.UI_STYLE_CONFIG["group_boxes"]["border_colors"]["conj"]
        set_groupbox_style(conj_groups, conj_border_color)
        conj_layout.addStretch()