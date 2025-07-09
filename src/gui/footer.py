from PyQt6.QtWidgets import (QLabel, QLineEdit, QPushButton, QFrame, QHBoxLayout, QGridLayout, QFileDialog, QVBoxLayout)
from PyQt6.QtCore import Qt
import os

class AppFooter(QFrame):
    """
    A QFrame component representing the application's footer, including:
    - Output path selection and display
    - Filename input
    - Action buttons (Generate PDF/Word, Preview PDF/Word)
    - Version and GitHub link

    It communicates with the parent_window (MainWindow) to trigger actions and update state.
    """
    def __init__(self, parent_window, UI_STYLE_CONFIG, __version__, GITHUB_URL):
        super().__init__()
        self.parent_window = parent_window # Reference to MainWindow
        self.UI_STYLE_CONFIG = UI_STYLE_CONFIG
        self.__version__ = __version__
        self.GITHUB_URL = GITHUB_URL

        self.selected_output_path = None # Managed by this component
        self.all_line_edits = [] # Collect line edits for styling in MainWindow

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # No extra margins for the frame itself

        # Separator before file controls/generation buttons
        sep_bottom = QFrame()
        sep_bottom.setFrameShape(QFrame.Shape.HLine)
        sep_bottom.setFrameShadow(QFrame.Shadow.Sunken)
        sep_bottom.setStyleSheet(self.UI_STYLE_CONFIG["separators"]["style"])
        main_layout.addWidget(sep_bottom)

        # Bottom band: generate buttons + filename on the same line
        bottom_controls_layout = QHBoxLayout()
        bottom_controls_layout.setContentsMargins(10, 5, 10, 5)

        # Left part for path and filename
        left_file_controls_layout = QGridLayout()
        self.filename_label = QLabel("Nom du fichier :")
        self.filename_label.setStyleSheet(self.UI_STYLE_CONFIG["labels"]["filename_label"])
        self.filename_entry = QLineEdit()
        self.filename_entry.setMinimumWidth(150)
        self.filename_entry.setMaximumWidth(200)
        self.all_line_edits.append(self.filename_entry)
        self.filename_entry.setText("workbook")

        file_controls_line_layout = QHBoxLayout()
        file_controls_line_layout.addWidget(self.filename_label)
        file_controls_line_layout.addWidget(self.filename_entry)
        file_controls_line_layout.addStretch(0)
        left_file_controls_layout.addLayout(file_controls_line_layout, 0, 0, 1, 2)

        bottom_controls_layout.addLayout(left_file_controls_layout)
        bottom_controls_layout.addStretch(1)

        # Styles for action buttons
        btn_cfg = self.UI_STYLE_CONFIG["buttons"]

        def get_action_button_style(type_key):
            return btn_cfg["action_button_base_style_template"].format(
                bg_color=btn_cfg[type_key]["bg_color"],
                disabled_bg_color=btn_cfg["disabled"]["bg_color"],
                disabled_text_color=btn_cfg["disabled"]["text_color"],
                pressed_bg_color=btn_cfg[type_key]["pressed_bg_color"]
            )

        action_buttons_layout = QHBoxLayout()
        self.generate_pdf_button = QPushButton("Générer PDF")
        self.generate_pdf_button.setStyleSheet(get_action_button_style("pdf"))
        self.generate_pdf_button.clicked.connect(self.parent_window.generate_pdf)
        action_buttons_layout.addWidget(self.generate_pdf_button)

        self.generate_word_button = QPushButton("Générer Word")
        self.generate_word_button.setStyleSheet(get_action_button_style("word"))
        self.generate_word_button.clicked.connect(self.parent_window.generate_word)
        action_buttons_layout.addWidget(self.generate_word_button)

        self.preview_pdf_button = QPushButton("Visualiser PDF")
        self.preview_pdf_button.setStyleSheet(get_action_button_style("preview_pdf"))
        self.preview_pdf_button.clicked.connect(self.parent_window.preview_pdf)
        action_buttons_layout.addWidget(self.preview_pdf_button)

        self.preview_word_button = QPushButton("Visualiser Word")
        self.preview_word_button.setStyleSheet(get_action_button_style("preview_word"))
        self.preview_word_button.clicked.connect(self.parent_window.preview_word)
        action_buttons_layout.addWidget(self.preview_word_button)

        action_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        bottom_controls_layout.addLayout(action_buttons_layout)
        main_layout.addLayout(bottom_controls_layout)

        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(15, 5, 10, 5)

        github_label_text = f"<a style='color: #90CAF9; text-decoration: none;' href='{self.GITHUB_URL}'>Code Source (GitHub)</a>"
        self.github_label = QLabel(github_label_text)
        self.github_label.setOpenExternalLinks(True)
        self.github_label.setStyleSheet(self.UI_STYLE_CONFIG["labels"]["footer_label"])
        footer_layout.addWidget(self.github_label)

        footer_layout.addStretch(1)

        self.version_label = QLabel(f"Apprentium v{self.__version__}")
        self.version_label.setStyleSheet(self.UI_STYLE_CONFIG["labels"]["version_label"])
        footer_layout.addWidget(self.version_label)
        main_layout.addLayout(footer_layout)

    def _select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Choisir le dossier de sortie", self.selected_output_path or os.getcwd())
        if directory:
            self.selected_output_path = os.path.normpath(directory)
        # Notify parent_window about the change for config saving
        self.parent_window.set_selected_output_path(self.selected_output_path)

    def set_output_path_from_config(self, path):
        self.selected_output_path = path

    def update_output_path_from_config_file(self):
        pass
