from PyQt6.QtWidgets import (QHBoxLayout, QWidget, QLabel, QLineEdit, QGroupBox, QVBoxLayout, QLayout, QCheckBox, QPushButton, QFrame, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt # Not strictly needed for these functions, but often useful for UI
from PyQt6.QtGui import QPalette, QColor # Not strictly needed here, but often useful for UI

# Assuming UI_STYLE_CONFIG is accessible or passed
# For now, let's assume it's imported directly or passed as an argument if needed.
# For this specific case, it's used in create_input_row, so it needs to be imported.
from PyQt6.QtCore import QTimer

from gui.template import UI_STYLE_CONFIG

def create_input_row(label_text, max_width=60):
    """Crée une ligne QHBoxLayout avec un QLabel et un QLineEdit."""
    # Le widget conteneur pour la ligne entière
    row_widget = QWidget()
    row_layout = QHBoxLayout(row_widget)
    # Pas de marges internes pour le layout de la ligne
    row_layout.setContentsMargins(0, 0, 0, 0)
    row_layout.setSpacing(5)  # Espacement entre label et line_edit

    label = QLabel(label_text)
    # Utilise la config
    label.setStyleSheet(UI_STYLE_CONFIG["labels"]["field_label"])
    row_layout.addWidget(label)

    line_edit = QLineEdit()
    # max_width est toujours un int ici
    line_edit.setMaximumWidth(max_width)
    # Le style des QLineEdit sera appliqué globalement via MainWindow
    row_layout.addWidget(line_edit)
    return row_widget, line_edit  # Retourner le widget conteneur et le line_edit

def set_groupbox_style(groups, color, UI_STYLE_CONFIG=UI_STYLE_CONFIG):
    """Utility function to apply compact style to a list of QGroupBoxes."""
    style_template = UI_STYLE_CONFIG["group_boxes"]["base_style_template"]
    for group in groups:
        group.setStyleSheet(style_template.format(border_color=color))


def create_generic_groupbox(parent_instance, title, fields_config, extra_items=None):
    """
    Crée un QGroupBox avec des champs de saisie et des éléments supplémentaires optionnels.
    parent_instance: L'instance de la classe (ex: MainWindow) à laquelle les QLineEdit seront attachés via setattr.
    title: Titre du QGroupBox.
    fields_config: liste de tuples (label_text, line_edit_attr_name, max_width)
    extra_items: liste de QWidget ou QLayout à ajouter à la fin.
    Retourne le QGroupBox, une liste des QLineEdit créés, et un dict des row_widgets créés.
    """

    group_box = QGroupBox(title)
    group_layout = QVBoxLayout()
    line_edits_created = []
    row_widgets_for_map_part = {}  # Spécifique à cet appel

    for label_text, line_edit_attr_name, max_width_val in fields_config:
        row_widget, line_edit = create_input_row(
            label_text, max_width_val)  # row_widget est le QWidget de la ligne
        group_layout.addWidget(row_widget)
        # Attach the QLineEdit to the parent_instance
        setattr(parent_instance, line_edit_attr_name, line_edit)
        line_edits_created.append(line_edit)
        # Store the row_widget for later addition to exercise_widgets_map
        row_widgets_for_map_part[f"{line_edit_attr_name}_row"] = row_widget

    if extra_items:
        for item in extra_items:
            if isinstance(item, QLayout):
                group_layout.addLayout(item)
            elif isinstance(item, QWidget):
                group_layout.addWidget(item)
    group_box.setLayout(group_layout)
    return group_box, line_edits_created, row_widgets_for_map_part

def create_level_selection_widgets(parent_instance, UI_STYLE_CONFIG, LEVEL_COLORS, LEVEL_ORDER):
    """
    Creates level selection widgets (label and buttons).

    Returns:
        level_selection_layout: QHBoxLayout containing the level selection widgets.
        level_buttons: dictionary of level buttons
    """
    level_selection_layout = QHBoxLayout()
    level_selection_layout.setContentsMargins(10, 5, 10, 5)
    level_selection_label = QLabel("Niveau :")
    level_selection_label.setStyleSheet(UI_STYLE_CONFIG["labels"]["level_selection"])
    level_selection_layout.addWidget(level_selection_label)

    level_buttons = {}
    for level_name in LEVEL_ORDER:
        color_hex = LEVEL_COLORS[level_name]
        button = QPushButton(level_name)
        hover_color = darken_color(color_hex, 0.95)
        pressed_color = darken_color(color_hex, 0.85)

        button.setStyleSheet(UI_STYLE_CONFIG["buttons"]["level_button_base_style_template"].format(
            text_color=UI_STYLE_CONFIG["buttons"]["level_button_text_color"],
            bg_color=color_hex,
            hover_bg_color=hover_color,
            pressed_bg_color=pressed_color,
        ))
        button.setProperty("selected", False)
        button.clicked.connect(
            lambda checked, b=button, ln=level_name: select_level_internal(parent_instance, ln, b, level_buttons, LEVEL_COLORS, UI_STYLE_CONFIG))
        button.setFixedWidth(150)
        level_buttons[level_name] = button
        level_selection_layout.addWidget(button)

    level_selection_layout.addStretch()
    return level_selection_layout, level_buttons

def darken_color(hex_color, factor=0.8):
    """Darkens a color by a factor."""
    color = QColor(hex_color)
    r = max(0, min(255, int(color.red() * factor)))
    g = max(0, min(255, int(color.green() * factor)))
    b = max(0, min(255, int(color.blue() * factor)))
    return QColor(r, g, b).name()

def select_level_internal(parent_instance, level_name, clicked_button, level_buttons, LEVEL_COLORS, UI_STYLE_CONFIG):
    """
    Handles the UI state of the level buttons and calls a method on the
    parent_instance to update the main application state.
    """

    # 1. Manage selection/deselection of internal button state.
    if parent_instance.current_selected_level_button == clicked_button:
        parent_instance.current_selected_level_button = None  # Deselect
    else:
        parent_instance.current_selected_level_button = clicked_button

    # 2. Update styles and opacity for ALL level buttons.
    for ln_iter, btn_iter in level_buttons.items():
        original_color_hex = LEVEL_COLORS[ln_iter]
        hover_color = darken_color(original_color_hex, 0.95)
        pressed_color = darken_color(original_color_hex, 0.85)

        is_currently_iter_selected_button = (
            btn_iter == parent_instance.current_selected_level_button)
        btn_iter.setProperty("selected", is_currently_iter_selected_button)

        style_str = UI_STYLE_CONFIG["buttons"]["level_button_base_style_template"].format(
            text_color=UI_STYLE_CONFIG["buttons"]["level_button_text_color"],
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

        if is_currently_iter_selected_button or not parent_instance.current_selected_level_button:
            opacity_effect.setOpacity(1.0)
        else:
            opacity_effect.setOpacity(0.55)

    # Call parent_window's method to update its current_level and trigger exercise visibility update.
    # Check if parent_instance has set_current_level method
    if hasattr(parent_instance, "set_current_level") and callable(getattr(parent_instance, "set_current_level")):
        parent_instance.set_current_level(
            level_name if parent_instance.current_selected_level_button else None)
    else:
        print("Error: parent_instance does not have set_current_level method.")

    QTimer.singleShot(0, lambda: refresh_level_button_styles(level_buttons))

def refresh_level_button_styles(level_buttons):
    """Refreshes the styles of level buttons."""
    for btn_iter in level_buttons.values():
        btn_iter.style().unpolish(btn_iter)
        btn_iter.style().polish(btn_iter)
        btn_iter.update()