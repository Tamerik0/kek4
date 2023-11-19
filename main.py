import sqlite3
import sys
from random import randint

from PyQt5 import uic
from PyQt5.QtWidgets import *

from addEditCoffeeForm import Ui_Dialog
from ui import Ui_MainWindow


class MyWidget(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.add_form = None
        self.con = sqlite3.connect('coffee.sqlite')
        self.cur = self.con.cursor()
        # uic.loadUi('main.ui', self)
        self.setupUi(self)
        layout = QVBoxLayout(self.centralWidget())
        self.tableWidget = QTableWidget(self)
        layout.addWidget(self.tableWidget)
        self.add_button = QPushButton(self)
        layout.addWidget(self.add_button)
        self.add_button.clicked.connect(lambda: AddEditForm(None, self).exec())
        self.edit_button = QPushButton(self)
        layout.addWidget(self.edit_button)
        self.edit_button.clicked.connect(lambda: AddEditForm(self.tableWidget.currentRow() + 1, self).exec())
        self.update_table()

    def update_table(self):
        query = """SELECT * FROM Coffee"""
        data = self.cur.execute(query).fetchall()
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(len(data[0]))
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(
            ['id', 'название сорта', 'степень обжарки', 'молотый/в зернах', 'описание вкуса', 'цена', 'объем упаковки'])
        for i, row in enumerate(data):
            self.tableWidget.insertRow(i)
            for j, value in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))


class AddEditForm(Ui_Dialog, QDialog):
    def __init__(self, id, *args):
        super().__init__(*args)
        self.id = id
        # uic.loadUi('addEditCoffeeForm.ui', self)
        self.setupUi(self)
        if id is not None:
            data = self.parent().cur.execute("SELECT * FROM Coffee WHERE id = ?", [id]).fetchone()
            self.name.setText(data[1])
            self.degree_of_roasting.setText(data[2])
            self.comboBox.setCurrentText(data[3])
            self.description.setPlainText(data[4])
            self.cost.setText(str(data[5]))
            self.volume.setText(str(data[6]))

        def handler():
            data = [self.name.text(), self.degree_of_roasting.text(), self.comboBox.currentText(),
                    self.description.toPlainText(), self.cost.text(), self.volume.text()]
            try:
                data[-1] = float(data[-1])
                data[-2] = int(data[-2])
            except:
                return
            if self.id is None:
                self.parent().cur.execute("INSERT INTO Coffee VALUES (NULL,?,?,?,?,?,?)", data)
            else:
                data += [self.id]
                self.parent().cur.execute("UPDATE Coffee SET name = ?, degree_of_roasting = ?, \
                ground_beans = ?, description = ?, cost = ?, volume = ? WHERE id = ?", data)
            self.parent().con.commit()
            self.parent().update_table()
            self.accept()

        self.ok.clicked.connect(handler)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    app.exec()
