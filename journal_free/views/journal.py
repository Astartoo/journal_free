from typing import Callable

from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, \
    QSpacerItem, QSizePolicy, QWidget, QScrollArea, QHBoxLayout
from PySide6.QtCore import Qt, QSize

from journal_free.settings import BASE_DIR
from journal_free.views.base import SCROLL_STYLE, FileSelectorWidget, Spinner


class JournalWindow(QWidget):
    title = "Настройки автозаполнения"
    back = True
    journal_url: str | None = None
    class_: str | None = None

    def __init__(self, parent=None):
        super().__init__(parent)
        parent.setStyleSheet(
            'background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(2px); border-radius: 20px;')
        self.layout = QVBoxLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.layout)
        self.initUI()

    def initUI(self):
        self.navigator = QFrame(self)
        self.navigator.setStyleSheet('background: none')
        self.navigator.setFixedHeight(50)
        self.navigator_layout = QHBoxLayout(self.navigator)
        self.navigator_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.navigator)

        # ---- button::backspace ----
        if self.back:
            self.backspace_button = QPushButton(self.navigator)
            self.backspace_button.setIcon(QIcon(str(BASE_DIR / "resource/images/back.svg")))
            self.backspace_button.setIconSize(QSize(20, 20))
            self.backspace_button.setFixedSize(50, 50)
            self.backspace_button.setFlat(True)
            self.backspace_button.setStyleSheet(
                "QPushButton {background-color: rgba(0, 0, 0, 0);border-radius: 10px;} QPushButton:hover {background-color: rgba(200, 200, 200, 0.2);} QPushButton:pressed {background-color: rgba(200, 200, 200, 0.1);}")
            self.navigator_layout.addWidget(self.backspace_button)

        # ---- title ----
        title = QLabel(self.navigator)
        title.setText(self.title)
        title.setStyleSheet("QLabel{font-family: 'Inter'; font-style: normal; font-weight: 800; font-size: 24px; line-height: 29px; color: #464646;}")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.navigator_layout.addWidget(title)

        self.navigator_layout.addItem(QSpacerItem(15, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

        # ---- horizontal line ----
        horizontal_line = QFrame(self)
        horizontal_line.setFrameShape(QFrame.Shape.HLine)
        horizontal_line.setFrameShadow(QFrame.Shadow.Sunken)
        horizontal_line.setStyleSheet("QFrame {border: 1px solid #ABABAB;}")
        horizontal_line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        horizontal_line.setFixedHeight(1)
        self.layout.addWidget(horizontal_line)

        # ---- scroll area ----
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(SCROLL_STYLE)

        # ---- page content ----
        self.content = QFrame(scroll_area)
        self.content.setStyleSheet('background: rgba(243, 243, 243, 1);')
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidget(self.content)
        self.layout.addWidget(scroll_area)

    def setBackEvent(self, event: Callable):
        self.backspace_button.clicked.connect(event)

    def setFillEvent(self, event: Callable):
        self.save_button.clicked.connect(event)

    @property
    def file_path(self):
        return self.file_selector.file_name

    def load_content(self, subject: str, class_: dict, selected_term: str):
        self.journal_url = class_['url']
        self.class_ = f"{subject} - {class_['name']}"

        # ---- selected journal ----
        sel_journal = QFrame(self)
        sel_journal.setStyleSheet('background: none;')
        sel_journal_layout = QVBoxLayout(sel_journal)
        sel_journal_layout.setContentsMargins(0, 10, 0, 10)

        sel_journal_header = QLabel(f"Выбранный журнал", sel_journal)
        sel_journal_header.setStyleSheet("QLabel{font-family: 'Inter'; font-style: normal; font-weight: 600; font-size: 16px; line-height: 19px; color: #464646;}")
        sel_journal_layout.addWidget(sel_journal_header)

        sel_journal_value = QLabel(sel_journal)
        sel_journal_value.setText(f"{subject} - {class_['name']}")
        sel_journal_value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sel_journal_value.setFixedHeight(40)
        sel_journal_value.setStyleSheet("QLabel{background: #ffffff; padding: 5px; border-radius: 5px; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 14px; line-height: 17px; color: #ababab;}")
        sel_journal_layout.addWidget(sel_journal_value)
        self.content_layout.addWidget(sel_journal)

        # ---- selected term ----
        sel_term = QFrame(self)
        sel_term.setStyleSheet('background: none;')
        sel_term_layout = QVBoxLayout(sel_term)
        sel_term_layout.setContentsMargins(0, 10, 0, 10)

        sel_term_header = QLabel(f"Выбранный семестр", sel_term)
        sel_term_header.setStyleSheet(
            "QLabel{font-family: 'Inter'; font-style: normal; font-weight: 600; font-size: 16px; line-height: 19px; color: #464646;}")
        sel_term_layout.addWidget(sel_term_header)

        sel_term_value = QLabel(sel_term)
        sel_term_value.setText(selected_term)
        sel_term_value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sel_term_value.setFixedHeight(40)
        sel_term_value.setStyleSheet("QLabel{background: #ffffff; padding: 5px; border-radius: 5px; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 14px; line-height: 17px; color: #ababab;}")
        sel_term_layout.addWidget(sel_term_value)
        self.content_layout.addWidget(sel_term)

        # ---- file ----
        file_frame = QFrame(self)
        file_frame.setStyleSheet('background: none;')
        file_layout = QVBoxLayout(file_frame)
        file_layout.setContentsMargins(0, 10, 0, 10)

        file_header = QLabel(f"Файл с календарным планированием", file_frame)
        file_header.setStyleSheet(
            "QLabel{font-family: 'Inter'; font-style: normal; font-weight: 600; font-size: 16px; line-height: 19px; color: #464646;}")
        file_layout.addWidget(file_header)

        file_subheader = QLabel(file_frame)
        file_subheader.setText("""
                    Для автоматического заполнения журнала у вас должен быть подготовлен файл с календарным планированием в формате <b>Excel</b>.<br>
                    Шаблон этого файла можно посмотреть по <a href="https://docs.google.com/spreadsheets/d/16Krgr5FEPiWZK7U0vy9VoxQ_P0O2DDgE/edit?usp=sharing&ouid=101386565985130001786&rtpof=true&sd=true" style="color: #FF4D00; font-weight: 600;">ccылке</a>.
                """)
        file_subheader.setStyleSheet(
            "QLabel{font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 12px; line-height: 15px; color: #464646;}")
        file_subheader.setOpenExternalLinks(True)

        file_layout.addWidget(file_subheader)

        self.file_selector = FileSelectorWidget(file_frame)
        file_layout.addWidget(self.file_selector)

        self.content_layout.addWidget(file_frame)

        self.content_layout.addItem(QSpacerItem(15, 15, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

        self.save_button = QPushButton(self)
        self.save_button.setFixedSize(150, 40)
        self.save_button.setStyleSheet("QPushButton {background-color: #FF4D00; border-radius: 10px;} QPushButton:hover {background-color: #FF7337;} QPushButton:pressed {background-color: #E1632D;}")
        self.save_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.save_button.setFlat(True)
        self.content_layout.addWidget(self.save_button)

        self.save_button_layout = QVBoxLayout(self.save_button)
        self.save_button_layout.setContentsMargins(0, 0, 0, 0)
        self.save_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.save_button_icon = Spinner(self.save_button)
        self.save_button_icon.setFixedSize(28, 28)
        self.save_button_icon.setStyleSheet("background: none;")
        self.save_button_icon.setVisible(False)
        self.save_button_layout.addWidget(self.save_button_icon)

        self.save_button_text = QLabel("Заполнить", self.save_button)
        self.save_button_text.setStyleSheet("background: none; font-family: 'Inter'; font-style: normal; font-weight: 700; font-size: 16px; line-height: 19px; color: #FFFFFF;")
        self.save_button_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.save_button_text.setVisible(True)
        self.save_button_layout.addWidget(self.save_button_text)

    def set_enabled(self, is_enabled: bool):
        self.backspace_button.setEnabled(is_enabled)
        self.save_button.setEnabled(is_enabled)
        self.file_selector.set_enable(is_enabled)

    def loading(self, is_loading: bool):
        self.save_button_text.setVisible(not is_loading)
        self.save_button_icon.setVisible(is_loading)
        if is_loading:
            self.save_button_icon.start()
        else:
            self.save_button_icon.stop()
