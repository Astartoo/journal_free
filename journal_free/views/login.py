from PySide6.QtGui import QCursor, QShortcut, QKeySequence
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QLineEdit, QSpacerItem, QSizePolicy, QWidget
from PySide6.QtCore import Qt

from journal_free.views.base import Spinner


class LoginWindow(QWidget):
    LOGIN_HEIGHT = 350
    LOGIN_WIDTH = 400

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)
        self.initUI()

    def initUI(self):
        login = QFrame(self)
        login.setFixedSize(self.LOGIN_WIDTH, self.LOGIN_HEIGHT)
        login.setStyleSheet("background-color: rgba(255, 255, 255, 0.5); border-radius: 10px;")
        self.layout.addWidget(login)

        login_layout = QVBoxLayout(login)
        login_layout.setContentsMargins(0, 20, 0, 0)

        title_frame = QFrame(login)
        title_frame.setStyleSheet("background: none")
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 10, 15, 10)
        title_layout.setSpacing(5)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(title_frame)

        login_title = QLabel(title_frame)
        login_title.setText("Войти")
        login_title.setStyleSheet("QLabel{background-color: none; font-family: 'Inter'; font-style: normal; font-weight: 600; font-size: 24px; line-height: 29px; color: #FFFFFF;}")
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(login_title)

        login_subtitle = QLabel(title_frame)
        login_subtitle.setText("Введите данные для авторизации на nz.ua")
        login_subtitle.setStyleSheet("QLabel{background-color: none; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 13px; line-height: 16px; color: #FFFFFF;}")
        login_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(login_subtitle)

        # ------ username ------
        username_frame = QFrame(login)
        username_frame.setStyleSheet("background: none")
        username_layout = QVBoxLayout(username_frame)
        username_layout.setContentsMargins(15, 10, 15, 10)
        username_layout.setSpacing(5)
        username_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(username_frame)

        login_username_label = QLabel(username_frame)
        login_username_label.setText("Имя пользователя или e-mail")
        login_username_label.setStyleSheet("QLabel{background-color: none; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 13px; line-height: 16px; color: #FFFFFF;}")
        login_username_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        username_layout.addWidget(login_username_label)

        self.login_username_input = QLineEdit("", username_frame)
        self.login_username_input.setStyleSheet("QLineEdit{letter-spacing: 1px; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 14px; line-height: 16px; color: #464646; padding: 10px; background: #FFFFFF; border-radius: 10px;}")
        self.login_username_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        username_layout.addWidget(self.login_username_input)

        # ------ password ------
        password_frame = QFrame(login)
        password_frame.setStyleSheet("background: none")
        password_layout = QVBoxLayout(password_frame)
        password_layout.setContentsMargins(15, 10, 15, 10)
        password_layout.setSpacing(5)
        password_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(password_frame)

        login_password_label = QLabel(password_frame)
        login_password_label.setText("Пароль")
        login_password_label.setStyleSheet("QLabel{background-color: none; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 13px; line-height: 16px; color: #FFFFFF;}")
        login_password_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        password_layout.addWidget(login_password_label)

        self.login_password_input = QLineEdit("", password_frame)
        self.login_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password_input.setStyleSheet("QLineEdit{letter-spacing: 1px; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 14px; line-height: 16px; color: #464646; padding: 10px; background: #FFFFFF; border-radius: 10px;}")
        self.login_password_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        password_layout.addWidget(self.login_password_input)
        login_layout.addItem(QSpacerItem(self.LOGIN_WIDTH, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

        # ------ button ------
        self.login_button = QPushButton(login)
        self.login_button.setFixedSize(self.LOGIN_WIDTH, 50)
        self.login_button.setDefault(True)
        self.login_button.setFocus()
        self.login_button.setStyleSheet("QPushButton {background-color: #FF4D00; border-radius: 0; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; font-family: 'Inter'; font-style: normal; font-weight: 700; font-size: 16px; line-height: 19px; color: #FFFFFF;} QPushButton:hover {background-color: #FF7337;} QPushButton:pressed {background-color: #E1632D;}")
        self.login_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.login_button_layout = QVBoxLayout(self.login_button)
        self.login_button_layout.setContentsMargins(0, 0, 0, 0)
        self.login_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.login_button_icon = Spinner(self.login_button)
        self.login_button_icon.setFixedSize(28, 28)
        self.login_button_icon.setStyleSheet("background: none;")
        self.login_button_icon.setVisible(False)
        self.login_button_layout.addWidget(self.login_button_icon)


        self.login_button_text = QLabel("Войти", self.login_button)
        self.login_button_text.setStyleSheet("background: none; font-family: 'Inter'; font-style: normal; font-weight: 700; font-size: 16px; line-height: 19px; color: #FFFFFF;")
        self.login_button_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_button_text.setVisible(True)
        self.login_button_layout.addWidget(self.login_button_text)

        login_layout.addWidget(self.login_button)

    def set_login_event(self, func):
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self.login_button)
        shortcut.activated.connect(self.login_button.click)
        self.login_button.clicked.connect(func)

    @property
    def username(self):
        return self.login_username_input.text()

    @property
    def password(self):
        return self.login_password_input.text()

    def set_enabled_form(self, is_enabled: bool):
        self.login_button.setEnabled(is_enabled)
        self.login_username_input.setEnabled(is_enabled)
        self.login_password_input.setEnabled(is_enabled)
        if is_enabled:
            self.login_username_input.setStyleSheet("QLineEdit{letter-spacing: 1px; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 14px; line-height: 16px; color: #464646; padding: 10px; background: #FFFFFF; border-radius: 10px;}")
            self.login_password_input.setStyleSheet("QLineEdit{letter-spacing: 1px; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 14px; line-height: 16px; color: #464646; padding: 10px; background: #FFFFFF; border-radius: 10px;}")
        else:
            self.login_username_input.setStyleSheet("QLineEdit{letter-spacing: 1px; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 14px; line-height: 16px; color: #ababab; padding: 10px; background: #FFFFFF; border-radius: 10px;}")
            self.login_password_input.setStyleSheet("QLineEdit{letter-spacing: 1px; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 14px; line-height: 16px; color: #ababab; padding: 10px; background: #FFFFFF; border-radius: 10px;}")

    def loading(self, is_loading: bool):
        self.login_button_text.setVisible(not is_loading)
        self.login_button_icon.setVisible(is_loading)
        if is_loading:
            self.login_button_icon.start()
        else:
            self.login_button_icon.stop()


