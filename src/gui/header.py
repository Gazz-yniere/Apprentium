from PyQt6.QtWidgets import (QLabel, QLineEdit, QCheckBox, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

class AppHeader(QFrame):
    """
    A QFrame component representing the application's header, including:
    - Header text input and display options (Name, Note)
    - Number of days input
    - Level selection buttons

    It communicates with the parent_window (MainWindow) to update the application's state.
    """
    def __init__(self, parent_window, UI_STYLE_CONFIG, LEVEL_COLORS, LEVEL_ORDER):
        super().__init__()
        self.parent_window = parent_window # Reference to MainWindow
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG
        self.LEVEL_COLORS = LEVEL_COLORS
        self.LEVEL_ORDER = LEVEL_ORDER

        self.current_selected_level_button = None
        # self.parent_window.current_level will hold the actual selected level name

        self.all_line_edits = [] # Collect line edits for styling in MainWindow

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # No extra margins for the frame itself

        # Top layout: Header text and days entry
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 5, 10, 5)

        # Header Section (left)
        header_section_layout = QHBoxLayout()
        self.header_label = QLabel("Titre :")
        self.header_label.setStyleSheet(self.UI_STYLE_CONFIG["labels"]["header_label"])
        self.header_entry = QLineEdit()
        self.all_line_edits.append(self.header_entry)
        self.header_entry.setPlaceholderText(self.UI_STYLE_CONFIG["line_edits"]["header_placeholder"])
        self.header_entry.setMinimumWidth(250)
        self.show_name_checkbox = QCheckBox("Afficher Nom")
        self.show_note_checkbox = QCheckBox("Afficher Note")

        header_section_layout.addWidget(self.header_label)
        header_section_layout.addWidget(self.header_entry)
        header_section_layout.addWidget(self.show_name_checkbox)
        header_section_layout.addWidget(self.show_note_checkbox)
        header_section_layout.setSpacing(10)
        header_section_layout.addStretch()

        top_layout.addLayout(header_section_layout)
        top_layout.addStretch()

        # Days Section (right)
        days_section_layout = QHBoxLayout()
        self.days_label = QLabel("Nombre de jours :")
        self.days_label.setStyleSheet(self.UI_STYLE_CONFIG["labels"]["days_label"])
        self.days_entry = QLineEdit()
        self.all_line_edits.append(self.days_entry)
        self.days_entry.setMaximumWidth(60)

        days_section_layout.addWidget(self.days_label)
        days_section_layout.addWidget(self.days_entry)
        days_section_layout.addStretch(1)

        days_section_layout.setSpacing(5)

        top_layout.addLayout(days_section_layout)
        main_layout.addLayout(top_layout)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setFrameShadow(QFrame.Shadow.Sunken)
        sep1.setStyleSheet(self.UI_STYLE_CONFIG["separators"]["style"])
        main_layout.addWidget(sep1)

        # Level Selection
        level_selection_layout = QHBoxLayout()
        level_selection_layout.setContentsMargins(10, 5, 10, 5)
        level_selection_label = QLabel("Niveau :")
        level_selection_label.setStyleSheet(self.UI_STYLE_CONFIG["labels"]["level_selection"])
        level_selection_layout.addWidget(level_selection_label)

        self.level_buttons = {}
        for level_name in self.LEVEL_ORDER:
            color_hex = self.LEVEL_COLORS[level_name]
            button = QPushButton(level_name)
            hover_color = self._darken_color(color_hex, 0.95)
            pressed_color = self._darken_color(color_hex, 0.85)

            button.setStyleSheet(self.UI_STYLE_CONFIG["buttons"]["level_button_base_style_template"].format(
                text_color=self.UI_STYLE_CONFIG["buttons"]["level_button_text_color"],
                bg_color=color_hex,
                hover_bg_color=hover_color,
                pressed_bg_color=pressed_color,
            ))
            button.setProperty("selected", False)
            button.clicked.connect(
                lambda checked, b=button, ln=level_name: self._select_level_internal(ln, b))
            button.setFixedWidth(150)
            self.level_buttons[level_name] = button
            level_selection_layout.addWidget(button)

        level_selection_layout.addStretch()
        main_layout.addLayout(level_selection_layout)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)
        sep2.setStyleSheet(self.UI_STYLE_CONFIG["separators"]["style"])
        main_layout.addWidget(sep2)

    def _darken_color(self, hex_color, factor=0.8):
        color = QColor(hex_color)
        r = max(0, min(255, int(color.red() * factor)))
        g = max(0, min(255, int(color.green() * factor)))
        b = max(0, min(255, int(color.blue() * factor)))
        return QColor(r, g, b).name()

    def _select_level_internal(self, level_name, clicked_button):
        # This method handles the UI state of the level buttons within the header.
        # It then calls a method on the parent_window to update the main application state.

        # 1. Manage selection/deselection of internal button state
        if self.current_selected_level_button == clicked_button:
            self.current_selected_level_button = None # Deselect
        else:
            self.current_selected_level_button = clicked_button

        # 2. Update styles and opacity for ALL level buttons
        for ln_iter, btn_iter in self.level_buttons.items():
            original_color_hex = self.LEVEL_COLORS[ln_iter]
            hover_color = self._darken_color(original_color_hex, 0.95)
            pressed_color = self._darken_color(original_color_hex, 0.85)

            is_currently_iter_selected_button = (btn_iter == self.current_selected_level_button)
            btn_iter.setProperty("selected", is_currently_iter_selected_button)

            style_str = self.UI_STYLE_CONFIG["buttons"]["level_button_base_style_template"].format(
                text_color=self.UI_STYLE_CONFIG["buttons"]["level_button_text_color"],
                bg_color=original_color_hex,
                hover_bg_color=hover_color,
                pressed_bg_color=pressed_color,
            )
            btn_iter.setStyleSheet(style_str)
            btn_iter.style().unpolish(btn_iter)
            btn_iter.style().polish(btn_iter)
            btn_iter.update()

            opacity_effect = btn_iter.graphicsEffect()
            if not isinstance(opacity_effect, QGraphicsOpacityEffect):
                if opacity_effect:
                    opacity_effect.deleteLater()
                opacity_effect = QGraphicsOpacityEffect(btn_iter)
                btn_iter.setGraphicsEffect(opacity_effect)

            if is_currently_iter_selected_button or not self.current_selected_level_button:
                opacity_effect.setOpacity(1.0)
            else:
                opacity_effect.setOpacity(0.55)

        # Call parent_window's method to update its current_level and trigger exercise visibility update
        self.parent_window.set_current_level(level_name if self.current_selected_level_button else None)

        QTimer.singleShot(0, self._refresh_level_button_styles)

    def _refresh_level_button_styles(self):
        for btn_iter in self.level_buttons.values():
            btn_iter.style().unpolish(btn_iter)
            btn_iter.style().polish(btn_iter)
            btn_iter.update()

    def set_level_selection_from_config(self, level_name):
        # This method is called by MainWindow.load_config to restore the UI state
        if level_name and level_name in self.level_buttons:
            button_to_select = self.level_buttons[level_name]
            self.current_selected_level_button = button_to_select
            self._select_level_internal(level_name, button_to_select)
        else:
            self.current_selected_level_button = None
            self._select_level_internal(None, None) # Deselect all
