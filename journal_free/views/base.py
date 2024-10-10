from abc import ABC, abstractmethod
from typing import Callable

from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QMainWindow, QFrame, QWidget, QVBoxLayout, \
    QHBoxLayout, QPushButton, QLabel, QSizePolicy, QBoxLayout, \
    QLayout, QFileDialog, QDialog
from PySide6.QtCore import Qt, QSize, QRect, QPoint, QMargins, Property, QPropertyAnimation
from PySide6.QtGui import QPalette, QBrush, QRadialGradient, QColor, QPainter, QPainterPath, QIcon, QPixmap, QTransform, \
    QCursor

from journal_free.settings import BASE_DIR

SCROLL_STYLE = """
        QScrollArea {background: rgba(243, 243, 243, 1); border: none;}
        QScrollBar:vertical {
            background: rgba(243, 243, 243, 1);
            width: 24px;
            padding: 0px 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #707070;
            min-height: 20px;
            border-radius: 4px;
            margin: 15px 0px;
        }
        QScrollBar::add-line:vertical {
            background: #707070;
            padding: 0px;
            height: 10px;
            width: 10px;
            subcontrol-origin: margin;
            subcontrol-position: bottom;
            border-radius: 5px;
        }
        QScrollBar::sub-line:vertical {
            background: #707070; 
            height: 10px;
            width: 10px;
            padding: 0px;
            subcontrol-origin: margin;
            subcontrol-position: top;
            border-radius: 5px;
        }
        QScrollBar::add-line:vertical:hover, QScrollBar::sub-line:vertical:hover {
            background: #555555;
        }
        QScrollBar::add-line:vertical:pressed, QScrollBar::sub-line:vertical:pressed {
            background: #777777;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        QScrollBar:horizontal {
            background: none;
            height: 24px;
            padding: 8px 0px;
            margin: 0px;
        }
        QScrollBar::handle:horizontal {
            background: #707070;
            min-width: 20px;
            border-radius: 4px;
            margin: 0px 15px;
        }
        QScrollBar::add-line:horizontal {
            background: #707070;
            height: 10px;
            width: 10px;
            padding: 0px;
            subcontrol-origin: margin;
            subcontrol-position: right;
            border-radius: 5px;
        }
        QScrollBar::sub-line:horizontal {
            background: #707070;
            height: 10px;
            width: 10px;
            padding: 0px;
            subcontrol-origin: margin;
            subcontrol-position: left;
            border-radius: 5px;
        }
        QScrollBar::add-line:horizontal:hover, QScrollBar::sub-line:horizontal:hover {
            background: #555555;
        }
        QScrollBar::add-line:horizontal:pressed, QScrollBar::sub-line:horizontal:pressed {
            background: #777777;
        }
        QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
            width: 10px;
            height: 10px;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
    """

COMBO_STYLE = """
            QComboBox {
                box-sizing: border-box;
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
                padding: 1px 10px;
                gap: 10px;

                width: 320px;
                height: 30px;

                background: #FFFFFF;
                border: 1px solid #464646;
                border-radius: 5px;

                font-family: 'Inter';
                font-style: normal;
                font-weight: 300;
                font-size: 12px;
                line-height: 15px;
                color: #464646;
            }

            QComboBox::drop-down {
                width: 18px;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }

            QComboBox::down-arrow {
                image: url('journal_free/resource/images/down.svg');
                width: 18px;
                height: 18px;
            }

            QComboBox QAbstractItemView {
                background: #FFFFFF;
                border: 1px solid #464646;
                border-radius: 5px;
                font-family: 'Inter';
                font-style: normal;
                font-weight: 300;
                font-size: 12px;
                line-height: 15px;
                color: #464646;
                padding: 5px;
                margin-top: 5px;
            }

            QComboBox QAbstractItemView::item {
                padding: 3px 0px;
                margin: 1px 0px;
            }
            QComboBox QAbstractItemView::item:selected {
                border: none;
                border-left: 2px solid #ff0000;
                color: #464646;
                padding: 0px 0px;
            }
        """


class OperationStatus:
    ERROR = "error"
    NO_LESSONS = "no lessons"
    SUCCESS = "success"

class Spinner(QWidget):
    def __init__(self, parent=None, path: str = str(BASE_DIR / "resource/images/loading.svg")):
        super().__init__(parent)
        self.svg_renderer = QSvgRenderer(path)
        self.setFixedSize(30, 30)
        self._angle = 0
        self.animation = QPropertyAnimation(self, b"angle", self)
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setLoopCount(-1)
        self.animation.setDuration(1000)

    @Property(float)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        transform = QTransform()
        transform.translate(self.width() / 2, self.height() / 2)
        transform.rotate(self._angle)
        transform.translate(-self.width() / 2, -self.height() / 2)
        painter.setTransform(transform)
        self.svg_renderer.render(painter)

    def start(self):
        self.animation.start()

    def stop(self):
        self.animation.stop()


