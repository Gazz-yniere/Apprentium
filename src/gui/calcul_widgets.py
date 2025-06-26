from PyQt6.QtWidgets import (QLabel, QCheckBox, QFrame, QGroupBox, QVBoxLayout, QGridLayout)
from .filter_widgets import create_input_row, create_generic_groupbox

class CalculsColumn(QFrame):
    """
    A QFrame component representing the 'Calculs' column in the main UI.
    It encapsulates all the widgets for calculation-related exercises.
    """
    def __init__(self, parent_window, UI_STYLE_CONFIG, math_problem_types_data):
        super().__init__()
        self.parent_window = parent_window # Reference to MainWindow
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG
        self.math_problem_types_data = math_problem_types_data

        self.all_line_edits = [] # Collect line edits for styling in MainWindow
        self.all_row_widgets_for_map = {} # Collect row widgets for exercise map

        # --- Widgets for this column ---
        # These will be populated by _setup_ui and accessed by MainWindow
        self.calc_title_label = None
        self.enumerate_group = None
        self.addition_group = None
        self.subtraction_group = None
        self.multiplication_group = None
        self.division_group = None
        self.math_problems_group = None
        self.math_problem_type_checkboxes = {}
        # ... other widgets will be set as attributes by create_generic_groupbox

        self._setup_ui()

    def _set_groupbox_style(self, groups, color):
        # Utiliser le template depuis UI_STYLE_CONFIG
        style_template = self.UI_STYLE_CONFIG["group_boxes"]["base_style_template"]
        for group in groups:
            group.setStyleSheet(style_template.format(border_color=color))

    def _setup_ui(self):
        calc_layout = QVBoxLayout(self)
        self.calc_title_label = QLabel("Calculs")
        calc_title_style = self.UI_STYLE_CONFIG["labels"]["column_title_base"] + f"color: {self.UI_STYLE_CONFIG['labels']['column_title_colors']['calc']};"
        self.calc_title_label.setStyleSheet(calc_title_style)
        calc_layout.addWidget(self.calc_title_label)
        calc_layout.setContentsMargins(5, 5, 5, 5)
        calc_layout.setSpacing(6)

        # Exercice : Enumérer un nombre
        enumerate_fields = [
            ("Nombre d'exercices :", "enumerate_count", 60),
            ("Chiffres par nombre :", "enumerate_digits", 60)
        ]
        self.enumerate_group, enumerate_les, enum_rows = create_generic_groupbox(self,
            "Enumérer un nombre", enumerate_fields)
        self.all_line_edits.extend(enumerate_les)
        self.all_row_widgets_for_map.update(enum_rows)

        # Addition
        addition_fields = [
            ("Nombre de calculs :", "addition_count", 60),
            ("Chiffres par opérande :", "addition_digits", 60),
            ("Nb décimales :", "addition_decimals", 60),
            ("Nombre d'opérandes :", "addition_num_operands", 60)
        ]
        self.addition_group, addition_les, add_rows = create_generic_groupbox(self,"Addition", addition_fields)
        self.all_line_edits.extend(addition_les)
        self.all_row_widgets_for_map.update(add_rows)
        if hasattr(self, 'addition_num_operands'):
            self.addition_num_operands.setText("2")

        # Soustraction
        self.subtraction_negative_checkbox = QCheckBox("Soustraction négative possible")
        subtraction_fields = [
            ("Nombre de calculs :", "subtraction_count", 60),
            ("Chiffres par opérande :", "subtraction_digits", 60),
            ("Nb décimales :", "subtraction_decimals", 60),
            ("Nombre d'opérandes :", "subtraction_num_operands", 60)
        ]
        self.subtraction_group, subtraction_les, sub_rows = create_generic_groupbox(self, "Soustraction", subtraction_fields, extra_items=[self.subtraction_negative_checkbox]
        )
        self.all_line_edits.extend(subtraction_les)
        self.all_row_widgets_for_map.update(sub_rows)
        if hasattr(self, 'subtraction_num_operands'):
            self.subtraction_num_operands.setText("2")

        # Multiplication
        multiplication_fields = [
            ("Nombre de calculs :", "multiplication_count", 60),
            ("Chiffres par opérande :", "multiplication_digits", 60),
            ("Nb décimales :", "multiplication_decimals", 60),
            ("Nombre d'opérandes :", "multiplication_num_operands", 60)
        ]
        self.multiplication_group, multiplication_les, mult_rows = create_generic_groupbox(self, "Multiplication", multiplication_fields)
        self.all_line_edits.extend(multiplication_les)
        self.all_row_widgets_for_map.update(mult_rows)
        if hasattr(self, 'multiplication_num_operands'):
            self.multiplication_num_operands.setText("2")

        # Division
        self.division_reste_checkbox = QCheckBox("Division avec reste")
        division_fields = [
            ("Nombre de calculs :", "division_count", 60),
            ("Chiffres par opérande :", "division_digits", 60),
            ("Nb décimales :", "division_decimals", 60)
        ]
        self.division_group, division_les, div_rows = create_generic_groupbox(self, "Division", division_fields, extra_items=[self.division_reste_checkbox]
        )
        self.all_line_edits.extend(division_les)
        self.all_row_widgets_for_map.update(div_rows)

        # Petits Problèmes Mathématiques
        self.math_problems_group = QGroupBox("Petits Problèmes")
        math_problems_layout = QVBoxLayout()
        
        row_math_pb_count, self.math_problems_count = create_input_row("Nombre de problèmes :", 60)
        self.all_line_edits.append(self.math_problems_count)
        self.all_row_widgets_for_map["math_problems_count_row"] = row_math_pb_count
        math_problems_layout.addWidget(row_math_pb_count)

        if self.math_problem_types_data:
            types_grid_layout = QGridLayout()
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
            types_grid_layout.setColumnStretch(2, 1)
            math_problems_layout.addLayout(types_grid_layout)

        self.math_problems_group.setLayout(math_problems_layout)

        # Harmonisation des couleurs
        calc_groups = [self.enumerate_group, self.addition_group, self.subtraction_group, self.multiplication_group, self.division_group, self.math_problems_group]
        calc_border_color = self.UI_STYLE_CONFIG["group_boxes"]["border_colors"]["calc"]
        self._set_groupbox_style(calc_groups, calc_border_color)

        calc_layout.addWidget(self.enumerate_group)
        calc_layout.addWidget(self.addition_group)
        calc_layout.addWidget(self.subtraction_group)
        calc_layout.addWidget(self.multiplication_group)
        calc_layout.addWidget(self.division_group)
        calc_layout.addWidget(self.math_problems_group)
        calc_layout.addStretch()