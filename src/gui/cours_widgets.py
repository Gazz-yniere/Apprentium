# File: Python_Scripts/Apprentium/src/gui/cours_widgets.py
import os
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget, QMenu, QPushButton)
from PyQt6.QtCore import Qt, QUrl, QObject, pyqtSlot, pyqtSignal, QSize
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

    # NEW: Class to handle edit/save requests from JavaScript
    class EditHandler(QObject):
        # Signal to emit when content is updated, carrying index and new content
        edit_requested = pyqtSignal(str, str, int, str) # subject, level, lesson_index, new_content
        lesson_deleted = pyqtSignal(str, str, int) # NEW: subject, level, lesson_index

        def __init__(self, parent_view, subject, level, lesson_index):
            super().__init__()
            self.parent_view = parent_view
            self.subject = subject
            self.level = level
            self.lesson_index = lesson_index

        @pyqtSlot(str)
        def saveContent(self, new_content):
            """Slot called by JavaScript to save the edited content."""
            self.edit_requested.emit(self.subject, self.level, self.lesson_index, new_content)

        @pyqtSlot()
        def deleteLesson(self):
            """Slot called by JS to delete the lesson."""
            self.lesson_deleted.emit(self.subject, self.level, self.lesson_index)

    def __init__(self, cours_column_widget, subject, level, lesson_index, *args, **kwargs): # Add subject, level, lesson_index
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

        # NEW: 4. Create and register the object to handle edit/save requests
        self.edit_handler = self.EditHandler(self, subject, level, lesson_index)
        self.channel.registerObject("edit_handler_obj", self.edit_handler)
        self.edit_handler.lesson_deleted.connect(self.cours_column.lesson_deleted)
        
        self.page().loadFinished.connect(self._on_load_finished)
        self.page().setBackgroundColor(Qt.GlobalColor.transparent)

    def _on_load_finished(self, ok):
        if ok:
            # 5. Injecter le script qui se connecte au QWebChannel.
            # Ce script rend les objets Python accessibles globalement en JavaScript
            # et met en place le ResizeObserver.
            js_script = """
            // --- Global Helper Functions ---
            // Moved to global scope to be accessible by onclick attributes
            function formatDoc(command, value = null) {
                const contentDiv = document.querySelector('.lesson-content-editable');
                if (contentDiv && contentDiv.isContentEditable) {
                    document.execCommand(command, false, value);
                    contentDiv.focus();
                }
            }

            function changeBlockFormat(selectElement) {
                const value = selectElement.value;
                if (value) {
                    formatDoc('formatBlock', value);
                }
                selectElement.selectedIndex = 0; // Reset dropdown to default
            }

            function insertStyledBox(className) {
                const selection = window.getSelection();
                if (!selection.rangeCount) return;

                const range = selection.getRangeAt(0);
                const selectedText = selection.toString();
                
                const box = document.createElement('div');
                box.className = className;
                
                const p = document.createElement('p');
                if (selectedText) {
                    p.textContent = selectedText;
                    range.deleteContents();
                } else {
                    p.innerHTML = 'Votre texte ici...';
                }
                box.appendChild(p);
                range.insertNode(box);
            }

            // --- Main Logic ---
            var print_handler_obj;
            var edit_handler_obj;
            var originalContent = ''; // To store content for cancellation

            new QWebChannel(qt.webChannelTransport, function(channel) {
                // Assign channel objects
                var height_reporter = channel.objects.height_reporter_obj;
                print_handler_obj = channel.objects.print_handler_obj;
                edit_handler_obj = channel.objects.edit_handler_obj;

                const wrapper = document.getElementById('content-wrapper');
                if (wrapper) {
                    const resizeObserver = new ResizeObserver(entries => {
                        // Use scrollHeight for a more reliable total height calculation, including margins and overflow.
                        // Add a small buffer to prevent scrollbars from appearing due to sub-pixel rendering.
                        height_reporter.setHeight(wrapper.scrollHeight + 20);
                    });
                    resizeObserver.observe(wrapper);
                }

                // --- Event Listeners Setup ---
                const editButton = document.querySelector('.edit-button-html');
                const cancelButton = document.querySelector('.cancel-button-html');
                const contentDiv = document.querySelector('.lesson-content-editable');
                const savedNotification = document.querySelector('.saved-notification');
                const editToolbar = document.querySelector('.edit-toolbar');
                const deleteButton = document.querySelector('.delete-button-html');

                if (editButton && cancelButton && contentDiv && editToolbar && deleteButton) {
                    // EDIT/SAVE button
                    editButton.addEventListener('click', function() {
                        const isEditing = contentDiv.isContentEditable;

                        if (isEditing) {
                            // --- SAVE ---
                            contentDiv.contentEditable = false;
                            editToolbar.style.display = 'none';
                            cancelButton.style.display = 'none';
                            editButton.textContent = '✏️ Éditer';
                            editButton.classList.remove('save-button-html');
                            editButton.classList.add('edit-button-html');

                            const updatedContent = contentDiv.innerHTML;
                            edit_handler_obj.saveContent(updatedContent);

                            // Show saved notification
                            savedNotification.style.opacity = '1';
                            savedNotification.style.transform = 'translateY(0)';
                            setTimeout(() => {
                                savedNotification.style.opacity = '0';
                                savedNotification.style.transform = 'translateY(-10px)';
                            }, 2000);
                        } else {
                            // --- START EDIT ---
                            originalContent = contentDiv.innerHTML;
                            contentDiv.contentEditable = true;
                            editToolbar.style.display = 'flex';
                            cancelButton.style.display = 'inline-block';
                            contentDiv.focus();
                            editButton.textContent = '💾 Enregistrer';
                            editButton.classList.remove('edit-button-html');
                            editButton.classList.add('save-button-html');
                        }
                    });

                    // CANCEL button
                    cancelButton.addEventListener('click', function() {
                        contentDiv.innerHTML = originalContent;
                        contentDiv.contentEditable = false;
                        editToolbar.style.display = 'none';
                        cancelButton.style.display = 'none';
                        editButton.textContent = '✏️ Éditer';
                        editButton.classList.remove('save-button-html');
                        editButton.classList.add('edit-button-html');
                    });

                    // DELETE button
                    deleteButton.addEventListener('click', function() {
                        confirmDialog.style.display = 'flex';
                    });

                    // --- Custom Confirmation Dialog Logic ---
                    const confirmDialog = document.querySelector('.confirm-dialog-overlay');
                    const confirmBtn = document.querySelector('.dialog-confirm-btn');
                    const cancelDialogBtn = document.querySelector('.dialog-cancel-btn');

                    // CONFIRM button in dialog
                    confirmBtn.addEventListener('click', function() {
                        if (edit_handler_obj) {
                            edit_handler_obj.deleteLesson();
                        }
                        confirmDialog.style.display = 'none';
                    });

                    // CANCEL button in dialog or clicking the overlay
                    [cancelDialogBtn, confirmDialog].forEach(el => {
                        el.addEventListener('click', function(e) {
                            if (e.target === el) { // Ensure we're not clicking on a child element for the overlay
                                confirmDialog.style.display = 'none';
                            }
                        });
                    });

                    // --- Custom Tooltip Logic ---
                    const tooltip = document.getElementById('custom-tooltip');
                    if (tooltip) {
                        document.querySelectorAll('[data-title]').forEach(elem => {
                            elem.addEventListener('mousemove', e => {
                                tooltip.style.left = e.pageX + 15 + 'px';
                                tooltip.style.top = e.pageY + 15 + 'px';
                            });
                            elem.addEventListener('mouseenter', e => {
                                tooltip.innerHTML = elem.getAttribute('data-title');
                                tooltip.style.display = 'block';
                            });
                            elem.addEventListener('mouseleave', e => {
                                tooltip.style.display = 'none';
                            });
                        });
                    }
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
    # NEW: Signal to notify the main window about a lesson update
    lesson_updated = pyqtSignal(str, str, int, str) # subject, level, lesson_index, new_content
    lesson_deleted = pyqtSignal(str, str, int) # NEW: For lesson deletion
    new_lesson_requested = pyqtSignal(str, str) # NEW: For creating a new lesson

    def __init__(self, parent_window, UI_STYLE_CONFIG, title, content_data_by_level, color_key):
        super().__init__()
        self.parent_window = parent_window
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG
        self.title = title
        self.content_data_by_level = content_data_by_level
        self.color_key = color_key
        self.cours_css_content = ""
        self.current_level = None # Store the current level

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
        self.current_level = level # Store the current level

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
            
            # Afficher le titre de la matière et le bouton "Nouveau Cours" si le niveau est défini pour cette matière
            if level in subject_data:
                any_lesson_found = True # Une section de matière est considérée comme "trouvée"

                # --- Header for the subject section (Title + New Lesson Button) ---
                header_widget = QWidget()
                header_layout = QHBoxLayout(header_widget)
                header_layout.setContentsMargins(0, 0, 0, 0)
                header_layout.setSpacing(10)

                subject_color = subject_colors.get(subject, '#FFFFFF')
                display_name = subject_display_names.get(subject, subject.capitalize())
                subject_title_label = QLabel(f"<h2>{display_name}</h2>")
                subject_title_label.setTextFormat(Qt.TextFormat.RichText)
                subject_title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {subject_color}; margin-top: 15px; margin-bottom: 5px; border-bottom: 2px solid {subject_color}; padding-bottom: 3px;")
                header_layout.addWidget(subject_title_label)

                header_layout.addStretch(1) # Pushes the button to the right

                # NEW: Add "New Lesson" button
                new_lesson_button = QPushButton("➕ Nouveau Cours")
                new_lesson_button.setStyleSheet("""
                    QPushButton {
                        background-color: #34495E;
                        color: #ECF0F1;
                        border: 1px solid #4A6572;
                        padding: 5px 10px;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #4A6572;
                    }
                """)
                new_lesson_button.setCursor(Qt.CursorShape.PointingHandCursor)
                # Utiliser une lambda pour passer les arguments au slot
                new_lesson_button.clicked.connect(lambda checked, s=subject, l=level: self.new_lesson_requested.emit(s, l))
                header_layout.addWidget(new_lesson_button)

                target_layout.addWidget(header_widget)

                lessons_for_level = subject_data.get(level, [])
                for lesson_index, lesson in enumerate(lessons_for_level):
                    # Récupérer le contenu brut de la leçon
                    raw_lesson_content = lesson.get('content', '')

                    # Déterminer la classe de couleur de fond en alternance
                    if lesson_index % 2 == 0:
                        subject_bg_class = f"lesson-card-bg-{subject}"
                    else:
                        subject_bg_class = f"lesson-card-bg-{subject}-alt"

                    # Définir le HTML pour les boutons
                    confirm_dialog_html = """
                    <div class="confirm-dialog-overlay">
                        <div class="confirm-dialog-box">
                            <p class="confirm-dialog-title">Confirmation de suppression</p>
                            <p class="confirm-dialog-text">Êtes-vous sûr de vouloir supprimer ce cours ?</p>
                            <p class="confirm-dialog-subtext">Cette action est irréversible.</p>
                            <div class="confirm-dialog-buttons">
                                <button class="dialog-cancel-btn">Annuler</button>
                                <button class="dialog-confirm-btn">Confirmer</button>
                            </div>
                        </div>
                    </div>
                    """
                    edit_toolbar_html = """
                    <div class="edit-toolbar">
                        <select onchange="changeBlockFormat(this)" data-title="Style de texte">
                            <option value="" disabled selected>Style</option>
                            <option value="h2">Titre 1</option>
                            <option value="h3">Titre 2</option>
                            <option value="h4">Titre 3</option>
                            <option value="p">Paragraphe</option>
                        </select>
                        <button type="button" onclick="formatDoc('bold');" data-title="Gras"><b>B</b></button>
                        <button type="button" onclick="formatDoc('italic');" data-title="Italique"><i>I</i></button>
                        <button type="button" onclick="formatDoc('underline');" data-title="Souligné"><u>U</u></button>
                        <button type="button" onclick="formatDoc('insertUnorderedList');" data-title="Liste à puces">●</button>
                        <button type="button" onclick="formatDoc('insertOrderedList');" data-title="Liste numérotée">1.</button>
                        <span class="toolbar-separator"></span>
                        <label for="font-color" class="color-label" data-title="Couleur du texte">A</label>
                        <input type="color" id="font-color" oninput="formatDoc('foreColor', this.value)" value="#ffffff">
                        <label for="bg-color" class="color-label" data-title="Couleur de surlignage">S</label>
                        <input type="color" id="bg-color" oninput="formatDoc('hiliteColor', this.value)" value="#3a3a3a">
                        <span class="toolbar-separator"></span>
                        <button type="button" onclick="insertStyledBox('memo-box')" data-title="Insérer un cadre Mémo">📝</button>
                        <button type="button" onclick="insertStyledBox('info-box')" data-title="Insérer un cadre Info">ℹ️</button>
                    </div>
                    """

                    buttons_html = f"""
                    <div class="lesson-buttons">
                        <div class="button-group-left">
                            <button class="edit-button-html" data-title="Éditer le cours">✏️ Éditer</button>
                            <button class="cancel-button-html" data-title="Annuler les modifications">Annuler</button>
                            <button class="print-button-html" onclick="print_handler_obj.requestPrint()" data-title="Imprimer le cours">🖨️ Imprimer</button>
                        </div>
                        <div class="button-group-right">
                            <button class="delete-button-html" data-title="Supprimer le cours">🗑️ Supprimer</button>
                        </div>
                        <div class="saved-notification">Sauvegardé !</div>
                    </div>
                    """

                    # Create the QWebEngineView for a full HTML/CSS rendering
                    # Pass lesson_index to AutoResizingWebEngineView
                    lesson_content_view = AutoResizingWebEngineView(self, subject, level, lesson_index)
                    
                    # Connect the edit_requested signal from the specific AutoResizingWebEngineView
                    lesson_content_view.edit_handler.edit_requested.connect(self.lesson_updated)
                    # The delete signal is connected inside AutoResizingWebEngineView's __init__

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

                                /* Style pour les boutons de leçon */
                                .lesson-card {{
                                    position: relative; /* Nécessaire pour positionner les boutons */
                                    margin-bottom: 20px; /* Pour éviter les barres de défilement */   
                                }}
                                .lesson-header {{
                                    padding: 15px 15px 5px 15px;
                                }}
                                .lesson-buttons {{
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;
                                    z-index: 10;
                                    margin-bottom: 10px;
                                }}
                                .button-group-left, .button-group-right {{
                                    display: flex;
                                    gap: 10px;
                                }}
                                .lesson-buttons button {{
                                    color: white;
                                    border: none;
                                    padding: 5px 10px;
                                    border-radius: 5px;
                                    font-weight: bold;
                                    cursor: pointer;
                                    transition: background-color 0.3s;
                                }}
                                .print-button-html {{
                                    background-color: #3498DB; /* Bleu */
                                }}
                                .print-button-html:hover {{ background-color: #2980B9; }}
                                
                                /* NEW: Style for the Save button */
                                .save-button-html {{
                                    background-color: #2ECC71; /* Vert */
                                }}
                                .save-button-html:hover {{ background-color: #27AE60; }}

                                .edit-button-html {{
                                    background-color: #F39C12; /* Orange */
                                }}
                                .edit-button-html:hover {{ background-color: #E67E22; }}

                                /* NEW: Style for the Cancel button */
                                .cancel-button-html {{
                                    display: none; /* Hidden by default */
                                    background-color: #E74C3C; /* Rouge */
                                }}
                                .cancel-button-html:hover {{
                                    background-color: #C0392B;
                                }}
                                .delete-button-html {{
                                    background-color: #C0392B; /* Rouge foncé */
                                }}
                                .delete-button-html:hover {{
                                    background-color: #A93226;
                                }}
                                /* NEW: Style for the saved notification */
                                .saved-notification {{
                                    position: absolute;
                                    top: 0;
                                    left: 50%;
                                    transform: translateX(-50%) translateY(-10px);
                                    background-color: #28a745; /* Green background */
                                    color: white;
                                    padding: 3px 8px;
                                    border-radius: 4px;
                                    font-size: 12px;
                                    opacity: 0;
                                    transition: opacity 0.3s ease-out, transform 0.3s ease-out;
                                    pointer-events: none; /* Allow clicks to pass through */
                                    white-space: nowrap; /* Prevent wrapping */
                                }}

                                /* Style for the editable content area */
                                .lesson-content-editable {{
                                    min-height: 50px; /* Ensure a minimum height for editing */
                                    outline: 2px solid transparent; /* Reserve space for focus outline to prevent layout shift */
                                    border-radius: 5px;
                                    transition: outline-color 0.2s ease-in-out;
                                }}
                                .lesson-content-editable[contenteditable="true"]:focus {{
                                    outline-color: #3498DB; /* Show blue outline only on focus when editable */
                                }}

                                /* Style for the edit toolbar */
                                .edit-toolbar {{
                                    display: none; /* Hidden by default */
                                    flex-wrap: wrap;
                                    padding: 5px;
                                    background-color: #2C3E50; /* Match window background */
                                    border-radius: 5px;
                                    margin-bottom: 10px;
                                    border: 1px solid #444;
                                }}
                                .edit-toolbar button, .edit-toolbar select {{
                                    background-color: #505050; /* Match app buttons */
                                    min-width: 30px;
                                    margin: 2px;
                                    color: white;
                                    border: 1px solid #5A5A5A;
                                    border-radius: 3px;
                                    padding: 2px 5px;
                                    cursor: pointer;
                                }}
                                .edit-toolbar select option {{
                                    background-color: #505050;
                                    cursor: pointer;
                                }}
                                .edit-toolbar button:hover, .edit-toolbar select:hover {{
                                    background-color: #3498DB;
                                    border-color: #2980B9;
                                }}
                                .edit-toolbar input[type="color"] {{
                                    padding: 0;
                                    width: 26px; /* Adjusted for border */
                                    height: 22px; /* Adjusted for border */
                                    border: 1px solid #7F8C8D; /* Add a border to make it visible */
                                    vertical-align: middle;
                                    border-radius: 4px;
                                    margin: 2px;
                                    cursor: pointer;
                                }}
                                .edit-toolbar .color-label {{
                                    padding: 0 5px;
                                    font-weight: bold;
                                    vertical-align: middle;
                                    cursor: pointer;
                                }}
                                .toolbar-separator {{
                                    border-left: 1px solid #666;
                                    margin: 2px 5px;
                                }}
                                .info-box {{
                                    background-color: rgba(52, 152, 219, 0.1);
                                    border-left: 4px solid #3498DB;
                                    padding: 10px 15px;
                                    margin: 10px 0;
                                }}
                                /* Fix for lists not showing bullets/numbers */
                                .lesson-content-editable ul, .lesson-content-editable ol {{
                                    padding-left: 40px;
                                }}

                                /* NEW: Custom Confirmation Dialog Styles */
                                .confirm-dialog-overlay {{
                                    display: none; /* Hidden by default */
                                    position: fixed; /* Cover the whole screen */
                                    top: 0;
                                    left: 0;
                                    width: 100%;
                                    height: 100%;
                                    background-color: rgba(0, 0, 0, 0.7);
                                    z-index: 10000;
                                    justify-content: center;
                                    align-items: center;
                                }}
                                .confirm-dialog-box {{
                                    background-color: #2C3E50; /* Match app theme */
                                    padding: 25px;
                                    border-radius: 8px;
                                    border: 1px solid #34495E;
                                    box-shadow: 0 5px 15px rgba(0,0,0,0.5);
                                    text-align: center;
                                    max-width: 400px;
                                    color: #ECF0F1;
                                }}
                                .confirm-dialog-title {{
                                    font-size: 18px;
                                    font-weight: bold;
                                    margin-top: 0;
                                    margin-bottom: 10px;
                                }}
                                .confirm-dialog-text {{
                                    font-size: 14px;
                                    margin-bottom: 5px;
                                }}
                                .confirm-dialog-subtext {{
                                    font-size: 12px;
                                    color: #BDC3C7;
                                    margin-bottom: 20px;
                                }}
                                .confirm-dialog-buttons {{
                                    display: flex;
                                    justify-content: center;
                                    gap: 15px;
                                }}
                                .dialog-cancel-btn, .dialog-confirm-btn {{
                                    padding: 8px 16px;
                                    border: none;
                                    border-radius: 5px;
                                    font-weight: bold;
                                    cursor: pointer;
                                    transition: background-color 0.2s;
                                }}
                                .dialog-cancel-btn {{
                                    background-color: #505050;
                                    color: white;
                                }}
                                .dialog-cancel-btn:hover {{
                                    background-color: #616161;
                                }}
                                .dialog-confirm-btn {{
                                    background-color: #E74C3C; /* Red for destructive action */
                                    color: white;
                                }}
                                .dialog-confirm-btn:hover {{
                                    background-color: #C0392B;
                                }}

                                /* NEW: Custom Tooltip Style */
                                .custom-tooltip {{
                                    display: none;
                                    position: absolute;
                                    z-index: 9999;
                                    background-color: #222222;
                                    color: #ECF0F1;
                                    border: 1px solid #34495E;
                                    border-radius: 4px;
                                    padding: 5px 8px;
                                    font-size: 12px;
                                    white-space: nowrap;
                                    pointer-events: none; /* So it doesn't interfere with mouse events */
                                }}

                                /* --- Contenu injecté depuis cours_style.css --- */
                                {self.cours_css_content}

                                /* --- STYLES SPÉCIFIQUES POUR L'IMPRESSION --- */
                                @media print {{
                                    .lesson-buttons {{ display: none !important; }}
                                    .saved-notification {{ display: none !important; }}
                                    .delete-button-html {{ display: none !important; }}
                                    .cancel-button-html {{ display: none !important; }}
                                    .edit-toolbar {{ display: none !important; }}
                                    /* Forcer le moteur de rendu à utiliser les couleurs de fond spécifiées */
                                    -webkit-print-color-adjust: exact;

                                    /* Reset général pour l'impression : fond blanc, texte noir */
                                    body, html {{
                                        background: #FFFFFF !important;
                                        color: #000000 !important;
                                        font-size: 10pt !important; /* Réduire la taille de la police */
                                        line-height: 1.4 !important; /* Ajuster la hauteur de ligne */
                                    }}
                                    body {{
                                        zoom: 0.85; /* Réduire l'ensemble du contenu */
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
                            <div id="custom-tooltip" class="custom-tooltip"></div>
                            {confirm_dialog_html}
                            <div id="content-wrapper" class="lesson-card {subject_bg_class}">
                                <div class="lesson-header">
                                    {buttons_html}
                                    {edit_toolbar_html}
                                </div>
                                <div class="lesson-content-editable">
                                    {raw_lesson_content}
                                </div>
                            </div>
                        </body>
                    </html>"""

                    lesson_content_view.setHtml(full_html, QUrl("qrc:/"))
                    lesson_content_view.setMinimumHeight(30) # Hauteur minimale pendant le chargement

                    # Ajouter la vue web directement à la colonne, sans QFrame supplémentaire
                    target_layout.addWidget(lesson_content_view)

        if not any_lesson_found:
            no_lesson_label = QLabel(f"<h3>Pas de cours pour le niveau {level}</h3><p>Le contenu pour ce niveau n'a pas encore été ajouté.</p>")
            no_lesson_label.setWordWrap(True)
            no_lesson_label.setTextFormat(Qt.TextFormat.RichText)
            no_lesson_label.setStyleSheet("font-size: 14px; color: #E0E0E0; background-color: #2C2C2C; border-radius: 8px; padding: 10px; margin-bottom: 10px;")
            no_lesson_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.left_column_layout.addWidget(no_lesson_label) # Ajouter à la colonne de gauche