class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


class BaseComponent(ABC):
    """
    Base class for all components.

    :param QWidget parent: The parent object for this component.
    """
    _widget: QWidget
    _layout: QBoxLayout

    @abstractmethod
    def __init__(self, parent: QWidget) -> None:
        pass

    @property
    def widget(self) -> QWidget:
        """
        Returns the widget object for this component.
        :return: QWidget
        """
        return self._widget

    @property
    def layout(self) -> QBoxLayout:
        """
        Returns the layout object for this component.
        :return: QBoxLayout
        """
        return self._layout

    def addWidget(self, widget: QWidget) -> None:
        """
        Add a widget to this layout.

        :param QWidget widget: QWidget Object to be added to this layout
        """
        self._layout.addWidget(widget)


class WindowSetup:
    """
    Base configuration for the application window.

    :param QMainWindow main: Windows object
    """
    WIDTH = 900
    HEIGHT = 650

    def __init__(self, main: QMainWindow) -> None:
        self.main = main
        self.main.setFixedSize(self.WIDTH, self.HEIGHT)
        self.main.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        gradient = QRadialGradient(0.2969 * self.main.width(), 0.3345 * self.main.height(), 0.6446 * self.main.width(),
                                   0.2969 * self.main.width(), 0.3345 * self.main.height())
        gradient.setColorAt(0, QColor("#530303"))
        gradient.setColorAt(0.49, QColor("#2F1444"))
        gradient.setColorAt(1, QColor("#2D2D2D"))

        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.main.setPalette(palette)

        self.main.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main.setWindowFlags(self.main.windowFlags() | Qt.WindowType.FramelessWindowHint)

        self.central_widget = QWidget(self.main)
        self.main.setCentralWidget(self.central_widget)

        self.base_layout = QVBoxLayout(self.central_widget)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setSpacing(0)
        self.base_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    @property
    def centralWidget(self) -> QWidget:
        """
        Returns the central widget.
        :return: QWidget
        """
        return self.central_widget

    @property
    def baseLayout(self) -> QBoxLayout:
        """
        Returns the central widget layout.
        :return: QBoxLayout
        """
        return self.base_layout

    def addWidget(self, widget: QWidget, alignment=Qt.AlignmentFlag.AlignHCenter) -> None:
        """
        Add a widget to the central widget layout.

        :param QWidget widget: QWidget Object to be added to the baseLayout
        :param alignment: (optional) Alignment of the base widget. Defaults to Qt.AlignmentFlag.AlignHCenter
        """
        self.base_layout.addWidget(widget, alignment=alignment)


