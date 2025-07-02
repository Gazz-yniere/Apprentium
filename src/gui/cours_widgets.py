import os
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget, QMenu, QPushButton)
from PyQt6.QtCore import Qt, QUrl, QObject, pyqtSlot, pyqtSignal, QSize
from PyQt6.QtGui import QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

class HeightReporter(QObject):
    """
    Python object exposed to JavaScript to report content height.
    """
    def __init__(self, view_to_resize):
        super().__init__()
        self._view = view_to_resize

    @pyqtSlot(float)
    def setHeight(self, height):
        """
        Slot called by JavaScript to update the widget's height.
        """
        if height is not None and height > 0:
            # Add 1 pixel to avoid scrollbar due to sub-pixel rounding.
            self._view.setFixedHeight(int(height) + 1)

class AutoResizingWebEngineView(QWebEngineView):
    """
    A QWebEngineView that automatically resizes its height based on its content,
    using a ResizeObserver for reliable detection.
    """
    class PrintHandler(QObject):
        def __init__(self, parent_view):
            super().__init__()
            self.parent_view = parent_view

        @pyqtSlot()
        def requestPrint(self):
            """Slot called by the 'Print' button in HTML to trigger the print dialog."""
            if self.parent_view and self.parent_view.cours_column:
                self.parent_view.cours_column._handle_print_request(self.parent_view)

    class EditHandler(QObject):
        edit_requested = pyqtSignal(str, str, int, str) # subject, level, lesson_index, new_content
        lesson_deleted = pyqtSignal(str, str, int) # subject, level, lesson_index

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

    def __init__(self, cours_column_widget, subject, level, lesson_index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cours_column = cours_column_widget

        self.channel = QWebChannel(self.page())
        self.page().setWebChannel(self.channel)

        self.height_reporter = HeightReporter(self)
        self.channel.registerObject("height_reporter_obj", self.height_reporter)

        self.print_handler = self.PrintHandler(self)
        self.channel.registerObject("print_handler_obj", self.print_handler)

        self.edit_handler = self.EditHandler(self, subject, level, lesson_index)
        self.channel.registerObject("edit_handler_obj", self.edit_handler)
        self.edit_handler.lesson_deleted.connect(self.cours_column.handle_lesson_deletion)
        
        self.page().loadFinished.connect(self._on_load_finished)
        self.page().setBackgroundColor(Qt.GlobalColor.transparent)

    def _on_load_finished(self, ok):
        if ok:
            # Ensure the path is correct if the script is run from different locations
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js', 'editor_logic.js')
            with open(script_path, "r", encoding="utf-8") as f:
                js_script = f.read()
            self.page().runJavaScript(js_script)

    def contextMenuEvent(self, event):
        """
        Creates and displays a custom context menu with a dark theme.
        """
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2C3E50; /* Dark background */
                color: #ECF0F1; /* Light text */
                border: 1px solid #34495E;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 25px 5px 20px;
                border: 1px solid transparent; /* For hover effect */
            }
            QMenu::item:selected {
                background-color: #3498DB; /* Hover/selection color */
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
        menu.addAction(page.action(page.WebAction.InspectElement))
        menu.exec(event.globalPos())

class CoursColumn(QFrame):
    """
    A generic widget to display a course column with a title and content.
    Content is updated based on the selected level.
    """
    lesson_updated = pyqtSignal(str, str, int, str) # subject, level, lesson_index, new_content
    new_lesson_requested = pyqtSignal(str, str) # For creating a new lesson
    lesson_data_deletion_requested = pyqtSignal(str, str, int) # Signal to request data model deletion

    SUBJECT_DISPLAY_NAMES = {
        'calc': 'Calculs',
        'geo': 'Mesures',
        'conj': 'Conjugaison',
        'grammar': 'Grammaire',
        'ortho': 'Orthographe',
        'english': 'Anglais'
    }

    SUBJECT_ORDER = ['calc', 'geo', 'conj', 'grammar', 'ortho', 'english']

    def __init__(self, parent_window, UI_STYLE_CONFIG, title, content_data_by_level, color_key):
        super().__init__()
        self.parent_window = parent_window
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG
        self.title = title
        self.content_data_by_level = content_data_by_level
        self.color_key = color_key
        self.current_level = None

        self.subject_headers = {}
        self.lesson_views = {}

        self._setup_ui()

    def _load_file_content(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: File not found: {filepath}")
            return ""
        except Exception as e:
            print(f"Error loading file {filepath}: {e}")
            return ""
        
    def _handle_print_request(self, web_view):
        """Opens the print dialog for the specified web content."""
        web_view.printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        web_view.print_dialog = QPrintDialog(web_view.printer, self.parent_window)
        if web_view.print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
            web_view.print(web_view.printer)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 5)
        layout.setSpacing(10)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")

        self.content_container = QWidget()
        main_content_layout = QHBoxLayout(self.content_container)
        main_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_content_layout.setSpacing(20)

        left_column_widget = QWidget()
        self.left_column_layout = QVBoxLayout(left_column_widget)
        self.left_column_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_content_layout.addWidget(left_column_widget, 1)

        right_column_widget = QWidget()
        self.right_column_layout = QVBoxLayout(right_column_widget)
        self.right_column_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_content_layout.addWidget(right_column_widget, 1)

        scrollbar_style = self.UI_STYLE_CONFIG["scroll_bar"]["style_template"].format(
            **self.UI_STYLE_CONFIG["scroll_bar"]["values"]
        )
        scroll_area.setStyleSheet(scrollbar_style)
        scroll_area.setWidget(self.content_container)
        layout.addWidget(scroll_area)

    def get_title_widget(self):
        return self.title_label # This attribute is not defined in the provided code. It seems like a remnant.

    def _clear_layouts(self):
        """Helper to clear all widgets from both column layouts."""
        for layout in [self.left_column_layout, self.right_column_layout]:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        self.subject_headers.clear()
        self.lesson_views.clear()

    def _add_placeholder_message(self, message):
        """Helper to add a styled placeholder message to the left column."""
        placeholder_label = QLabel(message)
        placeholder_label.setWordWrap(True)
        placeholder_label.setTextFormat(Qt.TextFormat.RichText)
        placeholder_label.setStyleSheet("font-size: 14px; color: #E0E0E0; background-color: #2C2C2C; border-radius: 8px; padding: 10px; margin-bottom: 10px;")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_column_layout.addWidget(placeholder_label)

    def update_content(self, level):
        """Updates the displayed content based on the level."""
        self.current_level = level
        self._clear_layouts()

        if not level:
            self._add_placeholder_message("<h3>Sélectionnez un niveau</h3><p>Choisissez un niveau ci-dessus pour afficher les leçons correspondantes.</p>")
            return

        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        CSS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'css'))
        HTML_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'html'))

        template_html = self._load_file_content(os.path.join(HTML_DIR, 'template.html'))
        cours_css_content = self._load_file_content(os.path.join(CSS_DIR, 'cours_style.css'))
        confirm_dialog_html = self._load_file_content(os.path.join(HTML_DIR, 'confirm_dialog_html.html'))
        edit_toolbar_html = self._load_file_content(os.path.join(HTML_DIR, 'edit_toolbar.html'))
        buttons_html = self._load_file_content(os.path.join(HTML_DIR, 'buttons.html'))

        subject_colors = self.UI_STYLE_CONFIG['labels']['column_title_colors']
        any_lesson_found = False
        
        num_subjects = len(self.SUBJECT_ORDER)
        mid_point = (num_subjects + 1) // 2

        for i, subject in enumerate(self.SUBJECT_ORDER):
            target_layout = self.left_column_layout if i < mid_point else self.right_column_layout
            
            # Create and add the header for every subject, regardless of whether it has lessons.
            # This ensures the "New Lesson" button is always available.
            header_widget = QWidget()
            header_layout = QHBoxLayout(header_widget)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(10)

            subject_color = subject_colors.get(subject, '#FFFFFF')
            display_name = self.SUBJECT_DISPLAY_NAMES.get(subject, subject.capitalize())
            subject_title_label = QLabel(f"<h2>{display_name}</h2>")
            subject_title_label.setTextFormat(Qt.TextFormat.RichText)
            subject_title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {subject_color}; margin-top: 15px; margin-bottom: 5px; border-bottom: 2px solid {subject_color}; padding-bottom: 3px;")
            header_layout.addWidget(subject_title_label)

            header_layout.addStretch(1)

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
            new_lesson_button.clicked.connect(lambda checked, s=subject, l=level: self.new_lesson_requested.emit(s, l))
            header_layout.addWidget(new_lesson_button)
            self.subject_headers[subject] = header_widget
            target_layout.addWidget(header_widget)

            # Now, add the lessons for the current level if they exist.
            subject_data = self.content_data_by_level.get(subject, {})
            lessons_for_level = subject_data.get(level, [])
            if lessons_for_level:
                any_lesson_found = True
                for lesson_index, lesson in enumerate(lessons_for_level):
                    raw_lesson_content = lesson.get('content', '')
                    subject_bg_class = f"lesson-card-bg-{subject}" if lesson_index % 2 == 0 else f"lesson-card-bg-{subject}-alt"
                    
                    lesson_content_view = AutoResizingWebEngineView(self, subject, level, lesson_index)
                    lesson_content_view.edit_handler.edit_requested.connect(self.lesson_updated)

                    full_html = (
                        template_html
                        .replace("{{cours_css_content}}", cours_css_content)
                        .replace("{{confirm_dialog_html}}", confirm_dialog_html)
                        .replace("{{edit_toolbar_html}}", edit_toolbar_html)
                        .replace("{{buttons_html}}", buttons_html)
                        .replace("{{raw_lesson_content}}", raw_lesson_content)
                        .replace("{{subject_bg_class}}", subject_bg_class)
                    )

                    lesson_content_view.setHtml(full_html, QUrl("qrc:/"))
                    lesson_content_view.setMinimumHeight(30)

                    self.lesson_views[(subject, lesson_index)] = lesson_content_view
                    target_layout.addWidget(lesson_content_view)

        if not any_lesson_found:
            self._add_placeholder_message(f"<h3>Pas de cours pour le niveau {level}</h3><p>Le contenu pour ce niveau n'a pas encore été ajouté.</p>")

    def add_new_lesson_widget(self, subject, level, new_lesson_data):
        """
        Adds a single new lesson widget to the UI in a targeted manner,
        without reloading everything.
        """
        # 1. Shift indices of existing lesson views for the same subject
        keys_to_update = []
        for (s, idx), view in self.lesson_views.items():
            if s == subject:
                keys_to_update.append(((s, idx), view))

        # Sort by index descending to avoid overwriting keys during update
        keys_to_update.sort(key=lambda item: item[0][1], reverse=True)

        for (s_old, idx_old), view_obj in keys_to_update:
            new_index = idx_old + 1
            view_obj.edit_handler.lesson_index = new_index
            # Move the view object to the new key in the dictionary
            self.lesson_views[(s_old, new_index)] = self.lesson_views.pop((s_old, idx_old))
            print(f"UI-UPDATE: Shifted index for {s_old} from {idx_old} to {new_index}.")

        # 2. Determine target layout and check for header
        subject_index = self.SUBJECT_ORDER.index(subject)
        mid_point = (len(self.SUBJECT_ORDER) + 1) // 2
        target_layout = self.left_column_layout if subject_index < mid_point else self.right_column_layout

        header_widget = self.subject_headers.get(subject)
        if not header_widget:
            # Create and add header if it's the first lesson for this subject
            header_widget = QWidget()
            header_layout = QHBoxLayout(header_widget)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(10)

            subject_color = self.UI_STYLE_CONFIG['labels']['column_title_colors'].get(subject, '#FFFFFF')
            display_name = self.SUBJECT_DISPLAY_NAMES.get(subject, subject.capitalize())
            subject_title_label = QLabel(f"<h2>{display_name}</h2>")
            subject_title_label.setTextFormat(Qt.TextFormat.RichText)
            subject_title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {subject_color}; margin-top: 15px; margin-bottom: 5px; border-bottom: 2px solid {subject_color}; padding-bottom: 3px;")
            header_layout.addWidget(subject_title_label)
            header_layout.addStretch(1)

            new_lesson_button = QPushButton("➕ Nouveau Cours")
            new_lesson_button.setStyleSheet("""
                QPushButton { background-color: #34495E; color: #ECF0F1; border: 1px solid #4A6572; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
                QPushButton:hover { background-color: #4A6572; }
            """)
            new_lesson_button.setCursor(Qt.CursorShape.PointingHandCursor)
            new_lesson_button.clicked.connect(lambda checked, s=subject, l=level: self.new_lesson_requested.emit(s, l))
            header_layout.addWidget(new_lesson_button)
            
            self.subject_headers[subject] = header_widget
            target_layout.insertWidget(0, header_widget) # Insert header at the top of its column

        # 3. Create and insert the new lesson widget
        lesson_index = 0 # New lesson is always at the top
        raw_lesson_content = new_lesson_data.get('content', '')
        subject_bg_class = f"lesson-card-bg-{subject}" # First lesson always gets the primary color

        new_lesson_view = AutoResizingWebEngineView(self, subject, level, lesson_index)
        new_lesson_view.edit_handler.edit_requested.connect(self.lesson_updated)

        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        CSS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'css'))
        HTML_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'html'))
        template_html = self._load_file_content(os.path.join(HTML_DIR, 'template.html'))
        cours_css_content = self._load_file_content(os.path.join(CSS_DIR, 'cours_style.css'))
        confirm_dialog_html = self._load_file_content(os.path.join(HTML_DIR, 'confirm_dialog_html.html'))
        edit_toolbar_html = self._load_file_content(os.path.join(HTML_DIR, 'edit_toolbar.html'))
        buttons_html = self._load_file_content(os.path.join(HTML_DIR, 'buttons.html'))

        full_html = template_html.replace("{{cours_css_content}}", cours_css_content).replace("{{confirm_dialog_html}}", confirm_dialog_html).replace("{{edit_toolbar_html}}", edit_toolbar_html).replace("{{buttons_html}}", buttons_html).replace("{{raw_lesson_content}}", raw_lesson_content).replace("{{subject_bg_class}}", subject_bg_class)
        new_lesson_view.setHtml(full_html, QUrl("qrc:/"))
        new_lesson_view.setMinimumHeight(30)

        self.lesson_views[(subject, lesson_index)] = new_lesson_view
        target_layout.insertWidget(target_layout.indexOf(header_widget) + 1, new_lesson_view)

    @pyqtSlot(str, str, int)
    def handle_lesson_deletion(self, subject, level, lesson_index_to_delete):
        """
        Handles the deletion of a lesson in a targeted manner without refreshing others.
        This method only removes the affected widget and updates the indices
        of subsequent lessons to maintain consistency.
        """
        widget_to_delete = self.lesson_views.pop((subject, lesson_index_to_delete), None)
        print(f"UI-UPDATE: Targeted deletion of widget for {subject}, index {lesson_index_to_delete}.")
        if widget_to_delete:
            widget_to_delete.setParent(None)
            widget_to_delete.deleteLater()

        # Update indices of remaining lessons in the same subject.
        keys_to_update = []
        for (s, idx), view in self.lesson_views.items():
            if s == subject and idx > lesson_index_to_delete:
                keys_to_update.append(((s, idx), view))

        # Trier par index croissant pour éviter d'écraser les clés du dictionnaire lors de la mise à jour.
        # C'est crucial pour garantir que la ré-indexation se fasse correctement.
        keys_to_update.sort(key=lambda item: item[0][1])

        for (s_old, idx_old), view_obj in keys_to_update:
            new_index = idx_old - 1
            view_obj.edit_handler.lesson_index = new_index
            # Déplacer l'objet de vue vers la nouvelle clé d'index dans le dictionnaire
            self.lesson_views[(s_old, new_index)] = self.lesson_views.pop((s_old, idx_old))
            print(f"UI-UPDATE: Updated index for {s_old} from {idx_old} to {new_index}.")

        # The header is now persistent and managed by update_content, so we no longer delete it here.

        self.lesson_data_deletion_requested.emit(subject, level, lesson_index_to_delete)