from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QFrame, QSizePolicy, QGroupBox, QSplitter, QSpacerItem, QFileDialog)
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
        self.setWindowTitle("EduForge")
        import os
        icon_path = os.path.join(os.path.dirname(__file__), "EduForge.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumWidth(1400)
        #self.setMinimumHeight(900)
        self.selected_output_path = None # Pour stocker le chemin choisi par l'utilisateur
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
        top_layout.addStretch()
        top_layout.addWidget(self.days_label)
        top_layout.addWidget(self.days_entry)
        main_layout.addLayout(top_layout)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setStyleSheet("border-top: 1px solid #505050;") # Couleur pour le séparateur
        main_layout.addWidget(sep)

        # --- Colonne Calculs ---
        calc_layout = QVBoxLayout()
        calc_title = QLabel("Calculs")
        calc_title.setStyleSheet("font-weight: bold; font-size: 20px; color: #4FC3F7; margin-bottom: 8px; margin-top: 0px;")
        calc_layout.addWidget(calc_title)
        calc_layout.setContentsMargins(5, 5, 5, 5)
        calc_layout.setSpacing(6)
        # Exercice : Enumérer un nombre
        enumerate_group = QGroupBox("Enumérer un nombre")
        enumerate_layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel("Nombre d'exercices :"))
        self.enumerate_count = QLineEdit(); self.enumerate_count.setMaximumWidth(60)
        row.addWidget(self.enumerate_count)
        enumerate_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Chiffres par nombre :"))
        self.enumerate_digits = QLineEdit(); self.enumerate_digits.setMaximumWidth(60)
        row.addWidget(self.enumerate_digits)
        enumerate_layout.addLayout(row)
        enumerate_group.setLayout(enumerate_layout)

        # (Suppression de la création de sort_group ici, il sera déplacé dans la colonne Mesures)

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
        # Fonction utilitaire pour appliquer le style compact à une liste de QGroupBox
        def set_groupbox_style(groups, color):
            for group in groups:
                group.setStyleSheet(f"QGroupBox {{ margin-top: 2px; margin-bottom: 2px; padding: 10px 12px 10px 12px; border: 2px solid {color}; border-radius: 8px; }} QGroupBox:title {{ subcontrol-origin: margin; subcontrol-position: top left; left: 10px; top: 0px; padding: 0 12px; color: #ffffff; font-weight: bold; font-size: 15px; background: #232323; }}")

        # Harmonisation des couleurs des bordures des QGroupBox selon la couleur du titre de colonne
        set_groupbox_style([enumerate_group, addition_group, subtraction_group, multiplication_group, division_group], "#4FC3F7")
        calc_layout.addWidget(enumerate_group)
        calc_layout.addWidget(addition_group)
        calc_layout.addWidget(subtraction_group)
        calc_layout.addWidget(multiplication_group)
        calc_layout.addWidget(division_group)
        calc_layout.addStretch()

        # (Suppression de l'appel fautif à set_groupbox_style et des widgets non définis)

        # --- Colonne Géométrie/Mesures ---
        geo_layout = QVBoxLayout()
        geo_title = QLabel("Mesures")
        geo_title.setStyleSheet("font-weight: bold; font-size: 20px; color: #BA68C8; margin-bottom: 8px; margin-top: 0px;")
        geo_layout.addWidget(geo_title)
        geo_layout.setContentsMargins(5, 5, 5, 5)
        geo_layout.setSpacing(6)
        # (Suppression de la section Paramètres de mesures qui est maintenant vide)
        # Section conversions
        geo_conv_group = QGroupBox("Conversions")
        geo_conv_layout = QVBoxLayout()
        row = QHBoxLayout()
        self.geo_ex_count_label = QLabel("Nombre d'exercices :")
        self.geo_ex_count = QLineEdit()
        self.geo_ex_count.setMaximumWidth(60)
        row.addWidget(self.geo_ex_count_label)
        row.addWidget(self.geo_ex_count)
        geo_conv_layout.addLayout(row)
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
        self.conv_sens_direct = QCheckBox("Aller (m → cm)")
        self.conv_sens_inverse = QCheckBox("Retour (cm → m)")
        self.conv_sens_direct.setChecked(True)
        self.conv_sens_inverse.setChecked(True)
        sens_layout = QHBoxLayout()
        sens_layout.addWidget(self.conv_sens_direct)
        sens_layout.addWidget(self.conv_sens_inverse)
        geo_conv_layout.addLayout(sens_layout)
        geo_conv_group.setLayout(geo_conv_layout)
        geo_layout.addWidget(geo_conv_group)

        # Section : Ranger les nombres (déplacée ici)
        sort_group = QGroupBox("Ranger les nombres")
        sort_layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel("Nombre d'exercices :"))
        self.sort_count = QLineEdit(); self.sort_count.setMaximumWidth(60)
        row.addWidget(self.sort_count)
        sort_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Chiffres par nombre :"))
        self.sort_digits = QLineEdit(); self.sort_digits.setMaximumWidth(60)
        row.addWidget(self.sort_digits)
        sort_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Nombres à ranger :"))
        self.sort_n_numbers = QLineEdit(); self.sort_n_numbers.setMaximumWidth(60)
        row.addWidget(self.sort_n_numbers)
        sort_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Type :"))
        self.sort_type_croissant = QCheckBox("Croissant")
        self.sort_type_decroissant = QCheckBox("Décroissant")
        self.sort_type_croissant.setChecked(True)
        sort_type_layout = QHBoxLayout()
        sort_type_layout.addWidget(self.sort_type_croissant)
        sort_type_layout.addWidget(self.sort_type_decroissant)
        row.addLayout(sort_type_layout)
        sort_layout.addLayout(row)
        sort_group.setLayout(sort_layout)
        geo_layout.addWidget(sort_group)

        # Section : Encadrer un nombre
        encadrement_group = QGroupBox("Encadrer un nombre")
        encadrement_layout = QVBoxLayout()
        # Nombre d'exercices
        row = QHBoxLayout()
        row.addWidget(QLabel("Nombre d'exercices :"))
        self.encadrement_count = QLineEdit(); self.encadrement_count.setMaximumWidth(60)
        self.encadrement_count.setStyleSheet("color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;")
        row.addWidget(self.encadrement_count)
        encadrement_layout.addLayout(row)
        # Chiffres par nombre
        row = QHBoxLayout()
        row.addWidget(QLabel("Chiffres par nombre :"))
        self.encadrement_digits = QLineEdit(); self.encadrement_digits.setMaximumWidth(60)
        self.encadrement_digits.setStyleSheet("color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;")
        row.addWidget(self.encadrement_digits)
        encadrement_layout.addLayout(row)
        # Types d'encadrement
        type_label = QLabel("Type :")
        encadrement_layout.addWidget(type_label)
        self.encadrement_unite = QCheckBox("Unité")
        self.encadrement_dizaine = QCheckBox("Dizaine")
        self.encadrement_centaine = QCheckBox("Centaine")
        self.encadrement_millier = QCheckBox("Millier")
        type_layout1 = QHBoxLayout()
        type_layout1.addWidget(self.encadrement_unite)
        type_layout1.addWidget(self.encadrement_dizaine)
        type_layout2 = QHBoxLayout()
        type_layout2.addWidget(self.encadrement_centaine)
        type_layout2.addWidget(self.encadrement_millier)
        encadrement_layout.addLayout(type_layout1)
        encadrement_layout.addLayout(type_layout2)
        encadrement_group.setLayout(encadrement_layout)
        geo_layout.addWidget(encadrement_group)

        # Mesures : violet (#BA68C8)
        set_groupbox_style([geo_conv_group, sort_group, encadrement_group], "#BA68C8")
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
        set_groupbox_style([number_group, group_group, tense_group], "#81C784")
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
        self.intransitive_checkbox = QCheckBox("Sans complément d'objet")
        self.transitive_direct_checkbox = QCheckBox("Avec complément d'objet direct")
        self.transitive_indirect_checkbox = QCheckBox("Avec complément d'objet indirect")
        self.ditransitive_checkbox = QCheckBox("Avec deux compléments d'objet")
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
        set_groupbox_style([grammar_number_group, grammar_type_group, grammar_transfo_group], "#FFD54F")
        grammar_layout.addStretch()

        # --- Colonne Orthographe ---
        orthographe_layout = QVBoxLayout()
        orthographe_title = QLabel("Orthographe")
        orthographe_title.setStyleSheet("font-weight: bold; font-size: 20px; color: #FFB300; margin-bottom: 8px; margin-top: 0px;")
        orthographe_layout.addWidget(orthographe_title)
        orthographe_layout.setContentsMargins(5, 5, 5, 5)
        orthographe_layout.setSpacing(6)
        # Paramètres orthographe
        orthographe_number_group = QGroupBox("Paramètres d'orthographe")
        orthographe_number_layout = QVBoxLayout()
        row = QHBoxLayout()
        self.orthographe_ex_count_label = QLabel("Nombre d'exercices :")
        self.orthographe_ex_count = QLineEdit()
        self.orthographe_ex_count.setMaximumWidth(60)
        row.addWidget(self.orthographe_ex_count_label)
        row.addWidget(self.orthographe_ex_count)
        orthographe_number_layout.addLayout(row)
        orthographe_number_group.setLayout(orthographe_number_layout)
        orthographe_layout.addWidget(orthographe_number_group)
        # Section homophones
        orthographe_homophone_group = QGroupBox("Homophones")
        orthographe_homophone_layout = QVBoxLayout()
        self.homophone_a_checkbox = QCheckBox("a / à")
        self.homophone_et_checkbox = QCheckBox("et / est")
        self.homophone_on_checkbox = QCheckBox("on / ont")
        self.homophone_son_checkbox = QCheckBox("son / sont")
        self.homophone_ce_checkbox = QCheckBox("ce / se")
        self.homophone_ou_checkbox = QCheckBox("ou / où")
        self.homophone_ces_checkbox = QCheckBox("ces / ses")
        self.homophone_mes_checkbox = QCheckBox("mes / mais / met / mets")
        self.orthographe_homophone_checkboxes = [
            self.homophone_a_checkbox, self.homophone_et_checkbox, self.homophone_on_checkbox,
            self.homophone_son_checkbox, self.homophone_ce_checkbox, self.homophone_mes_checkbox,
            self.homophone_ou_checkbox, self.homophone_ces_checkbox
        ]
        for cb in self.orthographe_homophone_checkboxes:
            orthographe_homophone_layout.addWidget(cb)
        orthographe_homophone_group.setLayout(orthographe_homophone_layout)
        orthographe_layout.addWidget(orthographe_homophone_group)
        # Orthographe : orange foncé (#FFB300)
        set_groupbox_style([orthographe_number_group, orthographe_homophone_group], "#FFB300")
        orthographe_layout.addStretch()

        # --- Colonne Anglais ---
        english_layout = QVBoxLayout()
        english_title = QLabel("Anglais")
        english_title.setStyleSheet("font-weight: bold; font-size: 20px; color: #64B5F6; margin-bottom: 8px; margin-top: 0px;")
        english_layout.addWidget(english_title)
        english_layout.setContentsMargins(5, 5, 5, 5)
        english_layout.setSpacing(6)
        # Section 1 : Phrases à compléter
        english_complete_group = QGroupBox("Phrases à compléter")
        english_complete_layout = QVBoxLayout()
        row = QHBoxLayout()
        self.english_complete_count_label = QLabel("Nombre d'exercices :")
        self.english_complete_count = QLineEdit()
        self.english_complete_count.setMaximumWidth(60)
        self.english_complete_count.setStyleSheet("color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;")
        row.addWidget(self.english_complete_count_label)
        row.addWidget(self.english_complete_count)
        english_complete_layout.addLayout(row)
        self.english_type_simple = QCheckBox("Phrase à compléter simple")
        self.english_type_complexe = QCheckBox("Phrase à compléter complexe")
        english_complete_layout.addWidget(self.english_type_simple)
        english_complete_layout.addWidget(self.english_type_complexe)
        english_complete_group.setLayout(english_complete_layout)
        english_layout.addWidget(english_complete_group)
        # Section 2 : Jeux à relier
        english_relier_group = QGroupBox("Jeux à relier")
        english_relier_layout = QVBoxLayout()
        row = QHBoxLayout()
        self.english_relier_count_label = QLabel("Nombre de jeux à relier :")
        self.english_relier_count = QLineEdit()
        self.english_relier_count.setMaximumWidth(60)
        self.english_relier_count.setStyleSheet("color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;")
        row.addWidget(self.english_relier_count_label)
        row.addWidget(self.english_relier_count)
        english_relier_layout.addLayout(row)
        row = QHBoxLayout()
        self.relier_count_label = QLabel("Nombre de mots par jeu :")
        self.relier_count = QLineEdit()
        self.relier_count.setMaximumWidth(60)
        self.relier_count.setStyleSheet("color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;")
        row.addWidget(self.relier_count_label)
        row.addWidget(self.relier_count)
        english_relier_layout.addLayout(row)
        english_relier_group.setLayout(english_relier_layout)
        english_layout.addWidget(english_relier_group)
        # Anglais : bleu moyen (#64B5F6)
        set_groupbox_style([english_complete_group, english_relier_group], "#64B5F6")
        english_layout.addStretch()
        # --- Splitter pour 6 colonnes ---
        calc_widget = QWidget(); calc_widget.setLayout(calc_layout); calc_widget.setMinimumWidth(270)
        geo_widget = QWidget(); geo_widget.setLayout(geo_layout); geo_widget.setMinimumWidth(270)
        conj_widget = QWidget(); conj_widget.setLayout(conj_layout); conj_widget.setMinimumWidth(270)
        grammar_widget = QWidget(); grammar_widget.setLayout(grammar_layout); grammar_widget.setMinimumWidth(270)
        orthographe_widget = QWidget(); orthographe_widget.setLayout(orthographe_layout); orthographe_widget.setMinimumWidth(270)
        english_widget = QWidget(); english_widget.setLayout(english_layout); english_widget.setMinimumWidth(270)
        # Bloc vertical pour orthographe + anglais
        ortho_anglais_layout = QVBoxLayout()
        ortho_anglais_layout.setContentsMargins(0, 0, 0, 0)
        ortho_anglais_layout.setSpacing(0)
        ortho_anglais_layout.addWidget(orthographe_widget, alignment=Qt.AlignmentFlag.AlignTop)
        ortho_anglais_layout.addWidget(english_widget, alignment=Qt.AlignmentFlag.AlignTop)
        ortho_anglais_widget = QWidget(); ortho_anglais_widget.setLayout(ortho_anglais_layout); ortho_anglais_widget.setMinimumWidth(270)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(calc_widget)
        splitter.addWidget(geo_widget)
        splitter.addWidget(conj_widget)
        splitter.addWidget(grammar_widget)
        splitter.addWidget(ortho_anglais_widget)
        splitter.setSizes([100, 100, 100, 100, 200])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)
        splitter.setStretchFactor(3, 1)
        splitter.setStretchFactor(4, 2)
        main_layout.addWidget(splitter)

        # Séparateur avant les contrôles de fichier/génération
        sep_bottom = QFrame()
        sep_bottom.setFrameShape(QFrame.Shape.HLine)
        sep_bottom.setFrameShadow(QFrame.Shadow.Sunken)
        sep_bottom.setStyleSheet("border-top: 1px solid #505050;") # Couleur pour le séparateur
        main_layout.addWidget(sep_bottom)

        # Bandeau bas : boutons générer + nom du fichier sur la même ligne
        bottom_controls_layout = QHBoxLayout() # Layout principal pour le bas

        # Partie gauche pour chemin et nom de fichier
        left_file_controls_layout = QGridLayout()
        self.output_path_button = QPushButton("Dossier ...")
        # Style sera appliqué plus bas avec les autres boutons
        self.output_path_button.clicked.connect(self.select_output_directory)
        self.output_path_display_label = QLabel("Dossier : output/") # Affichage du chemin
        self.output_path_display_label.setWordWrap(True)
        self.output_path_display_label.setMinimumWidth(200) # Réduit un peu pour faire de la place
        self.output_path_display_label.setStyleSheet("font-style: italic; color: #B0BEC5;")

        self.filename_label = QLabel("Nom du fichier :")
        self.filename_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.filename_entry = QLineEdit()
        self.filename_entry.setMinimumWidth(150) # Donne une largeur minimale
        self.filename_entry.setMaximumWidth(200)
        self.filename_entry.setText("workbook")        

        # Layout horizontal pour tous les contrôles de fichier
        file_controls_line_layout = QHBoxLayout()
        file_controls_line_layout.addWidget(self.output_path_button)
        file_controls_line_layout.addWidget(self.output_path_display_label)
        file_controls_line_layout.addWidget(self.filename_label)
        file_controls_line_layout.addWidget(self.filename_entry)
        file_controls_line_layout.addStretch(0) # Ajoute un peu d'espace extensible si nécessaire avant le stretch principal

        bottom_controls_layout.addLayout(left_file_controls_layout)
        bottom_controls_layout.addStretch(1) # Espace flexible pour pousser les boutons à droite

        # Styles pour les boutons (normal, désactivé, pressé)
        pdf_btn_style = """
            QPushButton {
                background-color: #FF7043;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 8px 20px; /* Taille réduite */
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
                padding: 8px 20px; /* Taille réduite */
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
        preview_btn_style = """
            QPushButton {
                background-color: #78909C; /* Blue Grey */
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 8px 15px; /* Taille réduite */
                border-radius: 8px;
            }
            QPushButton:disabled {
                background-color: #B0BEC5;
                color: #ECEFF1;
            }
            QPushButton:pressed {
                background-color: #546E7A;
            }
        """
        self.output_path_button.setStyleSheet(preview_btn_style) # Appliquer le style ici
        self.output_path_button.setMinimumWidth(100) # Pour que "Dossier..." soit visible
        left_file_controls_layout.addLayout(file_controls_line_layout, 0, 0, 1, 2) # Ajout du layout de ligne
        # Partie droite pour les boutons
        action_buttons_layout = QHBoxLayout()
        self.generate_pdf_button = QPushButton("Générer PDF")
        self.generate_pdf_button.setStyleSheet(pdf_btn_style)
        self.generate_pdf_button.clicked.connect(self.generate_pdf)
        action_buttons_layout.addWidget(self.generate_pdf_button)

        self.generate_word_button = QPushButton("Générer Word")
        self.generate_word_button.setStyleSheet(word_btn_style)
        self.generate_word_button.clicked.connect(self.generate_word)
        action_buttons_layout.addWidget(self.generate_word_button)

        self.preview_pdf_button = QPushButton("Prévisualiser PDF")
        self.preview_pdf_button.setStyleSheet(preview_btn_style)
        self.preview_pdf_button.clicked.connect(self.preview_pdf)
        action_buttons_layout.addWidget(self.preview_pdf_button)

        self.preview_word_button = QPushButton("Prévisualiser Word")
        self.preview_word_button.setStyleSheet(preview_btn_style)
        self.preview_word_button.clicked.connect(self.preview_word)
        action_buttons_layout.addWidget(self.preview_word_button)
        action_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        bottom_controls_layout.addLayout(action_buttons_layout)
        main_layout.addLayout(bottom_controls_layout)

        # Correction du style pour les QLineEdit (texte noir sur fond sombre)
        lineedit_style = "color: black; background-color: white; font-size: 14px; border-radius: 4px; padding: 2px 6px;"
        for le in [self.days_entry, self.enumerate_count, self.enumerate_digits, self.sort_count, self.sort_digits, self.sort_n_numbers,
                   self.addition_count, self.addition_digits, self.addition_decimals,
                   self.subtraction_count, self.subtraction_digits, self.subtraction_decimals,
                   self.multiplication_count, self.multiplication_digits, self.multiplication_decimals, # self.output_path_entry est retiré
                   self.division_count, self.division_digits, self.division_decimals, self.verbs_per_day_entry,
                   self.grammar_sentence_count, self.geo_ex_count, self.english_complete_count, self.english_relier_count, self.orthographe_ex_count,
                   self.filename_entry]:
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
            # Enumérer un nombre
            ('enumerate_count', self.enumerate_count, 'text'),
            ('enumerate_digits', self.enumerate_digits, 'text'),
            # Ranger les nombres
            ('sort_count', self.sort_count, 'text'),
            ('sort_digits', self.sort_digits, 'text'),
            ('sort_n_numbers', self.sort_n_numbers, 'text'),
            ('sort_type_croissant', self.sort_type_croissant, 'checked'),
            ('sort_type_decroissant', self.sort_type_decroissant, 'checked'),
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
            # Orthographe
            ('orthographe_ex_count', self.orthographe_ex_count, 'text'),
            ('orthographe_homophone_checkboxes', self.orthographe_homophone_checkboxes, 'checked_list'),
            #
            ('show_name_checkbox', self.show_name_checkbox, 'checked'),
            ('show_note_checkbox', self.show_note_checkbox, 'checked'),
            ('filename_entry', self.filename_entry, 'text'),
            ('selected_output_path', self, 'path_variable'), # Nouveau mode pour variable de chemin
            ('usual_verbs_checkbox', self.usual_verbs_checkbox, 'checked'),
            ('tense_checkboxes', self.tense_checkboxes, 'checked_list'),
            ('geo_ex_count', self.geo_ex_count, 'text'),
            ('geo_conv_type_checkboxes', self.geo_conv_type_checkboxes, 'checked_list'),
            ('conv_sens_direct', self.conv_sens_direct, 'checked'),
            ('conv_sens_inverse', self.conv_sens_inverse, 'checked'),
            # Anglais - phrases à compléter
            ('english_complete_count', self.english_complete_count, 'text'),
            ('english_type_simple', self.english_type_simple, 'checked'),
            ('english_type_complexe', self.english_type_complexe, 'checked'),
            # Anglais - jeux à relier
            ('english_relier_count', self.english_relier_count, 'text'),
            ('relier_count', self.relier_count, 'text'),
            # Encadrement
            ('encadrement_count', self.encadrement_count, 'text'),
            ('encadrement_digits', self.encadrement_digits, 'text'),
            ('encadrement_unite', self.encadrement_unite, 'checked'),
            ('encadrement_dizaine', self.encadrement_dizaine, 'checked'),
            ('encadrement_centaine', self.encadrement_centaine, 'checked'),
            ('encadrement_millier', self.encadrement_millier, 'checked'),
        ]
        self.load_config()

        self.days_entry.textChanged.connect(self.validate_days_entry)

        # --- Début des méthodes ---

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sortie", self.selected_output_path or os.getcwd())
        if directory:
            self.selected_output_path = os.path.normpath(directory) # Normaliser le chemin
            self.output_path_display_label.setText(f"Dossier de sortie : {directory}")
            self.output_path_display_label.setStyleSheet("font-style: normal; color: #E0E0E0;") # Style normal si chemin choisi
        elif not self.selected_output_path: # Si l'utilisateur annule et qu'aucun chemin n'était défini
            self.output_path_display_label.setText("Dossier de sortie : output/")
            self.output_path_display_label.setStyleSheet("font-style: italic; color: #B0BEC5;")


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
        self.preview_pdf_button.setEnabled(is_valid)
        self.preview_word_button.setEnabled(is_valid)

    def build_exercise_data(self):
        try:
            from exercise_data_builder import ExerciseDataBuilder
            from conjugation_generator import TENSES, VERBS
            from grammar_generator import get_random_phrases, get_random_transformation
            from conversion_generator import generate_conversion_exercises
            from anglais_generator import PHRASES_SIMPLES, PHRASES_COMPLEXES, MOTS_A_RELIER

            # Génération des exercices d'encadrement
            encadrement_count = self.get_int(self.encadrement_count, field_name="Encadrement - nombre d'exercices")
            encadrement_digits = self.get_int(self.encadrement_digits, field_name="Encadrement - chiffres par nombre")
            encadrement_types = []
            if self.encadrement_unite.isChecked():
                encadrement_types.append("unité")
            if self.encadrement_dizaine.isChecked():
                encadrement_types.append("dizaine")
            if self.encadrement_centaine.isChecked():
                encadrement_types.append("centaine")
            if self.encadrement_millier.isChecked():
                encadrement_types.append("millier")
            encadrement_exercises = {
                'count': encadrement_count,
                'digits': encadrement_digits,
                'types': encadrement_types
            }

            # Génération des exercices anglais (phrases à compléter + jeux à relier)
            from anglais_generator import generate_english_full_exercises
            english_types = self.get_selected_english_types()
            n_complete = self.get_int(self.english_complete_count)
            n_relier = self.get_int(self.english_relier_count)
            n_mots_reliés = self.get_int(self.relier_count)
            english_exercises = []
            n_days = self.get_int(self.days_entry)
            for _ in range(n_days):
                english_exercises.append(
                    generate_english_full_exercises(english_types, n_complete, n_relier, n_mots_reliés)
                )

            params = {
                # Enumérer un nombre
                'enumerate_count': self.get_int(self.enumerate_count, field_name="Enumérer - nombre d'exercices"),
                'enumerate_digits': self.get_int(self.enumerate_digits, field_name="Enumérer - chiffres par nombre"),
                # Ranger les nombres
                'sort_count': self.get_int(self.sort_count, field_name="Ranger - nombre d'exercices"),
                'sort_digits': self.get_int(self.sort_digits, field_name="Ranger - chiffres par nombre"),
                'sort_n_numbers': self.get_int(self.sort_n_numbers, field_name="Ranger - nombres à ranger"),
                'sort_type_croissant': self.sort_type_croissant.isChecked(),
                'sort_type_decroissant': self.sort_type_decroissant.isChecked(),
                'days': self.get_int(self.days_entry, field_name="Nombre de jours"),
                'relier_count': self.get_int(self.relier_count, field_name="Anglais - nombre de mots à relier"),
                'addition_count': self.get_int(self.addition_count, field_name="Addition - nombre de calculs"),
                'addition_digits': self.get_int(self.addition_digits, field_name="Addition - chiffres"),
                'addition_decimals': self.get_int(self.addition_decimals, field_name="Addition - décimales"),
                'subtraction_count': self.get_int(self.subtraction_count, field_name="Soustraction - nombre de calculs"),
                'subtraction_digits': self.get_int(self.subtraction_digits, field_name="Soustraction - chiffres"),
                'subtraction_decimals': self.get_int(self.subtraction_decimals, field_name="Soustraction - décimales"),
                'subtraction_negative': self.subtraction_negative_checkbox.isChecked(),
                'multiplication_count': self.get_int(self.multiplication_count, field_name="Multiplication - nombre de calculs"),
                'multiplication_digits': self.get_int(self.multiplication_digits, field_name="Multiplication - chiffres"),
                'multiplication_decimals': self.get_int(self.multiplication_decimals, field_name="Multiplication - décimales"),
                'division_count': self.get_int(self.division_count, field_name="Division - nombre de calculs"),
                'division_digits': self.get_int(self.division_digits, field_name="Division - chiffres"),
                'division_decimals': self.get_int(self.division_decimals, field_name="Division - décimales"),
                'division_reste': self.division_reste_checkbox.isChecked(),
                'conjugation_groups': [g for g, cb in zip([1,2,3], [self.group_1_checkbox, self.group_2_checkbox, self.group_3_checkbox]) if cb.isChecked()],
                'conjugation_usual': self.usual_verbs_checkbox.isChecked(),
                'TENSES': TENSES,
                'conjugation_tenses': [tense for tense, cb in zip(TENSES, self.tense_checkboxes) if cb.isChecked()],
                'verbs_per_day': self.get_int(self.verbs_per_day_entry, field_name="Verbes par jour"),
                'VERBS': VERBS,
                'grammar_sentence_count': self.get_int(self.grammar_sentence_count, field_name="Grammaire - nombre de phrases"),
                'grammar_types': [t for t, cb in zip(['intransitive', 'transitive_direct', 'transitive_indirect', 'ditransitive'], [self.intransitive_checkbox, self.transitive_direct_checkbox, self.transitive_indirect_checkbox, self.ditransitive_checkbox]) if cb.isChecked()],
                'grammar_transformations': [t.text() for t in self.transfo_checkboxes if t.isChecked()],
                'get_random_phrases': get_random_phrases,
                'get_random_transformation': get_random_transformation,
                'generate_conversion_exercises': generate_conversion_exercises,
                'geo_ex_count': self.get_int(self.geo_ex_count, field_name="Géométrie/mesures - nombre d'exercices"),
                'geo_types': self.get_selected_conversion_types(),
                'geo_senses': self.get_selected_conversion_senses(),
                'english_types': self.get_selected_english_types(),
                'PHRASES_SIMPLES': PHRASES_SIMPLES,
                'PHRASES_COMPLEXES': PHRASES_COMPLEXES,
                'MOTS_A_RELIER': MOTS_A_RELIER,
                # Anglais
                'english_complete_count': self.get_int(self.english_complete_count, field_name="Anglais - phrases à compléter - nombre d'exercices"),
                'english_relier_count': self.get_int(self.english_relier_count, field_name="Anglais - jeux à relier - nombre de jeux"),
                # Orthographe
                'orthographe_ex_count': self.get_int(self.orthographe_ex_count, field_name="Orthographe - nombre d'exercices"),
                'orthographe_homophones': [cb.text() for cb in self.orthographe_homophone_checkboxes if cb.isChecked()],
                # Encadrement
                'encadrement_exercises': encadrement_exercises,
            }
            result = ExerciseDataBuilder.build(params)
            result['encadrement_exercises'] = encadrement_exercises
            result['english_exercises'] = english_exercises
            return result
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
            output_directory = self.selected_output_path # Utilise le chemin stocké
            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"
            output_path = generate_workbook_pdf(
                data['days'], data['operations'], data['counts'], data['max_digits'],
                data['conjugations'], data['params_list'], data['grammar_exercises'],
                data['orthographe_exercises'],
                data['enumerate_exercises'], data['sort_exercises'],
                geo_exercises=data['geo_exercises'], english_exercises=data['english_exercises'],
                encadrement_exercises=data.get('encadrement_exercises'),
                header_text=header_text, show_name=show_name, show_note=show_note, filename=filename,
                output_dir_override=output_directory
            )
            if output_path and os.path.exists(output_path):
                print(f"PDF généré avec succès : {output_path}")
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
            output_directory = self.selected_output_path # Utilise le chemin stocké
            if not filename.lower().endswith(".docx"):
                filename += ".docx"
            output_path = generate_workbook_docx(
                data['days'], data['operations'], data['counts'], data['max_digits'],
                data['conjugations'], data['params_list'], data['grammar_exercises'],
                # Passer toutes les données d'exercices comme pour le PDF
                orthographe_exercises=data['orthographe_exercises'],
                enumerate_exercises=data['enumerate_exercises'],
                sort_exercises=data['sort_exercises'],
                geo_exercises=data['geo_exercises'], 
                english_exercises=data['english_exercises'],
                encadrement_exercises=data.get('encadrement_exercises'),
                header_text=header_text, show_name=show_name, show_note=show_note, filename=filename,
                output_dir_override=output_directory
            )
            if output_path and os.path.exists(output_path):
                print(f"Word généré avec succès : {output_path}")
        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite : {type(e).__name__} : {e}")
            traceback.print_exc()

    def preview_pdf(self):
        try:
            data = self.build_exercise_data()
            if data is None:
                return

            from pdf_generator import generate_workbook_pdf
            header_text = self.header_entry.text().strip()
            show_name = self.show_name_checkbox.isChecked()
            show_note = self.show_note_checkbox.isChecked()
            filename = self.filename_entry.text().strip() or "apercu_EduForge"
            output_directory = self.selected_output_path # Utiliser le chemin pour l'aperçu aussi
            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"

            output_path = generate_workbook_pdf(
                data['days'], data['operations'], data['counts'], data['max_digits'],
                data['conjugations'], data['params_list'], data['grammar_exercises'],
                data['orthographe_exercises'], data['enumerate_exercises'], data['sort_exercises'],
                geo_exercises=data['geo_exercises'], english_exercises=data['english_exercises'],
                encadrement_exercises=data.get('encadrement_exercises'),
                header_text=header_text, show_name=show_name, show_note=show_note, filename=filename,
                output_dir_override=output_directory
            )

            if output_path and os.path.exists(output_path):
                os.startfile(output_path)  # Ouvre le fichier avec l'application par défaut (Windows)
            else:
                print(f"Erreur : Fichier PDF non trouvé à {output_path} après la génération pour l'aperçu.")
        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite lors de la prévisualisation PDF : {type(e).__name__} : {e}")
            traceback.print_exc()

    def preview_word(self):
        try:
            data = self.build_exercise_data()
            if data is None:
                return
            from word_generator import generate_workbook_docx
            header_text = self.header_entry.text().strip()
            show_name = self.show_name_checkbox.isChecked()
            show_note = self.show_note_checkbox.isChecked()
            filename = self.filename_entry.text().strip() or "apercu_EduForge"
            output_directory = self.selected_output_path # Utiliser le chemin pour l'aperçu aussi
            if not filename.lower().endswith(".docx"):
                filename += ".docx"
            output_path = generate_workbook_docx(
                data['days'], data['operations'], data['counts'], data['max_digits'],
                data['conjugations'], data['params_list'], data['grammar_exercises'],
                orthographe_exercises=data['orthographe_exercises'],
                enumerate_exercises=data['enumerate_exercises'],
                sort_exercises=data['sort_exercises'],
                geo_exercises=data['geo_exercises'], 
                english_exercises=data['english_exercises'],
                encadrement_exercises=data.get('encadrement_exercises'),
                header_text=header_text, show_name=show_name, show_note=show_note, filename=filename,
                output_dir_override=output_directory)
            if output_path and os.path.exists(output_path):
                os.startfile(output_path) # Ouvre le fichier avec l'application par défaut (Windows)
            else:
                print(f"Erreur : Fichier Word non trouvé à {output_path} après la génération pour l'aperçu.")
        except InvalidFieldError as e:
            print(f"Veuillez entrer une valeur numérique valide pour : {e.field_name} (valeur saisie : '{e.value}')")
        except Exception as e:
            import traceback
            print(f"Une erreur s'est produite lors de la prévisualisation Word : {type(e).__name__} : {e}")
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
            elif mode == 'path_variable':
                config[name] = self.selected_output_path # Sauvegarde la variable directement
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
                elif mode == 'path_variable':
                    self.selected_output_path = config.get(name, None)
                    if self.selected_output_path:
                        self.output_path_display_label.setText(f"Dossier de sortie : {self.selected_output_path}")
                        self.output_path_display_label.setStyleSheet("font-style: normal; color: #E0E0E0;")
                    else:
                        self.output_path_display_label.setText("Dossier de sortie : output/")
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
        if self.english_type_simple.isChecked():
            types.append('simple')
        if self.english_type_complexe.isChecked():
            types.append('complexe')
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
    import os
    from PyQt6.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), "EduForge.ico")
    app = QApplication([])
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    app.exec()