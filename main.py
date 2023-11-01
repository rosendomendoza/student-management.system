from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidget, \
    QTableWidgetItem, QDialog, QVBoxLayout, QLineEdit, QPushButton, QComboBox, \
    QToolBar, QStatusBar, QGridLayout, QLabel, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys
import sqlite3
import mysql.connector


class MainWindows(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        # Add File Menu with Add Student option
        file_menu_item = self.menuBar().addMenu("&File")
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student",
                                     self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Add Help Menu with About option
        help_menu_item = self.menuBar().addMenu("&Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu_item.addAction(about_action)

        # Add Edit Menu with Search Students option
        edit_menu_item = self.menuBar().addMenu("&Edit")
        search_student_action = QAction(QIcon("icons/search.png"),
                                        "Search Student", self)
        search_student_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_student_action)

        # Add Table Data
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)

        # Create and add a Tool Bar with icons
        tool_bar = QToolBar()
        tool_bar.setMovable(True)
        self.addToolBar(tool_bar)
        tool_bar.addAction(add_student_action)
        tool_bar.addAction(search_student_action)

        # Create a Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.table.cellClicked.connect(self.cell_clicked)

        self.setCentralWidget(self.table)

    def insert(self):
        self.dialog = InsertDialog()
        self.dialog.exec()

    def about(self):
        self.dialog = AboutDialog()
        self.dialog.exec()

    def search(self):
        self.dialog = SearchDialog()
        self.dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()
        self.remove_statusbar_buttons()

    def delete(self):
        print("Delete Student...")
        dialog = DeleteDialog()
        dialog.exec()
        self.remove_statusbar_buttons()

    def load_data(self):
        self.remove_statusbar_buttons()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        data = cursor.fetchall()
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(data):
            self.table.insertRow(row_num)
            for column_num, cell_data in enumerate(row_data):
                self.table.setItem(row_num, column_num,
                                   QTableWidgetItem(str(cell_data)))
        cursor.close()
        connection.close()

    def remove_statusbar_buttons(self):
        # Remove button if there are.
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

    def cell_clicked(self):
        # Avoid duplicate buttons in the status bar
        self.remove_statusbar_buttons()

        # Add  Edit and Delete button
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit)
        self.status_bar.addWidget(edit_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete)
        self.status_bar.addWidget(delete_button)


class DatabaseConnection():
    def __init__(self, host="localhost", user="root", password="ramp0726",
                 database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password,
                                             database=self.database)
        return connection


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get the selected  student data
        index = main_windows.table.currentRow()
        student_name = main_windows.table.item(index, 1).text()
        student_course = main_windows.table.item(index, 2).text()
        student_mobile = main_windows.table.item(index, 3).text()

        # New name
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # New Course
        self.course_combo = QComboBox()
        courses = ["Maths", "Astronomy", "Physics", "Biology"]
        index = courses.index(student_course)
        self.course_combo.addItems(courses)
        self.course_combo.setCurrentText(student_course)

        layout.addWidget(self.course_combo)

        # New Mobile
        self.student_mobile = QLineEdit(student_mobile)
        self.student_mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.student_mobile)

        # Add Button Update
        update_button = QPushButton("Register")
        update_button.clicked.connect(self.update_student_db)
        layout.addWidget(update_button)

        self.setLayout(layout)

    def update_student_db(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()

        name = self.student_name.text()
        course = self.course_combo.currentText()
        mobile = self.student_mobile.text()
        index = main_windows.table.currentRow()
        id_row = main_windows.table.item(index, 0).text()
        cursor.execute("UPDATE students "
                       "SET name = %s, course = %s, mobile = %s "
                       "WHERE id = %s", (name, course, mobile, id_row))
        connection.commit()
        cursor.close()
        connection.close()
        main_windows.load_data()
        self.close()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        content = """
        This is a Student Management System App
        created during "The Python Mega Course" 
        """
        self.setText(content)

        layout = QVBoxLayout()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want delete this entry?")
        yes = QPushButton("yes")
        no = QPushButton("No")
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        yes.clicked.connect(self.delete_student_db)
        no.clicked.connect(self.non_delete_student)

        self.setLayout(layout)

    def non_delete_student(self):
        main_windows.load_data()
        self.close()

    def delete_student_db(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()

        index = main_windows.table.currentRow()
        id_row = main_windows.table.item(index, 0).text()
        cursor.execute("DELETE FROM students WHERE id = %s",
                       (id_row,))
        connection.commit()
        cursor.close()
        connection.close()
        main_windows.load_data()
        self.close()

        confirmation_msg = QMessageBox()
        confirmation_msg.setWindowTitle("Success")
        confirmation_msg.setText("The record was deleted successfully")
        confirmation_msg.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add Student Name widgets
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add Course Combo widgets
        self.course_combo = QComboBox()
        courses = ["Maths", "Astronomy", "Physics", "Biology"]
        self.course_combo.addItems(courses)
        layout.addWidget(self.course_combo)

        # Add Mobile Student widgets
        self.student_mobile = QLineEdit()
        self.student_mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.student_mobile)

        # Add Button Submit widgets
        insert_button = QPushButton("Submit")
        insert_button.clicked.connect(self.insert_student_db)
        layout.addWidget(insert_button)

        self.setLayout(layout)

    def insert_student_db(self):
        name = self.student_name.text()
        course = self.course_combo.currentText()
        mobile = self.student_mobile.text()
        new_data = (name, course, mobile)
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) "
                       "VALUES (%s, %s, %s)", new_data)
        connection.commit()
        cursor.close()
        connection.close()
        main_windows.load_data()
        self.close()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedWidth(300)

        layout = QVBoxLayout()

        # Add Student Name widgets
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add Button Search widgets
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_student_db)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search_student_db(self):
        name = self.student_name.text()
        items = main_windows.table.findItems(name,
                                             Qt.MatchFlag.MatchContains)
        for item in items:
            main_windows.table.item(item.row(), 1).setSelected(True)

        self.close()


app = QApplication(sys.argv)
main_windows = MainWindows()
main_windows.show()
main_windows.load_data()
sys.exit(app.exec())