class HeaderComponent(BaseComponent):
    HEIGHT = 50
    LOGO_WIDTH = 190
    BUTTONS_WIDTH = 450
    _user = None

    def __init__(self, parent: QWidget) -> None:

        self._is_dragging = False
        self._drag_start_position = None
        self.parent = parent
        # ---- header ----
        self._widget = QFrame(parent)
        self._widget.setFixedSize(WindowSetup.WIDTH, self.HEIGHT)
        self._widget.mousePressEvent = self.headerMousePressEvent
        self._widget.mouseMoveEvent = self.headerMouseMoveEvent
        self._widget.mouseReleaseEvent = self.headerMouseReleaseEvent
        self._layout = QHBoxLayout(self._widget)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(WindowSetup.WIDTH - (self.LOGO_WIDTH + self.BUTTONS_WIDTH))
        # ---- logo ----
        logo = QFrame(self._widget)
        logo.setFixedSize(self.LOGO_WIDTH, self.HEIGHT)
        logo.setContentsMargins(10, 10, 10, 10)
        logo_image = QSvgWidget(str(BASE_DIR / "resource/images/logo.svg"), logo)
        logo_image.setGeometry(20, 10, self.LOGO_WIDTH - 20, self.HEIGHT - 20)
        self._layout.addWidget(logo)

        # self._layout.addItem(QSpacerItem(15, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

        # ---- buttons ----
        buttons = QFrame(self._widget)
        buttons.setFixedSize(self.BUTTONS_WIDTH, self.HEIGHT)
        self.buttons_layout = QHBoxLayout(buttons)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(0)
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(buttons)

        self.user = QLabel(buttons)
        if self._user is None:
            self.user.setVisible(False)
        self.user.setStyleSheet("font-family: 'Inter'; font-style: normal; font-weight: 600; font-size: 14px; line-height: 17px; color: #FFFFFF;")
        self.buttons_layout.addWidget(self.user)

        # ---- button::logout ----
        self.user_logout = QPushButton(buttons)
        self.user_logout.setIcon(QIcon(str(BASE_DIR / "resource/images/logout.svg")))
        self.user_logout.setIconSize(QSize(20, 20))
        self.user_logout.setFixedSize(50, self.HEIGHT)
        if self._user is None:
            self.user_logout.setVisible(False)
        self.user_logout.setFlat(True)
        self.user_logout.setDefault(False)
        self.user_logout.setStyleSheet(
            "QPushButton {background-color: rgba(0, 0, 0, 0);border-radius: 5px;} QPushButton:hover {background-color: rgba(255, 255, 255, 0.2);} QPushButton:pressed {background-color: rgba(255, 255, 255, 0.1);}")
        self.buttons_layout.addWidget(self.user_logout)

        # ---- button::minimize ----
        self.button_minimize = QPushButton(buttons)
        self.button_minimize.setIcon(QIcon(str(BASE_DIR / "resource/images/line.svg")))
        self.button_minimize.setIconSize(QSize(20, 20))
        self.button_minimize.setFixedSize(50, self.HEIGHT)
        self.button_minimize.setFlat(True)
        self.button_minimize.setDefault(False)
        self.button_minimize.setStyleSheet("QPushButton {background-color: rgba(0, 0, 0, 0);border-radius: 5px;} QPushButton:hover {background-color: rgba(255, 255, 255, 0.2);} QPushButton:pressed {background-color: rgba(255, 255, 255, 0.1);}")
        self.buttons_layout.addWidget(self.button_minimize)

        # ---- button::close ----
        self.button_close = QPushButton(buttons)
        self.button_close.setIcon(QIcon(str(BASE_DIR / "resource/images/close.svg")))
        self.button_close.setIconSize(QSize(20, 20))
        self.button_close.setFixedSize(50, self.HEIGHT)
        self.button_close.setFlat(True)
        self.button_close.setDefault(False)
        self.button_close.setStyleSheet("QPushButton {background-color: rgba(0, 0, 0, 0);border-radius: 5px; border-top-right-radius: 15px;} QPushButton:hover {background-color: rgba(255, 255, 255, 0.2);} QPushButton:pressed {background-color: rgba(255, 255, 255, 0.1);}")
        self.buttons_layout.addWidget(self.button_close)

    def setCloseEvent(self, func: Callable) -> None:
        self.button_close.clicked.connect(func)

    def setMinimizeEvent(self, func: Callable) -> None:
        self.button_minimize.clicked.connect(func)

    def setLogoutEvent(self, func: Callable) -> None:
        self.user_logout.clicked.connect(func)

    def headerMousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_start_position = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def headerMouseMoveEvent(self, event) -> None:
        if self._is_dragging:
            self.parent.move(event.globalPosition().toPoint() - self._drag_start_position)
            event.accept()

    def headerMouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton:
            self._is_dragging = False
            event.accept()

    def set_user(self, user: str | None) -> None:
        self._user = user
        self.user.setText(user if user is not None else "")
        self.user.setVisible(bool(user))
        self.user_logout.setVisible(bool(user))

    def set_logout_enabled(self, is_enabled: bool) -> None:
        self.user_logout.setEnabled(is_enabled)



class FooterComponent(BaseComponent):
    HEIGHT = 50

    def __init__(self, parent: QWidget) -> None:
        self.parent = parent
        self._widget = QFrame(parent)
        self._widget.setFixedSize(WindowSetup.WIDTH, self.HEIGHT)
        self._layout = QHBoxLayout(self._widget)
        self._layout.setContentsMargins(0, 0, 0, 0)
        # ---- copyright ----
        copy_right = QFrame(self._widget)
        copy_right.setFixedSize(150, 16)
        copy_right.setContentsMargins(0, 0, 0, 0)
        logo_image = QSvgWidget(str(BASE_DIR / "resource/images/copyright.svg"), copy_right)
        logo_image.setGeometry(0, 0, 150, 16)
        self._layout.addWidget(copy_right)


class MainComponent(QFrame):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFixedSize(WindowSetup.WIDTH - 10, WindowSetup.HEIGHT - (HeaderComponent.HEIGHT + FooterComponent.HEIGHT))
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def addWidget(self, widget: QWidget) -> None:
        self.layout.addWidget(widget)

    def resetStyle(self) -> None:
        self.setStyleSheet("background: none;")


