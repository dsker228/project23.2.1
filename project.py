import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTime, QTimer
from PyQt5.QtWidgets import QLineEdit, QComboBox, QApplication, QWidget, QLCDNumber

import requests
from bs4 import BeautifulSoup


class ConnectionErr(QWidget):
    """
    Класс ошибки соединения
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ошибка')
        self.setGeometry(500, 450, 500, 50)
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setGeometry(0, 0, 500, 50)
        # изменение шрифта текста
        self.lineEdit.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))
        self.lineEdit.setText('Ошибка подключения')
        self.lineEdit.setEnabled(False)


# основной класс программы
class UiDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Конвентер валют')
        self.setGeometry(300, 300, 500, 350)

        self.currencies = self._get_currency()
        self.currencies['Российский рубль'] = 1

        # Виджет часов
        self.clock = QLCDNumber(self)
        self.clock.setSegmentStyle(QLCDNumber.Filled)
        self.clock.setWindowTitle("Digital Clock")
        self.clock.resize(150, 60)
        self.clock.move(160, 20)

        # Таймер для мигания точек на часах
        self.timer = QTimer(self.clock)
        self.timer.timeout.connect(self.show_time)
        self.timer.start(1000)

        # Верхний выпадающий список валют
        self.combo = QComboBox(self)
        self.combo.addItems(i for i in self.currencies)
        self.combo.setGeometry(31, 31, 150, 31)
        self.combo.move(260, 120)

        # Нижний выпадающий список валют
        self.combo_2 = QComboBox(self)
        self.combo_2.addItems(i for i in self.currencies)
        self.combo_2.setGeometry(31, 31, 150, 31)
        self.combo_2.move(260, 200)

        # Поле для ввода
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(60, 120, 201, 31))
        self.lineEdit.setText('0')

        # Поле для вывода
        self.lineEdit_2 = QLineEdit(self)
        self.lineEdit_2.setGeometry(QtCore.QRect(60, 200, 201, 31))
        self.lineEdit_2.setText('0')
        # Метод, запрещающий изменять текст
        self.lineEdit_2.setReadOnly(True)

        self.lineEdit.textEdited.connect(self.work)
        self.combo.currentIndexChanged.connect(self.work)
        self.combo_2.currentIndexChanged.connect(self.work)
        self.show_time()

    def show_time(self):
        """
        Отображение времени
        """
        time = QTime.currentTime()
        text = time.toString('hh:mm')
        if (time.second() % 2) == 0:
            text = text[:2] + ' ' + text[3:]
        self.clock.display(text)

    @staticmethod
    def _get_html(url):
        '''
        Определение браузеров, в которых будет работать программа
        '''
        browser = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) ' + \
                  'AppleWebKit/537.36 (KHTML, like Gecko) ' + \
                  'Chrome/71.0.3578.98 Safari/537.3'
        headers = {'User-Agent': browser}
        # проверка соединения
        try:
            r = requests.get(url=url, headers=headers)
        except requests.ConnectionError:
            app_err = QApplication(sys.argv)
            err = ConnectionErr()
            err.show()
            sys.exit(app_err.exec())
        return r.text

    def _get_currency(self):
        '''
        Парсинг
        '''
        url = "https://ru.myfin.by/currency/cb-rf/"
        # получение ссылки
        html = self._get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        # получение нужной информации в коде сайта
        facts = soup.find("table", class_="converter-icons content_table head_row_one default-table").find(
            "tbody").find_all("tr")
        cards = []

        for tr in facts:
            td = tr.find_all("td")
            tmp = []
            for item in td:
                tmp.append(item.text.strip())
            cards.append(tmp)
        temp = {}
        for i in cards:
            temp[i[0]] = float(i[1])
        return temp

    def work(self):
        try:
            value = float(self.lineEdit.text())
        except ValueError:
            # Если введено некорректное значение
            self.lineEdit_2.setText('Введите верное значение')
        else:
            # Если введено отрицательное значение
            if value < 0:
                self.lineEdit_2.setText('Введите верное значение')
            else:
                tmp = value / self.currencies[self.combo_2.currentText()] * \
                      self.currencies[self.combo.currentText()]
                self.lineEdit_2.setText(f"{tmp:.2f}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UiDialog()
    ex.show()
    sys.exit(app.exec())