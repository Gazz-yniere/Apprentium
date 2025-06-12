from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QFrame, QSizePolicy, QGroupBox, QSplitter)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QPalette, QColor
from pdf_generator import generate_workbook_pdf
from conjugation_generator import get_random_verb
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
        self.setMinimumWidth(1500)
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
        self.header_label = QLabel("En-tête (optionnel) :")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.header_entry = QLineEdit()
        self.header_entry.setMaximumWidth(400)
        self.header_entry.setStyleSheet("color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;")
        self.show_name_checkbox = QCheckBox("Afficher un champ Nom à gauche")
        self.show_note_checkbox = QCheckBox("Afficher un champ Note à droite")
        top_layout.addWidget(self.header_label)
        top_layout.addWidget(self.header_entry)
        top_layout.addWidget(self.show_name_checkbox)
        top_layout.addWidget(self.show_note_checkbox)
        top_layout.addWidget(self.days_label)
        top_layout.addWidget(self.days_entry)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

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
        # Harmonisation des couleurs des bordures des QGroupBox selon la couleur du titre de colonne
        # Calculs : bleu clair (#4FC3F7)
        for group in [addition_group, subtraction_group, multiplication_group, division_group]:
            group.setStyleSheet("QGroupBox { margin-top: 8px; margin-bottom: 8px; padding: 24px 12px 24px 12px; border: 2px solid #4FC3F7; border-radius: 8px; } QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; top: 0px; padding: 0 12px; color: #ffffff; font-weight: bold; font-size: 15px; background: #232323; }")
        calc_layout.addWidget(addition_group)
        calc_layout.addWidget(subtraction_group)
        calc_layout.addWidget(multiplication_group)
        calc_layout.addWidget(division_group)
        calc_layout.addStretch()

        # --- Colonne Géométrie/Mesures ---
        geo_layout = QVBoxLayout()
        geo_title = QLabel("Mesures")
        geo_title.setStyleSheet("font-weight: bold; font-size: 20px; color: #BA68C8; margin-bottom: 8px; margin-top: 0px;")
        geo_layout.addWidget(geo_title)
        geo_layout.setContentsMargins(5, 5, 5, 5)
        geo_layout.setSpacing(6)
        # Section nombre d'exercices
        geo_number_group = QGroupBox("Paramètres de mesures")
        geo_number_layout = QVBoxLayout()
        row = QHBoxLayout()
        self.geo_ex_count_label = QLabel("Nombre d'exercices :")
        self.geo_ex_count = QLineEdit()
        self.geo_ex_count.setMaximumWidth(60)
        row.addWidget(self.geo_ex_count_label)
        row.addWidget(self.geo_ex_count)
        geo_number_layout.addLayout(row)
        geo_number_group.setLayout(geo_number_layout)
        geo_layout.addWidget(geo_number_group)
        # Section conversions
        geo_conv_group = QGroupBox("Conversions")
        geo_conv_layout = QVBoxLayout()
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
        self.conv_sens_direct = QCheckBox("Aller (ex : m → cm)")
        self.conv_sens_inverse = QCheckBox("Retour (ex : cm → m)")
        self.conv_sens_direct.setChecked(True)
        self.conv_sens_inverse.setChecked(True)
        geo_conv_layout.addWidget(self.conv_sens_direct)
        geo_conv_layout.addWidget(self.conv_sens_inverse)
        geo_conv_group.setLayout(geo_conv_layout)
        geo_layout.addWidget(geo_conv_group)
        # Mesures : violet (#BA68C8)
        for group in [geo_number_group, geo_conv_group]:
            group.setStyleSheet("QGroupBox { margin-top: 8px; margin-bottom: 8px; padding: 24px 12px 24px 12px; border: 2px solid #BA68C8; border-radius: 8px; } QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; top: 0px; padding: 0 12px; color: #ffffff; font-weight: bold; font-size: 15px; background: #232323; }")
        geo_layout.addStretch()

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
        self.usual_verbs_checkbox = QCheckBox("Verbes usuels (à connaître par cœur)")
        group_layout.addWidget(self.group_1_checkbox)
        group_layout.addWidget(self.group_2_checkbox)
        group_layout.addWidget(self.group_3_checkbox)
        group_layout.addWidget(self.usual_verbs_checkbox)
        group_group.setLayout(group_layout)
        conj_layout.addWidget(group_group)
        # Temps (dynamique depuis conjugation_generator.TENSES)
        from conjugation_generator import TENSES
        tense_group = QGroupBox("Temps")
        tense_layout = QVBoxLayout()
        self.tense_checkboxes = []
        for tense in TENSES:
            cb = QCheckBox(tense.capitalize())
            tense_layout.addWidget(cb)
            self.tense_checkboxes.append(cb)
        tense_group.setLayout(tense_layout)
        conj_layout.addWidget(tense_group)
        # Conjugaison : vert (#81C784)
        for group in [number_group, group_group, tense_group]:
            group.setStyleSheet("QGroupBox { margin-top: 8px; margin-bottom: 8px; padding: 24px 12px 24px 12px; border: 2px solid #81C784; border-radius: 8px; } QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; top: 0px; padding: 0 12px; color: #ffffff; font-weight: bold; font-size: 15px; background: #232323; }")
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
        # Grammaire : jaune (#FFD54F)
        for group in [grammar_number_group, grammar_type_group, grammar_transfo_group]:
            group.setStyleSheet("QGroupBox { margin-top: 8px; margin-bottom: 8px; padding: 24px 12px 24px 12px; border: 2px solid #FFD54F; border-radius: 8px; } QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; top: 0px; padding: 0 12px; color: #ffffff; font-weight: bold; font-size: 15px; background: #232323; }")
        grammar_layout.addStretch()

        # --- Colonne Anglais ---
        english_layout = QVBoxLayout()
        english_title = QLabel("Anglais")
        english_title.setStyleSheet("font-weight: bold; font-size: 20px; color: #64B5F6; margin-bottom: 8px; margin-top: 0px;")
        english_layout.addWidget(english_title)
        english_layout.setContentsMargins(5, 5, 5, 5)
        english_layout.setSpacing(6)
        # Section nombre d'exercices
        english_number_group = QGroupBox("Paramètres d'anglais")
        english_number_layout = QVBoxLayout()
        row = QHBoxLayout()
        self.english_ex_count_label = QLabel("Nombre d'exercices :")
        self.english_ex_count = QLineEdit()
        self.english_ex_count.setMaximumWidth(60)
        self.english_ex_count.setStyleSheet("color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;")
        row.addWidget(self.english_ex_count_label)
        row.addWidget(self.english_ex_count)
        english_number_layout.addLayout(row)
        english_number_group.setLayout(english_number_layout)
        english_layout.addWidget(english_number_group)
        # Section types d'exercices
        english_type_group = QGroupBox("Types d'exercices")
        english_type_layout = QVBoxLayout()
        self.english_type_simple = QCheckBox("Phrase à compléter simple")
        self.english_type_complexe = QCheckBox("Phrase à compléter complexe")
        self.english_type_relier = QCheckBox("Relier mots anglais/français")
        self.english_type_checkboxes = [self.english_type_simple, self.english_type_complexe, self.english_type_relier]
        for cb in self.english_type_checkboxes:
            english_type_layout.addWidget(cb)
        # Champ pour le nombre de mots à relier (affiché seulement si 'relier' est coché)
        self.relier_count_label = QLabel("Nombre de mots à relier :")
        self.relier_count = QLineEdit()
        self.relier_count.setMaximumWidth(60)
        self.relier_count.setStyleSheet("color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;")
        relier_count_layout = QHBoxLayout()
        relier_count_layout.addWidget(self.relier_count_label)
        relier_count_layout.addWidget(self.relier_count)
        self.relier_count_label.hide()
        self.relier_count.hide()
        english_type_layout.addLayout(relier_count_layout)
        self.english_type_relier.stateChanged.connect(self.toggle_relier_count)
        english_type_group.setLayout(english_type_layout)
        english_layout.addWidget(english_type_group)
        # Anglais : bleu moyen (#64B5F6)
        for group in [english_number_group, english_type_group]:
            group.setStyleSheet("QGroupBox { margin-top: 8px; margin-bottom: 8px; padding: 24px 12px 24px 12px; border: 2px solid #64B5F6; border-radius: 8px; } QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; top: 0px; padding: 0 12px; color: #ffffff; font-weight: bold; font-size: 15px; background: #232323; }")
        english_layout.addStretch()
        # --- Splitter pour 5 colonnes ---
        calc_widget = QWidget(); calc_widget.setLayout(calc_layout)
        geo_widget = QWidget(); geo_widget.setLayout(geo_layout)
        conj_widget = QWidget(); conj_widget.setLayout(conj_layout)
        grammar_widget = QWidget(); grammar_widget.setLayout(grammar_layout)
        english_widget = QWidget(); english_widget.setLayout(english_layout)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(calc_widget)
        splitter.addWidget(geo_widget)
        splitter.addWidget(conj_widget)
        splitter.addWidget(grammar_widget)
        splitter.addWidget(english_widget)
        splitter.setSizes([100, 100, 100, 100, 100])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)
        splitter.setStretchFactor(3, 1)
        splitter.setStretchFactor(4, 1)
        main_layout.addWidget(splitter)

        # Bandeau bas : boutons générer + nom du fichier sur la même ligne
        bottom_layout = QHBoxLayout()
        self.filename_label = QLabel("Nom du fichier :")
        self.filename_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.filename_entry = QLineEdit()
        self.filename_entry.setMaximumWidth(250)
        self.filename_entry.setStyleSheet("color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;")
        self.filename_entry.setText("workbook")
        bottom_layout.addWidget(self.filename_label)
        bottom_layout.addWidget(self.filename_entry)
        bottom_layout.addStretch()
        # Styles pour les boutons (normal, désactivé, pressé)
        pdf_btn_style = """
            QPushButton {
                background-color: #FF7043;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 10px 30px;
                border-radius: 8px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
            QPushButton:pressed {
                background-color: #d84315;
            }
        """
        word_btn_style = """
            QPushButton {
                background-color: #1976D2;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 10px 30px;
                border-radius: 8px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """
        self.generate_pdf_button = QPushButton("Générer PDF")
        self.generate_pdf_button.setStyleSheet(pdf_btn_style)
        self.generate_pdf_button.clicked.connect(self.generate_pdf)
        bottom_layout.addWidget(self.generate_pdf_button)
        self.generate_word_button = QPushButton("Générer Word")
        self.generate_word_button.setStyleSheet(word_btn_style)
        self.generate_word_button.clicked.connect(self.generate_word)
        bottom_layout.addWidget(self.generate_word_button)
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        # Correction du style pour les QLineEdit (texte noir sur fond sombre)
        lineedit_style = "color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;"
        for le in [self.days_entry, self.addition_count, self.addition_digits, self.addition_decimals,
                   self.subtraction_count, self.subtraction_digits, self.subtraction_decimals,
                   self.multiplication_count, self.multiplication_digits, self.multiplication_decimals,
                   self.division_count, self.division_digits, self.division_decimals, self.verbs_per_day_entry,
                   self.grammar_sentence_count, self.geo_ex_count, self.english_ex_count]:
            le.setStyleSheet(lineedit_style)

        # Style pour les labels
        label_style = "color: #e0e0e0; font-size: 14px; font-weight: normal;"
        for layout in [addition_layout, subtraction_layout, multiplication_layout, division_layout]:
            for i in range(layout.count()):
                item = layout.itemAt(i).widget()
                if isinstance(item, QLabel):
                    item.setStyleSheet(label_style)

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
            ('header_entry', self.header_entry, 'text'),
            ('addition_count', self.addition_count, 'text'),
            ('addition_digits', self.addition_digits, 'text'),
            ('addition_decimals', self.addition_decimals, 'text'),
            ('subtraction_count', self.subtraction_count, 'text'),
            ('subtraction_digits', self.subtraction_digits, 'text'),
            ('subtraction_decimals', self.subtraction_decimals, 'text'),
            ('subtraction_negative_checkbox', self.subtraction_negative_checkbox, 'checked'),
            ('multiplication_count', self.multiplication_count, 'text'),
            ('multiplication_digits', self.multiplication_digits, 'text'),
            ('multiplication_decimals', self.multiplication_decimals, 'text'),
            ('division_count', self.division_count, 'text'),
            ('division_digits', self.division_digits, 'text'),
            ('division_decimals', self.division_decimals, 'text'),
            ('division_reste_checkbox', self.division_reste_checkbox, 'checked'),
            ('group_1_checkbox', self.group_1_checkbox, 'checked'),
            ('group_2_checkbox', self.group_2_checkbox, 'checked'),
            ('group_3_checkbox', self.group_3_checkbox, 'checked'),
            ('verbs_per_day_entry', self.verbs_per_day_entry, 'text'),
            ('grammar_sentence_count', self.grammar_sentence_count, 'text'),
            ('intransitive_checkbox', self.intransitive_checkbox, 'checked'),
            ('transitive_direct_checkbox', self.transitive_direct_checkbox, 'checked'),
            ('transitive_indirect_checkbox', self.transitive_indirect_checkbox, 'checked'),
            ('ditransitive_checkbox', self.ditransitive_checkbox, 'checked'),
            ('transfo_checkboxes', self.transfo_checkboxes, 'checked_list'),
            ('show_name_checkbox', self.show_name_checkbox, 'checked'),
            ('show_note_checkbox', self.show_note_checkbox, 'checked'),
            ('filename_entry', self.filename_entry, 'text'),
            ('usual_verbs_checkbox', self.usual_verbs_checkbox, 'checked'),
            ('tense_checkboxes', self.tense_checkboxes, 'checked_list'),
            ('geo_ex_count', self.geo_ex_count, 'text'),
            ('geo_conv_type_checkboxes', self.geo_conv_type_checkboxes, 'checked_list'),
            ('conv_sens_direct', self.conv_sens_direct, 'checked'),
            ('conv_sens_inverse', self.conv_sens_inverse, 'checked'),
            ('english_ex_count', self.english_ex_count, 'text'),
            ('english_type_checkboxes', self.english_type_checkboxes, 'checked_list'),
            ('relier_count', self.relier_count, 'text'),
        ]
        self.load_config()

        self.days_entry.textChanged.connect(self.validate_days_entry)

        # --- Début des méthodes ---

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
        style = "color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;"
        if not is_valid:
            style += "border: 2px solid red;"
        self.days_entry.setStyleSheet(style)
        self.generate_pdf_button.setEnabled(is_valid)
        self.generate_word_button.setEnabled(is_valid)

    def build_exercise_data(self):
        try:
            days = self.get_int(self.days_entry, field_name="Nombre de jours")
            relier_count = self.get_int(self.relier_count, field_name="Anglais - nombre de mots à relier")
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
            include_usuels = self.usual_verbs_checkbox.isChecked()
            from conjugation_generator import TENSES
            temps_choisis = [tense for tense, cb in zip(TENSES, self.tense_checkboxes) if cb.isChecked()]
            jours = self.get_int(self.days_entry, field_name="Nombre de jours")
            verbes_par_jour = self.get_int(self.verbs_per_day_entry, field_name="Verbes par jour")

            # Construction de la liste de tous les verbes possibles selon les groupes cochés
            from conjugation_generator import VERBS
            verbes_possibles = []
            for g in groupes_choisis:
                verbes_possibles += VERBS[g]
            if include_usuels and "usuels" in VERBS:
                verbes_possibles += VERBS["usuels"]
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

            # --- Génération des exercices de conversion ---
            from conversion_generator import generate_conversion_exercises
            geo_ex_count = self.get_int(self.geo_ex_count, field_name="Géométrie/mesures - nombre d'exercices")
            geo_types = self.get_selected_conversion_types()
            geo_senses = self.get_selected_conversion_senses()
            geo_exercises = []
            if geo_types and geo_ex_count > 0 and geo_senses:
                geo_exercises = generate_conversion_exercises(geo_types, geo_ex_count, geo_senses)

            # --- Génération des exercices d'anglais (simple) ---
            english_types = self.get_selected_english_types()
            from anglais_generator import PHRASES_SIMPLES, PHRASES_COMPLEXES, MOTS_A_RELIER
            english_ex_count = self.get_int(self.english_ex_count, field_name="Anglais - nombre d'exercices")
            relier_count = self.get_int(self.relier_count, field_name="Nombre de mots à relier")
            english_exercises = []
            for _ in range(jours):
                daily = []
                # Génère uniquement des exercices de complétion (simple/complexe)
                completion_types = []
                if 'simple' in english_types and PHRASES_SIMPLES:
                    completion_types.append('simple')
                if 'complexe' in english_types and PHRASES_COMPLEXES:
                    completion_types.append('complexe')
                for _ in range(english_ex_count):
                    if not completion_types:
                        break
                    t = random.choice(completion_types)
                    if t == 'simple':
                        daily.append({'type': 'simple', 'content': random.choice(PHRASES_SIMPLES)})
                    elif t == 'complexe':
                        daily.append({'type': 'complexe', 'content': random.choice(PHRASES_COMPLEXES)})
                # Ajoute un exercice relier si demandé
                if 'relier' in english_types and relier_count > 0 and MOTS_A_RELIER:
                    mots = random.sample(MOTS_A_RELIER, min(relier_count, len(MOTS_A_RELIER)))
                    daily.append({'type': 'relier', 'content': mots})
                english_exercises.append(daily)

            return {
                'days': days,
                'operations': operations,
                'counts': counts,
                'max_digits': max_digits,
                'conjugations': conjugations,
                'params_list': params_list,
                'grammar_exercises': grammar_exercises,
                'geo_exercises': geo_exercises,
                'english_exercises': english_exercises
            }
        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
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
            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"
            generate_workbook_pdf(
                data['days'], data['operations'], data['counts'], data['max_digits'],
                data['conjugations'], data['params_list'], data['grammar_exercises'],
                geo_exercises=data['geo_exercises'], english_exercises=data['english_exercises'],
                header_text=header_text, show_name=show_name, show_note=show_note, filename=filename
            )
        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
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
            if not filename.lower().endswith(".docx"):
                filename += ".docx"
            generate_workbook_docx(
                data['days'], data['operations'], data['counts'], data['max_digits'],
                data['conjugations'], data['params_list'], data['grammar_exercises'],
                geo_exercises=data['geo_exercises'], english_exercises=data['english_exercises'],
                header_text=header_text, show_name=show_name, show_note=show_note, filename=filename
            )
        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite : {type(e).__name__} : {e}")
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
            for name, widget, mode in self.config_fields:
                if name not in config:
                    continue
                if mode == 'text':
                    widget.setText(config.get(name, ''))
                elif mode == 'checked':
                    widget.setChecked(config.get(name, False))
                elif mode == 'checked_list':
                    states = config.get(name, [False]*len(widget))
                    for cb, state in zip(widget, states):
                        cb.setChecked(state)
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration : {e}")

    def closeEvent(self, event):
        self.save_config()
        super().closeEvent(event)

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
        labels = ['simple', 'complexe', 'relier']
        for cb, label in zip(self.english_type_checkboxes, labels):
            if cb.isChecked():
                types.append(label)
        return types

    def toggle_relier_count(self):
        if self.english_type_relier.isChecked():
            self.relier_count_label.show()
            self.relier_count.show()
        else:
            self.relier_count_label.hide()
            self.relier_count.hide()
# Note : Pour PyInstaller, les fichiers JSON (phrases_grammaire.json, verbes.json, config.json) doivent être à côté de l'exe pour être modifiables après compilation.

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()