class FileSelectorWidget(QFrame):
    HEIGHT = 120
    WIDTH = 400
    file_name: str | None = None


    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.layout = None
        self.initUI()

    def initUI(self):
        self.file_name = None
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setStyleSheet("background-color: #ffffff; border: 1px dashed #FF4D00; border-radius: 10px; padding: 0px;")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.create_file_select_button()
        self.setLayout(self.layout)

    def create_file_select_button(self):
        self.button = QPushButton(self)
        self.button.setFixedSize(self.WIDTH - 2, self.HEIGHT - 2)
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon = QIcon(str(BASE_DIR / "resource/images/folder.svg"))
        pixmap = icon.pixmap(64, 64)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_label = QLabel("Нажмите для выбора файла\nПоддерживаемые форматы XLS, XLSX")
        text_label.setStyleSheet("font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 14px; line-height: 20px; text-align: center; color: #707070;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout.addWidget(icon_label)
        button_layout.addWidget(text_label)

        self.button.setLayout(button_layout)
        self.button.setFlat(True)
        self.button.setStyleSheet("border: none;")
        self.button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.button.clicked.connect(self.openFileDialog)
        self.layout.addWidget(self.button)

    def openFileDialog(self):
        self.file_name, _ = QFileDialog.getOpenFileName(self, "Выбор файла", "", "Excel Files (*.xlsx *.xls)")
        if self.file_name:
            self.showSelectedFile()

    def showSelectedFile(self):
        self.layout.removeWidget(self.button)
        self.button.deleteLater()

        file_frame = QFrame(self)
        file_frame.setStyleSheet("background: #ffffff; border: 0.5px solid #464646; border-radius: 5px;")

        file_layout = QHBoxLayout(file_frame)
        file_layout.setContentsMargins(10, 10, 10, 10)
        file_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel(file_frame)
        icon = QIcon(str(BASE_DIR / "resource/images/excel.svg"))
        pixmap = icon.pixmap(32, 32)
        icon_label.setPixmap(pixmap)
        icon_label.setStyleSheet("background: none; border: none; border-radius: 0px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_layout.addWidget(icon_label)

        file_label = QLabel(self.file_name[self.file_name.rfind('/') + 1:], file_frame)
        file_label.setStyleSheet("background: none; border: none; border-radius: 0px; text-align: left; font-family: 'Inter'; font-style: normal; font-weight: 400; font-size: 14px; line-height: 20px; text-align: center; color: #707070;")
        file_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        file_layout.addWidget(file_label)

        self.remove_button = QPushButton(file_frame)
        self.remove_button.setStyleSheet("background: none; border: none; border-radius: 0px;")
        self.remove_button.setIcon(QIcon(str(BASE_DIR / "resource/images/close_red.svg")))
        self.remove_button.setFixedSize(32, 32)
        self.remove_button.setFlat(True)
        self.remove_button.setStyleSheet("border: none;")
        self.remove_button.clicked.connect(self.reset_widget)
        file_layout.addWidget(self.remove_button)
        self.layout.addWidget(file_frame)

    def reset_widget(self):
        self.file_name = None
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.create_file_select_button()

    def set_enable(self, is_enable: bool) -> None:
        try:
            self.button.setEnabled(is_enable)
        except Exception:
            pass
        try:
            self.button.setEnabled(is_enable)
        except Exception:
            pass


class Modal(QDialog):
    HEIGHT = 200
    WIDTH = 450

    def __init__(self, text: str, err: bool = False, parent=None):
        super().__init__(parent)
        self._is_dragging = False
        self._drag_start_position = None
        self.setWindowTitle("Error" if err else "Info")

        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        gradient = QRadialGradient(0.2969 * self.width(), 0.3345 * self.height(), 0.6446 * self.width(),
                                   0.2969 * self.width(), 0.3345 * self.height())
        gradient.setColorAt(0, QColor("#530303"))
        gradient.setColorAt(0.49, QColor("#2F1444"))
        gradient.setColorAt(1, QColor("#2D2D2D"))

        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon_label.setFixedSize(30, 30)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if err:
            icon_label.setStyleSheet("QLabel { color : red; font-size: 25px; }")
            icon_label.setText("⚠️")
        else:
            icon_label.setStyleSheet("QLabel { font-size: 25px; }")
            icon_label.setText("ℹ️")
        content_layout.addWidget(icon_label)

        message_label = QLabel(text)
        message_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        message_label.setStyleSheet("font-family: 'Inter'; font-style: normal; font-weight: 600; font-size: 13px; line-height: 18px; color: #FFFFFF;")
        message_label.setMaximumWidth(self.WIDTH - 80)
        content_layout.addWidget(message_label, alignment=Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("Продолжить")
        ok_button.setFixedSize(150, 30)
        ok_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        ok_button.setFlat(True)
        ok_button.setStyleSheet("QPushButton {background-color: #FF4D00; border-radius: 10px; font-family: 'Inter'; font-style: normal; font-weight: 700; font-size: 16px; line-height: 19px; color: #FFFFFF;} QPushButton:hover {background-color: #FF7337;} QPushButton:pressed {background-color: #E1632D;}")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(content_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._is_dragging:
            self.move(event.globalPosition().toPoint() - self._drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton:
            self._is_dragging = False
            event.accept()
