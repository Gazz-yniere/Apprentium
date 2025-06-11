from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QFrame, QSizePolicy, QGroupBox, QSplitter)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QPalette, QColor
from pdf_generator import generate_workbook_pdf
from conjugation_generator import get_random_verb, conjugate_verb
import random
import os
import json
import sys

class InvalidFieldError(Exception):
    def __init__(self, field_name, value):
        super().__init__(f"Champ '{field_name}' invalide : '{value}' n'est pas un nombre valide.")
        self.field_name = field_name
        self.value = value

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Générateur de fiches de travail")
        self.setWindowIcon(QIcon("logo-inv.png"))
        # Fenêtre redimensionnable

        # Mode dark
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(20, 20, 20))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        QApplication.instance().setPalette(dark_palette)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Partie supérieure : nombre de jours
        top_layout = QHBoxLayout()
        self.days_label = QLabel("Nombre de jours :")
        self.days_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.days_entry = QLineEdit()
        self.days_entry.setMaximumWidth(60)
        top_layout.addWidget(self.days_label)
        top_layout.addWidget(self.days_entry)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # Ajout d'un champ en-tête en haut du menu
        self.header_label = QLabel("En-tête (optionnel) :")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.header_entry = QLineEdit()
        self.header_entry.setMaximumWidth(400)
        self.header_entry.setStyleSheet("color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;")
        top_layout.insertWidget(0, self.header_label)
        top_layout.insertWidget(1, self.header_entry)
        # Ajout des options Nom/Note sous l'en-tête
        self.show_name_checkbox = QCheckBox("Afficher un champ Nom à gauche")
        self.show_note_checkbox = QCheckBox("Afficher un champ Note à droite")
        header_options_layout = QHBoxLayout()
        header_options_layout.addWidget(self.show_name_checkbox)
        header_options_layout.addWidget(self.show_note_checkbox)
        main_layout.addLayout(header_options_layout)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(sep)

        # --- Colonne Calculs ---
        calc_layout = QVBoxLayout()
        calc_title = QLabel("Calculs")
        calc_title.setStyleSheet("font-weight: bold; font-size: 20px; color: #4FC3F7; margin-bottom: 8px; margin-top: 0px;")
        calc_layout.addWidget(calc_title)
        calc_layout.setContentsMargins(5, 5, 5, 5)
        calc_layout.setSpacing(6)
        # Addition
        addition_group = QGroupBox("Addition")
        addition_layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel("Nombre de calculs :"))
        self.addition_count = QLineEdit(); self.addition_count.setMaximumWidth(60)
        row.addWidget(self.addition_count)
        addition_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Chiffres par nombre :"))
        self.addition_digits = QLineEdit(); self.addition_digits.setMaximumWidth(60)
        row.addWidget(self.addition_digits)
        addition_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Nb décimales :"))
        self.addition_decimals = QLineEdit(); self.addition_decimals.setMaximumWidth(60)
        row.addWidget(self.addition_decimals)
        addition_layout.addLayout(row)
        addition_group.setLayout(addition_layout)
        # Soustraction
        subtraction_group = QGroupBox("Soustraction")
        subtraction_layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel("Nombre de calculs :"))
        self.subtraction_count = QLineEdit(); self.subtraction_count.setMaximumWidth(60)
        row.addWidget(self.subtraction_count)
        subtraction_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Chiffres par nombre :"))
        self.subtraction_digits = QLineEdit(); self.subtraction_digits.setMaximumWidth(60)
        row.addWidget(self.subtraction_digits)
        subtraction_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Nb décimales :"))
        self.subtraction_decimals = QLineEdit(); self.subtraction_decimals.setMaximumWidth(60)
        row.addWidget(self.subtraction_decimals)
        subtraction_layout.addLayout(row)
        self.subtraction_negative_checkbox = QCheckBox("Soustraction négative possible")
        subtraction_layout.addWidget(self.subtraction_negative_checkbox)
        subtraction_group.setLayout(subtraction_layout)
        # Multiplication
        multiplication_group = QGroupBox("Multiplication")
        multiplication_layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel("Nombre de calculs :"))
        self.multiplication_count = QLineEdit(); self.multiplication_count.setMaximumWidth(60)
        row.addWidget(self.multiplication_count)
        multiplication_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Chiffres par nombre :"))
        self.multiplication_digits = QLineEdit(); self.multiplication_digits.setMaximumWidth(60)
        row.addWidget(self.multiplication_digits)
        multiplication_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Nb décimales :"))
        self.multiplication_decimals = QLineEdit(); self.multiplication_decimals.setMaximumWidth(60)
        row.addWidget(self.multiplication_decimals)
        multiplication_layout.addLayout(row)
        multiplication_group.setLayout(multiplication_layout)
        # Division
        division_group = QGroupBox("Division")
        division_layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel("Nombre de calculs :"))
        self.division_count = QLineEdit(); self.division_count.setMaximumWidth(60)
        row.addWidget(self.division_count)
        division_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Chiffres par nombre :"))
        self.division_digits = QLineEdit(); self.division_digits.setMaximumWidth(60)
        row.addWidget(self.division_digits)
        division_layout.addLayout(row)
        self.division_reste_checkbox = QCheckBox("Division avec reste")
        division_layout.addWidget(self.division_reste_checkbox)
        row = QHBoxLayout()
        row.addWidget(QLabel("Nb décimales :"))
        self.division_decimals = QLineEdit(); self.division_decimals.setMaximumWidth(60)
        row.addWidget(self.division_decimals)
        division_layout.addLayout(row)
        division_group.setLayout(division_layout)
        for group in [addition_group, subtraction_group, multiplication_group, division_group]:
            group.setStyleSheet("QGroupBox { margin-top: 8px; margin-bottom: 8px; padding: 24px 12px 24px 12px; border: 2px solid #6EC6FF; border-radius: 8px; } QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; top: 0px; padding: 0 12px; color: #ffffff; font-weight: bold; font-size: 15px; background: #232323; }")
        calc_layout.addWidget(addition_group)
        calc_layout.addWidget(subtraction_group)
        calc_layout.addWidget(multiplication_group)
        calc_layout.addWidget(division_group)
        calc_layout.addStretch()

        # --- Colonne Conjugaison ---
        conj_layout = QVBoxLayout()
        conj_title = QLabel("Conjugaison")
        conj_title.setStyleSheet("font-weight: bold; font-size: 20px; color: #81C784; margin-bottom: 8px; margin-top: 0px;")
        conj_layout.addWidget(conj_title)
        conj_layout.setContentsMargins(5, 5, 5, 5)
        conj_layout.setSpacing(6)
        # Paramètres de conjugaison (d'abord)
        number_group = QGroupBox("Paramètres de conjugaison")
        number_layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel("Nombre de verbes par jour :"))
        self.verbs_per_day_entry = QLineEdit()
        self.verbs_per_day_entry.setMaximumWidth(60)
        row.addWidget(self.verbs_per_day_entry)
        number_layout.addLayout(row)
        number_group.setLayout(number_layout)
        conj_layout.addWidget(number_group)
        # Groupes de verbes
        group_group = QGroupBox("Groupes de verbes")
        group_layout = QVBoxLayout()
        self.group_1_checkbox = QCheckBox("1er groupe")
        self.group_2_checkbox = QCheckBox("2ème groupe")
        self.group_3_checkbox = QCheckBox("3ème groupe")
        group_layout.addWidget(self.group_1_checkbox)
        group_layout.addWidget(self.group_2_checkbox)
        group_layout.addWidget(self.group_3_checkbox)
        group_group.setLayout(group_layout)
        conj_layout.addWidget(group_group)
        # Temps
        tense_group = QGroupBox("Temps")
        tense_layout = QVBoxLayout()
        self.present_checkbox = QCheckBox("Présent")
        self.imparfait_checkbox = QCheckBox("Imparfait")
        self.passe_simple_checkbox = QCheckBox("Passé simple")
        self.futur_checkbox = QCheckBox("Futur simple")
        self.passe_compose_checkbox = QCheckBox("Passé composé")
        self.plus_que_parfait_checkbox = QCheckBox("Plus-que-parfait")
        self.passe_anterieur_checkbox = QCheckBox("Passé antérieur")
        self.futur_anterieur_checkbox = QCheckBox("Futur antérieur")
        self.subjonctif_present_checkbox = QCheckBox("Subjonctif présent")
        self.subjonctif_imparfait_checkbox = QCheckBox("Subjonctif imparfait")
        self.subjonctif_passe_checkbox = QCheckBox("Subjonctif passé")
        self.subjonctif_plus_que_parfait_checkbox = QCheckBox("Subjonctif plus-que-parfait")
        self.conditionnel_present_checkbox = QCheckBox("Conditionnel présent")
        self.conditionnel_passe_checkbox = QCheckBox("Conditionnel passé")
        self.imperatif_present_checkbox = QCheckBox("Impératif présent")
        self.imperatif_passe_checkbox = QCheckBox("Impératif passé")
        tense_checkboxes = [
            self.present_checkbox, self.imparfait_checkbox, self.passe_simple_checkbox, self.futur_checkbox,
            self.passe_compose_checkbox, self.plus_que_parfait_checkbox, self.passe_anterieur_checkbox, self.futur_anterieur_checkbox,
            self.subjonctif_present_checkbox, self.subjonctif_imparfait_checkbox, self.subjonctif_passe_checkbox, self.subjonctif_plus_que_parfait_checkbox,
            self.conditionnel_present_checkbox, self.conditionnel_passe_checkbox, self.imperatif_present_checkbox, self.imperatif_passe_checkbox
        ]
        for cb in tense_checkboxes:
            tense_layout.addWidget(cb)
        tense_group.setLayout(tense_layout)
        conj_layout.addWidget(tense_group)
        for group in [number_group, group_group, tense_group]:
            group.setStyleSheet("QGroupBox { margin-top: 8px; margin-bottom: 8px; padding: 24px 12px 24px 12px; border: 2px solid #6EC6FF; border-radius: 8px; } QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; top: 0px; padding: 0 12px; color: #ffffff; font-weight: bold; font-size: 15px; background: #232323; }")
        conj_layout.addStretch()

        # --- Colonne Grammaire ---
        grammar_layout = QVBoxLayout()
        grammar_title = QLabel("Grammaire")
        grammar_title.setStyleSheet("font-weight: bold; font-size: 20px; color: #FFD54F; margin-bottom: 8px; margin-top: 0px;")
        grammar_layout.addWidget(grammar_title)
        grammar_layout.setContentsMargins(5, 5, 5, 5)
        grammar_layout.setSpacing(6)
        grammar_number_group = QGroupBox("Paramètres de grammaire")
        grammar_number_layout = QVBoxLayout()
        row = QHBoxLayout()
        self.grammar_sentence_count_label = QLabel("Nombre de phrases :")
        self.grammar_sentence_count = QLineEdit()
        self.grammar_sentence_count.setMaximumWidth(60)
        row.addWidget(self.grammar_sentence_count_label)
        row.addWidget(self.grammar_sentence_count)
        grammar_number_layout.addLayout(row)
        grammar_number_group.setLayout(grammar_number_layout)
        grammar_layout.addWidget(grammar_number_group)
        grammar_type_group = QGroupBox("Type de phrase")
        grammar_type_layout = QVBoxLayout()
        self.intransitive_checkbox = QCheckBox("Intransitive")
        self.transitive_direct_checkbox = QCheckBox("Transitive directe")
        self.transitive_indirect_checkbox = QCheckBox("Transitive indirecte")
        self.ditransitive_checkbox = QCheckBox("Ditransitive")
        grammar_type_layout.addWidget(self.intransitive_checkbox)
        grammar_type_layout.addWidget(self.transitive_direct_checkbox)
        grammar_type_layout.addWidget(self.transitive_indirect_checkbox)
        grammar_type_layout.addWidget(self.ditransitive_checkbox)
        grammar_type_group.setLayout(grammar_type_layout)
        grammar_layout.addWidget(grammar_type_group)
        from grammar_generator import TRANSFORMATIONS
        grammar_transfo_group = QGroupBox("Transformations")
        grammar_transfo_layout = QVBoxLayout()
        self.transfo_checkboxes = []
        for t in TRANSFORMATIONS:
            cb = QCheckBox(t)
            grammar_transfo_layout.addWidget(cb)
            self.transfo_checkboxes.append(cb)
        grammar_transfo_group.setLayout(grammar_transfo_layout)
        grammar_layout.addWidget(grammar_transfo_group)
        for group in [grammar_number_group, grammar_type_group, grammar_transfo_group]:
            group.setStyleSheet("QGroupBox { margin-top: 8px; margin-bottom: 8px; padding: 24px 12px 24px 12px; border: 2px solid #6EC6FF; border-radius: 8px; } QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; top: 0px; padding: 0 12px; color: #ffffff; font-weight: bold; font-size: 15px; background: #232323; }")
        grammar_layout.addStretch()

        # --- Splitter pour 3 colonnes égales ---
        calc_widget = QWidget(); calc_widget.setLayout(calc_layout)
        conj_widget = QWidget(); conj_widget.setLayout(conj_layout)
        grammar_widget = QWidget(); grammar_widget.setLayout(grammar_layout)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(calc_widget)
        splitter.addWidget(conj_widget)
        splitter.addWidget(grammar_widget)
        splitter.setSizes([100, 100, 100])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)
        main_layout.addWidget(splitter)

        # Bandeau bas : bouton générer
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.generate_button = QPushButton("Générer PDF")
        self.generate_button.setStyleSheet("background-color: #FF7043; color: white; font-weight: bold; font-size: 16px; padding: 10px 30px; border-radius: 8px;")
        self.generate_button.clicked.connect(self.generate_pdf)
        bottom_layout.addWidget(self.generate_button)
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        # Correction du style pour les QLineEdit (texte noir sur fond sombre)
        lineedit_style = "color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;"
        for le in [self.days_entry, self.addition_count, self.addition_digits, self.addition_decimals,
                   self.subtraction_count, self.subtraction_digits, self.subtraction_decimals,
                   self.multiplication_count, self.multiplication_digits, self.multiplication_decimals,
                   self.division_count, self.division_digits, self.division_decimals, self.verbs_per_day_entry,
                   self.grammar_sentence_count]:
            le.setStyleSheet(lineedit_style)

        # Style pour les labels
        label_style = "color: #e0e0e0; font-size: 14px; font-weight: normal;"
        for layout in [addition_layout, subtraction_layout, multiplication_layout, division_layout]:
            for i in range(layout.count()):
                item = layout.itemAt(i).widget()
                if isinstance(item, QLabel):
                    item.setStyleSheet(label_style)

        # Chargement de la configuration si elle existe
        def get_resource_path(filename):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, filename)
            return os.path.join(os.path.dirname(__file__), filename)
        self.config_path = get_resource_path('config.json')
        self.load_config()

    def get_int(self, lineedit, default=0, field_name=None):
        value = lineedit.text().strip()
        if value == '':
            return default
        if value.isdigit():
            return int(value)
        else:
            raise InvalidFieldError(field_name or lineedit.objectName(), value)

    def generate_pdf(self):
        try:
            days = self.get_int(self.days_entry, field_name="Nombre de jours")
            operations = []
            params_list = []
            # Addition
            if self.get_int(self.addition_count, field_name="Addition - nombre de calculs") > 0 and self.get_int(self.addition_digits, field_name="Addition - chiffres") > 0:
                count = self.get_int(self.addition_count, field_name="Addition - nombre de calculs")
                digits = self.get_int(self.addition_digits, field_name="Addition - chiffres")
                decimals = self.get_int(self.addition_decimals, field_name="Addition - décimales")
                params_list.append({
                    'operation': 'addition',
                    'count': count,
                    'digits': digits,
                    'with_decimals': decimals > 0,
                    'decimals': decimals
                })
                operations.append('addition')
            # Soustraction
            if self.get_int(self.subtraction_count, field_name="Soustraction - nombre de calculs") > 0 and self.get_int(self.subtraction_digits, field_name="Soustraction - chiffres") > 0:
                count = self.get_int(self.subtraction_count, field_name="Soustraction - nombre de calculs")
                digits = self.get_int(self.subtraction_digits, field_name="Soustraction - chiffres")
                decimals = self.get_int(self.subtraction_decimals, field_name="Soustraction - décimales")
                allow_negative = self.subtraction_negative_checkbox.isChecked()
                params_list.append({
                    'operation': 'soustraction',
                    'count': count,
                    'digits': digits,
                    'with_decimals': decimals > 0,
                    'decimals': decimals,
                    'allow_negative': allow_negative
                })
                operations.append('soustraction')
            # Multiplication
            if self.get_int(self.multiplication_count, field_name="Multiplication - nombre de calculs") > 0 and self.get_int(self.multiplication_digits, field_name="Multiplication - chiffres") > 0:
                count = self.get_int(self.multiplication_count, field_name="Multiplication - nombre de calculs")
                digits = self.get_int(self.multiplication_digits, field_name="Multiplication - chiffres")
                decimals = self.get_int(self.multiplication_decimals, field_name="Multiplication - décimales")
                params_list.append({
                    'operation': 'multiplication',
                    'count': count,
                    'digits': digits,
                    'with_decimals': decimals > 0,
                    'decimals': decimals
                })
                operations.append('multiplication')
            # Division
            if self.get_int(self.division_count, field_name="Division - nombre de calculs") > 0 and self.get_int(self.division_digits, field_name="Division - chiffres") > 0:
                count = self.get_int(self.division_count, field_name="Division - nombre de calculs")
                digits = self.get_int(self.division_digits, field_name="Division - chiffres")
                division_reste = self.division_reste_checkbox.isChecked()
                division_decimals = self.get_int(self.division_decimals, field_name="Division - décimales")
                division_quotient_decimal = division_decimals > 0
                params_list.append({
                    'operation': 'division',
                    'count': count,
                    'digits': digits,
                    'division_reste': division_reste,
                    'division_quotient_decimal': division_quotient_decimal,
                    'division_decimals': division_decimals
                })
                operations.append('division')

            # Récupération des groupes et temps cochés
            groupes_choisis = []
            if self.group_1_checkbox.isChecked():
                groupes_choisis.append(1)
            if self.group_2_checkbox.isChecked():
                groupes_choisis.append(2)
            if self.group_3_checkbox.isChecked():
                groupes_choisis.append(3)
            temps_choisis = []
            if self.present_checkbox.isChecked():
                temps_choisis.append("présent")
            if self.imparfait_checkbox.isChecked():
                temps_choisis.append("imparfait")
            if self.passe_simple_checkbox.isChecked():
                temps_choisis.append("passé simple")
            if self.futur_checkbox.isChecked():
                temps_choisis.append("futur simple")
            if self.passe_compose_checkbox.isChecked():
                temps_choisis.append("passé composé")
            if self.plus_que_parfait_checkbox.isChecked():
                temps_choisis.append("plus-que-parfait")
            if self.passe_anterieur_checkbox.isChecked():
                temps_choisis.append("passé antérieur")
            if self.futur_anterieur_checkbox.isChecked():
                temps_choisis.append("futur antérieur")
            if self.subjonctif_present_checkbox.isChecked():
                temps_choisis.append("subjonctif présent")
            if self.subjonctif_imparfait_checkbox.isChecked():
                temps_choisis.append("subjonctif imparfait")
            if self.subjonctif_passe_checkbox.isChecked():
                temps_choisis.append("subjonctif passé")
            if self.subjonctif_plus_que_parfait_checkbox.isChecked():
                temps_choisis.append("subjonctif plus-que-parfait")
            if self.conditionnel_present_checkbox.isChecked():
                temps_choisis.append("conditionnel présent")
            if self.conditionnel_passe_checkbox.isChecked():
                temps_choisis.append("conditionnel passé")
            if self.imperatif_present_checkbox.isChecked():
                temps_choisis.append("impératif présent")
            if self.imperatif_passe_checkbox.isChecked():
                temps_choisis.append("impératif passé") 
            jours = self.get_int(self.days_entry, field_name="Nombre de jours")
            verbes_par_jour = self.get_int(self.verbs_per_day_entry, field_name="Verbes par jour")

            # Construction de la liste de tous les verbes possibles selon les groupes cochés
            from conjugation_generator import VERBS
            verbes_possibles = []
            for g in groupes_choisis:
                verbes_possibles += VERBS[g]
            random.shuffle(verbes_possibles)
            if len(verbes_possibles) < verbes_par_jour * jours:
                print("Pas assez de verbes pour couvrir tous les jours sans doublon.")
                return

            # Génération de la structure pour le PDF
            index = 0
            conjugations = []
            for _ in range(jours):
                daily_conjugations = []
                for _ in range(verbes_par_jour):
                    verbe = verbes_possibles[index]
                    index += 1
                    temps = random.choice(temps_choisis)
                    daily_conjugations.append({"verb": verbe, "tense": temps})
                conjugations.append(daily_conjugations)

            # Construction des listes attendues par generate_workbook_pdf
            operations = []
            counts = []
            max_digits = []
            for param in params_list:
                operations.append(param['operation'])
                counts.append(param['count'])
                max_digits.append(param['digits'])

            # Récupération des paramètres grammaire dans generate_pdf
            from grammar_generator import PHRASES, TRANSFORMATIONS, get_random_phrase, get_random_transformation, get_random_phrases
            grammar_sentence_count = self.get_int(self.grammar_sentence_count, field_name="Grammaire - nombre de phrases")
            grammar_types = []
            if self.intransitive_checkbox.isChecked():
                grammar_types.append('intransitive')
            if self.transitive_direct_checkbox.isChecked():
                grammar_types.append('transitive_direct')
            if self.transitive_indirect_checkbox.isChecked():
                grammar_types.append('transitive_indirect')
            if self.ditransitive_checkbox.isChecked():
                grammar_types.append('ditransitive')
            grammar_transformations = [t.text() for t in self.transfo_checkboxes if t.isChecked()]
            # Génération des exercices de grammaire pour chaque jour
            grammar_exercises = []
            for _ in range(jours):
                phrases_choisies = get_random_phrases(grammar_types, grammar_sentence_count)
                daily_grammar = []
                for phrase in phrases_choisies:
                    transformation = get_random_transformation(grammar_transformations)
                    daily_grammar.append({
                        'phrase': phrase,
                        'transformation': transformation
                    })
                grammar_exercises.append(daily_grammar)

            # Appel à la génération du PDF avec la bonne signature
            from pdf_generator import generate_math_problems, generate_workbook_pdf
            header_text = self.header_entry.text().strip()
            show_name = self.show_name_checkbox.isChecked()
            show_note = self.show_note_checkbox.isChecked()
            generate_workbook_pdf(days, operations, counts, max_digits, conjugations, params_list, grammar_exercises, header_text=header_text, show_name=show_name, show_note=show_note)
        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def save_config(self):
        config = {
            'days_entry': self.days_entry.text(),
            'header_entry': self.header_entry.text(),
            'addition_count': self.addition_count.text(),
            'addition_digits': self.addition_digits.text(),
            'addition_decimals': self.addition_decimals.text(),
            'subtraction_count': self.subtraction_count.text(),
            'subtraction_digits': self.subtraction_digits.text(),
            'subtraction_decimals': self.subtraction_decimals.text(),
            'subtraction_negative_checkbox': self.subtraction_negative_checkbox.isChecked(),
            'multiplication_count': self.multiplication_count.text(),
            'multiplication_digits': self.multiplication_digits.text(),
            'multiplication_decimals': self.multiplication_decimals.text(),
            'division_count': self.division_count.text(),
            'division_digits': self.division_digits.text(),
            'division_decimals': self.division_decimals.text(),
            'division_reste_checkbox': self.division_reste_checkbox.isChecked(),
            'group_1_checkbox': self.group_1_checkbox.isChecked(),
            'group_2_checkbox': self.group_2_checkbox.isChecked(),
            'group_3_checkbox': self.group_3_checkbox.isChecked(),
            'present_checkbox': self.present_checkbox.isChecked(),
            'imparfait_checkbox': self.imparfait_checkbox.isChecked(),
            'passe_simple_checkbox': self.passe_simple_checkbox.isChecked(),
            'futur_checkbox': self.futur_checkbox.isChecked(),
            'passe_compose_checkbox': self.passe_compose_checkbox.isChecked(),
            'plus_que_parfait_checkbox': self.plus_que_parfait_checkbox.isChecked(),
            'passe_anterieur_checkbox': self.passe_anterieur_checkbox.isChecked(),
            'futur_anterieur_checkbox': self.futur_anterieur_checkbox.isChecked(),
            'subjonctif_present_checkbox': self.subjonctif_present_checkbox.isChecked(),
            'subjonctif_imparfait_checkbox': self.subjonctif_imparfait_checkbox.isChecked(),
            'subjonctif_passe_checkbox': self.subjonctif_passe_checkbox.isChecked(),
            'subjonctif_plus_que_parfait_checkbox': self.subjonctif_plus_que_parfait_checkbox.isChecked(),
            'conditionnel_present_checkbox': self.conditionnel_present_checkbox.isChecked(),
            'conditionnel_passe_checkbox': self.conditionnel_passe_checkbox.isChecked(),
            'imperatif_present_checkbox': self.imperatif_present_checkbox.isChecked(),
            'imperatif_passe_checkbox': self.imperatif_passe_checkbox.isChecked(),
            'verbs_per_day_entry': self.verbs_per_day_entry.text(),
            'grammar_sentence_count': self.grammar_sentence_count.text(),
            'intransitive_checkbox': self.intransitive_checkbox.isChecked(),
            'transitive_direct_checkbox': self.transitive_direct_checkbox.isChecked(),
            'transitive_indirect_checkbox': self.transitive_indirect_checkbox.isChecked(),
            'ditransitive_checkbox': self.ditransitive_checkbox.isChecked(),
            'transfo_checkboxes': [cb.isChecked() for cb in self.transfo_checkboxes],
            'show_name_checkbox': self.show_name_checkbox.isChecked(),
            'show_note_checkbox': self.show_note_checkbox.isChecked(),
        }
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration : {e}")

    def load_config(self):
        if not os.path.exists(self.config_path):
            return
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.days_entry.setText(config.get('days_entry', ''))
            self.header_entry.setText(config.get('header_entry', ''))
            self.addition_count.setText(config.get('addition_count', ''))
            self.addition_digits.setText(config.get('addition_digits', ''))
            self.addition_decimals.setText(config.get('addition_decimals', ''))
            self.subtraction_count.setText(config.get('subtraction_count', ''))
            self.subtraction_digits.setText(config.get('subtraction_digits', ''))
            self.subtraction_decimals.setText(config.get('subtraction_decimals', ''))
            self.subtraction_negative_checkbox.setChecked(config.get('subtraction_negative_checkbox', False))
            self.multiplication_count.setText(config.get('multiplication_count', ''))
            self.multiplication_digits.setText(config.get('multiplication_digits', ''))
            self.multiplication_decimals.setText(config.get('multiplication_decimals', ''))
            self.division_count.setText(config.get('division_count', ''))
            self.division_digits.setText(config.get('division_digits', ''))
            self.division_decimals.setText(config.get('division_decimals', ''))
            self.division_reste_checkbox.setChecked(config.get('division_reste_checkbox', False))
            self.group_1_checkbox.setChecked(config.get('group_1_checkbox', False))
            self.group_2_checkbox.setChecked(config.get('group_2_checkbox', False))
            self.group_3_checkbox.setChecked(config.get('group_3_checkbox', False))
            self.present_checkbox.setChecked(config.get('present_checkbox', False))
            self.imparfait_checkbox.setChecked(config.get('imparfait_checkbox', False))
            self.passe_simple_checkbox.setChecked(config.get('passe_simple_checkbox', False))
            self.futur_checkbox.setChecked(config.get('futur_checkbox', False))
            self.passe_compose_checkbox.setChecked(config.get('passe_compose_checkbox', False))
            self.plus_que_parfait_checkbox.setChecked(config.get('plus_que_parfait_checkbox', False))
            self.passe_anterieur_checkbox.setChecked(config.get('passe_anterieur_checkbox', False))
            self.futur_anterieur_checkbox.setChecked(config.get('futur_anterieur_checkbox', False))
            self.subjonctif_present_checkbox.setChecked(config.get('subjonctif_present_checkbox', False))
            self.subjonctif_imparfait_checkbox.setChecked(config.get('subjonctif_imparfait_checkbox', False))
            self.subjonctif_passe_checkbox.setChecked(config.get('subjonctif_passe_checkbox', False))
            self.subjonctif_plus_que_parfait_checkbox.setChecked(config.get('subjonctif_plus_que_parfait_checkbox', False))
            self.conditionnel_present_checkbox.setChecked(config.get('conditionnel_present_checkbox', False))
            self.conditionnel_passe_checkbox.setChecked(config.get('conditionnel_passe_checkbox', False))
            self.imperatif_present_checkbox.setChecked(config.get('imperatif_present_checkbox', False))
            self.imperatif_passe_checkbox.setChecked(config.get('imperatif_passe_checkbox', False))
            self.verbs_per_day_entry.setText(config.get('verbs_per_day_entry', ''))
            self.grammar_sentence_count.setText(config.get('grammar_sentence_count', ''))
            self.intransitive_checkbox.setChecked(config.get('intransitive_checkbox', False))
            self.transitive_direct_checkbox.setChecked(config.get('transitive_direct_checkbox', False))
            self.transitive_indirect_checkbox.setChecked(config.get('transitive_indirect_checkbox', False))
            self.ditransitive_checkbox.setChecked(config.get('ditransitive_checkbox', False))
            # Pour les transformations grammaire (liste de booléens)
            transfo_states = config.get('transfo_checkboxes', [])
            for cb, state in zip(self.transfo_checkboxes, transfo_states):
                cb.setChecked(state)
            self.show_name_checkbox.setChecked(config.get('show_name_checkbox', False))
            self.show_note_checkbox.setChecked(config.get('show_note_checkbox', False))
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration : {e}")

    def closeEvent(self, event):
        self.save_config()
        super().closeEvent(event)

# Note : Pour PyInstaller, les fichiers JSON (phrases_grammaire.json, verbes.json, config.json) doivent être à côté de l'exe pour être modifiables après compilation.

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()