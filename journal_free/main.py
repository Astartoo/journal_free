import sys
from typing import Callable

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QPainterPath, QPainter
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from client import NZClient, FileClient
from views.base import WindowSetup, HeaderComponent, FooterComponent, MainComponent, Modal, OperationStatus
from views.journal import JournalWindow
from views.login import LoginWindow
from views.main import MainWindow


class RequestWorker(QThread):
    finished = Signal(str)

    def __init__(self, parent: QWidget, func: Callable):
        super().__init__(parent)
        self.func = func

    def run(self):
        try:
            res = self.func()
            self.finished.emit(res)
        except Exception as e:
            self.finished.emit(f"Error: {e}")


class BaseWindow(QMainWindow):
    nz_client: NZClient

    def __init__(self):
        super().__init__()
        base = WindowSetup(self)
        self._load_header(base)
        self._load_main(base)
        self._load_footer(base)

    def _load_header(self, base: WindowSetup) -> None:
        self.header = HeaderComponent(self)
        self.header.setCloseEvent(self._close_program)
        self.header.setMinimizeEvent(self._minimize_window)
        self.header.setLogoutEvent(self.logout_event)
        base.addWidget(self.header.widget)

    def _load_footer(self, base: WindowSetup) -> None:
        footer = FooterComponent(self)
        base.addWidget(footer.widget)

    def _load_main(self, base: WindowSetup) -> None:
        self.main = MainComponent(self)
        base.addWidget(self.main)
        self.show_login_view()

    def show_login_view(self) -> None:
        self.login = LoginWindow(self.main)
        self.login.set_login_event(self.login_event)
        self.main.addWidget(self.login)

    def login_event(self, event: object) -> None:
        username = self.login.username
        password = self.login.password
        if username == '' or password == '':
            dialog = Modal('Введите имя пользователя или пароль')
            dialog.exec()
            return
        self.nz_client = NZClient(username, password)
        self.login.set_enabled_form(False)
        self.login.loading(True)
        worker = RequestWorker(parent=self.login, func=self.nz_client.authenticate)
        worker.finished.connect(self.login_event_finished)
        worker.start()

    def login_event_finished(self, result: str) -> None:
        self.login.set_enabled_form(True)
        self.login.loading(False)
        if self.nz_client.is_auth:
            self.header.set_user(self.nz_client.user)
            self.main.layout.removeWidget(self.login)
            self.login.deleteLater()
            del self.login
            self.show_main_view()
        else:
            dialog = Modal(result, err=True)
            dialog.exec()

    def logout_event(self):
        if self.nz_client.is_auth:
            for i in reversed(range(self.main.layout.count())):
                widget = self.main.layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            self.header.set_user(None)
            self.main.resetStyle()
            del self.nz_client
            self.show_login_view()

    def show_main_view(self) -> None:
        self.header.set_logout_enabled(False)
        self.main_view = MainWindow(self.main)
        self.main.addWidget(self.main_view)
        self.main_view.loading()
        worker = RequestWorker(parent=self.main_view, func=self.nz_client.get_journals)
        worker.finished.connect(self.main_view_finished)
        worker.start()

    def main_view_finished(self, result: str) -> None:
        self.header.set_logout_enabled(True)
        self.main_view.load_terms(self.nz_client.terms, self.nz_client.selected_term)
        self.main_view.load_journals(self.nz_client.journals, self.open_journal)
        self.main_view.termChangeEvent(self.change_term)
        self.main_view.termChangeEnabled(True)

    def change_term(self, index: int) -> None:
        self.main_view.termChangeEnabled(False)
        self.header.set_logout_enabled(False)
        term_id = self.main_view.get_term_value(index)
        self.main_view.loading()
        worker = RequestWorker(parent=self.main_view, func=lambda: self.nz_client.change_term(term_id))
        worker.finished.connect(self.main_view_finished)
        worker.start()

    def open_journal(self, subject: str, class_: dict) -> Callable:
        @Slot()
        def handler():
            self.main_view.deleteLater()
            self.show_journal_view(subject, class_)
        return handler

    def show_journal_view(self, subject: str, class_: dict) -> None:
        self.journal_view = JournalWindow(self.main)
        self.journal_view.setBackEvent(self.back_to_main_view)
        self.main.addWidget(self.journal_view)
        self.journal_view.load_content(subject, class_, self.nz_client.selected_term['name'])
        self.journal_view.setFillEvent(self.fill_journal)  # TODO: check

    def back_to_main_view(self) -> None:
        self.journal_view.deleteLater()
        del self.journal_view
        self.show_main_view()

    def fill_journal(self) -> None:
        if self.journal_view.file_path is None:
            dialog = Modal('Выберите файл')
            dialog.exec()
            return
        file = FileClient(self.journal_view.file_path)
        if not file.valid:
            dialog = Modal('Шаблон файла не верный.\nТема или номер урока не могут быть пустыми.\nТак же возможно есть пропуски в строках или\nсимволы ниже основной таблицы.')
            dialog.exec()
            return
        self.journal_view.set_enabled(False)
        self.journal_view.loading(True)
        self.header.set_logout_enabled(False)
        worker = RequestWorker(parent=self.journal_view, func=lambda: self.fill_journal_request(file))
        worker.finished.connect(self.fill_journal_finished)
        worker.start()

    def fill_journal_request(self, file: FileClient) -> str | None:
        self.nz_client.find_lessons_url(self.journal_view.journal_url)
        index = 0
        if self.nz_client.lessons_url is None:
            return OperationStatus.ERROR
        elif self.nz_client.lessons_url == 0:
            return OperationStatus.NO_LESSONS
        for lesson_url in self.nz_client.lessons_url:
            if index < file.count:
                status = self.nz_client.add_topic(lesson_url, file.validated_data[index])
                if status != 200:
                    return OperationStatus.ERROR
            index += 1
        return OperationStatus.SUCCESS

    def fill_journal_finished(self, result) -> None:
        self.journal_view.set_enabled(True)
        self.journal_view.loading(False)
        self.header.set_logout_enabled(True)

        if result == OperationStatus.SUCCESS:
            dialog = Modal('Журнал заполнен успешно')
            dialog.exec()

        elif result == OperationStatus.NO_LESSONS:
            dialog = Modal('На nz.ua не создано ниодного урока', err=True)
            dialog.exec()

        elif result == OperationStatus.ERROR:
            dialog = Modal('Ошибка сервера.', err=True)
            dialog.exec()

    # def parse_journal(self) -> None:
    #     self.journal_view.set_enabled(False)
    #     self.journal_view.loading(True)
    #     self.header.set_logout_enabled(False)
    #     worker = RequestWorker(parent=self.journal_view, func=self.parse_journal_request)
    #     worker.finished.connect(self.parse_journal_finished)
    #     worker.start()
    #
    # def parse_journal_request(self) -> str:
    #     self.nz_client.find_lessons_url(self.journal_view.journal_url)
    #     if self.nz_client.lessons_url is None:
    #         return OperationStatus.ERROR
    #     elif self.nz_client.lessons_url == 0:
    #         return OperationStatus.NO_LESSONS
    #     journal_data = []
    #     for lesson_url in self.nz_client.lessons_url:
    #         _data = self.nz_client.parse_lesson_data(lesson_url)
    #         if _data['status_code'] != 200:
    #             return OperationStatus.ERROR
    #         _data.pop('status_code')
    #         # if _data['topic'] == '' and _data['number'] == '' and _data['homework'] == '':
    #         #     break
    #         journal_data.append(_data)
    #     file = FileClient.create(f"{self.journal_view.class_}.xlsx", journal_data)
    #     return OperationStatus.SUCCESS
    #
    # def parse_journal_finished(self, result: str):
    #     self.journal_view.set_enabled(True)
    #     self.journal_view.loading(False)
    #     self.header.set_logout_enabled(True)
    #
    #     if result == OperationStatus.SUCCESS:
    #         dialog = Modal('Журнал скачан успешно')
    #         dialog.exec()
    #
    #     elif result == OperationStatus.NO_LESSONS:
    #         dialog = Modal('На nz.ua не создано ниодного урока', err=True)
    #         dialog.exec()
    #
    #     elif result == OperationStatus.ERROR:
    #         dialog = Modal('Ошибка сервера.', err=True)
    #         dialog.exec()


    def paintEvent(self, event):
        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillPath(path, self.palette().window())

        # Draw the shadow
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.palette().window())
        painter.drawRoundedRect(self.rect(), 15, 15)

    def _close_program(self):
        self.close()

    def _minimize_window(self):
        self.showMinimized()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BaseWindow()
    window.show()
    sys.exit(app.exec())
