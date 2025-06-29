import os
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget, QMenu, QPushButton)
from PyQt6.QtCore import Qt, QUrl, QObject, pyqtSlot
from PyQt6.QtGui import QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

class HeightReporter(QObject):
    """
    Objet Python exposé à JavaScript pour rapporter la hauteur du contenu.
    """
    def __init__(self, view_to_resize):
        super().__init__()
        self._view = view_to_resize

    @pyqtSlot(float)
    def setHeight(self, height):
        """
        Slot appelé par JavaScript pour mettre à jour la hauteur du widget.
        """
        if self._view and height is not None and height > 0:
            # On ajoute 1 pixel pour éviter l'apparition d'une barre de défilement
            # due à des arrondis de sous-pixels.
            self._view.setFixedHeight(int(height) + 1)

class AutoResizingWebEngineView(QWebEngineView):
    """
    Un QWebEngineView qui se redimensionne automatiquement en hauteur
    en fonction de son contenu, en utilisant un ResizeObserver pour une détection fiable.
    """
    # Classe interne pour gérer les appels depuis JavaScript
    class PrintHandler(QObject):
        def __init__(self, parent_view):
            super().__init__()
            self.parent_view = parent_view

        @pyqtSlot()
        def requestPrint(self):
            """Slot appelé par le bouton 'Imprimer' en HTML pour déclencher la boîte de dialogue d'impression."""
            if self.parent_view and self.parent_view.cours_column:
                self.parent_view.cours_column._handle_print_request(self.parent_view)

    def __init__(self, cours_column_widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cours_column = cours_column_widget # Garder une référence au widget parent

        # 1. Mettre en place le canal de communication entre Python et JavaScript
        self.channel = QWebChannel(self.page())
        self.page().setWebChannel(self.channel)

        # 2. Créer et enregistrer l'objet qui recevra la hauteur depuis JavaScript
        self.height_reporter = HeightReporter(self)
        self.channel.registerObject("height_reporter_obj", self.height_reporter)

        # 3. Créer et enregistrer l'objet qui gérera les demandes d'impression
        self.print_handler = self.PrintHandler(self)
        self.channel.registerObject("print_handler_obj", self.print_handler)

        self.page().loadFinished.connect(self._on_load_finished)
        self.page().setBackgroundColor(Qt.GlobalColor.transparent)

    def _on_load_finished(self, ok):
        if ok:
            # 4. Injecter le script qui se connecte au QWebChannel.
            # Ce script rend les objets Python accessibles globalement en JavaScript
            # et met en place le ResizeObserver.
            js_script = """
            var print_handler_obj; // Déclarer la variable dans la portée globale
            new QWebChannel(qt.webChannelTransport, function(channel) {
                // Assigner les objets Python aux variables JavaScript
                var height_reporter = channel.objects.height_reporter_obj;
                print_handler_obj = channel.objects.print_handler_obj;

                const wrapper = document.getElementById('content-wrapper');
                if (wrapper) {
                    const resizeObserver = new ResizeObserver(entries => {
                        height_reporter.setHeight(entries[0].contentRect.height);
                    });
                    resizeObserver.observe(wrapper);
                }
            });
            """
            self.page().runJavaScript(js_script)

    def contextMenuEvent(self, event):
        """
        Crée et affiche un menu contextuel personnalisé avec un thème sombre.
        """
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2C3E50; /* Fond sombre */
                color: #ECF0F1; /* Texte clair */
                border: 1px solid #34495E;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 25px 5px 20px;
                border: 1px solid transparent; /* Pour l'effet de survol */
            }
            QMenu::item:selected {
                background-color: #3498DB; /* Couleur de survol/sélection */
                color: #FFFFFF;
            }
            QMenu::separator {
                height: 1px;
                background: #34495E;
                margin-left: 10px;
                margin-right: 5px;
            }
        """)

        page = self.page()
        menu.addAction(page.action(page.WebAction.Copy))
        menu.addAction(page.action(page.WebAction.Paste))
        menu.addSeparator()
        menu.addAction(page.action(page.WebAction.InspectElement)) # Très utile pour le développement
        menu.exec(event.globalPos())

class CoursColumn(QFrame):
    """
    Un widget générique pour afficher une colonne de cours avec un titre et un contenu.
    Le contenu est mis à jour en fonction du niveau sélectionné.
    """
    def __init__(self, parent_window, UI_STYLE_CONFIG, title, content_data_by_level, color_key):
        super().__init__()
        self.parent_window = parent_window
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG
        self.title = title
        self.content_data_by_level = content_data_by_level
        self.color_key = color_key
        self.cours_css_content = ""

        self._load_cours_css()
        self._setup_ui()

    def _handle_print_request(self, web_view):
        """Ouvre la boîte de dialogue d'impression pour le contenu web spécifié."""
        # On attache l'instance de QPrinter et QPrintDialog directement au web_view pour garantir
        # que leur durée de vie est liée à l'opération d'impression de ce widget spécifique.
        # Cela évite les conflits et les avertissements de destruction prématurée.
        web_view.printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        # Il est préférable de parenter la boîte de dialogue à la fenêtre principale.
        web_view.print_dialog = QPrintDialog(web_view.printer, self.parent_window)
        if web_view.print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
            # En PyQt6, la méthode print() est sur la vue (QWebEngineView).
            # Elle ne prend plus de fonction de rappel (callback) comme en PyQt5.
            # L'impression est envoyée directement au système.
            web_view.print(web_view.printer)

    def _load_cours_css(self):
        """Charge le contenu du fichier CSS pour les leçons."""
        try:
            # Construit un chemin robuste vers le fichier CSS depuis l'emplacement de ce script
            current_dir = os.path.dirname(__file__)
            # Le chemin relatif pour aller de 'src/gui' à 'src/css'
            css_path = os.path.join(current_dir, '..', 'css', 'cours_style.css')
            with open(css_path, 'r', encoding='utf-8') as f:
                self.cours_css_content = f.read()
        except FileNotFoundError:
            print(f"Avertissement : Le fichier CSS '{css_path}' n'a pas été trouvé.")
            self.cours_css_content = ""

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 5) # Marge supérieure de 10px pour l'aération
        layout.setSpacing(10)

        # ScrollArea pour le contenu des cours
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")

        # Widget conteneur principal pour le contenu qui sera dans le ScrollArea
        self.content_container = QWidget()
        # Layout horizontal principal pour les deux colonnes
        main_content_layout = QHBoxLayout(self.content_container)
        main_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_content_layout.setSpacing(20)  # Espace entre les colonnes

        # Colonne de gauche
        left_column_widget = QWidget()
        self.left_column_layout = QVBoxLayout(left_column_widget)
        self.left_column_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_content_layout.addWidget(left_column_widget, 1)  # Facteur d'étirement 1

        # Colonne de droite
        right_column_widget = QWidget()
        self.right_column_layout = QVBoxLayout(right_column_widget)
        self.right_column_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_content_layout.addWidget(right_column_widget, 1)  # Facteur d'étirement 1

        # Appliquer le style de la barre de défilement
        scrollbar_style = self.UI_STYLE_CONFIG["scroll_bar"]["style_template"].format(
            **self.UI_STYLE_CONFIG["scroll_bar"]["values"]
        )
        scroll_area.setStyleSheet(scrollbar_style)
        scroll_area.setWidget(self.content_container)
        layout.addWidget(scroll_area)

    def get_title_widget(self):
        return self.title_label

    def update_content(self, level):
        """Met à jour le contenu affiché en fonction du niveau."""
        # 1. Nettoyer l'ancien contenu des deux colonnes
        for layout in [self.left_column_layout, self.right_column_layout]:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # 2. Construire le nouveau contenu
        if not level:
            placeholder_label = QLabel("<h3>Sélectionnez un niveau</h3><p>Choisissez un niveau ci-dessus pour afficher les leçons correspondantes.</p>")
            placeholder_label.setWordWrap(True)
            placeholder_label.setTextFormat(Qt.TextFormat.RichText)
            placeholder_label.setStyleSheet("font-size: 14px; color: #E0E0E0; background-color: #2C2C2C; border-radius: 8px; padding: 10px; margin-bottom: 10px;")
            placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.left_column_layout.addWidget(placeholder_label) # Ajouter à la colonne de gauche
            return

        subject_colors = self.UI_STYLE_CONFIG['labels']['column_title_colors']
        any_lesson_found = False
        
        # Dictionnaire pour mapper les clés de sujet aux noms d'affichage corrects
        subject_display_names = {
            'calc': 'Calculs',
            'geo': 'Mesures',
            'conj': 'Conjugaison',
            'grammar': 'Grammaire',
            'ortho': 'Orthographe',
            'english': 'Anglais'
        }

        subject_order = ['calc', 'geo', 'conj', 'grammar', 'ortho', 'english']
        
        # Répartir les matières dans les deux colonnes
        num_subjects = len(subject_order)
        mid_point = (num_subjects + 1) // 2 # Pour gérer les nombres impairs

        for i, subject in enumerate(subject_order):
            target_layout = self.left_column_layout if i < mid_point else self.right_column_layout
            if subject not in self.content_data_by_level:
                continue
            
            subject_data = self.content_data_by_level[subject]
            lessons_for_level = subject_data.get(level, [])
            
            if lessons_for_level:
                any_lesson_found = True
                
                subject_color = subject_colors.get(subject, '#FFFFFF')
                display_name = subject_display_names.get(subject, subject.capitalize())
                subject_title_label = QLabel(f"<h2>{display_name}</h2>")
                subject_title_label.setTextFormat(Qt.TextFormat.RichText)
                subject_title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {subject_color}; margin-top: 15px; margin-bottom: 5px; border-bottom: 2px solid {subject_color}; padding-bottom: 3px;")
                target_layout.addWidget(subject_title_label)
                
                for lesson_index, lesson in enumerate(lessons_for_level):
                    # Créer un QFrame pour servir de conteneur au bloc de cours
                    lesson_frame = QFrame()
                    # Appliquer le style avec la bordure colorée
                    lesson_frame.setStyleSheet(f"""
                        QFrame {{
                            background-color: #2C2C2C;
                            border: 1px solid {subject_color};
                            border-radius: 10px;
                            margin-bottom: 10px;
                        }}
                    """)
                    frame_layout = QVBoxLayout(lesson_frame)
                    # Padding intérieur symétrique pour un meilleur aspect.
                    frame_layout.setContentsMargins(10, 10, 10, 10)

                    # Préparer le contenu de la leçon
                    lesson_html_content = lesson.get('content', '')

                    # Ajouter dynamiquement la classe de couleur de fond basée sur la matière.
                    # On alterne la couleur pour une meilleure lisibilité.
                    if lesson_index % 2 == 0:
                        subject_bg_class = f"lesson-card-bg-{subject}"
                    else:
                        subject_bg_class = f"lesson-card-bg-{subject}-alt"

                    lesson_html_content = lesson_html_content.replace(
                        'class="lesson-card"',
                        f'class="lesson-card {subject_bg_class}"',
                        1
                    )
                    button_html = '<button class="print-button-html" onclick="print_handler_obj.requestPrint()">🖨️ Imprimer</button>'
                    
                    # Injecte le bouton juste après la balise ouvrante <div class="lesson-card...">
                    insertion_point = lesson_html_content.find('>')
                    if insertion_point != -1:
                        lesson_html_content = lesson_html_content[:insertion_point+1] + button_html + lesson_html_content[insertion_point+1:]

                    # Créer le QWebEngineView pour un rendu HTML/CSS complet
                    full_html = f"""
                    <html>
                        <head>
                            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
                            <style>
                                /* Styles pour l'intégration QWebEngineView */
                                html, body {{
                                    background-color: transparent;
                                    margin: 0;
                                    padding: 0;
                                    overflow: hidden; /* Empêche la barre de défilement du navigateur */
                                }}
                                #content-wrapper {{
                                    width: 100%;
                                    padding-top: 1px;
                                    margin-top: -1px;                                    
                                }}

                                /* Style pour le bouton d'impression HTML */
                                .lesson-card {{
                                    position: relative; /* Nécessaire pour positionner le bouton */
                                    margin-bottom: 20px; /* Pour éviter les barres de défilement */   
                                }}
                                .print-button-html {{
                                    position: absolute;
                                    top: 15px;
                                    right: 15px;
                                    background-color: #3498DB;
                                    color: white;
                                    border: none;
                                    padding: 5px 10px;
                                    border-radius: 5px;
                                    font-weight: bold;
                                    cursor: pointer;
                                    transition: background-color 0.3s;
                                    z-index: 10;
                                }}
                                .print-button-html:hover {{ background-color: #2980B9; }}

                                /* --- Contenu injecté depuis cours_style.css --- */
                                {self.cours_css_content}

                                /* --- STYLES SPÉCIFIQUES POUR L'IMPRESSION --- */
                                @media print {{
                                    .print-button-html {{ display: none !important; }}
                                    /* Forcer le moteur de rendu à utiliser les couleurs de fond spécifiées */
                                    -webkit-print-color-adjust: exact;

                                    /* Reset général pour l'impression : fond blanc, texte noir */
                                    body, html {{
                                        background: #FFFFFF !important;
                                        color: #000000 !important;
                                    }}

                                    /* Retirer les ombres et forcer un fond blanc sur les conteneurs principaux */
                                    .lesson-card, .column-item {{
                                        background-color: #FFFFFF !important;
                                        box-shadow: none !important;
                                        border: none !important; /* Pas de bordure pour la carte de leçon dans le PDF */
                                        page-break-inside: avoid; /* Empêche les éléments d'être coupés entre deux pages */
                                    }}

                                    /* Style spécifique pour le mémo dans le PDF */
                                    .memo-box {{
                                        border: 3px solid #000000 !important; /* Bordure noire et plus épaisse pour le mémo */
                                        background-color: transparent !important;
                                    }}

                                    /* S'assurer que tous les textes sont noirs et sans effets d'ombre */
                                    h2, h3, h4, p, li, strong, em, span, a, cite, figcaption, td, th {{
                                        color: #000000 !important;
                                        text-shadow: none !important;
                                        background-color: transparent !important;
                                    }}

                                    /* Rendre les liens visibles sur papier */
                                    a {{
                                        text-decoration: underline !important;
                                    }}
                                }}
                            </style>
                        </head>
                        <body>
                            <div id="content-wrapper">
                                {lesson_html_content}
                            </div>
                        </body>
                    </html>"""

                    lesson_content = AutoResizingWebEngineView(self)
                    lesson_content.setHtml(full_html, QUrl("qrc:/"))
                    lesson_content.setMinimumHeight(30) # Hauteur minimale pendant le chargement

                    # Le contenu est ajouté en premier dans le layout vertical
                    frame_layout.addWidget(lesson_content)
                    target_layout.addWidget(lesson_frame)

        if not any_lesson_found:
            no_lesson_label = QLabel(f"<h3>Pas de cours pour le niveau {level}</h3><p>Le contenu pour ce niveau n'a pas encore été ajouté.</p>")
            no_lesson_label.setWordWrap(True)
            no_lesson_label.setTextFormat(Qt.TextFormat.RichText)
            no_lesson_label.setStyleSheet("font-size: 14px; color: #E0E0E0; background-color: #2C2C2C; border-radius: 8px; padding: 10px; margin-bottom: 10px;")
            no_lesson_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.left_column_layout.addWidget(no_lesson_label) # Ajouter à la colonne de gauche