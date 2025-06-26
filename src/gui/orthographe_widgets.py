from PyQt6.QtWidgets import (QLabel, QCheckBox, QFrame, QGroupBox, QVBoxLayout)
from gui.filter_widgets import create_generic_groupbox

class OrthographeColumn(QFrame):
    """
    A QFrame component representing the 'Orthographe' column in the main UI.
    It encapsulates all the widgets for orthography-related exercises.
    """
    def __init__(self, parent_window, UI_STYLE_CONFIG):
        super().__init__()
        self.parent_window = parent_window # Reference to MainWindow
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG

        self.all_line_edits = [] # Collect line edits for styling in MainWindow
        self.all_row_widgets_for_map = {} # Collect row widgets for exercise map

        # --- Widgets for this column ---
        self.orthographe_title_label = None
        self.orthographe_number_group = None
        self.orthographe_ex_count = None # QLineEdit
        self.orthographe_homophone_group = None
        self.homophone_a_checkbox = None
        self.homophone_et_checkbox = None
        self.homophone_on_checkbox = None
        self.homophone_son_checkbox = None
        self.homophone_ce_checkbox = None
        self.homophone_ou_checkbox = None
        self.homophone_ces_checkbox = None
        self.homophone_mes_checkbox = None
        self.orthographe_homophone_checkboxes = [] # List of the above checkboxes

        self._setup_ui()

    def _set_groupbox_style(self, groups, color):
        """Utility function to apply compact style to a list of QGroupBoxes."""
        style_template = self.UI_STYLE_CONFIG["group_boxes"]["base_style_template"]
        for group in groups:
            group.setStyleSheet(style_template.format(border_color=color))

    def _setup_ui(self):
        orthographe_layout = QVBoxLayout(self)
        self.orthographe_title_label = QLabel("Orthographe")
        ortho_title_style = self.UI_STYLE_CONFIG["labels"]["column_title_base"] + \
            f"color: {self.UI_STYLE_CONFIG['labels']['column_title_colors']['ortho']};"
        self.orthographe_title_label.setStyleSheet(ortho_title_style)
        orthographe_layout.addWidget(self.orthographe_title_label)
        orthographe_layout.setContentsMargins(5, 5, 5, 5)
        orthographe_layout.setSpacing(6)

        ortho_param_fields = [("Nombre d'exercices :", "orthographe_ex_count", 60)]
        self.orthographe_number_group, ortho_param_les, ortho_param_rows = create_generic_groupbox(self, "Paramètres d'orthographe", ortho_param_fields)
        self.all_line_edits.extend(ortho_param_les)
        self.all_row_widgets_for_map.update(ortho_param_rows)
        orthographe_layout.addWidget(self.orthographe_number_group)

        self.orthographe_homophone_group = QGroupBox("Homophones")
        orthographe_homophone_layout = QVBoxLayout()
        self.homophone_a_checkbox = QCheckBox("a / à")
        self.homophone_et_checkbox = QCheckBox("et / est")
        self.homophone_on_checkbox = QCheckBox("on / ont")
        self.homophone_son_checkbox = QCheckBox("son / sont")
        self.homophone_ce_checkbox = QCheckBox("ce / se")
        self.homophone_ou_checkbox = QCheckBox("ou / où")
        self.homophone_ces_checkbox = QCheckBox("ces / ses")
        self.homophone_mes_checkbox = QCheckBox("mes / mais / met / mets")
        self.orthographe_homophone_checkboxes = [self.homophone_a_checkbox, self.homophone_et_checkbox, self.homophone_on_checkbox, self.homophone_son_checkbox, self.homophone_ce_checkbox, self.homophone_mes_checkbox, self.homophone_ou_checkbox, self.homophone_ces_checkbox]
        for cb in self.orthographe_homophone_checkboxes:
            orthographe_homophone_layout.addWidget(cb)
        self.orthographe_homophone_group.setLayout(orthographe_homophone_layout)
        orthographe_layout.addWidget(self.orthographe_homophone_group)

        ortho_groups = [self.orthographe_number_group, self.orthographe_homophone_group]
        ortho_border_color = self.UI_STYLE_CONFIG["group_boxes"]["border_colors"]["ortho"]
        self._set_groupbox_style(ortho_groups, ortho_border_color)
        orthographe_layout.addStretch()