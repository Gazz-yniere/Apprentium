from PyQt6.QtWidgets import (QLabel, QCheckBox, QFrame, QGroupBox, QVBoxLayout, QGridLayout)
from PyQt6.QtCore import Qt # Not strictly needed for these functions, but often useful for UI
from PyQt6.QtGui import QPalette, QColor # Not strictly needed here, but often useful for UI

from gui.filter_widgets import create_input_row, create_generic_groupbox
from gui.template import UI_STYLE_CONFIG
from grammar_generator import TRANSFORMATIONS # Import TRANSFORMATIONS here

class GrammarColumn(QFrame):
    """
    A QFrame component representing the 'Grammaire' column in the main UI.
    It encapsulates all the widgets for grammar-related exercises.
    """
    def __init__(self, parent_window, UI_STYLE_CONFIG):
        super().__init__()
        self.parent_window = parent_window # Reference to MainWindow
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG

        self.all_line_edits = [] # Collect line edits for styling in MainWindow
        self.all_row_widgets_for_map = {} # Collect row widgets for exercise map

        # --- Widgets for this column ---
        # These will be populated by _setup_ui and accessed by MainWindow
        self.grammar_title_label = None
        self.grammar_number_group = None
        self.grammar_sentence_count = None # QLineEdit
        self.grammar_type_group = None
        self.intransitive_checkbox = None
        self.transitive_direct_checkbox = None
        self.transitive_indirect_checkbox = None
        self.ditransitive_checkbox = None
        self.grammar_type_checkboxes = [] # List of the above checkboxes
        self.grammar_transfo_group = None
        self.transfo_checkboxes = [] # List of transformation checkboxes

        self._setup_ui()

    def _set_groupbox_style(self, groups, color):
        """Utility function to apply compact style to a list of QGroupBoxes."""
        style_template = self.UI_STYLE_CONFIG["group_boxes"]["base_style_template"]
        for group in groups:
            group.setStyleSheet(style_template.format(border_color=color))

    def _setup_ui(self):
        grammar_layout = QVBoxLayout(self)
        self.grammar_title_label = QLabel("Grammaire")
        grammar_title_style = self.UI_STYLE_CONFIG["labels"]["column_title_base"] + f"color: {self.UI_STYLE_CONFIG['labels']['column_title_colors']['grammar']};"
        self.grammar_title_label.setStyleSheet(grammar_title_style)
        grammar_layout.addWidget(self.grammar_title_label)
        grammar_layout.setContentsMargins(5, 5, 5, 5)
        grammar_layout.setSpacing(6)

        grammar_param_fields = [("Nombre de phrases :", "grammar_sentence_count", 60)]
        self.grammar_number_group, grammar_param_les, grammar_param_rows = create_generic_groupbox(self,"Paramètres de grammaire", grammar_param_fields)
        self.all_line_edits.extend(grammar_param_les)
        self.all_row_widgets_for_map.update(grammar_param_rows)
        grammar_layout.addWidget(self.grammar_number_group)

        self.grammar_type_group = QGroupBox("Type de phrase")
        grammar_type_layout = QVBoxLayout()
        self.intransitive_checkbox = QCheckBox("Sans complément d'objet")
        self.transitive_direct_checkbox = QCheckBox("Avec complément d'objet direct")
        self.transitive_indirect_checkbox = QCheckBox("Avec complément d'objet indirect")
        self.ditransitive_checkbox = QCheckBox("Avec deux compléments d'objet")
        self.grammar_type_checkboxes = [self.intransitive_checkbox, self.transitive_direct_checkbox, self.transitive_indirect_checkbox, self.ditransitive_checkbox]
        for cb in self.grammar_type_checkboxes:
            grammar_type_layout.addWidget(cb)
        self.grammar_type_group.setLayout(grammar_type_layout)
        grammar_layout.addWidget(self.grammar_type_group)

        self.grammar_transfo_group = QGroupBox("Transformations")
        grammar_transfo_layout = QVBoxLayout()
        self.transfo_checkboxes = []
        for t in TRANSFORMATIONS:
            cb = QCheckBox(t)
            grammar_transfo_layout.addWidget(cb)
            self.transfo_checkboxes.append(cb)
        self.grammar_transfo_group.setLayout(grammar_transfo_layout)
        grammar_layout.addWidget(self.grammar_transfo_group)

        # Apply styling
        grammar_groups = [self.grammar_number_group,self.grammar_type_group, self.grammar_transfo_group]
        grammar_border_color = self.UI_STYLE_CONFIG["group_boxes"]["border_colors"]["grammar"]
        self._set_groupbox_style(grammar_groups, grammar_border_color)
        grammar_layout.addStretch()