from PyQt6.QtWidgets import (QLabel, QCheckBox, QFrame, QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout)
from gui.filter_widgets import create_input_row, create_generic_groupbox

class MesuresColumn(QFrame):
    """
    A QFrame component representing the 'Mesures' column in the main UI.
    It encapsulates all the widgets for measurement-related exercises.
    """
    def __init__(self, parent_window, UI_STYLE_CONFIG):
        super().__init__()
        self.parent_window = parent_window # Reference to MainWindow
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG

        self.all_line_edits = [] # Collect line edits for styling in MainWindow
        self.all_row_widgets_for_map = {} # Collect row widgets for exercise map

        # --- Widgets for this column ---
        self.geo_title_label = None
        self.geo_conv_group = None
        self.geo_ex_count = None # QLineEdit
        self.conv_type_longueur = None
        self.conv_type_masse = None
        self.conv_type_volume = None
        self.conv_type_temps = None
        self.conv_type_monnaie = None
        self.geo_conv_type_checkboxes = []
        self.conv_sens_direct = None
        self.conv_sens_inverse = None
        self.measurement_problems_group = None
        self.measurement_problems_count = None # QLineEdit
        self.measurement_problem_longueur_cb = None
        self.measurement_problem_masse_cb = None
        self.measurement_problem_volume_cb = None
        self.measurement_problem_temps_cb = None
        self.measurement_problem_monnaie_cb = None
        self.measurement_problem_type_checkboxes = []
        self.sort_group = None
        self.sort_count = None # QLineEdit
        self.sort_digits = None # QLineEdit
        self.sort_n_numbers = None # QLineEdit
        self.sort_type_croissant = None
        self.sort_type_decroissant = None
        self.encadrement_group = None
        self.encadrement_count = None # QLineEdit
        self.encadrement_digits = None # QLineEdit
        self.encadrement_unite = None
        self.encadrement_dizaine = None
        self.encadrement_centaine = None
        self.encadrement_millier = None
        self.compare_numbers_group = None
        self.compare_numbers_count = None # QLineEdit
        self.compare_numbers_digits = None # QLineEdit
        self.logical_sequences_group = None
        self.logical_sequences_count = None # QLineEdit
        self.logical_sequences_length = None # QLineEdit
        self.logical_sequences_type_arithmetic_plus_cb = None
        self.logical_sequences_type_arithmetic_minus_cb = None
        self.logical_sequences_type_arithmetic_multiply_cb = None
        self.logical_sequences_type_arithmetic_divide_cb = None

        self._setup_ui()

    def _set_groupbox_style(self, groups, color):
        """Utility function to apply compact style to a list of QGroupBoxes."""
        style_template = self.UI_STYLE_CONFIG["group_boxes"]["base_style_template"]
        for group in groups:
            group.setStyleSheet(style_template.format(border_color=color))

    def _setup_ui(self):
        geo_layout = QVBoxLayout(self)
        self.geo_title_label = QLabel("Mesures")
        geo_title_style = self.UI_STYLE_CONFIG["labels"]["column_title_base"] + f"color: {self.UI_STYLE_CONFIG['labels']['column_title_colors']['geo']};"
        self.geo_title_label.setStyleSheet(geo_title_style)
        geo_layout.addWidget(self.geo_title_label)
        geo_layout.setContentsMargins(5, 5, 5, 5)
        geo_layout.setSpacing(6)

        # Section conversions
        self.geo_conv_group = QGroupBox("Conversions")
        geo_conv_layout = QVBoxLayout()

        row_widget_geo_count, self.geo_ex_count = create_input_row(
            "Nombre d'exercices :", 60)
        self.all_line_edits.append(self.geo_ex_count)
        self.all_row_widgets_for_map["geo_ex_count_row"] = row_widget_geo_count
        geo_conv_layout.addWidget(row_widget_geo_count)

        self.conv_type_longueur = QCheckBox("Longueur")
        self.conv_type_masse = QCheckBox("Masse")
        self.conv_type_volume = QCheckBox("Volume")
        self.conv_type_temps = QCheckBox("Temps")
        self.conv_type_monnaie = QCheckBox("Monnaie")
        self.geo_conv_type_checkboxes = [self.conv_type_longueur, self.conv_type_masse, self.conv_type_volume, self.conv_type_temps, self.conv_type_monnaie]
        for cb in self.geo_conv_type_checkboxes:
            geo_conv_layout.addWidget(cb)

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

        # Section Problèmes de Mesures
        self.measurement_problems_group = QGroupBox("Problèmes de mesures")
        measurement_problems_layout = QVBoxLayout()

        row_measurement_pb_count, self.measurement_problems_count = create_input_row("Nombre de problèmes :", 60)
        self.all_line_edits.append(self.measurement_problems_count)
        self.all_row_widgets_for_map["measurement_problems_count_row"] = row_measurement_pb_count
        measurement_problems_layout.addWidget(row_measurement_pb_count)

        self.measurement_problem_longueur_cb = QCheckBox("Longueur")
        self.measurement_problem_masse_cb = QCheckBox("Masse")
        self.measurement_problem_volume_cb = QCheckBox("Volume")
        self.measurement_problem_temps_cb = QCheckBox("Temps")
        self.measurement_problem_monnaie_cb = QCheckBox("Monnaie")
        self.measurement_problem_type_checkboxes = [
            self.measurement_problem_longueur_cb,
            self.measurement_problem_masse_cb,
            self.measurement_problem_volume_cb,
            self.measurement_problem_temps_cb,
            self.measurement_problem_monnaie_cb,
        ]
        for cb in self.measurement_problem_type_checkboxes:
            measurement_problems_layout.addWidget(cb)

        self.measurement_problems_group.setLayout(measurement_problems_layout)
        geo_layout.addWidget(self.measurement_problems_group)

        # Section : Ranger les nombres
        self.sort_type_croissant = QCheckBox("Croissant")
        self.sort_type_decroissant = QCheckBox("Décroissant")
        self.sort_type_croissant.setChecked(True)

        sort_grid_type_layout = QGridLayout()
        sort_grid_type_layout.setContentsMargins(0, 0, 0, 0)
        sort_grid_type_layout.setVerticalSpacing(5)
        sort_grid_type_layout.setHorizontalSpacing(10)
        sort_grid_type_layout.addWidget(self.sort_type_croissant, 0, 0)
        sort_grid_type_layout.addWidget(self.sort_type_decroissant, 0, 1)
        sort_grid_type_layout.setColumnStretch(2, 1)

        sort_fields = [
            ("Nombre d'exercices :", "sort_count", 60),
            ("Chiffres par nombre :", "sort_digits", 60),
            ("Nombres à ranger :", "sort_n_numbers", 60)
        ]
        self.sort_group, sort_les, sort_rows = create_generic_groupbox(self,"Ranger les nombres", sort_fields, extra_items=[sort_grid_type_layout])
        self.all_line_edits.extend(sort_les)
        self.all_row_widgets_for_map.update(sort_rows)
        geo_layout.addWidget(self.sort_group)

        # Section : Encadrer un nombre
        encadrement_fields = [
            ("Nombre d'exercices :", "encadrement_count", 60),
            ("Chiffres par nombre :", "encadrement_digits", 60)
        ]

        self.encadrement_unite = QCheckBox("Unité")
        self.encadrement_dizaine = QCheckBox("Dizaine")
        self.encadrement_centaine = QCheckBox("Centaine")
        self.encadrement_millier = QCheckBox("Millier")

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
            if col == 0: row += 1
        encadrement_grid_type_layout.setColumnStretch(2, 1)

        self.encadrement_group, encadrement_les, enc_rows = create_generic_groupbox(self, "Encadrer un nombre", encadrement_fields, extra_items=[encadrement_grid_type_layout])
        self.all_line_edits.extend(encadrement_les)
        self.all_row_widgets_for_map.update(enc_rows)
        geo_layout.addWidget(self.encadrement_group)

        # Section : Comparer des nombres
        compare_numbers_fields = [
            ("Nombre d'exercices :", "compare_numbers_count", 60),
            ("Chiffres par nombre :", "compare_numbers_digits", 60)
        ]
        self.compare_numbers_group, compare_numbers_les, cn_rows = create_generic_groupbox(self,
            "Comparer des nombres", compare_numbers_fields
        )
        self.all_line_edits.extend(compare_numbers_les)
        self.all_row_widgets_for_map.update(cn_rows)
        geo_layout.addWidget(self.compare_numbers_group)

        # Section : Suites Logiques
        logical_sequences_fields = [
            ("Nombre d'exercices :", "logical_sequences_count", 60),
            ("Nombre d'éléments (suite) :", "logical_sequences_length", 60)
        ]
        self.logical_sequences_type_arithmetic_plus_cb = QCheckBox("Suite arithmétique (+)")
        self.logical_sequences_type_arithmetic_minus_cb = QCheckBox("Suite arithmétique (-)")
        self.logical_sequences_type_arithmetic_multiply_cb = QCheckBox("Suite arithmétique (x)")
        self.logical_sequences_type_arithmetic_divide_cb = QCheckBox("Suite arithmétique (÷)")

        self.logical_sequences_group, logical_sequences_les, ls_rows = create_generic_groupbox(self,
            "Suites Logiques", logical_sequences_fields,
            extra_items=[QLabel("Types de suites :"), self.logical_sequences_type_arithmetic_plus_cb, self.logical_sequences_type_arithmetic_minus_cb, self.logical_sequences_type_arithmetic_multiply_cb, self.logical_sequences_type_arithmetic_divide_cb])
        self.all_line_edits.extend(logical_sequences_les)
        self.all_row_widgets_for_map.update(ls_rows)
        if hasattr(self, 'logical_sequences_length'):
            self.logical_sequences_length.setText("5")
        geo_layout.addWidget(self.logical_sequences_group)

        # Apply styling
        geo_groups = [self.geo_conv_group, self.measurement_problems_group, self.sort_group, self.encadrement_group, self.compare_numbers_group, self.logical_sequences_group]
        geo_border_color = self.UI_STYLE_CONFIG["group_boxes"]["border_colors"]["geo"]
        self._set_groupbox_style(geo_groups, geo_border_color)
        geo_layout.addStretch()