from typing import Callable

from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import QFrame, QPushButton, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout, QWidget, \
    QVBoxLayout, QComboBox, QScrollArea
from PySide6.QtCore import Qt, QSize

from journal_free.settings import BASE_DIR
from journal_free.views.base import Spinner, SCROLL_STYLE, COMBO_STYLE, FlowLayout


class MainWindow(QWidget):
    title = "Журналы"
    back = False
    loader: QFrame = None
    terms_frame: QFrame = None

    def __init__(self, parent=None):
        super().__init__(parent)
        parent.setStyleSheet('background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(2px); border-radius: 20px;')
        self.layout = QVBoxLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.layout)
        self.initUI()

    def loading(self):
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.loader = QFrame(self.content)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        loader_layout = QVBoxLayout(self.loader)

        load_icon = Spinner(self.loader, path=str(BASE_DIR / "resource/images/loading_black.svg"))
        load_icon.setFixedSize(150, 150)
        load_icon.setStyleSheet("background: none;")
        loader_layout.addWidget(load_icon)
        load_icon.start()
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.loader)

    def initUI(self):
        self.navigator = QFrame(self)
        self.navigator.setStyleSheet('background: none')
        self.navigator.setFixedHeight(50)
        self.navigator_layout = QHBoxLayout(self.navigator)
        self.navigator_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.navigator)

        # ---- button::backspace ----
        if self.back:
            backspace_button = QPushButton(self.navigator)
            backspace_button.setIcon(QIcon(str(BASE_DIR / "resource/images/back.svg")))
            backspace_button.setIconSize(QSize(20, 20))
            backspace_button.setFixedSize(50, 50)
            backspace_button.setFlat(True)
            backspace_button.setStyleSheet(
                "QPushButton {background-color: rgba(0, 0, 0, 0);border-radius: 10px;} QPushButton:hover {background-color: rgba(200, 200, 200, 0.2);} QPushButton:pressed {background-color: rgba(200, 200, 200, 0.1);}")
            self.navigator_layout.addWidget(backspace_button)

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

    def termChangeEvent(self, func: Callable):
        if self.combo_box:
            self.combo_box.currentIndexChanged.connect(func)

    def get_term_value(self, index: int):
        return self.combo_box.itemData(index)

    def set_current_term(self, current_term: dict):
        index = self.combo_box.findData(current_term["value"])
        if index != -1:
            self.combo_box.setCurrentIndex(index)

    def termChangeEnabled(self, is_enabled: bool):
        if self.combo_box:
            self.combo_box.setEnabled(is_enabled)


    def load_terms(self, terms, current_term: dict | None = None):
        if self.terms_frame:
            self.terms_frame.deleteLater()
        if terms is not None:
            self.terms_frame = QFrame(self.navigator)
            self.terms_frame.setStyleSheet('background: none; border-radius: 0px;')
            self.terms_frame.setFixedHeight(50)
            terms_layout = QHBoxLayout(self.terms_frame)
            terms_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            terms_layout.setContentsMargins(0, 0, 0, 0)

            terms_title = QLabel(self.terms_frame)
            terms_title.setText("семестр")
            terms_title.setStyleSheet(
                "QLabel{font-family: 'Inter'; font-style: normal; font-weight: 800; font-size: 14px; line-height: 17px; color: #464646;}")
            terms_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            terms_layout.addWidget(terms_title)

            self.combo_box = QComboBox(self.terms_frame)
            self.combo_box.setFixedWidth(340)
            for term in terms:
                self.combo_box.addItem(term['name'], term['value'])
            self.combo_box.setStyleSheet(COMBO_STYLE)
            if current_term is not None:
                self.set_current_term(current_term)
            terms_layout.addWidget(self.combo_box)
            self.navigator_layout.addWidget(self.terms_frame)

    def load_journals(self, journals: list, event: Callable):
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        if self.loader:
            self.content_layout.removeWidget(self.loader)
            self.loader.deleteLater()
        for journal in journals:
            journal_frame = QFrame(self.content)
            journal_frame.setStyleSheet('background: none;')
            journal_layout = QHBoxLayout(journal_frame)
            journal_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            journal_layout.setContentsMargins(0, 20, 0, 20)
            self.content_layout.addWidget(journal_frame)

            header = QLabel(journal['subject'], journal_frame)
            header.setStyleSheet(
                "QLabel{font-family: 'Inter'; font-style: normal; font-weight: 600; font-size: 16px; line-height: 19px; color: #464646;}")
            header.setFixedWidth(150)
            journal_layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignTop)
            journal_layout.addItem(QSpacerItem(15, 15, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

            journals = QFrame(journal_frame)
            journals.setStyleSheet('background: none;')
            journals.setFixedWidth(630)
            journals_layout = FlowLayout(journals)
            journals_layout.setContentsMargins(0, 0, 0, 0)
            journals_layout.setSpacing(10)
            journal_layout.addWidget(journals)


            for class_ in journal['classes']:
                journal_button = QPushButton(journals)
                journal_button.setText(class_['name'])
                journal_button.setMinimumSize(90, 40)
                journal_button.setMaximumSize(300, 40)
                journal_button.setStyleSheet(
                    "QPushButton {background-color: #ffffff; border: 1px solid #ABABAB; border-radius: 10px; padding: 0px 10px; font-family: 'Inter'; font-style: normal; font-weight: 600; font-size: 15px; line-height: 18px; color: #464646;} QPushButton:hover {background-color: #FF4D00; color: #ffffff;} QPushButton:pressed {background-color: #E1632D; color: #ffffff;}")
                journal_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                journal_button.clicked.connect(event(journal['subject'], class_))
                journals_layout.addWidget(journal_button)


